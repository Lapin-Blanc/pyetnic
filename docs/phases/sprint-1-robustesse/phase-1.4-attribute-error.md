# Phase 1.4 — Remove AttributeError from call_service catch (Q1)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **Q1**
- `plan.md`

Small, surgical fix. Phases 1.4, 1.5, and 1.6 are hygiene-level changes that can all be done in one Claude Code session.

## Objective

Remove `AttributeError` from the `except` clause in `SoapClientManager.call_service`. This exception type was masking real bugs (typos in method names, missing kwargs) by wrapping them as `SoapError` instead of letting them propagate as the developer errors they are.

## Tasks

### 1. Locate the catch

In `pyetnic/soap_client.py`, find the `call_service` method. Current code:

```python
except (Fault, TransportError, RequestException, AttributeError) as e:
    error_msg = f"Erreur lors de l'appel à {method_name} sur {self.service_name}: {str(e)}"
    logger.error(f"{error_msg} (request_id: {request_id})")
    raise SoapError(error_msg, soap_fault=e, request_id=request_id)
```

### 2. Remove `AttributeError`

```python
except (Fault, TransportError, RequestException) as e:
    error_msg = f"Erreur lors de l'appel à {method_name} sur {self.service_name}: {str(e)}"
    logger.error(f"{error_msg} (request_id: {request_id})")
    raise SoapError(error_msg, soap_fault=e, request_id=request_id)
```

That's it. No other change.

### 3. Add a regression test

Create or extend `tests/regression/test_call_service_errors.py`:

```python
"""Regression tests for SoapClientManager.call_service error handling."""

import pytest
from unittest.mock import patch, MagicMock

from pyetnic.config import Config
from pyetnic.soap_client import SoapClientManager, SoapError


def test_attribute_error_is_not_swallowed_as_soap_error():
    """AttributeError must propagate, not be wrapped in SoapError.
    
    Before phase 1.4, call_service caught AttributeError and wrapped it
    in SoapError. This masked real bugs like typos in method names. Now,
    AttributeError propagates as-is so the developer sees the actual error.
    """
    Config.ENV = "dev"
    Config.USERNAME = "test"
    Config.PASSWORD = "test"
    
    mgr = SoapClientManager("ORGANISATION")
    
    # Create a fake service object that raises AttributeError when accessed
    fake_service = MagicMock()
    fake_method = MagicMock()
    fake_method.side_effect = AttributeError("simulated attribute error")
    fake_service.SomeMethod = fake_method
    
    with patch.object(mgr, '_initialize_client', return_value=fake_service):
        with pytest.raises(AttributeError, match="simulated attribute error"):
            mgr.call_service("SomeMethod")


def test_fault_is_still_wrapped_as_soap_error():
    """zeep Fault is still caught and wrapped (regression baseline)."""
    from zeep.exceptions import Fault
    
    Config.ENV = "dev"
    Config.USERNAME = "test"
    Config.PASSWORD = "test"
    
    mgr = SoapClientManager("ORGANISATION")
    
    fake_service = MagicMock()
    fake_method = MagicMock()
    fake_method.side_effect = Fault("simulated SOAP fault")
    fake_service.SomeMethod = fake_method
    
    with patch.object(mgr, '_initialize_client', return_value=fake_service):
        with pytest.raises(SoapError):
            mgr.call_service("SomeMethod")
```

### 4. Run tests

```bash
pytest tests/regression/ tests/unit/ -v
```

All green expected. The new tests verify the new behavior; no existing test should break (since no existing test was relying on `AttributeError` being wrapped).

## Constraints

- **Surgical change only.** Do not refactor the method, do not change the other exception types caught, do not modify error messages.
- **No SEPS changes.**

## Validation

- [ ] `pyetnic/soap_client.py`: `AttributeError` removed from the except tuple in `call_service`
- [ ] `tests/regression/test_call_service_errors.py` exists with 2 tests, both passing
- [ ] All existing tests still green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 1.4 as complete. Commit message:

```
fix(sprint-1): phase 1.4 — let AttributeError propagate (Q1)

call_service no longer catches AttributeError, which was masking real
developer bugs (typos, missing kwargs) as SoapError. AttributeError
now propagates so the actual error surfaces.

Closes audit defect Q1.
```

Next phase: **Phase 1.5 — Remove except Exception from formations_liste**.
