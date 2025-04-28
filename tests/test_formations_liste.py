# test_formations_liste.py

import pytest
from pyetnic.services.formations_liste import FormationsListeService
from pyetnic.services.models import Formation, Organisation

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
                assert organisation.numOrganisation > 0
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
