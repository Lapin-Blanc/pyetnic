"""Regression tests for the error mode of the EPROM services.

- Since 0.3.0 (#35) ``Config.RAISE_ON_ERROR`` defaults to ``True``: EPROM
  services raise typed exceptions on a server refusal.
- ``permissive_errors()`` (or ``Config.RAISE_ON_ERROR = False``) restores the
  pre-0.3.0 contract, ``None`` / ``FormationsListeResult(success=False)``, and
  warns that it is deprecated.
- ``strict_errors()`` keeps working and forces raising inside a permissive block.
- The flag is backed by a ``ContextVar``: each thread / asyncio task sees
  its own value.
"""

import threading
import warnings

import pytest

from pyetnic import Config, permissive_errors, strict_errors
from pyetnic.eprom import (
    EtnicAlreadyApprovedError,
    EtnicBusinessError,
    EtnicConcurrencyError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
    OrganisationId,
    SoapError,
    lire_document_1,
    lire_document_2,
    lire_document_3,
    lire_organisation,
    lister_formations,
    supprimer_organisation,
)
from pyetnic.exceptions import map_etnic_error_code_to_class

# ---------------------------------------------------------------------------
# Common sample
# ---------------------------------------------------------------------------


SAMPLE_ORG_ID = OrganisationId(
    anneeScolaire="2024-2025",
    etabId=1234,
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
# Default mode: raise (since 0.3.0)
# ---------------------------------------------------------------------------


def test_default_mode_raise_on_error_is_true():
    Config._reset()
    assert Config.RAISE_ON_ERROR is True


def test_default_mode_lire_organisation_raises(mock_soap_call):
    mock_soap_call.return_value = _empty_response()
    with pytest.raises(EtnicBusinessError):
        lire_organisation(SAMPLE_ORG_ID)


def test_default_mode_error_response_raises_typed(mock_soap_call):
    mock_soap_call.return_value = _error_response("20102", "Doc non accessible")
    with pytest.raises(EtnicDocumentNotAccessibleError):
        lire_document_3(SAMPLE_ORG_ID)


def test_default_mode_supprimer_raises_on_failure(mock_soap_call):
    mock_soap_call.return_value = _error_response("00009", "Organisation inconnue")
    with pytest.raises(EtnicNotFoundError):
        supprimer_organisation(SAMPLE_ORG_ID)


# ---------------------------------------------------------------------------
# Permissive mode (deprecated): the pre-0.3.0 contract
# ---------------------------------------------------------------------------


def test_permissive_mode_returns_none_and_warns(mock_soap_call):
    mock_soap_call.return_value = _error_response("20102", "Doc non accessible")
    with pytest.warns(DeprecationWarning, match="removed in 1.0"):
        with permissive_errors():
            assert lire_document_3(SAMPLE_ORG_ID) is None
            mock_soap_call.return_value = _empty_response()
            assert lire_organisation(SAMPLE_ORG_ID) is None
            mock_soap_call.return_value = _error_response("00009", "Organisation inconnue")
            assert supprimer_organisation(SAMPLE_ORG_ID) is False
    assert Config.RAISE_ON_ERROR is True


def test_permissive_mode_via_config_flag_warns(mock_soap_call):
    mock_soap_call.return_value = _empty_response()
    try:
        with pytest.warns(DeprecationWarning):
            Config.RAISE_ON_ERROR = False
        assert lire_organisation(SAMPLE_ORG_ID) is None
    finally:
        Config._reset()


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
        Config._reset()


# ---------------------------------------------------------------------------
# Strict mode via context manager
# ---------------------------------------------------------------------------


def test_strict_mode_via_context_manager(mock_soap_call):
    """strict_errors() makes lire_organisation raise inside the block."""
    mock_soap_call.return_value = _empty_response()
    with strict_errors():
        with pytest.raises(EtnicBusinessError):
            lire_organisation(SAMPLE_ORG_ID)


def test_strict_mode_inside_permissive_block_restores_it(mock_soap_call):
    """strict_errors() forces raising, then gives the permissive mode back."""
    mock_soap_call.return_value = _empty_response()

    with pytest.warns(DeprecationWarning), permissive_errors():
        assert Config.RAISE_ON_ERROR is False
        with strict_errors():
            assert Config.RAISE_ON_ERROR is True
            with pytest.raises(EtnicBusinessError):
                lire_organisation(SAMPLE_ORG_ID)
        assert Config.RAISE_ON_ERROR is False
        assert lire_organisation(SAMPLE_ORG_ID) is None
    assert Config.RAISE_ON_ERROR is True


def test_permissive_mode_restored_on_exception(mock_soap_call):
    """The flag is restored even if an exception leaves the block."""
    with pytest.warns(DeprecationWarning), pytest.raises(RuntimeError):
        with permissive_errors():
            raise RuntimeError("boom")
    assert Config.RAISE_ON_ERROR is True


def test_strict_mode_context_manager_nested_preserves_outer():
    """Nesting strict_errors() keeps the outer value."""
    with strict_errors():
        with strict_errors():
            assert Config.RAISE_ON_ERROR is True
        assert Config.RAISE_ON_ERROR is True
    assert Config.RAISE_ON_ERROR is True


# ---------------------------------------------------------------------------
# Specialized exception classes (error-code mapping)
# ---------------------------------------------------------------------------


def test_strict_mode_raises_document_not_accessible_on_20102(mock_soap_call):
    """ETNIC error code 20102 maps to EtnicDocumentNotAccessibleError."""
    mock_soap_call.return_value = _error_response(
        "20102", 'Les "Doc A" et "Doc 2" doivent être approuvés pour pouvoir accéder au "Doc 3"'
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


# ---------------------------------------------------------------------------
# Full catalogue routing (map_etnic_error_code_to_class)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        # Discrete codes
        ("00009", EtnicNotFoundError),
        ("20102", EtnicDocumentNotAccessibleError),
        ("20101", EtnicDocumentNotAccessibleError),  # Doc A not approved (Documents 1, 1D)
        ("20103", EtnicDocumentNotAccessibleError),  # Doc 1 population not validated (Document 2)
        ("20112", EtnicDocumentNotAccessibleError),  # Doc 1D fee before the population is approved
        ("1546", EtnicDocumentNotAccessibleError),  # the same, as the Doc 1D manual numbers it
        ("20104", EtnicConcurrencyError),  # approval with values that differ from the stored ones
        ("30003", EtnicDocumentNotAccessibleError),
        ("30006", EtnicDocumentNotAccessibleError),
        ("1530", EtnicAlreadyApprovedError),
        ("1545", EtnicAlreadyApprovedError),
        ("00011", EtnicConcurrencyError),
        ("30001", EtnicValidationError),
        ("30002", EtnicValidationError),
        ("30004", EtnicValidationError),  # the 2026-06-01 masked-symptom code
        ("30005", EtnicValidationError),
        ("30007", EtnicValidationError),
        ("30008", EtnicValidationError),
        ("30009", EtnicValidationError),
        ("30010", EtnicValidationError),  # BESAeSI before 2026-2027 (Organisation v8)
        ("20005", EtnicValidationError),
        ("20016", EtnicValidationError),
        ("20038", EtnicValidationError),
        ("20042", EtnicValidationError),  # BESAeSI switch (Organisation v8)
        ("20041", EtnicValidationError),  # Doc 2: sub-type imposed by the type (rev 1.4)
        ("1113", EtnicValidationError),
        ("1114", EtnicValidationError),
        ("2106", EtnicValidationError),
        ("2118", EtnicValidationError),
        ("1574", EtnicValidationError),  # Doc 3: attributions above the periods organised
        ("20108", EtnicValidationError),  # Doc 3: staff number unknown to EPROM
        ("20110", EtnicValidationError),  # Doc 3: status incorrect
        # Numeric ranges
        ("4004", EtnicValidationError),
        ("4012", EtnicValidationError),
        ("1527", EtnicValidationError),
        ("1600", EtnicValidationError),
        ("20020", EtnicValidationError),
        ("30016", EtnicValidationError),
        ("30017", EtnicValidationError),
        # Unmapped / not client-fixable → base class
        ("00025", EtnicBusinessError),
        ("00999", EtnicBusinessError),
        ("99999", EtnicBusinessError),
        (None, EtnicBusinessError),
    ],
)
def test_map_etnic_error_code_to_class(code, expected):
    assert map_etnic_error_code_to_class(code) is expected


