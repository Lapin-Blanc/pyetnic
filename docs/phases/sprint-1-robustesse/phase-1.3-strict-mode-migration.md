# Phase 1.3 — Migrate EPROM services to typed exceptions (D3b)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D3**
- `docs/BACKWARDS_COMPAT.md` — especially the deprecation process and the rule on opt-in error behavior
- `docs/PUBLIC_API_SURFACE.md`
- `plan.md`
- `pyetnic/exceptions.py` (created in phase 1.2)
- `tests/regression/test_exceptions.py` (created in phase 1.2)

This is **the most delicate phase of Sprint 1**. It changes how every EPROM service signals errors. The rule that governs everything below:

> **The default behavior must remain unchanged.** Existing callers that today receive `None` on error must continue to receive `None` on error. The new exception-raising behavior is opt-in via a global Config flag or a context manager. NO existing test case asserting the old behavior should be modified — only NEW tests for the new behavior are added.

Read this rule again. Internalize it. If you find yourself updating an existing `assert result is None` to `with pytest.raises(...)`, **stop immediately** — that is a backwards-incompatible change and it's forbidden in this phase.

## Objective

1. Introduce `Config.RAISE_ON_ERROR` (a boolean attribute, defaulting to `False`)
2. Introduce a `strict_errors()` context manager
3. Implement both using `contextvars.ContextVar` for thread/async safety
4. Modify every EPROM service to consult this flag and raise typed exceptions when it's `True`
5. Add new regression tests for the strict-mode behavior, in addition to (not replacing) the existing tests for the default behavior

## Tasks

### 1. Implement `Config.RAISE_ON_ERROR` and `strict_errors()` context manager

Open `pyetnic/config.py`. Add a `ContextVar` at module level and integrate it into the existing metaclass:

```python
from contextvars import ContextVar

# Module-level: thread-safe and asyncio-safe storage for the raise-on-error flag
_raise_on_error: ContextVar[bool] = ContextVar("pyetnic_raise_on_error", default=False)
```

Add `"RAISE_ON_ERROR"` to `_ALL_CONFIG_ATTRS` and handle it specially in `_ConfigMeta.__getattr__` and `__setattr__`:

```python
_ALL_CONFIG_ATTRS = {*_SIMPLE_ENV_MAP, "USERNAME", "PASSWORD", "SERVICES", "RAISE_ON_ERROR"}


class _ConfigMeta(type):
    # ... existing code ...
    
    def __getattr__(cls, name: str) -> Any:
        if name not in _ALL_CONFIG_ATTRS:
            raise AttributeError(f"type object 'Config' has no attribute {name!r}")
        
        # Special handling: RAISE_ON_ERROR is stored in a ContextVar, not in _overrides
        if name == "RAISE_ON_ERROR":
            return _raise_on_error.get()
        
        # ... rest of existing logic ...
    
    def __setattr__(cls, name: str, value: Any) -> None:
        if name == "RAISE_ON_ERROR":
            _raise_on_error.set(bool(value))
            return
        if name in _ALL_CONFIG_ATTRS:
            _ConfigMeta._overrides[name] = value
        else:
            type.__setattr__(cls, name, value)
```

Note: `RAISE_ON_ERROR` is intentionally NOT stored in `_overrides`. It lives in a `ContextVar` so that:

- It's automatically per-thread (different threads have independent values)
- It's automatically per-asyncio-task (different tasks have independent values)
- It's reset cleanly by Config._reset() — see below

Update `Config._reset()` to also reset the ContextVar:

```python
@classmethod
def _reset(cls) -> None:
    """Reset all overrides and dotenv state. For testing only."""
    _ConfigMeta._overrides.clear()
    _ConfigMeta._dotenv_loaded = False
    _raise_on_error.set(False)
```

### 2. Implement `strict_errors()` context manager

Add to `pyetnic/__init__.py` (or a new `pyetnic/error_mode.py` if you prefer to keep `__init__.py` clean):

