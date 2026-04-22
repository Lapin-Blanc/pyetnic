# test_organisation_unit.py — mock-only unit tests for OrganisationService.

import logging
from datetime import date

import pytest

from pyetnic.services.organisation import OrganisationService
from pyetnic.services.models import Organisation, OrganisationId

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_org_response(annee_scolaire, etab_id, num_adm, num_org, date_fin_str="2025-06-27"):
    return {
        "body": {
            "success": True,
            "response": {
                "organisation": {
                    "id": {
                        "anneeScolaire": annee_scolaire,
                        "etabId": etab_id,
                        "numAdmFormation": num_adm,
                        "numOrganisation": num_org,
                        "implId": None,
                    },
                    "dateDebutOrganisation": date(2024, 9, 2),
                    "dateFinOrganisation": date.fromisoformat(date_fin_str),
                    "nombreSemaineFormation": 36,
                    "statut": None,
                    "organisationPeriodesSupplOuEPT": None,
                    "valorisationAcquis": None,
                    "enPrison": None,
                    "eLearning": None,
                    "activiteFormation": None,
                    "conseillerPrevention": None,
                    "partiellementDistance": None,
                    "enseignementHybride": None,
                    "numOrganisation2AnneesScolaires": None,
                    "typeInterventionExterieure": None,
                    "interventionExterieure50p": None,
                }
            },
        }
    }


@pytest.fixture
def service():
    return OrganisationService()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_lire_organisation_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireOrganisation."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 1),
    )

    org = service.lire_organisation(org_id)

    assert isinstance(org, Organisation)
    assert org.id == org_id
    assert org.dateDebutOrganisation == date(2024, 9, 2)
    assert org.dateFinOrganisation == date(2025, 6, 27)
    assert org.nombreSemaineFormation == 36


def test_lire_organisation_mock_reponse_vide(service, monkeypatch):
    """Vérifie que lire_organisation retourne None si la réponse est vide."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True, "response": {}}},
    )

    assert service.lire_organisation(org_id) is None


def test_creer_organisation_mock(service, monkeypatch):
    """Vérifie que creer_organisation parse correctement l'id attribué par le serveur."""
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 99),
    )

    org = service.creer_organisation(
        annee_scolaire="2023-2024",
        etab_id=3052, impl_id=6050,
        num_adm_formation=328,
        date_debut=date(2024, 9, 2),
        date_fin=date(2025, 6, 27),
    )

    assert isinstance(org, Organisation)
    assert org.id.numOrganisation == 99
    assert org.id.numAdmFormation == 328


def test_modifier_organisation_mock(service, monkeypatch):
    """Vérifie que modifier_organisation retourne l'organisation mise à jour."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    org = Organisation(
        id=org_id,
        dateDebutOrganisation=date(2024, 9, 2),
        dateFinOrganisation=date(2025, 6, 27),
        valorisationAcquis=True,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 1),
    )

    result = service.modifier_organisation(org)
    assert isinstance(result, Organisation)
    assert result.id == org_id


def test_supprimer_organisation_mock_succes(service, monkeypatch):
    """Vérifie que supprimer_organisation retourne True si success=True."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True}},
    )

    assert service.supprimer_organisation(org_id) is True


def test_supprimer_organisation_mock_echec(service, monkeypatch):
    """Vérifie que supprimer_organisation retourne False si success=False."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": False}},
    )

    assert service.supprimer_organisation(org_id) is False
