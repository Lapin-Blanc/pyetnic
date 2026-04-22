# Phase 2.3 — Migrate to_soap_dict in EPROM document services (D2)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D2**
- `plan.md`
- `pyetnic/services/_helpers.py` — the `to_soap_dict` function
- `tests/unit/test_helpers.py` — proof that the helper works

This phase replaces `dataclasses.asdict()` with `to_soap_dict()` in the three EPROM document services. These are **stable API** — the regression tests must continue to pass without modification.

## Objective

Replace every `asdict(payload_dataclass)` call in `document1.py`, `document2.py`, and `document3.py` with `to_soap_dict(payload_dataclass)`, so that `None`-valued optional fields are no longer sent as empty XML elements to ETNIC.

## Tasks

### 1. Identify all `asdict` call sites in EPROM

```bash
grep -rn "asdict" pyetnic/services/document*.py
```

Expected call sites:

**`document1.py`** — `modifier_document_1` and `approuver_document_1`:
```python
request_data['populationListe'] = asdict(population_liste)
```

**`document2.py`** — `modifier_document_2`:
```python
request_data['activiteEnseignementListe'] = asdict(activite_enseignement_liste)
request_data['interventionExterieureListe'] = asdict(intervention_exterieure_liste)
```

**`document3.py`** — `modifier_document_3`:
```python
activiteListe=asdict(activite_liste),
```

### 2. Migrate each file

For each file:

1. Replace the import:
   ```python
   # Before
   from dataclasses import asdict
   
   # After
   from ._helpers import to_soap_dict
   ```

2. Replace each `asdict(obj)` call with `to_soap_dict(obj)`.

3. If `asdict` is still used for other purposes in the file (unlikely but check), keep both imports.

**Concrete example for `document1.py`**:

Before:
```python
from dataclasses import asdict

def modifier_document_1(self, organisation_id, population_liste=None):
    request_data = {'id': organisation_request_id(organisation_id)}
    if population_liste is not None:
        request_data['populationListe'] = asdict(population_liste)
    ...
```

After:
```python
from ._helpers import to_soap_dict, organisation_request_id

def modifier_document_1(self, organisation_id, population_liste=None):
    request_data = {'id': organisation_request_id(organisation_id)}
    if population_liste is not None:
        request_data['populationListe'] = to_soap_dict(population_liste)
    ...
```

### 3. Understand the behavioral change

This is the one place where the migration is NOT purely mechanical — it changes observable behavior:

**Before**: `asdict()` sends `{'coAnnEtude': 1, 'nbEleveA': 12, 'nbEleveEhr': None, 'nbEleveFse': None, ...}`
**After**: `to_soap_dict()` sends `{'coAnnEtude': 1, 'nbEleveA': 12}`

zeep translates the "before" dict into XML elements like `<nbEleveEhr/>` (empty tag), which ETNIC may interpret as "set this to zero" or reject outright. The "after" dict simply omits the tag, which ETNIC interprets as "don't touch this field".

**This is the fix for D2 — it's intentionally different behavior.**

However, the **callers** of `modifier_document_1` don't see this change: they still pass a `Doc1PopulationListSave` dataclass and get back a `FormationDocument1`. The change is transparent at the API level. The regression tests (which mock `call_service` and verify return values) should remain green.

### 4. Add a regression test that verifies the new payload shape

While existing tests verify the return values, we should add a test that checks what dict shape reaches `call_service`. This pins the "no None values" contract:

Add to `tests/regression/test_public_api_eprom.py` or create a new `tests/regression/test_soap_payload_shape.py`:

```python
"""Regression tests for SOAP payload serialization (D2 fix).

These tests verify that None-valued optional fields are NOT sent
to the SOAP layer, preventing ETNIC from misinterpreting empty XML tags.
"""

from pyetnic.eprom import (
    modifier_document_1,
    OrganisationId,
)
from pyetnic.services.models import Doc1PopulationLineSave, Doc1PopulationListSave


def test_modifier_document_1_payload_excludes_none_fields(mock_soap_call):
    """Verify that optional None fields are stripped from the SOAP payload.

    Before D2 fix: asdict() sent nbEleveEhr=None as an empty XML element.
    After D2 fix: to_soap_dict() omits nbEleveEhr entirely.
    """
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document1': {
                    'populationListe': {
                        'population': [{
                            'coAnnEtude': 1, 'nbEleveA': 12,
                            'nbEleveEhr': 0, 'nbEleveFse': 0, 'nbElevePi': 0,
                            'nbEleveB': 0, 'nbEleveTot2a5': 0, 'nbEleveDem': 0,
                            'nbEleveMin': 0, 'nbEleveExm': 0, 'nbElevePl': 0,
                            'nbEleveTot6et8': 0, 'nbEleveTotFse': 0, 'nbEleveTotPi': 0,
                            'nbEleveTotHom': 5, 'nbEleveTotFem': 7,
                            'swAppPopD1': False, 'swAppD1': False,
                        }]
                    }
                }
            }
        }
    }

    org_id = OrganisationId(
        anneeScolaire="2024-2025", etabId=3052,
        numAdmFormation=455, numOrganisation=1,
    )
    line = Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12, nbEleveTotHom=5, nbEleveTotFem=7)
    liste = Doc1PopulationListSave(population=[line])

    modifier_document_1(org_id, population_liste=liste)

    # Inspect the payload sent to call_service
    call_kwargs = mock_soap_call.call_args.kwargs
    population_dict = call_kwargs['populationListe']

    # The population list should contain one item
    pop_line = population_dict['population'][0]

    # Required fields are present
    assert pop_line['coAnnEtude'] == 1
    assert pop_line['nbEleveA'] == 12

    # Optional fields that were None should be ABSENT (D2 fix)
    assert 'nbEleveEhr' not in pop_line
    assert 'nbEleveDem' not in pop_line
    assert 'nbEleveMin' not in pop_line
```

Add similar tests for `modifier_document_2` and `modifier_document_3` with their respective models.

### 5. Verify

```bash
pytest tests/regression/ tests/unit/ -v
```

**Expected**:
- All existing regression tests pass (return values unchanged)
- New payload shape tests pass (None fields absent)
- Unit tests for helpers still pass

If an existing regression test breaks, investigate carefully. The most likely cause is a test fixture that includes `None` values in a way that triggers a structural assertion. Adapt the fixture if needed, but document the reason in the commit message.

## Constraints

- **Only touch document1.py, document2.py, document3.py** in this phase. SEPS write services are phase 2.4.
- **Do not touch `organisation.py`** — it doesn't use `asdict` for payloads (it builds dicts manually).
- **Do not touch `formations_liste.py`** — it doesn't use `asdict`.
- **Existing regression tests should NOT be modified** unless a fixture contains fabricated None values that no longer round-trip identically (unlikely but possible).

## Validation

- [ ] `grep -rn "from dataclasses import asdict" pyetnic/services/document*.py` returns **zero** results
- [ ] `grep -rn "to_soap_dict" pyetnic/services/document*.py` shows calls in all 3 files
- [ ] `tests/regression/test_soap_payload_shape.py` exists with 3+ payload-shape tests
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.3 as complete. Commit message:

```
fix(sprint-2): phase 2.3 — replace asdict() with to_soap_dict() in EPROM docs (D2)

- Migrate document1.py, document2.py, document3.py from asdict() to
  to_soap_dict(exclude_none=True)
- None-valued optional fields no longer sent as empty XML elements
- Add 3 payload-shape regression tests verifying absence of None fields
- Existing return-value regression tests unchanged

Partial fix for audit defect D2 (EPROM side).
```

Next phase: **Phase 2.4 — Migrate to_soap_dict in SEPS write services (D2)**.