```python
from contextlib import contextmanager
from .config import Config


@contextmanager
def strict_errors():
    """Context manager that enables strict error mode for the enclosed block.
    
    Inside the `with` block, EPROM service calls raise typed exceptions
    (EtnicBusinessError, EtnicTransportError, etc.) instead of returning
    None or a result with success=False.
    
    On exit, the previous value of Config.RAISE_ON_ERROR is restored.
    
    The flag is stored in a ContextVar, so this is safe to use in
    multi-threaded and asyncio code: each thread/task sees its own value.
    
    Usage:
        from pyetnic import strict_errors
        from pyetnic.eprom import lire_organisation
        
        with strict_errors():
            org = lire_organisation(org_id)  # raises on failure
    
    Equivalent to:
        Config.RAISE_ON_ERROR = True
        try:
            org = lire_organisation(org_id)
        finally:
            Config.RAISE_ON_ERROR = False
    
    But thread-safe and exception-safe.
    """
    previous = Config.RAISE_ON_ERROR
    Config.RAISE_ON_ERROR = True
    try:
        yield
    finally:
        Config.RAISE_ON_ERROR = previous
```

Export `strict_errors` from `pyetnic/__init__.py` and `pyetnic/eprom/__init__.py`. Add to `__all__` in both.

### 3. Create the helper that decides what to do on error

Rather than putting `if Config.RAISE_ON_ERROR: raise ... else: return None` in every service method, create a helper. Add to `pyetnic/exceptions.py`:

```python
from .config import Config


def signal_business_error(
    message: str,
    code: Optional[str] = None,
    description: Optional[str] = None,
    request_id: Optional[str] = None,
    error_class: type = None,  # default: EtnicBusinessError
) -> None:
    """Raise a typed business error if strict mode is enabled, else return None.
    
    Service methods call this when they detect a server-side failure
    (success=False, no response, etc.). In default mode, it returns None
    silently (preserving legacy behavior). In strict mode, it raises.
    
    Args:
        message: Human-readable error message.
        code: ETNIC error code if known.
        description: ETNIC error description if known.
        request_id: Request ID for traceability.
        error_class: The specific subclass to raise. Defaults to EtnicBusinessError.
            Pass EtnicDocumentNotAccessibleError, EtnicNotFoundError, or
            EtnicValidationError for more precise typing when the code is known.
    
    Returns:
        None — but only when strict mode is OFF. When strict mode is ON,
        this function raises and never returns.
    """
    if not Config.RAISE_ON_ERROR:
        return None
    
    cls = error_class or EtnicBusinessError
    raise cls(message, code=code, description=description, request_id=request_id)


def map_etnic_error_code_to_class(code: Optional[str]) -> type:
    """Map a known ETNIC error code to its specialized exception class.
    
    Returns EtnicBusinessError for unknown codes.
    """
    if code is None:
        return EtnicBusinessError
    if code == "20102":
        return EtnicDocumentNotAccessibleError
    if code == "00009":
        return EtnicNotFoundError
    return EtnicBusinessError
```

### 4. Migrate the services — one at a time

For each EPROM service file, find every place where the current code does one of:

- `return None` after a failed parse / empty response check
- `return FormationsListeResult(False, [], messages=...)`

Replace it with a call to `signal_business_error(...)` that:

1. Returns `None` (the existing behavior) if strict mode is off
2. Raises an appropriate typed exception if strict mode is on

**Concrete migration pattern** for `pyetnic/services/organisation.py` `lire_organisation`:

Before:
```python
def lire_organisation(self, organisation_id: OrganisationId) -> Optional[Organisation]:
    logger.info(f"Lecture de l'organisation {organisation_id}")
    result = self.client_manager.call_service(
        "LireOrganisation",
        id=self._organisation_id_dict(organisation_id),
    )
    return self._parse_organisation_response(result, organisation_id)


def _parse_organisation_response(self, result, organisation_id=None):
    if (
        result
        and 'body' in result
        and result['body'].get('response')
        and 'organisation' in result['body']['response']
    ):
        # ... build Organisation ...
        return Organisation(...)
    return None
```

