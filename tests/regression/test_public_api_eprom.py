"""Regression tests for the stable EPROM public API.

Covers every function listed as stable in ``docs/PUBLIC_API_SURFACE.md``.
Tests are mock-based (no network) and capture the *current* observable
behavior, not aspired behavior. If a Sprint 1+ refactoring changes the
contract (e.g. raises instead of returning None), update the corresponding
test in the same commit.

Each function gets:
- a signature test (parameter names, kinds, defaults)
- a happy-path return-type test against a canonical SOAP dict
- an edge-case test (empty / None response)
- a request-shape test verifying the dict sent to ``call_service``,
  including the critical ``implId`` exclusion rule for Lire/Modifier/Supprimer.
"""

import inspect
from datetime import date

import pytest

import pyetnic.eprom
from pyetnic.eprom import (
    Doc1PopulationLineSave,
    Doc1PopulationListSave,
    Doc2ActiviteEnseignementLineSave,
    Doc2ActiviteEnseignementListSave,
    Doc2InterventionExtLineSave,
    Doc2InterventionExtListSave,
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    Formation,
    FormationDocument1,
    FormationDocument2,
    FormationDocument3,
    FormationsListeResult,
    Organisation,
    OrganisationApercu,
    OrganisationId,
    StatutDocument,
    approuver_document_1,
    creer_organisation,
    lire_document_1,
    lire_document_2,
    lire_document_3,
    lire_organisation,
    lister_formations,
    lister_formations_organisables,
    modifier_document_1,
    modifier_document_2,
    modifier_document_3,
    modifier_organisation,
    supprimer_organisation,
)

