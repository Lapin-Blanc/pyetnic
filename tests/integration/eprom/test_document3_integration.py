# test_document3_integration.py — integration tests against ws-tq.etnic.be.

import logging

import pytest

from pyetnic.config import Config
from pyetnic.services import lister_formations
from pyetnic.services.document3 import Document3Service
from pyetnic.services.models import (
    Doc3ActiviteDetailSave,
    Doc3ActiviteListeSave,
    Doc3EnseignantDetailSave,
    Doc3EnseignantListSave,
    FormationDocument3,
)

logger = logging.getLogger(__name__)


def _etab_id() -> int:
    return int(Config.ETAB_ID)


_ANNEES_CANDIDATES = [
    Config.ANNEE_SCOLAIRE,
    "2023-2024",
    "2024-2025",
]


def _find_accessible_doc3():
    """Retourne (svc, org_id, doc) pour la première org avec doc3 accessible
    et au moins un enseignant assigné, en cherchant sur plusieurs années."""
    svc = Document3Service()
    for annee in _ANNEES_CANDIDATES:
        formations = lister_formations(annee_scolaire=annee, etab_id=_etab_id())
        for f in formations.formations:
            for o in f.organisations:
                doc = svc.lire_document_3(o.id)
                if doc is None:
                    continue
                for act in (doc.activiteListe.activite if doc.activiteListe else []):
                    enseignants = act.enseignantListe.enseignant if act.enseignantListe else []
                    if any(e.noMatEns for e in enseignants):
                        return svc, o.id, doc
    return None, None, None


def test_lire_document3_reel():
    """Lit le document 3 d'une organisation existante et vérifie la structure."""
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")

    svc, org_id, doc = _find_accessible_doc3()
    if svc is None:
        pytest.skip("Aucune organisation avec doc3 accessible trouvée")

    assert isinstance(doc, FormationDocument3)
    assert doc.id.numOrganisation == org_id.numOrganisation
    assert doc.activiteListe is not None


def test_modifier_document3_reel():
    """Modifie nbPeriodesAttribuees d'un enseignant et vérifie la persistance, puis restaure."""
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")

    svc, org_id, doc = _find_accessible_doc3()
    if svc is None:
        pytest.skip("Aucune organisation avec doc3 accessible et enseignant assigné")

    act_orig = next(
        act for act in doc.activiteListe.activite
        if act.enseignantListe and any(e.noMatEns for e in act.enseignantListe.enseignant)
    )
    ens_orig = next(e for e in act_orig.enseignantListe.enseignant if e.noMatEns)
    periodes_orig = ens_orig.nbPeriodesAttribuees
    periodes_modif = periodes_orig - 2.0

    def _build_liste_save(periodes_act1: float) -> Doc3ActiviteListeSave:
        activites = []
        for act in doc.activiteListe.activite:
            enseignants = []
            for ens in (act.enseignantListe.enseignant if act.enseignantListe else []):
                p = periodes_act1 if (act.coNumBranche == act_orig.coNumBranche and ens.coNumAttribution == ens_orig.coNumAttribution) else ens.nbPeriodesAttribuees
                enseignants.append(Doc3EnseignantDetailSave(
                    coNumAttribution=ens.coNumAttribution,
                    noMatEns=ens.noMatEns,
                    coDispo=ens.coDispo,
                    teStatut=ens.teStatut,
                    nbPeriodesAttribuees=p,
                ))
            activites.append(Doc3ActiviteDetailSave(
                coNumBranche=act.coNumBranche,
                noAnneeEtude=act.noAnneeEtude,
                enseignantListe=Doc3EnseignantListSave(enseignant=enseignants),
            ))
        return Doc3ActiviteListeSave(activite=activites)

    try:
        doc_modifie = svc.modifier_document_3(org_id, _build_liste_save(periodes_modif))
        assert isinstance(doc_modifie, FormationDocument3)
        act_modif = next(a for a in doc_modifie.activiteListe.activite if a.coNumBranche == act_orig.coNumBranche)
        ens_modif = next(e for e in act_modif.enseignantListe.enseignant if e.coNumAttribution == ens_orig.coNumAttribution)
        assert ens_modif.nbPeriodesAttribuees == periodes_modif
    finally:
        doc_restaure = svc.modifier_document_3(org_id, _build_liste_save(periodes_orig))
        assert doc_restaure is not None, "Échec de la restauration du document 3"
        act_rest = next(a for a in doc_restaure.activiteListe.activite if a.coNumBranche == act_orig.coNumBranche)
        ens_rest = next(e for e in act_rest.enseignantListe.enseignant if e.coNumAttribution == ens_orig.coNumAttribution)
        assert ens_rest.nbPeriodesAttribuees == periodes_orig