@pytest.mark.parametrize("service, expected", [
    (None, EtnicAlreadyApprovedError),
    ("DOCUMENT1", EtnicAlreadyApprovedError),  # "Le Doc 1 est approuvé"
    ("DOCUMENT1D", EtnicAlreadyApprovedError),  # "Document déjà approuvé !"
    ("DOCUMENT2", EtnicValidationError),  # "créer une 5ième intervention extérieure"
])
def test_code_1545_depends_on_the_service(service, expected):
    assert map_etnic_error_code_to_class("1545", service) is expected


def test_document2_refusal_1545_is_a_validation_error(mock_soap_call):
    """The Document 2 service passes its name, so 1545 reads as a validation error there."""
    mock_soap_call.return_value = {
        "header": {"requestId": "r"},
        "body": {"success": False, "response": None, "messages": {"error": [
            {"code": "1545", "description": "Vous ne pouvez pas créer une 5ième intervention extérieure"}]}},
    }
    org_id = OrganisationId(anneeScolaire="2025-2026", etabId=1234, numAdmFormation=1, numOrganisation=1)
    with strict_errors(), pytest.raises(EtnicValidationError):
        lire_document_2(org_id)


def test_map_handles_non_numeric_code():
    """A non-numeric, unknown code must not raise — falls back to base."""
    assert map_etnic_error_code_to_class("ABC") is EtnicBusinessError