After:
```python
from ..exceptions import signal_business_error, map_etnic_error_code_to_class


def lire_organisation(self, organisation_id: OrganisationId) -> Optional[Organisation]:
    logger.info(f"Lecture de l'organisation {organisation_id}")
    result = self.client_manager.call_service(
        "LireOrganisation",
        id=self._organisation_id_dict(organisation_id),
    )
    return self._parse_organisation_response(result, organisation_id)


def _parse_organisation_response(self, result, organisation_id=None):
    if (
        result
        and 'body' in result
        and result['body'].get('response')
        and 'organisation' in result['body']['response']
    ):
        # ... build Organisation ...
        return Organisation(...)
    
    # Empty / failed response. Extract error info if available.
    code = None
    description = None
    if result and result.get('body'):
        messages = result['body'].get('messages') or {}
        errors = messages.get('error') if isinstance(messages, dict) else None
        if errors:
            err = errors[0] if isinstance(errors, list) else errors
            code = str(err.get('code')) if err.get('code') else None
            description = err.get('description')
    
    return signal_business_error(
        message=f"LireOrganisation returned no organisation (code={code}, desc={description})",
        code=code,
        description=description,
        error_class=map_etnic_error_code_to_class(code),
    )
```

Note that `signal_business_error` returns `None` in default mode, so the function still returns `None` to its caller — preserving the legacy behavior exactly. The function signature still says `Optional[Organisation]` because in default mode it can still return `None`.

### Per-file checklist

Apply the same pattern to:

**`pyetnic/services/organisation.py`**
- `_parse_organisation_response`: replace final `return None`
- `supprimer_organisation`: when `success` is False, signal business error instead of just returning False (NB: the return type is `bool`, not `Optional[Organisation]`, so think carefully — see "Special cases" below)

**`pyetnic/services/document1.py`**
- `_parse_document1_response`: replace final `return None`

**`pyetnic/services/document2.py`**
- `_parse_document2_response`: replace final `return None`

**`pyetnic/services/document3.py`**
- `_parse_document3_response`: replace final `return None`

**`pyetnic/services/formations_liste.py`**
- This one is special because it returns `FormationsListeResult(False, ...)` instead of `None`. See "Special cases" below.

### Special cases

**Special case 1: `FormationsListeService`**

Today, `lister_formations` and `lister_formations_organisables` return a `FormationsListeResult` with `success=False` on error, NOT `None`. The legacy contract is: callers check `result.success` or use `if not result:`.

In strict mode, we still need to raise. But in default mode, we still need to return `FormationsListeResult(False, ...)` for backwards compat.

```python
def lister_formations(self, ...):
    try:
        result = self.client_manager.call_service(...)
        if result['body']['success']:
            # parse and return FormationsListeResult(True, formations)
            ...
        else:
            messages = result['body'].get('messages', [])
            if Config.RAISE_ON_ERROR:
                raise EtnicBusinessError(
                    f"ListerFormations failed: {messages}",
                    description=str(messages),
                )
            return FormationsListeResult(False, [], messages=messages)
    except EtnicTransportError:
        if Config.RAISE_ON_ERROR:
            raise
        # Legacy behavior: wrap transport errors too
        return FormationsListeResult(False, [], messages=[...])
```

Note: the existing code in `formations_liste.py` has an `except Exception` that swallows everything. **DO NOT FIX that here** — that's phase 1.5. In this phase, only handle the `EtnicTransportError` / `SoapError` path correctly. Leave the `except Exception` in place but add a TODO comment for phase 1.5.

**Special case 2: `supprimer_organisation`**

Returns `bool`. In legacy mode, returns `False` on failure. In strict mode, should raise.

```python
def supprimer_organisation(self, organisation_id):
    logger.info(f"Suppression de l'organisation {organisation_id}")
    result = self.client_manager.call_service(
        "SupprimerOrganisation",
        id=self._organisation_id_dict(organisation_id),
    )
    success = bool(result and result.get('body', {}).get('success', False))
    if not success and Config.RAISE_ON_ERROR:
        # Extract error info as in _parse_organisation_response
        ...
        raise EtnicBusinessError(...)
    return success
```

**Special case 3: transport-level errors**

`SoapClientManager.call_service` already raises `SoapError` on transport failures. Now that `SoapError` inherits from `EtnicTransportError`, this works automatically — strict mode does nothing extra for transport errors, they always propagate. The opt-in is only for the "success=False but no exception" case.

