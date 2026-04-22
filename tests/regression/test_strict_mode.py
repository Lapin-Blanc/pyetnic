"""Regression tests for strict error mode (opt-in raise-on-error).

Default-mode behavior is covered by the existing regression tests
(``test_public_api_eprom.py``). This file adds tests for the new opt-in
strict mode:

- ``Config.RAISE_ON_ERROR`` defaults to ``False``.
- Setting it to ``True`` (directly or via ``strict_errors()``) makes EPROM
  services raise typed exceptions instead of returning ``None`` /
  ``FormationsListeResult(success=False)``.
- The flag is backed by a ``ContextVar``: each thread / asyncio task sees
  its own value.
"""

import threading

import pytest

from pyetnic import Config, strict_errors
from pyetnic.eprom import (
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    OrganisationId,
    SoapError,
    lire_document_1,
    lire_document_2,
    lire_document_3,
    lire_organisation,
    lister_formations,
    supprimer_organisation,
)


# ---------------------------------------------------------------------------
# Common sample
# ---------------------------------------------------------------------------


SAMPLE_ORG_ID = OrganisationId(
    anneeScolaire="2024-2025",
    etabId=3052,
    numAdmFormation=455,
    numOrganisation=1,
)


def _empty_response() -> dict:
    return {"body": {"success": True, "response": None}}


def _error_response(code: str, description: str) -> dict:
    return {
        "header": {"requestId": "req-abc-123"},
        "body": {
            "success": False,
            "response": None,
            "messages": {"error": {"code": code, "description": description}},
        },
    }


# ---------------------------------------------------------------------------
# Default mode: legacy behavior must be preserved
# ---------------------------------------------------------------------------


def test_default_mode_raise_on_error_is_false():
    """The default value of Config.RAISE_ON_ERROR must remain False."""
    Config._reset()
    assert Config.RAISE_ON_ERROR is False


def test_default_mode_lire_organisation_returns_none(mock_soap_call):
    """In default mode, an empty response still returns None (legacy)."""
    mock_soap_call.return_value = _empty_response()
    assert lire_organisation(SAMPLE_ORG_ID) is None


def test_default_mode_error_response_returns_none(mock_soap_call):
    """In default mode, an error response still returns None (legacy)."""
    mock_soap_call.return_value = _error_response("20102", "Doc non accessible")
    assert lire_document_3(SAMPLE_ORG_ID) is None


def test_default_mode_supprimer_returns_false_on_failure(mock_soap_call):
    """In default mode, supprimer_organisation returns False on failure."""
    mock_soap_call.return_value = _error_response("00009", "Organisation inconnue")
    assert supprimer_organisation(SAMPLE_ORG_ID) is False


# ---------------------------------------------------------------------------
# Strict mode via Config.RAISE_ON_ERROR
# ---------------------------------------------------------------------------


def test_strict_mode_via_config_flag(mock_soap_call):
    """Setting Config.RAISE_ON_ERROR = True makes lire_organisation raise."""
    mock_soap_call.return_value = _empty_response()
    Config.RAISE_ON_ERROR = True
    try:
        with pytest.raises(EtnicBusinessError):
            lire_organisation(SAMPLE_ORG_ID)
    finally:
        Config.RAISE_ON_ERROR = False


# ---------------------------------------------------------------------------
# Strict mode via context manager
# ---------------------------------------------------------------------------


def test_strict_mode_via_context_manager(mock_soap_call):
    """strict_errors() makes lire_organisation raise inside the block."""
    mock_soap_call.return_value = _empty_response()
    with strict_errors():
        with pytest.raises(EtnicBusinessError):
            lire_organisation(SAMPLE_ORG_ID)


def test_strict_mode_context_manager_restores_previous_value(mock_soap_call):
    """After exiting the context, the flag returns to its previous value."""
    mock_soap_call.return_value = _empty_response()

    assert Config.RAISE_ON_ERROR is False
    with strict_errors():
        assert Config.RAISE_ON_ERROR is True
    assert Config.RAISE_ON_ERROR is False

    # And legacy behavior resumes outside the block
    assert lire_organisation(SAMPLE_ORG_ID) is None


def test_strict_mode_context_manager_restores_on_exception(mock_soap_call):
    """The flag is restored even if an exception is raised inside."""
    mock_soap_call.return_value = _empty_response()

    with pytest.raises(EtnicBusinessError):
        with strict_errors():
            lire_organisation(SAMPLE_ORG_ID)

    assert Config.RAISE_ON_ERROR is False


def test_strict_mode_context_manager_nested_preserves_outer():
    """Nesting strict_errors() restores the outer value, not False."""
    Config.RAISE_ON_ERROR = True
    try:
        with strict_errors():
            assert Config.RAISE_ON_ERROR is True
        assert Config.RAISE_ON_ERROR is True
    finally:
        Config.RAISE_ON_ERROR = False


