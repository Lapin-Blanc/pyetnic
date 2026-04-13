# Phase 0.3 — Regression tests

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` (for understanding what will change later)
- `docs/BACKWARDS_COMPAT.md`
- `docs/PUBLIC_API_SURFACE.md` (authoritative list of what to cover)
- `plan.md`

This is the **most important phase of Sprint 0**. The regression tests written here become the safety net for every subsequent refactoring phase. If they are incomplete, refactorings can silently break the stable API. If they are over-specified, they will produce false failures on harmless internal changes.

## Objective

Create a regression test suite that captures the current behavior of the stable API (as listed in `PUBLIC_API_SURFACE.md`). Tests are **mock-based** (no network), run in CI on every push, and serve as the automated enforcement of the backwards compatibility policy.

**Philosophy**: capture behavior, not implementation. A test should fail if and only if a caller would observe a change. Internal details (how a response is parsed, how the SOAP dict is structured) are NOT directly tested — what's tested is what the caller receives.

## Tasks

### 1. Create `tests/regression/conftest.py`

This file provides shared fixtures for all regression tests. Key fixtures:

```python
"""Shared fixtures for regression tests. Mock-based, no network."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_soap_call():
    """Patches SoapClientManager.call_service globally for the test duration.

    Yields a MagicMock. Tests configure its return_value to the dict they want
    the SOAP layer to produce, then call the public pyetnic function, and
    assert on the returned dataclass.

    Usage:
        def test_lire_organisation(mock_soap_call):
            mock_soap_call.return_value = {
                'body': {
                    'success': True,
                    'response': {'organisation': {...}},
                },
            }
            org = pyetnic.eprom.lire_organisation(organisation_id)
            assert isinstance(org, Organisation)
            assert org.dateDebutOrganisation == date(2024, 9, 2)
    """
    with patch(
        "pyetnic.soap_client.SoapClientManager.call_service",
        new_callable=MagicMock,
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def isolate_config():
    """Ensures each regression test starts with a clean Config state.

    Resets any programmatic overrides and reloads .env state.
    Prevents test order dependencies.
    """
    from pyetnic.config import Config
    Config._reset()
    # Set minimal valid config so services can instantiate
    Config.ENV = "dev"
    Config.USERNAME = "test_user"
    Config.PASSWORD = "test_pass"
    yield
    Config._reset()
```

### 2. Create `tests/regression/test_public_api_eprom.py`

For each stable EPROM function listed in `PUBLIC_API_SURFACE.md`, write tests that verify:

**A. Signature** — parameters, defaults, types via `inspect`:

```python
import inspect
import pyetnic.eprom


def test_lire_organisation_signature():
    sig = inspect.signature(pyetnic.eprom.lire_organisation)
    params = sig.parameters
    assert "organisation_id" in params
    # Add assertions for parameter kinds and defaults
```

**B. Happy-path return type** — given a canonical SOAP response, the function returns the expected dataclass with the expected field types:

```python
from datetime import date
from pyetnic.eprom import lire_organisation, Organisation, OrganisationId


CANONICAL_ORGANISATION_RESPONSE = {
    'body': {
        'success': True,
        'response': {
            'organisation': {
                'id': {
                    'anneeScolaire': '2024-2025',
                    'etabId': 3052,
                    'numAdmFormation': 455,
                    'numOrganisation': 1,
                    'implId': 6050,
                },
                'dateDebutOrganisation': date(2024, 9, 2),
                'dateFinOrganisation': date(2025, 6, 27),
                'nombreSemaineFormation': 36,
                'statut': None,
                # ... include all fields the parser reads
            }
        }
    }
}


def test_lire_organisation_returns_organisation(mock_soap_call):
    mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
    org_id = OrganisationId(
        anneeScolaire="2024-2025",
        etabId=3052,
        numAdmFormation=455,
        numOrganisation=1,
    )
    result = lire_organisation(org_id)
    assert isinstance(result, Organisation)
    assert result.dateDebutOrganisation == date(2024, 9, 2)
    assert result.dateFinOrganisation == date(2025, 6, 27)
```

**C. Error path — current behavior captured, not aspired behavior**:

The audit (D3) notes that error handling is inconsistent. For the regression tests, capture the **current** behavior exactly as it is, even if we plan to change it later. The point of regression tests is to detect unintended changes, not to enforce the future ideal.

```python
def test_lire_organisation_returns_none_on_empty_response(mock_soap_call):
    """Current behavior: server returns success=True but no organisation → returns None."""
    mock_soap_call.return_value = {'body': {'success': True, 'response': None}}
    org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1)
    result = lire_organisation(org_id)
    assert result is None  # <-- current behavior, to be changed in Sprint 1


def test_lire_organisation_raises_soap_error_on_network_failure(mock_soap_call):
    """Current behavior: network failures propagate as SoapError."""
    from pyetnic.soap_client import SoapError
    mock_soap_call.side_effect = SoapError("network down")
    org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1)
    import pytest
    with pytest.raises(SoapError):
        lire_organisation(org_id)
```

**D. Request payload shape** — when the function calls the SOAP layer, what dict does it produce? This is critical for detecting regressions in Sprint 2 when we change how dicts are built.

```python
def test_lire_organisation_sends_correct_request(mock_soap_call):
    mock_soap_call.return_value = CANONICAL_ORGANISATION_RESPONSE
    org_id = OrganisationId(
        anneeScolaire="2024-2025",
        etabId=3052,
        numAdmFormation=455,
        numOrganisation=1,
        implId=6050,  # explicitly present
    )
    lire_organisation(org_id)

    # Verify the SOAP layer was called with the expected method and args
    assert mock_soap_call.call_count == 1
    call = mock_soap_call.call_args
    assert call.args[0] == "LireOrganisation"
    # CRITICAL: implId must NOT be in the request (ETNIC rule)
    assert "implId" not in call.kwargs["id"]
    assert call.kwargs["id"] == {
        'anneeScolaire': '2024-2025',
        'etabId': 3052,
        'numAdmFormation': 455,
        'numOrganisation': 1,
    }
```

### Coverage checklist for EPROM

Write tests covering, at minimum:

**FormationsListeService**:
- `lister_formations` — happy path, empty list, success=False
- `lister_formations_organisables` — happy path, empty list

**OrganisationService**:
- `lire_organisation` — happy path, None response, request shape (implId exclusion!)
- `creer_organisation` — happy path, request shape (implId INCLUDED here!), all optional params
- `modifier_organisation` — happy path, request shape (implId exclusion!)
- `supprimer_organisation` — success=True, success=False

**Document1Service**:
- `lire_document_1` — happy path with population lines, None response
- `modifier_document_1` — with population_liste, without population_liste (both should work)
- `approuver_document_1` — with and without population_liste

**Document2Service**:
- `lire_document_2` — happy path with activites and interventions
- `modifier_document_2` — with activite only, with intervention only, with both, with neither

**Document3Service**:
- `lire_document_3` — happy path with activites containing enseignants
- `modifier_document_3` — happy path

### 3. Create `tests/regression/test_public_api_seps_read.py`

Cover SEPS **read** operations only (see `PUBLIC_API_SURFACE.md`):

- `lire_etudiant` — happy path returning Etudiant, None response
- `rechercher_etudiants` by NISS — happy path, NissMutationError (code 30401), TropDeResultatsError (code 30501), SepsAuthError (code 30550)
- `rechercher_etudiants` by nom/prenom — happy path, empty result
- `rechercher_etudiants` without niss or nom — raises ValueError (current behavior)

For exceptions, the test should verify:

```python
def test_rechercher_etudiants_raises_niss_mutation_on_30401(mock_soap_call):
    mock_soap_call.return_value = {
        'body': {
            'success': False,
            'messages': {
                'error': {
                    'code': '30401',
                    'description': 'NISS remplacé par 12345678901',
                },
            },
        },
    }
    with pytest.raises(NissMutationError) as exc_info:
        rechercher_etudiants(niss="old_niss_value")
    assert exc_info.value.ancien_niss == "old_niss_value"
    assert exc_info.value.nouveau_niss == "12345678901"
```

### 4. Capture canonical SOAP responses

To avoid hardcoding SOAP response dicts inline in tests, create a fixtures file:

```
tests/regression/
├── conftest.py
├── fixtures/
│   ├── __init__.py
│   ├── eprom_responses.py          # canonical SOAP responses as Python dicts
│   └── seps_responses.py
├── test_public_api_eprom.py
└── test_public_api_seps_read.py
```

Each fixture file defines module-level constants like `CANONICAL_ORGANISATION_RESPONSE`, `CANONICAL_FORMATIONS_LIST_RESPONSE`, etc. These are the "golden" dict shapes the tests use.

**How to build these canonical responses**: read the existing tests in `tests/test_formation_*.py` — they contain `_mock_*_response()` helpers that show what zeep actually returns. Use those as the starting point, enriched with all the fields the parsers actually read from.

### 5. Migrate existing tests to `tests/unit/` and `tests/integration/`

The current `tests/test_formation_*.py` and `tests/test_formations_liste.py` contain a mix of:

- Mock-based unit tests (keep in `tests/unit/`)
- Integration tests that call the dev ETNIC service (move to `tests/integration/eprom/`)

For each existing test file:

1. Read the file.
2. Identify which tests use `pytest.skip()` conditional on `Config.ETAB_ID` or similar — these are integration tests.
3. Identify which tests use inline `_mock_*_response` helpers — these are unit tests.
4. Split the file:
   - Unit tests → `tests/unit/test_xxx_unit.py`
   - Integration tests → `tests/integration/eprom/test_xxx_integration.py`
5. Use `git mv` followed by edits to preserve history as much as possible.

If a single test mixes both (unusual), prefer moving to integration and keeping a mock-only subset in unit.

After migration, `tests/` at the repo root should contain ONLY:

```
tests/
├── __init__.py
├── conftest.py                      (if any root-level fixtures remain)
├── regression/
│   └── ...
├── unit/
│   └── test_*.py
└── integration/
    ├── eprom/
    │   └── test_*.py
    └── seps_readonly/               (empty for now, add in a future phase if needed)
```

No `test_*.py` file directly under `tests/`.

### 6. Verify

Run in this order:

```bash
# Regression tests run without any network, any credentials
pytest tests/regression/ -v

# Unit tests run without network
pytest tests/unit/ -v

# Integration tests: only if .env is configured (they skip otherwise)
pytest tests/integration/ -v
```

All three should pass. The regression tests are the mandatory gate — if they fail, the phase is not complete. Integration tests are best-effort.

## Constraints

- **No network calls** in regression or unit tests. `mock_soap_call` fixture is mandatory.
- **Do not modify any code under `pyetnic/`** — this phase only adds tests.
- **Capture current behavior faithfully**, not aspired behavior. If `lire_organisation` returns `None` on error today, the regression test asserts `None`. The Sprint 1 phase that introduces exceptions will update the test accordingly.
- **Canonical responses should be realistic** — based on actual zeep output format, not imagined. Use existing `_mock_*_response` helpers in current tests as reference.
- **Coverage goal**: every stable symbol in `PUBLIC_API_SURFACE.md` has at least one test exercising its happy path AND one test exercising its error/edge case.

## Validation

Before completing, verify:

- [ ] `pytest tests/regression/ -v` passes with at least 30 tests collected (roughly 2 tests × 15 stable EPROM functions + ~10 SEPS read tests)
- [ ] `pytest tests/unit/ -v` passes (migrated unit tests)
- [ ] `pytest tests/integration/ -v` passes or skips cleanly (no crashes)
- [ ] No `test_*.py` file sits directly under `tests/` — all are under `regression/`, `unit/`, or `integration/`
- [ ] Every function listed as stable in `PUBLIC_API_SURFACE.md` is referenced by at least one test function in `tests/regression/`
- [ ] Git history is preserved for moved files (`git log --follow` on a moved test file shows pre-migration commits)

## Next

Update `plan.md`: mark Phase 0.3 as complete. Commit with message:

```
refactor(sprint-0): phase 0.3 — regression test suite

- Add tests/regression/ with mock-based coverage of stable API
- Add tests/regression/fixtures/ with canonical SOAP response dicts
- Migrate existing tests to tests/unit/ and tests/integration/eprom/
- Coverage: EPROM happy path, error path, request shape (implId rule enforced)
- Coverage: SEPS read happy path, typed exceptions, input validation

This is the safety net for Sprints 1-4 refactoring.
```

Next phase: **Phase 0.4 — CI setup**.
