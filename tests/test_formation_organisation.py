# test_formation_organisation.py

import pytest
import logging
from datetime import date, timedelta
from dataclasses import fields

from pyetnic.services.organisation import OrganisationService
from pyetnic.services.models import OrganisationId, Organisation
from pyetnic.services import lister_formations_organisables
from pyetnic.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _etab_id() -> int:
    return int(Config.ETAB_ID)

def _impl_id() -> int:
    return int(Config.IMPL_ID)

def _mock_org_response(annee_scolaire, etab_id, num_adm, num_org, date_fin_str="2025-06-27"):
    return {
        'body': {
            'success': True,
            'response': {
                'organisation': {
                    'id': {
                        'anneeScolaire': annee_scolaire,
                        'etabId': etab_id,
                        'numAdmFormation': num_adm,
                        'numOrganisation': num_org,
                        'implId': None,
                    },
                    'dateDebutOrganisation': date(2024, 9, 2),
                    'dateFinOrganisation': date.fromisoformat(date_fin_str),
                    'nombreSemaineFormation': 36,
                    'statut': None,
                    'organisationPeriodesSupplOuEPT': None,
                    'valorisationAcquis': None,
                    'enPrison': None,
                    'eLearning': None,
                    'activiteFormation': None,
                    'conseillerPrevention': None,
                    'partiellementDistance': None,
                    'enseignementHybride': None,
                    'numOrganisation2AnneesScolaires': None,
                    'typeInterventionExterieure': None,
                    'interventionExterieure50p': None,
                }
            }
        }
    }

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return OrganisationService()


@pytest.fixture
def organisation_temporaire():
    """Crée une organisation sur le service dev et la supprime après le test.

    Garantit la suppression même si le test échoue (try/finally).
    Skip automatiquement si la config ou les formations organisables sont absentes.
    """
    if not Config.ETAB_ID or not Config.IMPL_ID:
        pytest.skip("Config DEFAULT_ETABID / DEFAULT_IMPLID non définie dans .env")

    formations = lister_formations_organisables(
        annee_scolaire=Config.ANNEE_SCOLAIRE,
        etab_id=_etab_id(),
        impl_id=_impl_id(),
    )
    if not formations or not formations.formations:
        pytest.skip("Aucune formation organisable disponible pour le test")

    num_adm = formations.formations[0].numAdmFormation
    svc = OrganisationService()

    org = svc.creer_organisation(
        annee_scolaire=Config.ANNEE_SCOLAIRE,
        etab_id=_etab_id(),
        impl_id=_impl_id(),
        num_adm_formation=num_adm,
        date_debut=date(2024, 9, 2),
        date_fin=date(2025, 6, 27),
    )
    assert org is not None, "La création de l'organisation a échoué — fixture impossible à initialiser"

    try:
        yield org
    finally:
        try:
            supprime = svc.supprimer_organisation(org.id)
            if not supprime:
                logger.warning(f"Suppression de l'organisation de test {org.id} a renvoyé False")
        except Exception as e:
            logger.error(f"Échec de la suppression de l'organisation de test {org.id}: {e}")


# ---------------------------------------------------------------------------
# Tests unitaires (mock — sans credentials)
# ---------------------------------------------------------------------------

def test_lire_organisation_mock(service, monkeypatch):
    """Vérifie le parsing de la réponse LireOrganisation."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 1),
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
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {'body': {'success': True, 'response': {}}},
    )

    assert service.lire_organisation(org_id) is None


def test_creer_organisation_mock(service, monkeypatch):
    """Vérifie que creer_organisation parse correctement l'id attribué par le serveur."""
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 99),
    )

    org = service.creer_organisation(
        annee_scolaire="2023-2024",
        etab_id=3052, impl_id=6050,
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
        anneeScolaire="2023-2024", etabId=3052,
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
        lambda *a, **kw: _mock_org_response("2023-2024", 3052, 328, 1),
    )

    result = service.modifier_organisation(org)
    assert isinstance(result, Organisation)
    assert result.id == org_id