from .fixtures.eprom_responses import (
    CANONICAL_DOCUMENT1_APPROUVE_RESPONSE,
    CANONICAL_DOCUMENT1_RESPONSE,
    CANONICAL_DOCUMENT2_RESPONSE,
    CANONICAL_DOCUMENT3_RESPONSE,
    CANONICAL_LISTER_FORMATIONS_ORGANISABLES_RESPONSE,
    CANONICAL_LISTER_FORMATIONS_RESPONSE,
    CANONICAL_ORGANISATION_RESPONSE,
    EMPTY_FORMATIONS_LISTE_RESPONSE,
    EMPTY_RESPONSE,
    SUCCESS_FALSE_RESPONSE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQ_ID_FIELDS = {"anneeScolaire", "etabId", "numAdmFormation", "numOrganisation"}


def _org_id(num_org: int = 1, with_impl: bool = False) -> OrganisationId:
    return OrganisationId(
        anneeScolaire="2024-2025",
        etabId=3052,
        numAdmFormation=328,
        numOrganisation=num_org,
        implId=6050 if with_impl else None,
    )


# ===========================================================================
# FormationsListeService
# ===========================================================================


class TestListerFormations:
    def test_signature(self):
        sig = inspect.signature(lister_formations)
        params = sig.parameters
        assert set(params) == {"annee_scolaire", "etab_id", "impl_id"}
        for p in params.values():
            assert p.default is None

    def test_happy_path_returns_formations_liste_result(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LISTER_FORMATIONS_RESPONSE
        result = lister_formations(annee_scolaire="2024-2025", etab_id=3052, impl_id=6050)

        assert isinstance(result, FormationsListeResult)
        assert result.success is True
        assert bool(result) is True
        assert len(result) == 2
        assert all(isinstance(f, Formation) for f in result)

        first = result.formations[0]
        assert first.numAdmFormation == 328
        assert first.libelleFormation == "Formation Test 1"
        assert first.codeFormation == "F328"
        assert len(first.organisations) == 1
        org = first.organisations[0]
        assert isinstance(org, OrganisationApercu)
        assert org.id.numOrganisation == 1
        assert org.dateDebutOrganisation == date(2024, 9, 2)
        assert isinstance(org.statutDocumentOrganisation, StatutDocument)

    def test_empty_response(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_FORMATIONS_LISTE_RESPONSE
        result = lister_formations()
        assert result.success is True
        assert len(result) == 0

    def test_error_response_returns_failure(self, mock_soap_call):
        mock_soap_call.return_value = SUCCESS_FALSE_RESPONSE
        result = lister_formations()
        assert result.success is False
        assert result.formations == []

    def test_request_shape(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LISTER_FORMATIONS_RESPONSE
        lister_formations(annee_scolaire="2024-2025", etab_id=3052, impl_id=6050)

        assert mock_soap_call.call_count == 1
        call = mock_soap_call.call_args
        assert call.args[0] == "ListerFormations"
        assert call.kwargs == {
            "anneeScolaire": "2024-2025",
            "etabId": 3052,
            "implId": 6050,
        }


class TestListerFormationsOrganisables:
    def test_signature(self):
        sig = inspect.signature(lister_formations_organisables)
        params = sig.parameters
        assert set(params) == {"annee_scolaire", "etab_id", "impl_id"}

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LISTER_FORMATIONS_ORGANISABLES_RESPONSE
        result = lister_formations_organisables(annee_scolaire="2024-2025", etab_id=3052, impl_id=6050)

        assert isinstance(result, FormationsListeResult)
        assert result.success is True
        assert len(result) == 2
        assert all(f.organisations == [] for f in result)

    def test_empty_response(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_FORMATIONS_LISTE_RESPONSE
        result = lister_formations_organisables()
        assert result.success is True
        assert len(result) == 0

    def test_request_shape(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_LISTER_FORMATIONS_ORGANISABLES_RESPONSE
        lister_formations_organisables(annee_scolaire="2024-2025", etab_id=3052, impl_id=6050)

        call = mock_soap_call.call_args
        assert call.args[0] == "ListerFormationsOrganisables"
        assert call.kwargs == {
            "anneeScolaire": "2024-2025",
            "etabId": 3052,
            "implId": 6050,
        }


# ===========================================================================
# OrganisationService
# ===========================================================================


class TestLireOrganisation:
    def test_signature(self):
        sig = inspect.signature(lire_organisation)
        assert list(sig.parameters) == ["organisation_id"]

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        org = lire_organisation(_org_id())

        assert isinstance(org, Organisation)
        assert org.dateDebutOrganisation == date(2024, 9, 2)
        assert org.dateFinOrganisation == date(2025, 6, 27)
        assert org.nombreSemaineFormation == 36
        assert isinstance(org.statutDocumentOrganisation, StatutDocument)
        assert org.valorisationAcquis is True

    def test_empty_response_returns_none(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_RESPONSE
        assert lire_organisation(_org_id()) is None

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        lire_organisation(_org_id(with_impl=True))

        call = mock_soap_call.call_args
        assert call.args[0] == "LireOrganisation"
        assert "implId" not in call.kwargs["id"]
        assert set(call.kwargs["id"]) == REQ_ID_FIELDS


class TestCreerOrganisation:
    def test_signature(self):
        sig = inspect.signature(creer_organisation)
        params = sig.parameters
        # required positional args
        for name in ("annee_scolaire", "etab_id", "impl_id", "num_adm_formation", "date_debut", "date_fin"):
            assert name in params
            assert params[name].default is inspect.Parameter.empty
        # optional params have defaults of None
        for name in ("organisationPeriodesSupplOuEPT", "valorisationAcquis", "reorientation7TP"):
            assert name in params
            assert params[name].default is None

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        org = creer_organisation(
            annee_scolaire="2024-2025",
            etab_id=3052,
            impl_id=6050,
            num_adm_formation=328,
            date_debut=date(2024, 9, 2),
            date_fin=date(2025, 6, 27),
        )
        assert isinstance(org, Organisation)
        assert org.id.numOrganisation == 1
        assert org.id.implId == 6050

    def test_request_includes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        creer_organisation(
            annee_scolaire="2024-2025",
            etab_id=3052,
            impl_id=6050,
            num_adm_formation=328,
            date_debut=date(2024, 9, 2),
            date_fin=date(2025, 6, 27),
            valorisationAcquis=True,
            reorientation7TP=False,
        )
        call = mock_soap_call.call_args
        assert call.args[0] == "CreerOrganisation"
        # CreerOrganisation IS the only operation that includes implId
        assert call.kwargs["id"]["implId"] == 6050
        assert "numOrganisation" not in call.kwargs["id"]
        assert call.kwargs["dateDebutOrganisation"] == date(2024, 9, 2)
        assert call.kwargs["valorisationAcquis"] is True
        assert call.kwargs["reorientation7TP"] is False


class TestModifierOrganisation:
    def test_signature(self):
        sig = inspect.signature(modifier_organisation)
        assert list(sig.parameters) == ["organisation"]

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        org = Organisation(
            id=_org_id(with_impl=True),
            dateDebutOrganisation=date(2024, 9, 2),
            dateFinOrganisation=date(2025, 6, 27),
            valorisationAcquis=True,
        )
        result = modifier_organisation(org)
        assert isinstance(result, Organisation)
        assert result.id == _org_id(with_impl=True)

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
        org = Organisation(
            id=_org_id(with_impl=True),
            dateDebutOrganisation=date(2024, 9, 2),
            dateFinOrganisation=date(2025, 6, 27),
        )
        modifier_organisation(org)
        call = mock_soap_call.call_args
        assert call.args[0] == "ModifierOrganisation"
        assert "implId" not in call.kwargs["id"]
        assert set(call.kwargs["id"]) == REQ_ID_FIELDS


class TestSupprimerOrganisation:
    def test_signature(self):
        sig = inspect.signature(supprimer_organisation)
        assert list(sig.parameters) == ["organisation_id"]

    def test_success_returns_true(self, mock_soap_call):
        mock_soap_call.return_value = {"body": {"success": True}}
        assert supprimer_organisation(_org_id()) is True

    def test_failure_returns_false(self, mock_soap_call):
        mock_soap_call.return_value = {"body": {"success": False}}
        assert supprimer_organisation(_org_id()) is False

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = {"body": {"success": True}}
        supprimer_organisation(_org_id(with_impl=True))
        call = mock_soap_call.call_args
        assert call.args[0] == "SupprimerOrganisation"
        assert "implId" not in call.kwargs["id"]


# ===========================================================================
# Document1Service
# ===========================================================================


class TestLireDocument1:
    def test_signature(self):
        assert list(inspect.signature(lire_document_1).parameters) == ["organisation_id"]

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_RESPONSE
        doc = lire_document_1(_org_id())
        assert isinstance(doc, FormationDocument1)
        assert doc.populationListe is not None
        assert len(doc.populationListe.population) == 1
        line = doc.populationListe.population[0]
        assert line.coAnnEtude == 1
        assert line.nbEleveA == 10
        assert line.swAppD1 is False

    def test_empty_response_returns_none(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_RESPONSE
        assert lire_document_1(_org_id()) is None

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_RESPONSE
        lire_document_1(_org_id(with_impl=True))
        call = mock_soap_call.call_args
        assert call.args[0] == "LireDocument1"
        assert "implId" not in call.kwargs["id"]


class TestModifierDocument1:
    def test_signature(self):
        sig = inspect.signature(modifier_document_1)
        assert list(sig.parameters) == ["organisation_id", "population_liste"]
        assert sig.parameters["population_liste"].default is None

    def test_happy_path_with_population(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_RESPONSE
        liste = Doc1PopulationListSave(
            population=[Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=10)]
        )
        doc = modifier_document_1(_org_id(), population_liste=liste)
        assert isinstance(doc, FormationDocument1)

        call = mock_soap_call.call_args
        assert call.args[0] == "ModifierDocument1"
        assert "implId" not in call.kwargs["id"]
        assert "populationListe" in call.kwargs

    def test_happy_path_without_population(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_RESPONSE
        modifier_document_1(_org_id())
        call = mock_soap_call.call_args
        assert "populationListe" not in call.kwargs


class TestApprouverDocument1:
    def test_signature(self):
        sig = inspect.signature(approuver_document_1)
        assert list(sig.parameters) == ["organisation_id", "population_liste"]
        assert sig.parameters["population_liste"].default is None

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_APPROUVE_RESPONSE
        doc = approuver_document_1(_org_id())
        assert isinstance(doc, FormationDocument1)
        assert doc.populationListe.population[0].swAppD1 is True

        call = mock_soap_call.call_args
        assert call.args[0] == "ApprouverDocument1"
        assert "implId" not in call.kwargs["id"]

    def test_with_population_liste(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT1_APPROUVE_RESPONSE
        liste = Doc1PopulationListSave(
            population=[Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12)]
        )
        approuver_document_1(_org_id(), population_liste=liste)
        call = mock_soap_call.call_args
        assert "populationListe" in call.kwargs


# ===========================================================================
# Document2Service
# ===========================================================================


class TestLireDocument2:
    def test_signature(self):
        assert list(inspect.signature(lire_document_2).parameters) == ["organisation_id"]

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        doc = lire_document_2(_org_id())
        assert isinstance(doc, FormationDocument2)
        assert doc.swAppD2 is True

        ae = doc.activiteEnseignementDetail
        assert ae is not None
        assert ae.nbTotPeriodePrevueAn1 == 28.0
        assert len(ae.activiteEnseignementListe.activiteEnseignement) == 1
        line = ae.activiteEnseignementListe.activiteEnseignement[0]
        assert line.coNumBranche == 10
        assert line.nbEleveC1 == 15

        ie = doc.interventionExterieureListe
        assert ie is not None
        assert len(ie.interventionExterieure) == 1
        assert ie.interventionExterieure[0].coNumIex == 1
        assert ie.interventionExterieure[0].periodeListe is not None
        assert len(ie.interventionExterieure[0].periodeListe.periode) == 1

    def test_empty_response_returns_none(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_RESPONSE
        assert lire_document_2(_org_id()) is None

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        lire_document_2(_org_id(with_impl=True))
        call = mock_soap_call.call_args
        assert call.args[0] == "LireDocument2"
        assert "implId" not in call.kwargs["id"]


class TestModifierDocument2:
    def test_signature(self):
        sig = inspect.signature(modifier_document_2)
        assert list(sig.parameters) == [
            "organisation_id",
            "activite_enseignement_liste",
            "intervention_exterieure_liste",
        ]
        assert sig.parameters["activite_enseignement_liste"].default is None
        assert sig.parameters["intervention_exterieure_liste"].default is None

    def test_with_activite_only(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        liste = Doc2ActiviteEnseignementListSave(
            activiteEnseignement=[Doc2ActiviteEnseignementLineSave(coNumBranche=10, nbEleveC1=20)]
        )
        modifier_document_2(_org_id(), activite_enseignement_liste=liste)
        call = mock_soap_call.call_args
        assert call.args[0] == "ModifierDocument2"
        assert "activiteEnseignementListe" in call.kwargs
        assert "interventionExterieureListe" not in call.kwargs
        assert "implId" not in call.kwargs["id"]

    def test_with_intervention_only(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        liste = Doc2InterventionExtListSave(
            interventionExterieure=[Doc2InterventionExtLineSave(coCatCol="X")]
        )
        modifier_document_2(_org_id(), intervention_exterieure_liste=liste)
        call = mock_soap_call.call_args
        assert "interventionExterieureListe" in call.kwargs
        assert "activiteEnseignementListe" not in call.kwargs

    def test_with_both(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        modifier_document_2(
            _org_id(),
            activite_enseignement_liste=Doc2ActiviteEnseignementListSave(),
            intervention_exterieure_liste=Doc2InterventionExtListSave(),
        )
        call = mock_soap_call.call_args
        assert "activiteEnseignementListe" in call.kwargs
        assert "interventionExterieureListe" in call.kwargs

    def test_with_neither(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT2_RESPONSE
        modifier_document_2(_org_id())
        call = mock_soap_call.call_args
        assert "activiteEnseignementListe" not in call.kwargs
        assert "interventionExterieureListe" not in call.kwargs


# ===========================================================================
# Document3Service
# ===========================================================================


class TestLireDocument3:
    def test_signature(self):
        assert list(inspect.signature(lire_document_3).parameters) == ["organisation_id"]

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT3_RESPONSE
        doc = lire_document_3(_org_id())
        assert isinstance(doc, FormationDocument3)
        assert doc.activiteListe is not None
        assert len(doc.activiteListe.activite) == 1

        act = doc.activiteListe.activite[0]
        assert act.coNumBranche == 10
        assert act.teNomBranche == "Mathématiques"
        assert act.enseignantListe is not None
        assert len(act.enseignantListe.enseignant) == 1

        ens = act.enseignantListe.enseignant[0]
        assert ens.noMatEns == "123456"
        assert ens.nbPeriodesAttribuees == 4.0

    def test_empty_response_returns_none(self, mock_soap_call):
        mock_soap_call.return_value = EMPTY_RESPONSE
        assert lire_document_3(_org_id()) is None

    def test_request_excludes_impl_id(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT3_RESPONSE
        lire_document_3(_org_id(with_impl=True))
        call = mock_soap_call.call_args
        assert call.args[0] == "LireDocument3"
        assert "implId" not in call.kwargs["id"]


class TestModifierDocument3:
    def test_signature(self):
        sig = inspect.signature(modifier_document_3)
        assert list(sig.parameters) == ["organisation_id", "activite_liste"]
        # activite_liste has no default — it's required by the XSD
        assert sig.parameters["activite_liste"].default is inspect.Parameter.empty

    def test_happy_path(self, mock_soap_call):
        mock_soap_call.return_value = CANONICAL_DOCUMENT3_RESPONSE
        liste = Doc3ActiviteListeSave(
            activite=[
                Doc3ActiviteDetailSave(
                    coNumBranche=10,
                    noAnneeEtude="1",
                    enseignantListe=Doc3EnseignantListSave(
                        enseignant=[
                            Doc3EnseignantDetailSave(
                                coNumAttribution=1,
                                noMatEns="123456",
                                coDispo="D",
                                teStatut="DEF",
                                nbPeriodesAttribuees=4.0,
                            )
                        ]
                    ),
                )
            ]
        )
        doc = modifier_document_3(_org_id(), liste)
        assert isinstance(doc, FormationDocument3)

        call = mock_soap_call.call_args
        assert call.args[0] == "ModifierDocument3"
        assert "implId" not in call.kwargs["id"]
        assert "activiteListe" in call.kwargs


# ===========================================================================
# Stable dataclasses — smoke import test
# ===========================================================================


def test_stable_dataclasses_importable_from_eprom():
    """Each stable dataclass must be reachable via ``pyetnic.eprom.X``."""
    stable_names = [
        "StatutDocument",
        "OrganisationId",
        "OrganisationApercu",
        "Organisation",
        "Formation",
        "FormationsListeResult",
        "Doc1PopulationLine",
        "Doc1PopulationList",
        "Doc1PopulationLineSave",
        "Doc1PopulationListSave",
        "FormationDocument1",
        "Doc2ActiviteEnseignementLine",
        "Doc2ActiviteEnseignementList",
        "Doc2ActiviteEnseignementDetail",
        "Doc2PeriodeExtLine",
        "Doc2PeriodeExtList",
        "Doc2InterventionExtLine",
        "Doc2InterventionExtList",
        "Doc2ActiviteEnseignementLineSave",
        "Doc2ActiviteEnseignementListSave",
        "Doc2PeriodeExtLineSave",
        "Doc2PeriodeExtListSave",
        "Doc2InterventionExtLineSave",
        "Doc2InterventionExtListSave",
        "FormationDocument2",
        "Doc3EnseignantDetail",
        "Doc3EnseignantList",
        "Doc3ActiviteDetail",
        "Doc3ActiviteListe",
        "Doc3EnseignantDetailSave",
        "Doc3EnseignantListSave",
        "Doc3ActiviteDetailSave",
        "Doc3ActiviteListeSave",
        "FormationDocument3",
    ]
    for name in stable_names:
        assert hasattr(pyetnic.eprom, name), f"Missing stable export: pyetnic.eprom.{name}"


def test_types_intervention_exterieure_constant():
    """The TYPES_INTERVENTION_EXTERIEURE constant is part of the stable surface."""
    assert hasattr(pyetnic.eprom, "TYPES_INTERVENTION_EXTERIEURE")
    types = pyetnic.eprom.TYPES_INTERVENTION_EXTERIEURE
    # Used in form dropdowns — must remain non-empty and iterable
    assert len(types) > 0
