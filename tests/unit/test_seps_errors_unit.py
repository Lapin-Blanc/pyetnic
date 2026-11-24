"""One SEPS response check for every operation (issue #20).

Answers are shaped like the ones the ETNIC manuals document (Enregistrer
Étudiants 2.3, Enregistrer / Recherche Inscriptions 2.4) and the one production
sent on 2026-11-10 (``success=false`` with only the warning 30101). Identifiers
are fictitious.
"""

from __future__ import annotations

import logging

import pytest

from pyetnic.exceptions import EtnicBusinessError, EtnicNotFoundError, EtnicValidationError
from pyetnic.services.enregistrer_etudiant import EnregistrerEtudiantService
from pyetnic.services.inscriptions import InscriptionsService
from pyetnic.services.models import (
    EtudiantDetailsSave,
    InscriptionInputDataSave,
    InscriptionInputSave,
    SepsAdmission,
    SepsSpecificiteSave,
    SepsUESave,
)
from pyetnic.services.seps import RechercheEtudiantsService
from pyetnic.services.seps_errors import (
    NissMutationError,
    SepsAucuneModificationError,
    SepsConflictError,
    SepsDoublonsError,
    SepsEtnicError,
    SepsEtudiantExisteError,
    SepsEtudiantInconnuError,
    SepsInscriptionExisteError,
    SepsNotFoundError,
    SepsUeInconnueError,
    SepsValidationError,
    TropDeResultatsError,
    check_seps_response,
)

VERSION = {"code": "2.4.6", "description": "version"}


def answer(success, *, error=(), warning=(), info=(), response=None, request_id=None):
    body = {"success": success, "messages": {"error": list(error), "warning": list(warning), "info": list(info)}}
    if response is not None:
        body["response"] = response
    result = {"body": body}
    if request_id:
        result["header"] = {"requestId": request_id}
    return result


def msg(code, description=""):
    return {"code": code, "description": description}


def inscription_payload():
    return InscriptionInputDataSave(
        cfNum="1234567-89",
        idEtab=1234,
        idImplantation=5678,
        codePostalLieuCours="1000",
        inscription=InscriptionInputSave(
            dateInscription="2026-09-25",
            statut="DE",
            anneeScolaire=2026,
            ue=SepsUESave(noAdministratif=100, noOrganisation=2),
            specificite=SepsSpecificiteSave(admission=SepsAdmission(codeAdmission="AUTRE", valorisationAcquis="C10")),
        ),
    )


# ---------------------------------------------------------------------------
# The warning-only refusal seen in production (the bug of issue #20)
# ---------------------------------------------------------------------------


class TestWarningOnlyRefusal:
    def test_enregistrer_inscription_raises_on_30101_warning(self, monkeypatch):
        service = InscriptionsService()
        monkeypatch.setattr(
            service._enregistrer,
            "call_service",
            lambda *a, **k: answer(
                False,
                warning=[msg("30101", "Les informations ne correspondent pas à une UE existante")],
                info=[VERSION],
            ),
        )
        with pytest.raises(SepsUeInconnueError) as exc_info:
            service.enregistrer_inscription(inscription_payload())
        error = exc_info.value
        assert error.code == "30101"
        assert isinstance(error, SepsNotFoundError)
        assert isinstance(error, EtnicNotFoundError)
        assert isinstance(error, EtnicBusinessError)

    def test_check_raises_on_any_warning_when_success_is_false(self):
        with pytest.raises(SepsEtnicError) as exc_info:
            check_seps_response(answer(False, warning=[msg("30999", "inattendu")]))
        assert exc_info.value.code == "30999"


# ---------------------------------------------------------------------------
# Reads: "nothing found" codes give an empty result
# ---------------------------------------------------------------------------


class TestNothingFound:
    def test_rechercher_inscriptions_30103_warning_is_empty(self, monkeypatch):
        service = InscriptionsService()
        monkeypatch.setattr(
            service._recherche,
            "call_service",
            lambda *a, **k: answer(False, warning=[msg("30103", "No inscription found for those criteria")]),
        )
        assert service.rechercher_inscriptions(annee_scolaire=2026, etab_id=1234) == []

    def test_rechercher_inscriptions_bad_criteria_raises(self, monkeypatch):
        service = InscriptionsService()
        monkeypatch.setattr(
            service._recherche,
            "call_service",
            lambda *a, **k: answer(False, error=[msg("30036", "Invalid input parameters combination")]),
        )
        with pytest.raises(SepsValidationError):
            service.rechercher_inscriptions(etab_id=1234)

    def test_lire_etudiant_not_found_warning_is_none(self, monkeypatch):
        service = RechercheEtudiantsService()
        monkeypatch.setattr(
            service.client_manager, "call_service", lambda *a, **k: answer(False, warning=[msg("30110", "")])
        )
        assert service.lire_etudiant("1234567-89") is None

    def test_a_blocking_refusal_wins_over_a_not_found_code(self):
        result = answer(False, error=[msg("30115", "aucun"), msg("30550", "certificat")])
        with pytest.raises(SepsEtnicError) as exc_info:
            check_seps_response(result, not_found=frozenset({"30115"}))
        assert exc_info.value.code == "30550"

    def test_not_found_code_raises_on_an_operation_that_does_not_declare_it(self):
        with pytest.raises(SepsNotFoundError):
            check_seps_response(answer(False, warning=[msg("30103", "")]))


# ---------------------------------------------------------------------------
# Successes
# ---------------------------------------------------------------------------


