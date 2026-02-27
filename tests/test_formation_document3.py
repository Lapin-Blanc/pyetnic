# test_formation_document3.py

import pytest
import logging

from pyetnic.services.document3 import Document3Service
from pyetnic.services.models import (
    FormationDocument3, OrganisationId,
    Doc3ActiviteDetail, Doc3EnseignantDetail,
    Doc3EnseignantDetailSave, Doc3EnseignantListSave,
    Doc3ActiviteDetailSave, Doc3ActiviteListeSave,
)
from pyetnic.services import lister_formations
from pyetnic.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _etab_id() -> int:
    return int(Config.ETAB_ID)

def _mock_doc3_response(num_adm: int = 328, num_org: int = 1, activites: list | None = None):
    acts = activites or [
        {
            'coNumBranche': 10,
            'coCategorie': 'A',
            'teNomBranche': 'Mathématiques',
            'noAnneeEtude': '1',
            'nbPeriodesDoc8': 4,
            'nbPeriodesPrevuesDoc2': 4,
            'nbPeriodesReellesDoc2': 4,
            'enseignantListe': {
                'enseignant': [
                    {
                        'coNumAttribution': 1,
                        'noMatEns': '123456',
                        'teNomEns': 'Dupont',
                        'tePrenomEns': 'Jean',
                        'teAbrEns': 'DUP',
                        'teEnseignant': 'Dupont Jean',
                        'coDispo': 'D',
                        'teStatut': 'DEF',
                        'nbPeriodesAttribuees': 4.0,
                        'tsMaj': None,
                        'teUserMaj': None,
                    }
                ]
            },
        }
    ]
    return {
        'body': {
            'success': True,
            'response': {
                'document3': {
                    'id': {
                        'anneeScolaire': Config.ANNEE_SCOLAIRE,
                        'etabId': _etab_id(),
                        'numAdmFormation': num_adm,
                        'numOrganisation': num_org,
                    },
                    'activiteListe': {'activite': acts},
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return Document3Service()


# ---------------------------------------------------------------------------
# Tests unitaires (mock — sans credentials)
# ---------------------------------------------------------------------------

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
        lambda *a, **kw: {'body': {'success': True, 'response': {}}},
    )

    assert service.lire_document_3(org_id) is None


def test_lire_document3_activite_sans_enseignants(service, monkeypatch):
    """Vérifie que lire_document_3 gère correctement une activité sans enseignants."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    activite_sans_ens = {
        'coNumBranche': 20, 'coCategorie': 'B', 'teNomBranche': 'Français',
        'noAnneeEtude': '2', 'nbPeriodesDoc8': 2, 'nbPeriodesPrevuesDoc2': 2,
        'nbPeriodesReellesDoc2': 2, 'enseignantListe': None,
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
            'coNumBranche': 10, 'coCategorie': 'A', 'teNomBranche': 'Mathématiques',
            'noAnneeEtude': '1', 'nbPeriodesDoc8': 4, 'nbPeriodesPrevuesDoc2': 4,
            'nbPeriodesReellesDoc2': 4,
            'enseignantListe': {
                'enseignant': [
                    {
                        'coNumAttribution': 1, 'noMatEns': '123456',
                        'teNomEns': 'Dupont', 'tePrenomEns': 'Jean',
                        'teAbrEns': 'DUP', 'teEnseignant': 'Dupont Jean',
                        'coDispo': 'D', 'teStatut': 'DEF',
                        'nbPeriodesAttribuees': 6.0,
                        'tsMaj': None, 'teUserMaj': None,
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
                noAnneeEtude='1',
                enseignantListe=Doc3EnseignantListSave(
                    enseignant=[
                        Doc3EnseignantDetailSave(
                            coNumAttribution=1,
                            noMatEns='123456',
                            coDispo='D',
                            teStatut='DEF',
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

    # Trouver la première activité avec enseignant assigné
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