# ---------------------------------------------------------------------------
# Specialized exception classes (error-code mapping)
# ---------------------------------------------------------------------------


def test_strict_mode_raises_document_not_accessible_on_20102(mock_soap_call):
    """ETNIC error code 20102 maps to EtnicDocumentNotAccessibleError."""
    mock_soap_call.return_value = _error_response(
        "20102", "Doc 1 et Doc 2 doivent être approuvés"
    )
    with strict_errors():
        with pytest.raises(EtnicDocumentNotAccessibleError) as exc_info:
            lire_document_3(SAMPLE_ORG_ID)

    assert exc_info.value.code == "20102"
    assert "approuvés" in (exc_info.value.description or "")
    assert exc_info.value.request_id == "req-abc-123"
    # Also catchable as the parent class.
    assert isinstance(exc_info.value, EtnicBusinessError)


def test_strict_mode_raises_not_found_on_00009(mock_soap_call):
    """ETNIC error code 00009 maps to EtnicNotFoundError."""
    mock_soap_call.return_value = _error_response("00009", "Aucun enregistrement")
    with strict_errors():
        with pytest.raises(EtnicNotFoundError) as exc_info:
            lire_organisation(SAMPLE_ORG_ID)

    assert exc_info.value.code == "00009"


def test_strict_mode_unknown_code_raises_generic_business_error(mock_soap_call):
    """Unknown codes fall back to plain EtnicBusinessError."""
    mock_soap_call.return_value = _error_response("99999", "Erreur inconnue")
    with strict_errors():
        with pytest.raises(EtnicBusinessError) as exc_info:
            lire_document_1(SAMPLE_ORG_ID)

    assert type(exc_info.value) is EtnicBusinessError
    assert exc_info.value.code == "99999"


def test_strict_mode_document2_raises(mock_soap_call):
    """All EPROM _parse_*_response helpers participate in strict mode."""
    mock_soap_call.return_value = _empty_response()
    with strict_errors():
        with pytest.raises(EtnicBusinessError):
            lire_document_2(SAMPLE_ORG_ID)


def test_strict_mode_supprimer_raises_on_failure(mock_soap_call):
    """supprimer_organisation raises in strict mode on server refusal."""
    mock_soap_call.return_value = _error_response("00009", "Organisation inconnue")
    with strict_errors():
        with pytest.raises(EtnicNotFoundError):
            supprimer_organisation(SAMPLE_ORG_ID)


# ---------------------------------------------------------------------------
# FormationsListeResult remains on success in both modes; raises on error in strict
# ---------------------------------------------------------------------------


def test_strict_mode_lister_formations_raises_on_error(mock_soap_call):
    """lister_formations raises EtnicBusinessError in strict mode on success=False."""
    mock_soap_call.return_value = {
        "body": {
            "success": False,
            "response": None,
            "messages": {"error": {"code": "20102", "description": "refus"}},
        }
    }
    with strict_errors():
        with pytest.raises(EtnicDocumentNotAccessibleError):
            lister_formations()


def test_default_mode_lister_formations_returns_failure_result(mock_soap_call):
    """Default mode keeps the FormationsListeResult(success=False) contract."""
    mock_soap_call.return_value = {
        "body": {
            "success": False,
            "response": None,
            "messages": {"error": [{"code": "20102", "description": "refus"}]},
        }
    }
    result = lister_formations()
    assert result.success is False
    assert result.formations == []


# ---------------------------------------------------------------------------
# Transport errors propagate in both modes (they always have)
# ---------------------------------------------------------------------------


def test_strict_mode_transport_error_propagates(mock_soap_call):
    """In strict mode, SoapError / EtnicTransportError propagates as-is."""
    mock_soap_call.side_effect = SoapError("network down")
    with strict_errors():
        with pytest.raises(SoapError):
            lire_organisation(SAMPLE_ORG_ID)


# ---------------------------------------------------------------------------
# Thread isolation (ContextVar)
# ---------------------------------------------------------------------------


def test_context_var_is_isolated_across_threads():
    """Setting RAISE_ON_ERROR in one thread does not affect another."""
    results: dict[str, bool] = {}
    start_b = threading.Event()
    a_done = threading.Event()

    def thread_a():
        Config.RAISE_ON_ERROR = True
        results["a"] = Config.RAISE_ON_ERROR
        a_done.set()

    def thread_b():
        a_done.wait(timeout=2.0)
        # Should see the default (False), not thread A's setting.
        results["b"] = Config.RAISE_ON_ERROR
        start_b.set()

    t_a = threading.Thread(target=thread_a)
    t_b = threading.Thread(target=thread_b)
    t_a.start()
    t_b.start()
    t_a.join(timeout=2.0)
    t_b.join(timeout=2.0)

    assert results["a"] is True
    assert results["b"] is False
