# test_formation_document1.py

import pytest
import logging

from pyetnic.services.document1 import Document1Service
from pyetnic.services.models import (
    FormationDocument1, OrganisationId,
    Doc1PopulationLine, Doc1PopulationList,
    Doc1PopulationLineSave, Doc1PopulationListSave,
)
from pyetnic.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _etab_id() -> int:
    return int(Config.ETAB_ID)

def _mock_pop_line(co_ann_etude: int = 1, nb_eleve_a: int = 10, approuve: bool = False) -> dict:
    return {
        'coAnnEtude': co_ann_etude,
        'nbEleveA': nb_eleve_a,
        'nbEleveEhr': 0,
        'nbEleveFse': 0,
        'nbElevePi': 0,
        'nbEleveB': 0,
        'nbEleveTot2a5': 0,
        'nbEleveDem': 1,
        'nbEleveMin': 0,
        'nbEleveExm': 0,
        'nbElevePl': 0,
        'nbEleveTot6et8': 0,
        'nbEleveTotFse': 0,
        'nbEleveTotPi': 0,
        'nbEleveTotHom': 4,
        'nbEleveTotFem': 6,
        'swAppPopD1': approuve,
        'swAppD1': approuve,
        'tsMaj': '2025-01-01T00:00:00',
        'teUserMaj': 'TEST',
    }

def _mock_doc1_response(num_adm: int = 328, num_org: int = 1, populations: list | None = None):
    pops = populations or [_mock_pop_line()]
    return {
        'body': {
            'success': True,
            'response': {
                'document1': {
                    'id': {
                        'anneeScolaire': Config.ANNEE_SCOLAIRE,
                        'etabId': _etab_id(),
                        'numAdmFormation': num_adm,
                        'numOrganisation': num_org,
                    },
                    'populationListe': {
                        'population': pops,
                    },
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return Document1Service()


# ---------------------------------------------------------------------------
# Tests unitaires (mock — sans credentials)
# ---------------------------------------------------------------------------

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
        lambda *a, **kw: {'body': {'success': True, 'response': {}}},
    )

    assert service.lire_document_1(org_id) is None


def test_lire_document1_mock_sans_populations(service, monkeypatch):
    """Vérifie le parsing quand populationListe est absent."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    response = {
        'body': {
            'success': True,
            'response': {
                'document1': {
                    'id': {'anneeScolaire': "2023-2024", 'etabId': 3052,
                           'numAdmFormation': 328, 'numOrganisation': 1},
                    'populationListe': None,
                }
            }
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

def test_lire_document1_reel():
    """Lit le document 1 d'une organisation existante et vérifie la structure."""
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
    svc = Document1Service()
    doc = svc.lire_document_1(org_apercu.id)

    if doc is None:
        pytest.skip("Document 1 non accessible pour cette organisation (statut insuffisant ?)")

    assert isinstance(doc, FormationDocument1)
    assert doc.id.numOrganisation == org_apercu.id.numOrganisation


def test_modifier_document1_reel():
    """Modifie nbEleveA sur la première population, vérifie, puis restaure.

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
    svc = Document1Service()
    doc_original = svc.lire_document_1(org_apercu.id)
    if doc_original is None:
        pytest.skip("Document 1 non accessible pour cette organisation (statut insuffisant ?)")

    if not (doc_original.populationListe and doc_original.populationListe.population):
        pytest.skip("Pas de population dans ce document 1")

    premiere_pop = doc_original.populationListe.population[0]
    nb_eleve_original = premiere_pop.nbEleveA
    nb_eleve_modifie = nb_eleve_original + 1

    try:
        liste_save = Doc1PopulationListSave(
            population=[
                Doc1PopulationLineSave(
                    coAnnEtude=premiere_pop.coAnnEtude,
                    nbEleveA=nb_eleve_modifie,
                )
            ]
        )
        doc_modifie = svc.modifier_document_1(org_apercu.id, population_liste=liste_save)
        if doc_modifie is None:
            pytest.skip("Document 1 non modifiable pour cette organisation (statut insuffisant ?)")

        doc_relu = svc.lire_document_1(org_apercu.id)
        assert doc_relu is not None
        pop_relue = doc_relu.populationListe.population[0]
        assert pop_relue.nbEleveA == nb_eleve_modifie
        logger.info(f"Modification vérifiée : nbEleveA = {nb_eleve_modifie}")

    finally:
        liste_restore = Doc1PopulationListSave(
            population=[
                Doc1PopulationLineSave(
                    coAnnEtude=premiere_pop.coAnnEtude,
                    nbEleveA=nb_eleve_original,
                )
            ]
        )
        doc_restaure = svc.modifier_document_1(org_apercu.id, population_liste=liste_restore)
        if doc_restaure is None:
            logger.error(f"Échec de la restauration de nbEleveA à {nb_eleve_original}")
        else:
            logger.info(f"Valeur originale restaurée : nbEleveA = {nb_eleve_original}")
