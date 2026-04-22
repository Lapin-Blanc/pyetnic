# Phase 1.5 — Remove except Exception from formations_liste (Q2)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **Q2**
- `plan.md`

Hygiene phase, paired with 1.4 and 1.6 in the same conversation.

## Objective

Remove the broad `except Exception` clauses in `pyetnic/services/formations_liste.py` that swallow all exceptions and wrap them in `FormationsListeResult(False, ...)`. These swallowed exceptions hide real bugs (KeyError on unexpected response shape, ValueError on parsing, etc.) by converting them into "result.success=False" with no traceback.

After this phase, only `EtnicTransportError` (and its alias `SoapError`) will be caught and wrapped — anything else propagates with full traceback.

## Tasks

### 1. Locate the offending catches

In `pyetnic/services/formations_liste.py`, both `lister_formations_organisables` and `lister_formations` have a structure like:

```python
try:
    request_data = {...}
    result = self.client_manager.call_service(...)
    if result['body']['success']:
        # parse and build formations
        return FormationsListeResult(True, formations)
    else:
        return FormationsListeResult(False, [], messages=result['body'].get('messages', []))

except SoapError as e:
    return FormationsListeResult(False, [], messages=[str(e)])
except Exception as e:
    return FormationsListeResult(False, [], messages=[f"Une erreur inattendue s'est produite : {str(e)}"])
```

### 2. Remove the broad catch

For both functions, remove the `except Exception` clause entirely:

```python
try:
    request_data = {...}
    result = self.client_manager.call_service(...)
    if result['body']['success']:
        # parse and build formations
        return FormationsListeResult(True, formations)
    else:
        messages = result['body'].get('messages', [])
        if Config.RAISE_ON_ERROR:
            raise EtnicBusinessError(
                f"ListerFormations failed: {messages}",
                description=str(messages),
            )
        return FormationsListeResult(False, [], messages=messages)

except SoapError as e:
    if Config.RAISE_ON_ERROR:
        raise
    return FormationsListeResult(False, [], messages=[str(e)])
```

Note: phase 1.3 was supposed to add the `Config.RAISE_ON_ERROR` check to these functions but explicitly left the `except Exception` in place. Now we remove the broad catch AND complete the strict-mode integration in one pass. Make sure both functions are consistent.

### 3. Add a regression test for unexpected exceptions

Create or extend `tests/regression/test_unexpected_errors.py`:

```python
"""Regression tests verifying that unexpected exceptions propagate."""

from unittest.mock import patch
import pytest

from pyetnic.eprom import lister_formations, lister_formations_organisables


def test_lister_formations_propagates_keyerror_from_parser(mock_soap_call):
    """If the SOAP response shape is unexpected (parser KeyError), the
    KeyError must propagate, not be silently wrapped in a result.
    
    Before phase 1.5, formations_liste had `except Exception` that
    swallowed parser bugs as result.success=False. Now KeyError
    surfaces with full traceback.
    """
    # Return a response that's missing the 'success' key
    mock_soap_call.return_value = {'body': {}}
    
    with pytest.raises(KeyError):
        lister_formations(annee_scolaire="2024-2025")


def test_lister_formations_organisables_propagates_keyerror(mock_soap_call):
    mock_soap_call.return_value = {'body': {}}
    
    with pytest.raises(KeyError):
        lister_formations_organisables(annee_scolaire="2024-2025")
```

### 4. Verify existing tests still pass

The existing regression tests in `test_public_api_eprom.py` use canonical, well-formed responses, so they should not trigger any KeyError. They should remain green.

```bash
pytest tests/regression/ tests/unit/ -v
```

If a test fails, investigate. The most likely cause is that one of the canonical fixtures was relying on the broad catch to mask a missing field — in which case, fix the fixture, not the catch.

## Constraints

- **Do NOT add a new broad catch elsewhere.** The point is to surface unexpected errors.
- **Do NOT modify the canonical fixture responses** to "make them safe". If a canonical fixture relies on a broad catch, the fixture is wrong.
- **No SEPS changes.**

## Validation

- [ ] Both `lister_formations` and `lister_formations_organisables` no longer have `except Exception`
- [ ] Both functions correctly handle `Config.RAISE_ON_ERROR` (delayed from phase 1.3 to be done atomically here)
- [ ] `tests/regression/test_unexpected_errors.py` exists with 2 passing tests
- [ ] All existing tests still green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 1.5 as complete. Commit message:

```
fix(sprint-1): phase 1.5 — let unexpected errors propagate from formations_liste (Q2)

- Remove `except Exception` from lister_formations and
  lister_formations_organisables. Parser bugs and other unexpected
  errors now surface with full traceback.
- Complete Config.RAISE_ON_ERROR integration in formations_liste
  (deferred from phase 1.3 to be done atomically here).
- Add 2 regression tests verifying KeyError propagation.

Closes audit defect Q2.
```

Next phase: **Phase 1.6 — De-hardcode CLI and update README**.