def test_supprimer_organisation_mock_succes(service, monkeypatch):
    """Vérifie que supprimer_organisation retourne True si success=True."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {'body': {'success': True}},
    )

    assert service.supprimer_organisation(org_id) is True


def test_supprimer_organisation_mock_echec(service, monkeypatch):
    """Vérifie que supprimer_organisation retourne False si success=False."""
    org_id = OrganisationId(
        anneeScolaire="2023-2024", etabId=3052,
        numAdmFormation=328, numOrganisation=1,
    )
    monkeypatch.setattr(
        service.client_manager, "call_service",
        lambda *a, **kw: {'body': {'success': False}},
    )

    assert service.supprimer_organisation(org_id) is False


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

def test_lire_organisation_creee(organisation_temporaire):
    """Vérifie que l'organisation créée est bien lisible sur le service."""
    svc = OrganisationService()
    org = svc.lire_organisation(organisation_temporaire.id)

    assert org is not None
    assert org.id.numOrganisation == organisation_temporaire.id.numOrganisation
    assert org.dateDebutOrganisation == date(2024, 9, 2)
    assert org.dateFinOrganisation == date(2025, 6, 27)
    for f in fields(Organisation):
        assert hasattr(org, f.name), f"Champ manquant : {f.name}"


def test_modifier_organisation_creee(organisation_temporaire):
    """Modifie la date de fin et vérifie la persistance du changement."""
    svc = OrganisationService()
    nouvelle_date_fin = date(2025, 6, 20)

    org_modifiee = Organisation(
        id=organisation_temporaire.id,
        dateDebutOrganisation=organisation_temporaire.dateDebutOrganisation,
        dateFinOrganisation=nouvelle_date_fin,
    )
    result = svc.modifier_organisation(org_modifiee)
    assert result is not None

    # Relecture pour confirmer la persistance
    org_relu = svc.lire_organisation(organisation_temporaire.id)
    assert org_relu is not None
    assert org_relu.dateFinOrganisation == nouvelle_date_fin


def test_cycle_complet_organisation():
    """Test du cycle complet : créer → lire → modifier → supprimer.

    Ce test gère lui-même son nettoyage via try/finally.
    """
    if not Config.ETAB_ID or not Config.IMPL_ID:
        pytest.skip("Config DEFAULT_ETABID / DEFAULT_IMPLID non définie dans .env")

    formations = lister_formations_organisables(
        annee_scolaire=Config.ANNEE_SCOLAIRE,
        etab_id=_etab_id(),
        impl_id=_impl_id(),
    )
    if not formations or not formations.formations:
        pytest.skip("Aucune formation organisable disponible")

    svc = OrganisationService()
    num_adm = formations.formations[0].numAdmFormation
    org_id = None

    try:
        # 1. Créer
        org = svc.creer_organisation(
            annee_scolaire=Config.ANNEE_SCOLAIRE,
            etab_id=_etab_id(),
            impl_id=_impl_id(),
            num_adm_formation=num_adm,
            date_debut=date(2024, 9, 2),
            date_fin=date(2025, 6, 27),
        )
        assert org is not None
        assert org.id.numOrganisation is not None
        org_id = org.id
        logger.info(f"Organisation créée : {org_id.numOrganisation}")

        # 2. Lire
        org_lu = svc.lire_organisation(org_id)
        assert org_lu is not None
        assert org_lu.dateDebutOrganisation == date(2024, 9, 2)

        # 3. Modifier
        org_lu.dateFinOrganisation = date(2025, 6, 20)
        org_modifie = svc.modifier_organisation(org_lu)
        assert org_modifie is not None

        org_relu = svc.lire_organisation(org_id)
        assert org_relu.dateFinOrganisation == date(2025, 6, 20)
        logger.info("Modification vérifiée")

    finally:
        # 4. Supprimer — garanti même en cas d'échec
        if org_id:
            supprime = svc.supprimer_organisation(org_id)
            assert supprime, f"La suppression de l'organisation {org_id.numOrganisation} a échoué"
            logger.info(f"Organisation {org_id.numOrganisation} supprimée")
