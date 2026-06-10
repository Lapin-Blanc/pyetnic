# test_formations_liste_unit.py — mock-only unit tests for FormationsListeService.

import pytest

from pyetnic.services.formations_liste import FormationsListeService
from pyetnic.soap_client import SoapError


def test_lister_formations_wraps_soap_error(monkeypatch):
    """SoapError from the transport layer is wrapped into a failure result."""
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise SoapError("Test transport error")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    result = svc.lister_formations()

    assert result.success is False
    assert result.formations == []
    assert "Test transport error" in result.messages[0]


def test_lister_formations_organisables_wraps_soap_error(monkeypatch):
    """Same wrap-on-SoapError contract for lister_formations_organisables."""
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise SoapError("Test transport error")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    result = svc.lister_formations_organisables()

    assert result.success is False
    assert result.formations == []
    assert "Test transport error" in result.messages[0]


def test_lister_formations_does_not_swallow_unexpected_exceptions(monkeypatch):
    """Unexpected exceptions must propagate, not be wrapped (phase 1.5)."""
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise RuntimeError("unexpected bug")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    with pytest.raises(RuntimeError, match="unexpected bug"):
        svc.lister_formations()


def test_lister_formations_organisables_does_not_swallow_unexpected_exceptions(monkeypatch):
    svc = FormationsListeService()

    def mock_call_service(*args, **kwargs):
        raise RuntimeError("unexpected bug")

    monkeypatch.setattr(svc.client_manager, "call_service", mock_call_service)

    with pytest.raises(RuntimeError, match="unexpected bug"):
        svc.lister_formations_organisables()


def test_lister_formations_flattens_messages_block(monkeypatch):
    """On success=False, messages must be a flat List[str], not the raw dict."""
    svc = FormationsListeService()
    mock_response = {
        "body": {
            "success": False,
            "messages": {
                "error": [{"code": "00009", "description": "Aucun enregistrement"}],
                "warning": {"code": "12345", "description": "Attention"},
            },
        }
    }
    monkeypatch.setattr(svc.client_manager, "call_service", lambda *a, **kw: mock_response)

    result = svc.lister_formations()

    assert result.success is False
    assert result.messages == ["00009: Aucun enregistrement", "12345: Attention"]
    assert all(isinstance(m, str) for m in result.messages)


def test_lister_formations_organisables_flattens_messages_block(monkeypatch):
    """Same flattening contract for lister_formations_organisables."""
    svc = FormationsListeService()
    mock_response = {
        "body": {
            "success": False,
            "messages": {"error": [{"code": "30001", "description": "Établissement incorrect"}]},
        }
    }
    monkeypatch.setattr(svc.client_manager, "call_service", lambda *a, **kw: mock_response)

    result = svc.lister_formations_organisables()

    assert result.success is False
    assert result.messages == ["30001: Établissement incorrect"]


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
