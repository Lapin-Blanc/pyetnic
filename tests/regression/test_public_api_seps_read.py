"""Regression tests for the stable SEPS read API.

Covers the symbols listed as **stable** under ``pyetnic.seps`` in
``docs/PUBLIC_API_SURFACE.md``: read functions (``lire_etudiant``,
``rechercher_etudiants``), exceptions (``SepsEtnicError``,
``SepsAuthError``, ``NissMutationError``, ``TropDeResultatsError``),
and the read-side dataclasses.

Mock-based, no network. SEPS construction APIs are out of scope here.
"""

import inspect

import pytest

import pyetnic.seps
from pyetnic.seps import (
    Etudiant,
    EtudiantDetails,
    NissMutationError,
    SepsAdresse,
    SepsAuthError,
    SepsDeces,
    SepsEtnicError,
    SepsLocalite,
    SepsNaissance,
    TropDeResultatsError,
    lire_etudiant,
    rechercher_etudiants,
)

from .fixtures.seps_responses import (
    CANONICAL_LIRE_ETUDIANT_RESPONSE,
    CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE,
    CANONICAL_RECHERCHER_ETUDIANTS_SINGLE_RESPONSE,
    EMPTY_RECHERCHER_ETUDIANTS_RESPONSE,
    GENERIC_SEPS_ERROR_RESPONSE,
    LIRE_ETUDIANT_NONE_RESPONSE,
    NISS_MUTATION_ERROR_RESPONSE,
    SEPS_AUTH_ERROR_RESPONSE,
    TROP_DE_RESULTATS_ERROR_RESPONSE,
)

# ===========================================================================
# lire_etudiant
# ===========================================================================


