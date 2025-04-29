# test_formations_liste.py

import pytest
from pyetnic.services.formations_liste import FormationsListeService
from pyetnic.services.models import Formation, Organisation
import time
from datetime import date

@pytest.fixture
def formations_liste_service():
    return FormationsListeService()

def test_lister_formations_organisables(formations_liste_service):
    result = formations_liste_service.lister_formations_organisables()
    
    assert result.success == True
    assert len(result.formations) > 0
    
    for formation in result.formations:
        assert isinstance(formation, Formation)
        assert formation.numAdmFormation > 0
        assert formation.libelleFormation != ""
        assert formation.codeFormation != ""
        assert formation.organisations == []  # Les formations organisables n'ont pas d'organisations

def test_lister_formations(formations_liste_service):
    result = formations_liste_service.lister_formations()
    
    assert result.success == True
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
                assert isinstance(organisation, Organisation)
                assert organisation.id.numOrganisation > 0
                assert organisation.dateDebutOrganisation is not None
                assert organisation.dateFinOrganisation is not None
    
    if formations_with_organisations == 0:
        pytest.fail("No formation with an organisation found.")

def test_lister_formations_error(formations_liste_service, monkeypatch):
    def mock_call_service(*args, **kwargs):
        raise Exception("Test error")
    
    monkeypatch.setattr(formations_liste_service.client_manager, "call_service", mock_call_service)
    
    result = formations_liste_service.lister_formations()
    
    assert result.success == False
    assert len(result.formations) == 0
    assert len(result.messages) > 0
    assert "Test error" in result.messages[0]

def test_lister_formations_organisables_error(formations_liste_service, monkeypatch):
    def mock_call_service(*args, **kwargs):
        raise Exception("Test error")
    
    monkeypatch.setattr(formations_liste_service.client_manager, "call_service", mock_call_service)
    
    result = formations_liste_service.lister_formations_organisables()
    
    assert result.success == False
    assert len(result.formations) == 0
    assert len(result.messages) > 0
    assert "Test error" in result.messages[0]

def test_performance_lister_formations(formations_liste_service):
    start_time = time.time()
    result = formations_liste_service.lister_formations()
    end_time = time.time()
    assert result.success == True
    assert end_time - start_time < 5  # La requête devrait prendre moins de 5 secondes

def test_validation_donnees_formations(formations_liste_service):
    result = formations_liste_service.lister_formations()
    assert result.success == True
    for formation in result.formations:
        assert isinstance(formation.numAdmFormation, int)
        assert isinstance(formation.libelleFormation, str)
        assert isinstance(formation.codeFormation, str)
        for org in formation.organisations:
            assert isinstance(org.dateDebutOrganisation, date)
            assert isinstance(org.dateFinOrganisation, date)
            assert org.dateDebutOrganisation <= org.dateFinOrganisation

def test_lister_formations_cas_limites(formations_liste_service):
    # Test avec une année scolaire future
    result_future = formations_liste_service.lister_formations(annee_scolaire="2030-2031")
    assert result_future.success == False
    assert len(result_future.formations) == 0

    # Test avec un établissement inexistant
    result_invalid_etab = formations_liste_service.lister_formations(etab_id=99999)
    assert result_invalid_etab.success == False

def test_lister_formations_mock_response(formations_liste_service, monkeypatch):
    mock_response = {
        "body": {
            "success": True,
            "response": {
                "formation": [
                    {"numAdmFormation": 1, "libelleFormation": "Test Formation", "codeFormation": "TEST001"}
                ]
            }
        }
    }
    
    def mock_call_service(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(formations_liste_service.client_manager, "call_service", mock_call_service)
    
    result = formations_liste_service.lister_formations()
    assert result.success == True
    assert len(result.formations) == 1
    assert result.formations[0].numAdmFormation == 1
    assert result.formations[0].libelleFormation == "Test Formation"
    assert result.formations[0].codeFormation == "TEST001"
