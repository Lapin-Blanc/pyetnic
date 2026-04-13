# test_formations_liste_integration.py — integration tests against ws-tq.etnic.be.

import time
from datetime import date

import pytest

from pyetnic.config import Config
from pyetnic.services.formations_liste import FormationsListeService
from pyetnic.services.models import Formation, OrganisationApercu


@pytest.fixture
def formations_liste_service():
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")
    return FormationsListeService()


def test_lister_formations_organisables(formations_liste_service):
    result = formations_liste_service.lister_formations_organisables()

    assert result.success is True
    assert len(result.formations) > 0

    for formation in result.formations:
        assert isinstance(formation, Formation)
        assert formation.numAdmFormation > 0
        assert formation.libelleFormation != ""
        assert formation.codeFormation != ""
        assert formation.organisations == []


def test_lister_formations(formations_liste_service):
    result = formations_liste_service.lister_formations()

    assert result.success is True
    assert len(result.formations) > 0

    formations_with_organisations = 0
    for formation in result.formations:
        assert isinstance(formation, Formation)
        assert formation.numAdmFormation > 0
        assert formation.libelleFormation != ""
        assert formation.codeFormation != ""

        if formation.organisations:
            formations_with_organisations += 1
            for organisation in formation.organisations:
                assert isinstance(organisation, OrganisationApercu)
                assert organisation.id.numOrganisation > 0
                assert organisation.dateDebutOrganisation is not None
                assert organisation.dateFinOrganisation is not None

    if formations_with_organisations == 0:
        pytest.fail("No formation with an organisation found.")


def test_performance_lister_formations(formations_liste_service):
    start_time = time.time()
    result = formations_liste_service.lister_formations()
    end_time = time.time()
    assert result.success is True
    assert end_time - start_time < 5


def test_validation_donnees_formations(formations_liste_service):
    result = formations_liste_service.lister_formations()
    assert result.success is True
    for formation in result.formations:
        assert isinstance(formation.numAdmFormation, int)
        assert isinstance(formation.libelleFormation, str)
        assert isinstance(formation.codeFormation, str)
        for org in formation.organisations:
            assert isinstance(org.dateDebutOrganisation, date)
            assert isinstance(org.dateFinOrganisation, date)
            assert org.dateDebutOrganisation <= org.dateFinOrganisation


def test_lister_formations_cas_limites(formations_liste_service):
    result_future = formations_liste_service.lister_formations(annee_scolaire="2030-2031")
    assert result_future.success is False
    assert len(result_future.formations) == 0

    result_invalid_etab = formations_liste_service.lister_formations(etab_id=99999)
    assert result_invalid_etab.success is False
