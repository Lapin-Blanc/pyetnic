# test_document2_unit.py — mock-only unit tests for Document2Service.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services.document2 import Document2Service
from pyetnic.services.models import (
    Doc2ActiviteEnseignementLineSave,
    Doc2ActiviteEnseignementListSave,
    FormationDocument2,
    OrganisationId,
)

logger = logging.getLogger(__name__)


def _mock_doc2_response(num_adm: int = 328, num_org: int = 1, activites: list | None = None):
    activite_list = activites or [
        {
            "coNumBranche": 10,
            "coCategorie": "A",
            "teNomBranche": "Branche test",
            "coAnnEtude": "1",
            "nbEleveC1": 15,
            "nbPeriodeBranche": 30.0,
            "nbPeriodePrevueAn1": 28.0,
            "nbPeriodePrevueAn2": 0.0,
            "nbPeriodeReelleAn1": 26.0,
            "nbPeriodeReelleAn2": 0.0,
            "coAdmReg": num_adm,
            "coOrgReg": num_org,
            "coBraReg": 10,
            "coEtuReg": "1",
        }
    ]
    return {
        "body": {
            "success": True,
            "response": {
                "document2": {
                    "id": {
                        "anneeScolaire": Config.ANNEE_SCOLAIRE or "2023-2024",
                        "etabId": int(Config.ETAB_ID) if Config.ETAB_ID else 3052,
                        "numAdmFormation": num_adm,
                        "numOrganisation": num_org,
                    },
                    "activiteEnseignementDetail": {
                        "activiteEnseignementListe": {
                            "activiteEnseignement": activite_list,
                        },
                        "nbTotPeriodePrevueAn1": sum(a["nbPeriodePrevueAn1"] for a in activite_list),
                        "nbTotPeriodePrevueAn2": 0.0,
                        "nbTotPeriodeReelleAn1": sum(a["nbPeriodeReelleAn1"] for a in activite_list),
                        "nbTotPeriodeReelleAn2": 0.0,
                    },
                    "interventionExterieureListe": None,
                    "swAppD2": True,
                    "tsMaj": "2025-01-01T00:00:00",
                    "teUserMaj": "TEST",
                }
            },
        }
    }


@pytest.fixture
def service():
    return Document2Service()


def test_lire_document2_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireDocument2."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc2_response(328, 1),
    )

    doc = service.lire_document_2(org_id)

    assert isinstance(doc, FormationDocument2)
    assert doc.id == org_id
    assert doc.swAppD2 is True
    assert doc.activiteEnseignementDetail is not None
    lignes = doc.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement
    assert len(lignes) == 1
    assert lignes[0].coNumBranche == 10
    assert lignes[0].nbEleveC1 == 15


def test_lire_document2_mock_reponse_vide(service, monkeypatch):
    """Vérifie que lire_document_2 retourne None si la réponse est vide."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True, "response": {}}},
    )

    assert service.lire_document_2(org_id) is None


def test_lire_document2_mock_sans_activites(service, monkeypatch):
    """Vérifie le parsing quand activiteEnseignementDetail est absent."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    response = {
        "body": {
            "success": True,
            "response": {
                "document2": {
                    "id": {"anneeScolaire": "2023-2024", "etabId": 3052,
                           "numAdmFormation": 328, "numOrganisation": 1},
                    "activiteEnseignementDetail": None,
                    "interventionExterieureListe": None,
                    "swAppD2": False,
                    "tsMaj": None,
                    "teUserMaj": None,
                }
            },
        }
    }
    monkeypatch.setattr(service.client_manager, "call_service", lambda *a, **kw: response)

    doc = service.lire_document_2(org_id)
    assert isinstance(doc, FormationDocument2)
    assert doc.activiteEnseignementDetail is None
    assert doc.swAppD2 is False


def test_modifier_document2_mock(service, monkeypatch):
    """Vérifie que modifier_document_2 retourne le document mis à jour."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    activites_modifiees = [
        {
            "coNumBranche": 10, "coCategorie": "A", "teNomBranche": "Branche test",
            "coAnnEtude": "1", "nbEleveC1": 20,
            "nbPeriodeBranche": 30.0, "nbPeriodePrevueAn1": 28.0,
            "nbPeriodePrevueAn2": 0.0, "nbPeriodeReelleAn1": 26.0,
            "nbPeriodeReelleAn2": 0.0,
            "coAdmReg": 328, "coOrgReg": 1, "coBraReg": 10, "coEtuReg": "1",
        }
    ]
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc2_response(328, 1, activites_modifiees),
    )

    liste_save = Doc2ActiviteEnseignementListSave(
        activiteEnseignement=[
            Doc2ActiviteEnseignementLineSave(coNumBranche=10, nbEleveC1=20),
        ]
    )
    doc = service.modifier_document_2(org_id, activite_enseignement_liste=liste_save)

    assert isinstance(doc, FormationDocument2)
    assert doc.id == org_id
    lignes = doc.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement
    assert lignes[0].nbEleveC1 == 20


def test_organisation_id_dict(service):
    """Vérifie que _organisation_id_dict n'inclut pas implId."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1, implId=6050,
    )
    result = service._organisation_id_dict(org_id)

    assert "implId" not in result
    assert result == {
        "anneeScolaire": "2023-2024",
        "etabId": 3052,
        "numAdmFormation": 328,
        "numOrganisation": 1,
    }