This is correct: transport errors are catastrophic and have always been raised; we keep that behavior. Only the silent business errors need the opt-in.

### 5. Add new regression tests

Create `tests/regression/test_strict_mode.py`:

```python
"""Regression tests for strict error mode (raise-on-error)."""

from datetime import date
import pytest

from pyetnic import strict_errors, Config
from pyetnic.eprom import (
    lire_organisation,
    lire_document_1,
    lire_document_2,
    lire_document_3,
    OrganisationId,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
)


# ---------------------------------------------------------------------------
# Default mode: legacy behavior must be preserved
# ---------------------------------------------------------------------------
# These tests duplicate the existing ones in test_public_api_eprom.py but
# add an explicit assertion that Config.RAISE_ON_ERROR is False by default.
# Their failure indicates a backwards compatibility regression.

def test_default_mode_raise_on_error_is_false():
    """The default value of Config.RAISE_ON_ERROR must remain False."""
    Config._reset()
    assert Config.RAISE_ON_ERROR is False


def test_default_mode_lire_organisation_returns_none(mock_soap_call):
    """In default mode, an empty response still returns None (legacy behavior)."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    result = lire_organisation(org_id)
    assert result is None


# ---------------------------------------------------------------------------
# Strict mode via Config.RAISE_ON_ERROR
# ---------------------------------------------------------------------------

def test_strict_mode_via_config_flag(mock_soap_call):
    """Setting Config.RAISE_ON_ERROR = True makes lire_organisation raise."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    Config.RAISE_ON_ERROR = True
    try:
        with pytest.raises(EtnicBusinessError):
            lire_organisation(org_id)
    finally:
        Config.RAISE_ON_ERROR = False


# ---------------------------------------------------------------------------
# Strict mode via context manager
# ---------------------------------------------------------------------------

def test_strict_mode_via_context_manager(mock_soap_call):
    """strict_errors() makes lire_organisation raise inside the block."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    with strict_errors():
        with pytest.raises(EtnicBusinessError):
            lire_organisation(org_id)


def test_strict_mode_context_manager_restores_previous_value(mock_soap_call):
    """After exiting the context, the flag returns to its previous value."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    
    assert Config.RAISE_ON_ERROR is False
    with strict_errors():
        assert Config.RAISE_ON_ERROR is True
    assert Config.RAISE_ON_ERROR is False
    
    # And legacy behavior resumes outside the block
    result = lire_organisation(org_id)
    assert result is None


def test_strict_mode_context_manager_restores_on_exception(mock_soap_call):
    """The flag is restored even if an exception is raised inside."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    
    try:
        with strict_errors():
            lire_organisation(org_id)  # raises
    except EtnicBusinessError:
        pass
    
    assert Config.RAISE_ON_ERROR is False  # restored despite the exception


# ---------------------------------------------------------------------------
# Specialized exception classes
# ---------------------------------------------------------------------------

def test_strict_mode_raises_document_not_accessible_on_20102(mock_soap_call):
    """ETNIC error code 20102 maps to EtnicDocumentNotAccessibleError."""
    mock_soap_call.return_value = {
        'body': {
            'success': False,
            'response': None,
            'messages': {
                'error': {
                    'code': '20102',
                    'description': 'Doc 1 et Doc 2 doivent être approuvés',
                },
            },
        },
    }
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    with strict_errors():
        with pytest.raises(EtnicDocumentNotAccessibleError) as exc_info:
            lire_document_3(org_id)
        assert exc_info.value.code == "20102"
        # Also catchable as the parent class
        assert isinstance(exc_info.value, EtnicBusinessError)


def test_strict_mode_raises_not_found_on_00009(mock_soap_call):
    """ETNIC error code 00009 maps to EtnicNotFoundError."""
    mock_soap_call.return_value = {
        'body': {
            'success': False,
            'response': None,
            'messages': {
                'error': {
                    'code': '00009',
                    'description': 'Aucun enregistrement trouvé',
                },
            },
        },
    }
    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    with strict_errors():
        with pytest.raises(EtnicNotFoundError):
            lire_organisation(org_id)


# ---------------------------------------------------------------------------
# Thread/task isolation (ContextVar)
# ---------------------------------------------------------------------------

def test_context_var_is_isolated_across_threads():
    """Setting RAISE_ON_ERROR in one thread does not affect another."""
    import threading
    
    results = {}
    
    def thread_a():
        Config.RAISE_ON_ERROR = True
        results['a'] = Config.RAISE_ON_ERROR
    
    def thread_b():
        # Should see the default (False), not thread A's setting
        results['b'] = Config.RAISE_ON_ERROR
    
    t_a = threading.Thread(target=thread_a)
    t_b = threading.Thread(target=thread_b)
    t_a.start()
    t_a.join()
    t_b.start()
    t_b.join()
    
    assert results['a'] is True
    assert results['b'] is False
```

