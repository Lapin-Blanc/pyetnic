# test_document1_integration.py — integration tests against ws-tq.etnic.be.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services.document1 import Document1Service
from pyetnic.services.models import (
    Doc1PopulationLineSave,
    Doc1PopulationListSave,
    FormationDocument1,
)

logger = logging.getLogger(__name__)


def _etab_id() -> int:
    return Config.ETAB_ID


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
    """Modifie nbEleveA sur la première population, vérifie, puis restaure."""
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
