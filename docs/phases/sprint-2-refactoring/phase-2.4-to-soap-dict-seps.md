# Phase 2.4 — Migrate to_soap_dict in SEPS write services (D2)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D2**
- `docs/PUBLIC_API_SURFACE.md` — SEPS write functions are classified **construction**
- `plan.md`

This phase migrates `asdict()` → `to_soap_dict()` in the SEPS write services. These are **construction API** — there are no backwards compatibility constraints and no regression tests to protect. You have complete freedom to refactor.

## Objective

Replace `dataclasses.asdict()` with `to_soap_dict()` in `enregistrer_etudiant.py` and `inscriptions.py`.

## Tasks

### 1. Identify call sites

```bash
grep -rn "asdict" pyetnic/services/enregistrer_etudiant.py pyetnic/services/inscriptions.py
```

Expected:
- `enregistrer_etudiant.py`: `dataclasses.asdict(etudiant_details)` in `enregistrer_etudiant` and `modifier_etudiant`
- `inscriptions.py`: `dataclasses.asdict(...)` in `enregistrer_inscription` and `modifier_inscription`

### 2. Migrate

Same pattern as phase 2.3:

1. Replace `import dataclasses` / `from dataclasses import asdict` with `from ._helpers import to_soap_dict`
2. Replace `dataclasses.asdict(obj)` or `asdict(obj)` with `to_soap_dict(obj)`

### 3. Add basic unit tests

Since these functions have no regression tests (construction API), add simple unit tests in `tests/unit/test_seps_write_unit.py` that verify the payload shape:

```python
"""Unit tests for SEPS write services — construction API.

These are basic sanity checks, not regression-level guards.
The SEPS write API is classified 'construction' and may change freely.
"""

from unittest.mock import MagicMock, patch
import pytest

from pyetnic.config import Config
from pyetnic.services.enregistrer_etudiant import EnregistrerEtudiantService
from pyetnic.services.models import EtudiantDetailsSave, SepsNaissanceSave


@pytest.fixture(autouse=True)
def isolate():
    Config._reset()
    Config.ENV = "dev"
    Config.USERNAME = "test"
    Config.PASSWORD = "test"
    yield
    Config._reset()


def test_enregistrer_etudiant_payload_excludes_none(monkeypatch):
    """Verify None fields stripped from the SOAP payload."""
    service = EnregistrerEtudiantService()
    
    captured = {}
    def fake_call(method_name, **kwargs):
        captured.update(kwargs)
        return {'body': {'success': True, 'response': {'etudiant': {'cfNum': '123-01'}}}}
    
    monkeypatch.setattr(service.client_manager, 'call_service', fake_call)
    
    details = EtudiantDetailsSave(
        niss="12345678901",
        nom="DUPONT",
        prenom="Jean",
        # All other fields left as None
    )
    service.enregistrer_etudiant(
        mode_enregistrement="DETAILS",
        etudiant_details=details,
    )
    
    payload = captured.get('etudiantDetails', {})
    assert payload['niss'] == '12345678901'
    assert payload['nom'] == 'DUPONT'
    # None fields should be absent
    assert 'sexe' not in payload
    assert 'deces' not in payload
    assert 'adresse' not in payload
```

### 4. Opportunity for light cleanup (optional)

Since SEPS write is construction API, you may also fix minor issues you notice while migrating — inconsistent naming, missing docstrings, etc. But don't go beyond what's natural while you're in the file. The main objective is the `asdict` → `to_soap_dict` migration.

### 5. Verify

```bash
pytest tests/regression/ tests/unit/ -v
```

Regression tests should be unaffected (they don't cover SEPS write). The new unit test should pass.

## Constraints

- **Free to refactor** — construction API, no backwards compat.
- **Do NOT touch SEPS read services** (`seps.py` / `RechercheEtudiantsService`) — those are stable.
- Keep changes focused on `asdict` migration. Larger refactoring of SEPS write can happen in a future sprint.

## Validation

- [ ] `grep -rn "asdict" pyetnic/services/enregistrer_etudiant.py pyetnic/services/inscriptions.py` returns zero
- [ ] `tests/unit/test_seps_write_unit.py` exists with at least 1 passing test
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.4 as complete. Commit message:

```
refactor(sprint-2): phase 2.4 — replace asdict() in SEPS write services (D2)

- Migrate enregistrer_etudiant.py and inscriptions.py from asdict()
  to to_soap_dict(exclude_none=True)
- Add unit test verifying None-field stripping in SEPS write payloads
- Construction API — no backwards compat constraints

Closes audit defect D2 (all asdict() call sites migrated).
```

Next phase: **Phase 2.5 — Config int casting (Q4)**.
