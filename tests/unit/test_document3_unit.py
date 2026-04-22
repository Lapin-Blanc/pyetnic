# test_document3_unit.py — mock-only unit tests for Document3Service.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services.document3 import Document3Service
from pyetnic.services.models import (
    Doc3ActiviteDetail,
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    Doc3EnseignantDetail,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    FormationDocument3,
    OrganisationId,
)

logger = logging.getLogger(__name__)


def _mock_doc3_response(num_adm: int = 328, num_org: int = 1, activites: list | None = None):
    acts = activites or [
        {
            "coNumBranche": 10,
            "coCategorie": "A",
            "teNomBranche": "Mathématiques",
            "noAnneeEtude": "1",
            "nbPeriodesDoc8": 4,
            "nbPeriodesPrevuesDoc2": 4,
            "nbPeriodesReellesDoc2": 4,
            "enseignantListe": {
                "enseignant": [
                    {
                        "coNumAttribution": 1,
                        "noMatEns": "123456",
                        "teNomEns": "Dupont",
                        "tePrenomEns": "Jean",
                        "teAbrEns": "DUP",
                        "teEnseignant": "Dupont Jean",
                        "coDispo": "D",
                        "teStatut": "DEF",
                        "nbPeriodesAttribuees": 4.0,
                        "tsMaj": None,
                        "teUserMaj": None,
                    }
                ]
            },
        }
    ]
    return {
        "body": {
            "success": True,
            "response": {
                "document3": {
                    "id": {
                        "anneeScolaire": Config.ANNEE_SCOLAIRE or "2023-2024",
                        "etabId": int(Config.ETAB_ID) if Config.ETAB_ID else 3052,
                        "numAdmFormation": num_adm,
                        "numOrganisation": num_org,
                    },
                    "activiteListe": {"activite": acts},
                }
            },
        }
    }


@pytest.fixture
def service():
    return Document3Service()


def test_lire_document3_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireDocument3."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1),
    )

    doc = service.lire_document_3(org_id)

    assert isinstance(doc, FormationDocument3)
    assert doc.id == org_id
    assert doc.activiteListe is not None
    activites = doc.activiteListe.activite
    assert len(activites) == 1
    act = activites[0]
    assert isinstance(act, Doc3ActiviteDetail)
    assert act.coNumBranche == 10
    assert act.teNomBranche == "Mathématiques"
    assert act.enseignantListe is not None
    assert len(act.enseignantListe.enseignant) == 1
    ens = act.enseignantListe.enseignant[0]
    assert isinstance(ens, Doc3EnseignantDetail)
    assert ens.coNumAttribution == 1
    assert ens.noMatEns == "123456"
    assert ens.teNomEns == "Dupont"
    assert ens.nbPeriodesAttribuees == 4.0


def test_lire_document3_mock_reponse_vide(service, monkeypatch):
    """Vérifie que lire_document_3 retourne None si la réponse est vide."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {"body": {"success": True, "response": {}}},
    )

    assert service.lire_document_3(org_id) is None


def test_lire_document3_activite_sans_enseignants(service, monkeypatch):
    """Vérifie que lire_document_3 gère correctement une activité sans enseignants."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    activite_sans_ens = {
        "coNumBranche": 20, "coCategorie": "B", "teNomBranche": "Français",
        "noAnneeEtude": "2", "nbPeriodesDoc8": 2, "nbPeriodesPrevuesDoc2": 2,
        "nbPeriodesReellesDoc2": 2, "enseignantListe": None,
    }
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1, [activite_sans_ens]),
    )

    doc = service.lire_document_3(org_id)
    assert doc is not None
    assert doc.activiteListe.activite[0].enseignantListe is None


def test_modifier_document3_mock(service, monkeypatch):
    """Vérifie que modifier_document_3 retourne le document mis à jour."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    activite_modifiee = [
        {
            "coNumBranche": 10, "coCategorie": "A", "teNomBranche": "Mathématiques",
            "noAnneeEtude": "1", "nbPeriodesDoc8": 4, "nbPeriodesPrevuesDoc2": 4,
            "nbPeriodesReellesDoc2": 4,
            "enseignantListe": {
                "enseignant": [
                    {
                        "coNumAttribution": 1, "noMatEns": "123456",
                        "teNomEns": "Dupont", "tePrenomEns": "Jean",
                        "teAbrEns": "DUP", "teEnseignant": "Dupont Jean",
                        "coDispo": "D", "teStatut": "DEF",
                        "nbPeriodesAttribuees": 6.0,
                        "tsMaj": None, "teUserMaj": None,
                    }
                ]
            },
        }
    ]
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_doc3_response(328, 1, activite_modifiee),
    )

    liste_save = Doc3ActiviteListeSave(
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
                            nbPeriodesAttribuees=6.0,
                        )
                    ]
                ),
            )
        ]
    )
    doc = service.modifier_document_3(org_id, liste_save)

    assert isinstance(doc, FormationDocument3)
    assert doc.id == org_id
    ens = doc.activiteListe.activite[0].enseignantListe.enseignant[0]
    assert ens.nbPeriodesAttribuees == 6.0
    assert ens.coNumAttribution == 1