def test_strict_mode_raises_validation_on_30004(mock_soap_call):
    """ETNIC code 30004 must raise EtnicValidationError, not a generic error."""
    mock_soap_call.return_value = _error_response(
        "30004", "Le type d'intervention extérieure est incorrect"
    )
    with strict_errors():
        with pytest.raises(EtnicValidationError) as exc_info:
            lire_organisation(SAMPLE_ORG_ID)
    assert exc_info.value.code == "30004"


def test_strict_mode_surfaces_real_etnic_message(mock_soap_call):
    """str(exc) must carry the real ETNIC code + description, not the generic
    "response was empty or success=False" placeholder (the 2026-06-01 masking
    bug)."""
    mock_soap_call.return_value = _error_response(
        "30004", "Le type d'intervention extérieure est incorrect"
    )
    with strict_errors():
        with pytest.raises(EtnicValidationError) as exc_info:
            lire_organisation(SAMPLE_ORG_ID)
    message = str(exc_info.value)
    assert "30004" in message
    assert "Le type d'intervention extérieure est incorrect" in message
    assert "empty or success=False" not in message
    # The description attribute must always be populated when ETNIC provided one.
    assert exc_info.value.description == "Le type d'intervention extérieure est incorrect"


def test_strict_mode_raises_already_approved_on_1530(mock_soap_call):
    mock_soap_call.return_value = _error_response("1530", "Document déjà approuvé")
    with strict_errors():
        with pytest.raises(EtnicAlreadyApprovedError):
            lire_document_1(SAMPLE_ORG_ID)


def test_strict_mode_raises_concurrency_on_00011(mock_soap_call):
    mock_soap_call.return_value = _error_response("00011", "Modifié par un autre utilisateur")
    with strict_errors():
        with pytest.raises(EtnicConcurrencyError):
            lire_document_2(SAMPLE_ORG_ID)


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


def test_permissive_mode_lister_formations_returns_failure_result(mock_soap_call):
    """Permissive mode keeps the FormationsListeResult(success=False) contract."""
    mock_soap_call.return_value = {
        "body": {
            "success": False,
            "response": None,
            "messages": {"error": [{"code": "20102", "description": "refus"}]},
        }
    }
    with pytest.warns(DeprecationWarning), permissive_errors():
        result = lister_formations()
    assert result.success is False
    assert result.formations == []


def test_default_mode_lister_formations_raises(mock_soap_call):
    mock_soap_call.return_value = {
        "body": {
            "success": False,
            "response": None,
            "messages": {"error": [{"code": "20102", "description": "refus"}]},
        }
    }
    with pytest.raises(EtnicDocumentNotAccessibleError):
        lister_formations()


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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            Config.RAISE_ON_ERROR = False
        results["a"] = Config.RAISE_ON_ERROR
        a_done.set()

    def thread_b():
        a_done.wait(timeout=2.0)
        # Should see the default (True), not thread A's setting.
        results["b"] = Config.RAISE_ON_ERROR
        start_b.set()

    t_a = threading.Thread(target=thread_a)
    t_b = threading.Thread(target=thread_b)
    t_a.start()
    t_b.start()
    t_a.join(timeout=2.0)
    t_b.join(timeout=2.0)

    assert results["a"] is False
    assert results["b"] is True