### 6. Run the full test suite

```bash
pytest tests/regression/ tests/unit/ -v
```

**Expected outcome**:

- All previous tests still pass (the legacy default-mode behavior is unchanged)
- The new tests in `test_strict_mode.py` pass
- The total test count increases by ~10-15

If any **existing** test fails, you have introduced a backwards-incompatible change. Find it and fix it before proceeding. Do NOT update the assertion of an existing test.

## Constraints

- **DEFAULT BEHAVIOR MUST BE UNCHANGED.** Re-read the rule at the top.
- **No existing regression test may be modified.** New tests are added; old tests are untouched.
- **SEPS services are out of scope.** Do not touch `pyetnic/services/seps.py` or any SEPS code.
- **`FormationsListeService` keeps its `except Exception`** for now — phase 1.5 will fix that.
- **`SoapError` continues to work** as a legacy alias.
- **No public API removal.** Only additions: `strict_errors`, `Config.RAISE_ON_ERROR`.

## Validation

- [ ] `Config.RAISE_ON_ERROR` accessible and defaults to `False`
- [ ] `strict_errors()` context manager works and restores previous value on exit (including on exception)
- [ ] All EPROM `_parse_*_response` methods migrated to `signal_business_error`
- [ ] `supprimer_organisation` raises in strict mode but returns `False` in default mode
- [ ] `lister_formations` and `lister_formations_organisables` raise in strict mode but return `FormationsListeResult(success=False)` in default mode
- [ ] `tests/regression/test_strict_mode.py` exists and all tests pass
- [ ] All existing regression tests still pass without modification
- [ ] Total test count increased, total green
- [ ] CI green on push
- [ ] Manual smoke test in REPL:
  ```python
  from pyetnic import strict_errors, Config, EtnicBusinessError
  from pyetnic.eprom import lire_organisation, OrganisationId
  
  # Default mode: legacy
  Config.ENV = "dev"  # plus your credentials
  org_id = OrganisationId(anneeScolaire="2024-2025", etabId=99999, numAdmFormation=99999, numOrganisation=99999)
  result = lire_organisation(org_id)
  print("Default:", result)  # None
  
  # Strict mode
  try:
      with strict_errors():
          lire_organisation(org_id)
  except EtnicBusinessError as e:
      print("Strict:", e)
  ```

## Next

Update `plan.md`: mark Phase 1.3 as complete. Commit message:

```
feat(sprint-1): phase 1.3 — opt-in strict error mode for EPROM (D3b)

- Add Config.RAISE_ON_ERROR (ContextVar-backed for thread/asyncio safety)
- Add strict_errors() context manager
- Add signal_business_error() helper used by all EPROM services
- Migrate all EPROM _parse_*_response methods to consult the flag
- Map ETNIC error codes 20102 → EtnicDocumentNotAccessibleError,
  00009 → EtnicNotFoundError; others → EtnicBusinessError
- Add ~10 regression tests for strict mode, all preserving legacy default

DEFAULT BEHAVIOR UNCHANGED. Existing callers see no difference.
New behavior is opt-in via Config.RAISE_ON_ERROR or strict_errors().

Closes audit defect D3 for EPROM. SEPS exception hierarchy unchanged.
```

Next phase: **Phase 1.4 — Remove AttributeError from call_service catch**. You can open a fresh Claude Code conversation for the hygiene phases (1.4, 1.5, 1.6) — they're small and unrelated.
