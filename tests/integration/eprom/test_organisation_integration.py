# test_organisation_integration.py — integration tests against ws-tq.etnic.be.

import logging
from dataclasses import fields
from datetime import date

import pytest

from pyetnic.config import Config
from pyetnic.services import lister_formations_organisables
from pyetnic.services.models import Organisation
from pyetnic.services.organisation import OrganisationService

logger = logging.getLogger(__name__)


def _etab_id() -> int:
    return int(Config.ETAB_ID)


def _impl_id() -> int:
    return int(Config.IMPL_ID)


@pytest.fixture
def organisation_temporaire():
    """Crée une organisation sur le service dev et la supprime après le test."""
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

    org_relu = svc.lire_organisation(organisation_temporaire.id)
    assert org_relu is not None
    assert org_relu.dateFinOrganisation == nouvelle_date_fin


def test_cycle_complet_organisation():
    """Test du cycle complet : créer → lire → modifier → supprimer."""
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

        org_lu = svc.lire_organisation(org_id)
        assert org_lu is not None
        assert org_lu.dateDebutOrganisation == date(2024, 9, 2)

        org_lu.dateFinOrganisation = date(2025, 6, 20)
        org_modifie = svc.modifier_organisation(org_lu)
        assert org_modifie is not None

        org_relu = svc.lire_organisation(org_id)
        assert org_relu.dateFinOrganisation == date(2025, 6, 20)
        logger.info("Modification vérifiée")

    finally:
        if org_id:
            supprime = svc.supprimer_organisation(org_id)
            assert supprime, f"La suppression de l'organisation {org_id.numOrganisation} a échoué"
            logger.info(f"Organisation {org_id.numOrganisation} supprimée")
