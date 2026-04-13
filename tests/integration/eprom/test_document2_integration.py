# test_document2_integration.py — integration tests against ws-tq.etnic.be.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services.document2 import Document2Service
from pyetnic.services.models import (
    Doc2ActiviteEnseignementLineSave,
    Doc2ActiviteEnseignementListSave,
    FormationDocument2,
)

logger = logging.getLogger(__name__)


def _etab_id() -> int:
    return int(Config.ETAB_ID)


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
    """Modifie nbEleveC1 sur la première activité, vérifie, puis restaure."""
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

        doc_relu = svc.lire_document_2(org_apercu.id)
        assert doc_relu is not None
        ligne_relue = doc_relu.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement[0]
        assert ligne_relue.nbEleveC1 == nb_eleve_modifie
        logger.info(f"Modification vérifiée : nbEleveC1 = {nb_eleve_modifie}")

    finally:
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
