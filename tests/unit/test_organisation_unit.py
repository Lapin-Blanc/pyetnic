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
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 1234, 328, 1),
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
        anneeScolaire="2023-2024", etabId=1234,
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
        lambda *a, **kw: _mock_org_response("2023-2024", 1234, 328, 99),
    )

    org = service.creer_organisation(
        annee_scolaire="2023-2024",
        etab_id=1234, impl_id=5678,
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
        anneeScolaire="2023-2024", etabId=1234,
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
        lambda *a, **kw: _mock_org_response("2023-2024", 1234, 328, 1),
    )

    result = service.modifier_organisation(org)
    assert isinstance(result, Organisation)
    assert result.id == org_id


def test_creer_organisation_strips_none_from_payload(service, monkeypatch):
    """None-valued optional fields must be absent from the CreerOrganisation payload.

    zeep would otherwise serialize them as empty XML elements that ETNIC reads
    as 'erase this value' (D2 defect — previously unfixed on organisation).
    """
    captured: dict = {}

    def fake_call(method_name, **kwargs):
        captured["method"] = method_name
        captured["kwargs"] = kwargs
        return _mock_org_response("2023-2024", 1234, 328, 99)

    monkeypatch.setattr(service.client_manager, "call_service", fake_call)

    service.creer_organisation(
        annee_scolaire="2023-2024",
        etab_id=1234, impl_id=5678,
        num_adm_formation=328,
        date_debut=date(2024, 9, 2),
        date_fin=date(2025, 6, 27),
        valorisationAcquis=True,
    )

    kwargs = captured["kwargs"]
    assert captured["method"] == "CreerOrganisation"
    # implId IS sent on create (required there, unlike Lire/Modifier)
    assert kwargs["id"] == {
        "anneeScolaire": "2023-2024",
        "etabId": 1234,
        "implId": 5678,
        "numAdmFormation": 328,
    }
    assert kwargs["valorisationAcquis"] is True
    for absent in (
        "organisationPeriodesSupplOuEPT",
        "enPrison",
        "reorientation7TP",
        "activiteFormation",
        "conseillerPrevention",
        "enseignementHybride",
        "numOrganisation2AnneesScolaires",
        "typeInterventionExterieure",
        "interventionExterieure50p",
    ):
        assert absent not in kwargs, f"expected {absent!r} to be stripped"


def test_modifier_organisation_strips_none_from_payload(service, monkeypatch):
    """None-valued optional fields must be absent from the ModifierOrganisation payload."""
    captured: dict = {}

    def fake_call(method_name, **kwargs):
        captured["method"] = method_name
        captured["kwargs"] = kwargs
        return _mock_org_response("2023-2024", 1234, 328, 1)

    monkeypatch.setattr(service.client_manager, "call_service", fake_call)

    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1, implId=5678,
    )
    org = Organisation(
        id=org_id,
        dateDebutOrganisation=date(2024, 9, 2),
        dateFinOrganisation=date(2025, 6, 27),
        enPrison=True,
    )

    service.modifier_organisation(org)

    kwargs = captured["kwargs"]
    assert captured["method"] == "ModifierOrganisation"
    # implId must NOT be sent on modify (organisation_request_id excludes it)
    assert "implId" not in kwargs["id"]
    assert kwargs["enPrison"] is True
    for absent in (
        "valorisationAcquis",
        "reorientation7TP",
        "activiteFormation",
        "typeInterventionExterieure",
        "interventionExterieure50p",
    ):
        assert absent not in kwargs, f"expected {absent!r} to be stripped"


def test_supprimer_organisation_mock_succes(service, monkeypatch):
    """Vérifie que supprimer_organisation retourne True si success=True."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=1234,
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
        anneeScolaire="2023-2024", etabId=1234,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": False}},
    )

    assert service.supprimer_organisation(org_id) is False


# ---------------------------------------------------------------------------
# Organisation v8: BESAeSI
# ---------------------------------------------------------------------------

def test_organisation_v8_endpoint_and_contract():
    """The service calls Organisation v8 and loads its embedded contract."""
    from pyetnic.config import Config

    config = Config.SERVICES["ORGANISATION"]
    assert config.endpoint.endswith("/eprom/formation/organisation/v8")
    assert config.wsdl_path.startswith("EPROM_Formation_Organisation_8.0/")
    assert "V8Binding" in config.binding_name


def test_lire_organisation_reads_besaesi(service, monkeypatch):
    response = _mock_org_response("2026-2027", 1234, 328, 1)
    response["body"]["response"]["organisation"]["BESAeSI"] = True
    monkeypatch.setattr(service.client_manager, "call_service", lambda *a, **kw: response)

    org = service.lire_organisation(OrganisationId("2026-2027", 1234, 328, 1))

    assert org.BESAeSI is True


def test_lire_organisation_without_besaesi_reads_none(service, monkeypatch):
    monkeypatch.setattr(service.client_manager, "call_service",
                        lambda *a, **kw: _mock_org_response("2026-2027", 1234, 328, 1))

    assert service.lire_organisation(OrganisationId("2026-2027", 1234, 328, 1)).BESAeSI is None


def test_creer_organisation_sends_besaesi_only_when_given(service, monkeypatch):
    calls = []

    def fake_call(method, **kwargs):
        calls.append(kwargs)
        return _mock_org_response("2026-2027", 1234, 328, 1)

    monkeypatch.setattr(service.client_manager, "call_service", fake_call)
    service.creer_organisation("2026-2027", 1234, 5678, 328, date(2026, 9, 1), date(2027, 6, 30), BESAeSI=True)
    service.creer_organisation("2026-2027", 1234, 5678, 328, date(2026, 9, 1), date(2027, 6, 30))

    assert calls[0]["BESAeSI"] is True
    assert "BESAeSI" not in calls[1]


def test_modifier_organisation_sends_besaesi(service, monkeypatch):
    calls = []

    def fake_call(method, **kwargs):
        calls.append(kwargs)
        return _mock_org_response("2026-2027", 1234, 328, 1)

    monkeypatch.setattr(service.client_manager, "call_service", fake_call)
    org = Organisation(
        id=OrganisationId("2026-2027", 1234, 328, 1),
        dateDebutOrganisation=date(2026, 9, 1),
        dateFinOrganisation=date(2027, 6, 30),
        BESAeSI=False,
    )
    service.modifier_organisation(org)

    assert calls[0]["BESAeSI"] is False
    assert "eLearning" not in calls[0] and "partiellementDistance" not in calls[0]
