# test_formations_liste_unit.py — mock-only unit tests for FormationsListeService.

from pyetnic.services.formations_liste import FormationsListeService


def test_lister_formations_error(monkeypatch):
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    result = svc.lister_formations()

    assert result.success is False
    assert len(result.formations) == 0
    assert len(result.messages) > 0
    assert "Test error" in result.messages[0]


def test_lister_formations_organisables_error(monkeypatch):
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    result = svc.lister_formations_organisables()

    assert result.success is False
    assert len(result.formations) == 0
    assert len(result.messages) > 0
    assert "Test error" in result.messages[0]


def test_lister_formations_mock_response(monkeypatch):
    svc = FormationsListeService()
    mock_response = {
        "body": {
            "success": True,
            "response": {
                "formation": [
                    {"numAdmFormation": 1, "libelleFormation": "Test Formation", "codeFormation": "TEST001"}
                ]
            },
        }
    }

    def mock_call_service(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    result = svc.lister_formations()
    assert result.success is True
    assert len(result.formations) == 1
    assert result.formations[0].numAdmFormation == 1
    assert result.formations[0].libelleFormation == "Test Formation"
    assert result.formations[0].codeFormation == "TEST001"