class TestLireEtudiant:
    def test_signature(self):
        sig = inspect.signature(lire_etudiant)
        assert list(sig.parameters) == ["cf_num", "from_date"]
        assert sig.parameters["from_date"].default is None

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LIRE_ETUDIANT_RESPONSE
        et = lire_etudiant("1234567-89")

        assert isinstance(et, Etudiant)
        assert et.cfNum == "1234567-89"
        assert isinstance(et.rnDetails, EtudiantDetails)
        assert et.rnDetails.niss == "85010112345"
        assert et.rnDetails.nom == "Dupont"
        assert isinstance(et.rnDetails.naissance, SepsNaissance)
        assert isinstance(et.rnDetails.naissance.localite, SepsLocalite)
        assert isinstance(et.rnDetails.adresse, SepsAdresse)
        assert et.rnDetails.deces is None
        assert et.cfwbDetails is None

    def test_none_response(self, mock_soap_call):
        mock_soap_call.return_value = LIRE_ETUDIANT_NONE_RESPONSE
        assert lire_etudiant("1234567-89") is None

    def test_request_shape_default(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LIRE_ETUDIANT_RESPONSE
        lire_etudiant("1234567-89")
        call = mock_soap_call.call_args
        assert call.args[0] == "lireEtudiant"
        assert call.kwargs == {"cfNum": "1234567-89"}

    def test_request_shape_with_from_date(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LIRE_ETUDIANT_RESPONSE
        lire_etudiant("1234567-89", from_date="2024-01-01")
        call = mock_soap_call.call_args
        assert call.kwargs == {"cfNum": "1234567-89", "fromDate": "2024-01-01"}


# ===========================================================================
# rechercher_etudiants
# ===========================================================================


class TestRechercherEtudiants:
    def test_signature(self):
        sig = inspect.signature(rechercher_etudiants)
        assert list(sig.parameters) == [
            "niss",
            "nom",
            "prenom",
            "date_naissance",
            "sexe",
            "force_rn_flag",
        ]
        for p in sig.parameters.values():
            assert p.default is None

    def test_happy_path_by_niss(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE
        result = rechercher_etudiants(niss="85010112345")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Etudiant)

    def test_request_shape_by_niss(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE
        rechercher_etudiants(niss="85010112345")
        call = mock_soap_call.call_args
        assert call.args[0] == "rechercherEtudiants"
        assert call.kwargs == {"niss": "85010112345"}

    def test_happy_path_by_nom(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE
        result = rechercher_etudiants(nom="Dupont", prenom="Jean", sexe="M")
        assert len(result) == 1

    def test_request_shape_by_nom(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE
        rechercher_etudiants(
            nom="Dupont",
            prenom="Jean",
            date_naissance="1985",
            sexe="M",
            force_rn_flag=True,
        )
        call = mock_soap_call.call_args
        assert call.kwargs == {
            "nom": "Dupont",
            "prenom": "Jean",
            "dateNaissance": "1985",
            "sexe": "M",
            "forceRnFlag": True,
        }

    def test_zeep_returns_single_dict_not_list(self, mock_soap_call):
        """zeep returns a dict (not list) when there's exactly one match."""
        mock_soap_call.return_value = CANONICAL_RECHERCHER_ETUDIANTS_SINGLE_RESPONSE
        result = rechercher_etudiants(niss="85010112345")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_empty_response(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_RECHERCHER_ETUDIANTS_RESPONSE
        assert rechercher_etudiants(niss="00000000000") == []

    def test_no_args_raises_value_error(self, mock_soap_call):
        with pytest.raises(ValueError):
            rechercher_etudiants()
        # The SOAP layer must not be reached when validation fails
        assert mock_soap_call.call_count == 0

    # -- Typed exceptions -----------------------------------------------------

    def test_niss_mutation_raises(self, mock_soap_call):
        mock_soap_call.return_value = NISS_MUTATION_ERROR_RESPONSE
        with pytest.raises(NissMutationError) as exc_info:
            rechercher_etudiants(niss="11111111111")
        assert exc_info.value.ancien_niss == "11111111111"
        assert exc_info.value.nouveau_niss == "99887766554"
        assert exc_info.value.code == "30401"
        # Subclass relationship preserved
        assert isinstance(exc_info.value, SepsEtnicError)

    def test_trop_de_resultats_raises(self, mock_soap_call):
        mock_soap_call.return_value = TROP_DE_RESULTATS_ERROR_RESPONSE
        with pytest.raises(TropDeResultatsError) as exc_info:
            rechercher_etudiants(nom="Dupont")
        assert exc_info.value.code == "30501"
        assert isinstance(exc_info.value, SepsEtnicError)

    def test_seps_auth_error_raises(self, mock_soap_call):
        mock_soap_call.return_value = SEPS_AUTH_ERROR_RESPONSE
        with pytest.raises(SepsAuthError) as exc_info:
            rechercher_etudiants(nom="Dupont")
        assert exc_info.value.code == "30550"
        assert isinstance(exc_info.value, SepsEtnicError)

    def test_generic_error_raises_base_class(self, mock_soap_call):
        mock_soap_call.return_value = GENERIC_SEPS_ERROR_RESPONSE
        with pytest.raises(SepsEtnicError) as exc_info:
            rechercher_etudiants(nom="Dupont")
        assert exc_info.value.code == "30999"
        # Must NOT be one of the specialized subclasses
        assert not isinstance(exc_info.value, (NissMutationError, TropDeResultatsError, SepsAuthError))


# ===========================================================================
# Stable dataclasses and exceptions — smoke import test
# ===========================================================================


def test_stable_seps_symbols_importable():
    """Each stable SEPS symbol must be reachable via ``pyetnic.seps.X``."""
    stable_names = [
        # Functions
        "lire_etudiant",
        "rechercher_etudiants",
        # Exceptions
        "SepsEtnicError",
        "SepsAuthError",
        "NissMutationError",
        "TropDeResultatsError",
        # Read dataclasses
        "Etudiant",
        "EtudiantDetails",
        "SepsAdresse",
        "SepsLocalite",
        "SepsNaissance",
        "SepsDeces",
    ]
    for name in stable_names:
        assert hasattr(pyetnic.seps, name), f"Missing stable export: pyetnic.seps.{name}"


def test_seps_exception_hierarchy():
    """The SEPS exception hierarchy must remain stable for callers using ``except``."""
    assert issubclass(SepsAuthError, SepsEtnicError)
    assert issubclass(NissMutationError, SepsEtnicError)
    assert issubclass(TropDeResultatsError, SepsEtnicError)
    assert issubclass(SepsEtnicError, Exception)
