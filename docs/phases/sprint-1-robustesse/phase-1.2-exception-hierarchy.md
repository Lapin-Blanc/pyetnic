# Phase 1.2 — Create EPROM exception hierarchy (D3a)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D3**
- `docs/BACKWARDS_COMPAT.md`
- `plan.md`

This is phase 1.2 of **Sprint 1 — Robustness**. It addresses the first half of defect **D3**: the EPROM services have no typed exception hierarchy. Errors are signaled inconsistently (sometimes by returning `None`, sometimes by wrapping in `FormationsListeResult(success=False)`, sometimes by raising `SoapError`).

This phase creates the new exception types **without yet using them in the services**. The actual migration to raising these exceptions happens in phase 1.3, behind an opt-in mechanism.

This separation is intentional: by creating the types first and testing them in isolation, we make phase 1.3 a pure migration with zero design decisions left to make.

## Objective

Define a clean, typed exception hierarchy for EPROM errors. Make `SoapError` (the existing exception) a backwards-compatible alias inside the new hierarchy, so that no existing `except SoapError` code breaks.

## Tasks

### 1. Create the new exceptions module

Create `pyetnic/exceptions.py` (new file at the top level of the package, not under `services/`):

```python
"""Exception hierarchy for pyetnic.

This module defines the typed exceptions raised by EPROM services when
strict error mode is enabled (see Config.RAISE_ON_ERROR or strict_errors()).

The hierarchy is designed so that:
- A generic `except EtnicError` catches everything pyetnic can raise.
- A more specific `except EtnicBusinessError` catches only server-side
  refusals (success=False), letting transport errors propagate.
- The legacy `SoapError` is an alias for `EtnicTransportError`, so existing
  `except SoapError` code keeps working.

SEPS exceptions (SepsEtnicError and subclasses) live in pyetnic.services.seps
and are intentionally separate. They will be unified with this hierarchy in
a future major version.
"""

from typing import Optional


class EtnicError(Exception):
    """Base class for all pyetnic exceptions.
    
    Catch this if you want to handle any error from pyetnic.
    """


class EtnicTransportError(EtnicError):
    """Network-level or SOAP-protocol-level error.
    
    Raised when the SOAP request itself fails: connection refused, timeout,
    invalid SOAP envelope, malformed WSDL, etc. This is NOT raised when the
    server processes the request and returns success=False — see
    EtnicBusinessError for that case.
    
    Attributes:
        message: Human-readable error description.
        soap_fault: The original zeep/requests exception, if any.
        request_id: The pyetnic-generated request ID for this call (useful
            when reporting bugs to ETNIC support).
    """
    
    def __init__(
        self,
        message: str,
        soap_fault: Optional[Exception] = None,
        request_id: Optional[str] = None,
    ):
        self.message = message
        self.soap_fault = soap_fault
        self.request_id = request_id
        super().__init__(message)


class EtnicBusinessError(EtnicError):
    """Server-side refusal of a valid request.
    
    Raised when ETNIC processes the request but returns success=False.
    Examples: workflow violations (Doc1 not approved yet), invalid input
    values, business rule violations, document not accessible.
    
    The `code` and `description` attributes carry the ETNIC error details
    when available.
    
    Attributes:
        code: ETNIC error code (e.g. "20102", "00009"). May be None if
            the response had no structured error.
        description: ETNIC's human-readable error description.
        request_id: The pyetnic-generated request ID for this call.
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.code = code
        self.description = description
        self.request_id = request_id
        super().__init__(message)


class EtnicDocumentNotAccessibleError(EtnicBusinessError):
    """A document is not yet accessible in the workflow.
    
    Raised when accessing Doc 1 / Doc 2 / Doc 3 before the prerequisite
    documents have been approved. Most notably, ETNIC error code 20102
    ("Doc 1 and Doc 2 must be approved before Doc 3 is accessible").
    
    This is a NORMAL workflow state, not a hard error — calling code may
    legitimately catch this exception to mean "not ready yet".
    """


class EtnicNotFoundError(EtnicBusinessError):
    """The requested resource does not exist.
    
    Raised when ETNIC reports that no record matches the query. ETNIC
    error code 00009 typically maps to this.
    """


class EtnicValidationError(EtnicBusinessError):
    """The request was rejected as malformed or invalid.
    
    Raised when ETNIC refuses the request for input-validation reasons:
    missing required fields, invalid format, value out of range, etc.
    """
```

### 2. Make the existing SoapError compatible

Open `pyetnic/soap_client.py`. Find the existing `SoapError` class and modify it to inherit from `EtnicTransportError`:

```python
from .exceptions import EtnicTransportError


class SoapError(EtnicTransportError):
    """Deprecated alias for EtnicTransportError.
    
    Kept for backwards compatibility with code that does `except SoapError`.
    New code should use EtnicTransportError directly.
    
    Will be removed in version 1.0.0.
    """
```

