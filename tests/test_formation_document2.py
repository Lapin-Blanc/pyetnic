# test_formation_document2.py

import pytest
import logging
from datetime import date

from pyetnic.services.document2 import Document2Service
from pyetnic.services.models import (
    FormationDocument2, OrganisationId,
    Doc2ActiviteEnseignementDetail, Doc2ActiviteEnseignementList, Doc2ActiviteEnseignementLine,
    Doc2ActiviteEnseignementLineSave, Doc2ActiviteEnseignementListSave,
)
from pyetnic.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _etab_id() -> int:
    return int(Config.ETAB_ID)

def _org_id(num_adm: int = 328, num_org: int = 1) -> OrganisationId:
    return OrganisationId(
        anneeScolaire=Config.ANNEE_SCOLAIRE,
        etabId=_etab_id(),
        numAdmFormation=num_adm,
        numOrganisation=num_org,
    )

def _mock_doc2_response(num_adm: int = 328, num_org: int = 1, activites: list | None = None):
    activite_list = activites or [
        {
            'coNumBranche': 10,
            'coCategorie': 'A',
            'teNomBranche': 'Branche test',
            'coAnnEtude': '1',
            'nbEleveC1': 15,
            'nbPeriodeBranche': 30.0,
            'nbPeriodePrevueAn1': 28.0,
            'nbPeriodePrevueAn2': 0.0,
            'nbPeriodeReelleAn1': 26.0,
            'nbPeriodeReelleAn2': 0.0,
            'coAdmReg': num_adm,
            'coOrgReg': num_org,
            'coBraReg': 10,
            'coEtuReg': '1',
        }
    ]
    return {
        'body': {
            'success': True,
            'response': {
                'document2': {
                    'id': {
                        'anneeScolaire': Config.ANNEE_SCOLAIRE,
                        'etabId': _etab_id(),
                        'numAdmFormation': num_adm,
                        'numOrganisation': num_org,
                    },
                    'activiteEnseignementDetail': {
                        'activiteEnseignementListe': {
                            'activiteEnseignement': activite_list,
                        },
                        'nbTotPeriodePrevueAn1': sum(a['nbPeriodePrevueAn1'] for a in activite_list),
                        'nbTotPeriodePrevueAn2': 0.0,
                        'nbTotPeriodeReelleAn1': sum(a['nbPeriodeReelleAn1'] for a in activite_list),
                        'nbTotPeriodeReelleAn2': 0.0,
                    },
                    'interventionExterieureListe': None,
                    'swAppD2': True,
                    'tsMaj': '2025-01-01T00:00:00',
                    'teUserMaj': 'TEST',
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return Document2Service()


# ---------------------------------------------------------------------------
# Tests unitaires (mock — sans credentials)
# ---------------------------------------------------------------------------

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
        lambda *a, **kw: {'body': {'success': True, 'response': {}}},
    )

    assert service.lire_document_2(org_id) is None


def test_lire_document2_mock_sans_activites(service, monkeypatch):
    """Vérifie le parsing quand activiteEnseignementDetail est absent."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    response = {
        'body': {
            'success': True,
            'response': {
                'document2': {
                    'id': {'anneeScolaire': "2023-2024", 'etabId': 3052,
                           'numAdmFormation': 328, 'numOrganisation': 1},
                    'activiteEnseignementDetail': None,
                    'interventionExterieureListe': None,
                    'swAppD2': False,
                    'tsMaj': None,
                    'teUserMaj': None,
                }
            }
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
            'coNumBranche': 10, 'coCategorie': 'A', 'teNomBranche': 'Branche test',
            'coAnnEtude': '1', 'nbEleveC1': 20,
            'nbPeriodeBranche': 30.0, 'nbPeriodePrevueAn1': 28.0,
            'nbPeriodePrevueAn2': 0.0, 'nbPeriodeReelleAn1': 26.0,
            'nbPeriodeReelleAn2': 0.0,
            'coAdmReg': 328, 'coOrgReg': 1, 'coBraReg': 10, 'coEtuReg': '1',
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

    assert 'implId' not in result
    assert result == {
        'anneeScolaire': "2023-2024",
        'etabId': 3052,
        'numAdmFormation': 328,
        'numOrganisation': 1,
    }


# ---------------------------------------------------------------------------
# Tests d'intégration (service dev — nécessitent un .env valide)
# ---------------------------------------------------------------------------

def test_lire_document2_reel():
    """Lit le document 2 d'une organisation existante et vérifie la structure."""
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")

    from pyetnic.services import lister_formations
    formations = lister_formations(
        annee_scolaire=Config.ANNEE_SCOLAIRE,
        etab_id=_etab_id(),
    )
    formations_avec_org = [f for f in formations.formations if f.organisations]
    if not formations_avec_org:
        pytest.skip("Aucune formation avec organisation disponible")

    org_apercu = formations_avec_org[0].organisations[0]
    svc = Document2Service()
    doc = svc.lire_document_2(org_apercu.id)

    if doc is None:
        pytest.skip("Document 2 non accessible pour cette organisation (statut insuffisant ?)")

    assert isinstance(doc, FormationDocument2)
    assert doc.id.numOrganisation == org_apercu.id.numOrganisation


def test_modifier_document2_reel():
    """Modifie nbEleveC1 sur la première activité, vérifie, puis restaure.

    Ce test gère son propre nettoyage : la valeur originale est restaurée
    dans le bloc finally, même en cas d'échec.
    """
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")

    from pyetnic.services import lister_formations
    formations = lister_formations(
        annee_scolaire=Config.ANNEE_SCOLAIRE,
        etab_id=_etab_id(),
    )
    formations_avec_org = [f for f in formations.formations if f.organisations]
    if not formations_avec_org:
        pytest.skip("Aucune formation avec organisation disponible")

    org_apercu = formations_avec_org[0].organisations[0]
    svc = Document2Service()
    doc_original = svc.lire_document_2(org_apercu.id)
    if doc_original is None:
        pytest.skip("Document 2 non accessible pour cette organisation (statut insuffisant ?)")

    if not (
        doc_original.activiteEnseignementDetail
        and doc_original.activiteEnseignementDetail.activiteEnseignementListe
        and doc_original.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement
    ):
        pytest.skip("Pas d'activité d'enseignement dans ce document 2")

    premiere_activite = doc_original.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement[0]
    nb_eleve_original = premiere_activite.nbEleveC1
    nb_eleve_modifie = nb_eleve_original + 1

    try:
        # Modification
        liste_save = Doc2ActiviteEnseignementListSave(
            activiteEnseignement=[
                Doc2ActiviteEnseignementLineSave(
                    coNumBranche=premiere_activite.coNumBranche,
                    nbEleveC1=nb_eleve_modifie,
                )
            ]
        )
        doc_modifie = svc.modifier_document_2(org_apercu.id, activite_enseignement_liste=liste_save)
        if doc_modifie is None:
            pytest.skip("Document 2 non modifiable pour cette organisation (statut insuffisant ?)")

        # Relecture pour confirmer
        doc_relu = svc.lire_document_2(org_apercu.id)
        assert doc_relu is not None
        ligne_relue = doc_relu.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement[0]
        assert ligne_relue.nbEleveC1 == nb_eleve_modifie
        logger.info(f"Modification vérifiée : nbEleveC1 = {nb_eleve_modifie}")

    finally:
        # Restauration de la valeur originale
        liste_restore = Doc2ActiviteEnseignementListSave(
            activiteEnseignement=[
                Doc2ActiviteEnseignementLineSave(
                    coNumBranche=premiere_activite.coNumBranche,
                    nbEleveC1=nb_eleve_original,
                )
            ]
        )
        doc_restaure = svc.modifier_document_2(org_apercu.id, activite_enseignement_liste=liste_restore)
        if doc_restaure is None:
            logger.error(f"Échec de la restauration de nbEleveC1 à {nb_eleve_original}")
        else:
            logger.info(f"Valeur originale restaurée : nbEleveC1 = {nb_eleve_original}")
