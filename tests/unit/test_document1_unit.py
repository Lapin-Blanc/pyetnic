# test_document1_unit.py — mock-only unit tests for Document1Service.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services.document1 import Document1Service
from pyetnic.services.models import (
    Doc1PopulationLineSave,
    Doc1PopulationListSave,
    FormationDocument1,
    OrganisationId,
)

logger = logging.getLogger(__name__)


def _mock_pop_line(co_ann_etude: int = 1, nb_eleve_a: int = 10, approuve: bool = False) -> dict:
    return {
        "coAnnEtude": co_ann_etude,
        "nbEleveA": nb_eleve_a,
        "nbEleveEhr": 0,
        "nbEleveFse": 0,
        "nbElevePi": 0,
        "nbEleveB": 0,
        "nbEleveTot2a5": 0,
        "nbEleveDem": 1,
        "nbEleveMin": 0,
        "nbEleveExm": 0,
        "nbElevePl": 0,
        "nbEleveTot6et8": 0,
        "nbEleveTotFse": 0,
        "nbEleveTotPi": 0,
        "nbEleveTotHom": 4,
        "nbEleveTotFem": 6,
        "swAppPopD1": approuve,
        "swAppD1": approuve,
        "tsMaj": "2025-01-01T00:00:00",
        "teUserMaj": "TEST",
    }


def _mock_doc1_response(num_adm: int = 328, num_org: int = 1, populations: list | None = None):
    pops = populations or [_mock_pop_line()]
    return {
        "body": {
            "success": True,
            "response": {
                "document1": {
                    "id": {
                        "anneeScolaire": Config.ANNEE_SCOLAIRE or "2023-2024",
                        "etabId": Config.ETAB_ID or 3052,
                        "numAdmFormation": num_adm,
                        "numOrganisation": num_org,
                    },
                    "populationListe": {
                        "population": pops,
                    },
                }
            },
        }
    }


@pytest.fixture
def service():
    return Document1Service()


def test_lire_document1_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireDocument1."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc1_response(328, 1),
    )

    doc = service.lire_document_1(org_id)

    assert isinstance(doc, FormationDocument1)
    assert doc.id == org_id
    assert doc.populationListe is not None
    lignes = doc.populationListe.population
    assert len(lignes) == 1
    assert lignes[0].coAnnEtude == 1
    assert lignes[0].nbEleveA == 10
    assert lignes[0].swAppD1 is False


def test_lire_document1_mock_reponse_vide(service, monkeypatch):
    """Vérifie que lire_document_1 retourne None si la réponse est vide."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True, "response": {}}},
    )

    assert service.lire_document_1(org_id) is None


def test_lire_document1_mock_sans_populations(service, monkeypatch):
    """Vérifie le parsing quand populationListe est absent."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    response = {
        "body": {
            "success": True,
            "response": {
                "document1": {
                    "id": {"anneeScolaire": "2023-2024", "etabId": 3052,
                           "numAdmFormation": 328, "numOrganisation": 1},
                    "populationListe": None,
                }
            },
        }
    }
    monkeypatch.setattr(service.client_manager, "call_service", lambda *a, **kw: response)

    doc = service.lire_document_1(org_id)
    assert isinstance(doc, FormationDocument1)
    assert doc.populationListe is None


def test_modifier_document1_mock(service, monkeypatch):
    """Vérifie que modifier_document_1 retourne le document mis à jour."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc1_response(328, 1, [_mock_pop_line(nb_eleve_a=15)]),
    )

    liste_save = Doc1PopulationListSave(
        population=[Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=15)]
    )
    doc = service.modifier_document_1(org_id, population_liste=liste_save)

    assert isinstance(doc, FormationDocument1)
    assert doc.id == org_id
    assert doc.populationListe.population[0].nbEleveA == 15


def test_approuver_document1_mock(service, monkeypatch):
    """Vérifie que approuver_document_1 retourne le document approuvé."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc1_response(328, 1, [_mock_pop_line(approuve=True)]),
    )

    doc = service.approuver_document_1(org_id)

    assert isinstance(doc, FormationDocument1)
    assert doc.populationListe.population[0].swAppD1 is True