The constructor signature of `EtnicTransportError` is the same as the old `SoapError` (`message`, `soap_fault`, `request_id`), so all existing code that constructs or raises `SoapError` continues to work without changes.

**Important**: do NOT delete the `SoapError` symbol. Existing user code (including your own scripts in `examples/`) may catch it.

### 3. Re-export from the package root

Open `pyetnic/__init__.py` and add the new exceptions to the public exports:

```python
from .exceptions import (
    EtnicError,
    EtnicTransportError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
)
from .soap_client import SoapError  # legacy alias

__all__ = [
    # ... existing entries ...
    "EtnicError",
    "EtnicTransportError",
    "EtnicBusinessError",
    "EtnicDocumentNotAccessibleError",
    "EtnicNotFoundError",
    "EtnicValidationError",
    "SoapError",  # deprecated, kept for compat
]
```

Also re-export from `pyetnic/eprom/__init__.py`:

```python
from ..exceptions import (
    EtnicError,
    EtnicTransportError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
)
from ..soap_client import SoapError  # legacy alias

__all__ = [
    # ... existing entries ...
    "EtnicError",
    "EtnicTransportError",
    "EtnicBusinessError",
    "EtnicDocumentNotAccessibleError",
    "EtnicNotFoundError",
    "EtnicValidationError",
    "SoapError",
]
```

Do NOT export them from `pyetnic.seps` — SEPS keeps its own hierarchy (`SepsEtnicError` etc.) for now.

### 4. Update PUBLIC_API_SURFACE.md

Add the new exceptions to the stable API list under a new "Exceptions" section in the EPROM namespace:

```markdown
### Stable — Exceptions

| Symbol | Notes |
|---|---|
| `EtnicError` | Base class, catch to handle any pyetnic error |
| `EtnicTransportError` | Network/SOAP-level failures |
| `EtnicBusinessError` | Server-side refusals (success=False) |
| `EtnicDocumentNotAccessibleError` | Doc1/Doc2/Doc3 workflow violation (e.g. error 20102) |
| `EtnicNotFoundError` | Resource not found (e.g. error 00009) |
| `EtnicValidationError` | Input rejected by validation |
| `SoapError` | **Deprecated** alias for EtnicTransportError. Will be removed in 1.0.0 |
```

### 5. Write regression tests for the exception types

Create `tests/regression/test_exceptions.py`:

```python
"""Regression tests for the EPROM exception hierarchy.

These tests verify the type hierarchy and the construction signatures.
They do NOT test that any service actually raises these — that's phase 1.3.
"""

import pytest

from pyetnic import (
    EtnicError,
    EtnicTransportError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
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
        pass  # success
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
```

### 6. Verify nothing else broke

Run the full suite:

```bash
pytest tests/regression/ tests/unit/ -v
```

The new exception tests should pass. All existing tests should continue to pass — this phase only adds new types, it doesn't change any existing behavior.

## Constraints

- **Do not modify any service** (`pyetnic/services/*.py`) in this phase. The new exceptions are defined but not yet raised by anyone. That's phase 1.3.
- **Do not modify SEPS exceptions** (`SepsEtnicError` and friends remain as they are).
- **Preserve `SoapError` as a working symbol** — code that imports or catches it must continue to work.
- **Don't delete the old `SoapError` class definition**, just change its parent.

## Validation

- [ ] `pyetnic/exceptions.py` exists with the 6 new classes
- [ ] `pyetnic/soap_client.py` `SoapError` now inherits from `EtnicTransportError`
- [ ] `pyetnic/__init__.py` and `pyetnic/eprom/__init__.py` export the new exceptions
- [ ] `tests/regression/test_exceptions.py` exists and all tests pass
- [ ] `pytest tests/regression/ tests/unit/ -v` is green with the new tests added
- [ ] `PUBLIC_API_SURFACE.md` updated with the new symbols
- [ ] CI green on push
- [ ] Quick smoke test:
  ```python
  from pyetnic import EtnicError, SoapError
  try:
      raise SoapError("test")
  except EtnicError as e:
      print("caught as EtnicError:", e)  # should print
  ```

## Next

Update `plan.md`: mark Phase 1.2 as complete. Commit message:

```
feat(sprint-1): phase 1.2 — EPROM exception hierarchy (D3a)

- Add pyetnic/exceptions.py with EtnicError, EtnicTransportError,
  EtnicBusinessError, and three specialized subclasses
- Make SoapError inherit from EtnicTransportError (backwards compat)
- Re-export new exceptions from pyetnic/__init__.py and pyetnic.eprom
- Add 14 regression tests for hierarchy and construction signatures
- Update PUBLIC_API_SURFACE.md

Services do not yet raise these exceptions — that's phase 1.3.

Partial fix for audit defect D3.
```

Next phase: **Phase 1.3 — Migration to typed exceptions with opt-in**. This is the most delicate phase of Sprint 1 — open a fresh Claude Code conversation for it (recommended).