class TestSuccess:
    def test_success_returns_false(self):
        assert check_seps_response(answer(True, info=[msg("201", "The student is registered."), VERSION])) is False

    def test_success_warning_is_logged_not_raised(self, caplog):
        result = answer(True, warning=[msg("30051", "Ok création mais inscrit dans plus de 4 Ues")])
        with caplog.at_level(logging.WARNING, logger="pyetnic.services.seps_errors"):
            assert check_seps_response(result) is False
        assert "30051" in caplog.text

    def test_success_false_with_info_200_is_a_success(self, monkeypatch):
        """The manual's modifierEtudiant example: success=false, info 200 'changes applied'."""
        service = EnregistrerEtudiantService()
        monkeypatch.setattr(
            service.client_manager,
            "call_service",
            lambda *a, **k: answer(
                False,
                info=[msg("200", "The student changes have been applied.")],
                response={"etudiantDetails": {"cfNum": "1234567-89"}},
            ),
        )
        result = service.modifier_etudiant(cf_num="1234567-89", etudiant_details=EtudiantDetailsSave(nom="DUPONT"))
        assert result.etudiant.cfNum == "1234567-89"
        assert result.code == "200"

    def test_version_message_alone_is_not_a_success(self):
        with pytest.raises(SepsEtnicError) as exc_info:
            check_seps_response(answer(False, info=[VERSION]))
        assert exc_info.value.code is None


# ---------------------------------------------------------------------------
# Typed refusals and what their description carries
# ---------------------------------------------------------------------------


class TestTypedRefusals:
    def test_30201_carries_the_existing_cf_number(self):
        result = answer(False, error=[msg("30201", "The student you are trying to register already exists (1234567-89).")])
        with pytest.raises(SepsEtudiantExisteError) as exc_info:
            check_seps_response(result)
        assert exc_info.value.cf_num == "1234567-89"
        assert isinstance(exc_info.value, SepsConflictError)

    def test_30203_carries_the_listed_cf_numbers(self):
        description = "The student you are trying to register already exists ([1111111-11;2222222-2;3333333-3])."
        with pytest.raises(SepsDoublonsError) as exc_info:
            check_seps_response(answer(False, error=[msg("30203", description)]))
        assert exc_info.value.cf_nums == ["1111111-11", "2222222-2", "3333333-3"]
        assert exc_info.value.niss == []

    def test_30204_carries_niss_without_mistaking_them_for_cf_numbers(self):
        description = "Plusieurs personnes trouvées : 900101-123-45, 91020212345"
        with pytest.raises(SepsDoublonsError) as exc_info:
            check_seps_response(answer(False, error=[msg("30204", description)]))
        assert exc_info.value.niss == ["900101-123-45", "91020212345"]
        assert exc_info.value.cf_nums == []

    def test_30401_carries_the_new_niss(self):
        result = answer(False, error=[msg("30401", "Mutation NISS : le nouveau NISS 91020212345")])
        with pytest.raises(NissMutationError) as exc_info:
            check_seps_response(result, ancien_niss="90010112345")
        assert exc_info.value.ancien_niss == "90010112345"
        assert exc_info.value.nouveau_niss == "91020212345"

    def test_30503_is_too_many_results(self):
        with pytest.raises(TropDeResultatsError) as exc_info:
            check_seps_response(answer(False, error=[msg("30503", "Erreur si trop de résultats")]))
        assert exc_info.value.code == "30503"

    @pytest.mark.parametrize(
        "code", ["30010", "30013", "30024", "30033", "30042", "30043", "30046", "30047", "30048", "30070", "30079", "30076"]
    )
    def test_bad_request_codes_are_validation_errors(self, code):
        with pytest.raises(SepsValidationError) as exc_info:
            check_seps_response(answer(False, error=[msg(code, "refus")]))
        assert isinstance(exc_info.value, EtnicValidationError)

    @pytest.mark.parametrize(
        "code, cls",
        [
            ("30100", SepsUeInconnueError),
            ("30011", SepsEtudiantInconnuError),
            ("30120", SepsEtudiantInconnuError),
            ("30102", SepsNotFoundError),
            ("30200", SepsInscriptionExisteError),
        ],
    )
    def test_not_found_and_conflict_codes(self, code, cls):
        with pytest.raises(cls):
            check_seps_response(answer(False, error=[msg(code, "")]))

    def test_30443_no_change_as_error_or_as_info(self):
        for result in (
            answer(False, error=[msg("30443", "No changes detected")]),
            answer(False, info=[msg("30443", "No changes detected.")]),
        ):
            with pytest.raises(SepsAucuneModificationError):
                check_seps_response(result)

    def test_unknown_code_is_the_base_class(self):
        with pytest.raises(SepsEtnicError) as exc_info:
            check_seps_response(answer(False, error=[msg("50509", "erreur interne")]))
        assert type(exc_info.value) is SepsEtnicError

    def test_request_id_is_kept(self):
        result = answer(False, error=[msg("30200", "")], request_id="0129a908-ccd8-47bb-a116-5437eb496d48")
        with pytest.raises(SepsEtnicError) as exc_info:
            check_seps_response(result)
        assert exc_info.value.request_id == "0129a908-ccd8-47bb-a116-5437eb496d48"


def test_historical_constructors_still_work():
    assert SepsEtnicError("30999", "x").code == "30999"
    assert TropDeResultatsError().code == "30501"
    error = NissMutationError("90010112345", "91020212345")
    assert (error.code, error.ancien_niss, error.nouveau_niss) == ("30401", "90010112345", "91020212345")
