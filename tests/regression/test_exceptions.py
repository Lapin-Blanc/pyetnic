"""Regression tests for the EPROM exception hierarchy.

These tests verify the type hierarchy and the construction signatures.
They do NOT test that any service actually raises these — that's phase 1.3.
"""

import pytest

from pyetnic import (
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicError,
    EtnicNotFoundError,
    EtnicTransportError,
    EtnicValidationError,
    SoapError,
)


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------


def test_etnic_error_is_base():
    assert issubclass(EtnicError, Exception)


def test_transport_error_inherits_from_etnic_error():
    assert issubclass(EtnicTransportError, EtnicError)


def test_business_error_inherits_from_etnic_error():
    assert issubclass(EtnicBusinessError, EtnicError)


def test_document_not_accessible_inherits_from_business_error():
    assert issubclass(EtnicDocumentNotAccessibleError, EtnicBusinessError)


def test_not_found_inherits_from_business_error():
    assert issubclass(EtnicNotFoundError, EtnicBusinessError)


def test_validation_inherits_from_business_error():
    assert issubclass(EtnicValidationError, EtnicBusinessError)


# ---------------------------------------------------------------------------
# Backwards compatibility: SoapError is still catchable
# ---------------------------------------------------------------------------


def test_soap_error_is_alias_for_transport_error():
    """Existing code doing `except SoapError` must still work."""
    assert issubclass(SoapError, EtnicTransportError)


def test_soap_error_caught_by_etnic_error():
    """New code can catch all errors with a single except."""
    try:
        raise SoapError("test")
    except EtnicError:
        pass
    else:
        pytest.fail("EtnicError did not catch SoapError")


def test_soap_error_caught_by_transport_error():
    try:
        raise SoapError("test")
    except EtnicTransportError:
        pass
    else:
        pytest.fail("EtnicTransportError did not catch SoapError")


# ---------------------------------------------------------------------------
# Construction signatures
# ---------------------------------------------------------------------------


def test_transport_error_construction():
    err = EtnicTransportError("network down", soap_fault=ValueError("inner"), request_id="abc-123")
    assert err.message == "network down"
    assert isinstance(err.soap_fault, ValueError)
    assert err.request_id == "abc-123"
    assert str(err) == "network down"


def test_transport_error_minimal_construction():
    err = EtnicTransportError("oops")
    assert err.message == "oops"
    assert err.soap_fault is None
    assert err.request_id is None


def test_business_error_construction():
    err = EtnicBusinessError(
        "Doc 3 not accessible",
        code="20102",
        description="Documents 1 and 2 must be approved",
        request_id="abc-123",
    )
    assert err.code == "20102"
    assert err.description == "Documents 1 and 2 must be approved"
    assert err.request_id == "abc-123"


def test_business_error_minimal_construction():
    err = EtnicBusinessError("vague error")
    assert err.code is None
    assert err.description is None


def test_specialized_business_errors_inherit_constructor():
    """Subclasses of EtnicBusinessError accept the same kwargs."""
    err = EtnicDocumentNotAccessibleError(
        "Doc 3 not accessible",
        code="20102",
        description="Doc 1 and Doc 2 must be approved",
    )
    assert err.code == "20102"

    nf = EtnicNotFoundError("not found", code="00009")
    assert nf.code == "00009"

    val = EtnicValidationError("bad input", code="X")
    assert val.code == "X"
