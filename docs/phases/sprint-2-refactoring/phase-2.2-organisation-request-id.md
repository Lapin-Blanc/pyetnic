# Phase 2.2 — Migrate organisation_request_id across services (D5)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D5**
- `plan.md`
- `pyetnic/services/_helpers.py` (created in phase 2.1)

This phase replaces the 4 copy-pasted `_organisation_id_dict` static methods with calls to the shared `organisation_request_id` helper.

## Objective

Deduplicate the `_organisation_id_dict` static method across `organisation.py`, `document1.py`, `document2.py`, `document3.py` by replacing all call sites with `organisation_request_id` from `_helpers.py`.

## Tasks

### 1. Identify all call sites

```bash
grep -rn "_organisation_id_dict" pyetnic/services/
```

Expected: 4 definitions (one per file) + multiple call sites within each file.

### 2. Migrate each file

For each of the 4 service files, the change is identical:

**Before** (in each file):

```python
@staticmethod
def _organisation_id_dict(organisation_id: OrganisationId) -> dict:
    """Retourne les champs attendus par OrganisationReqIdCT (sans implId)."""
    return {
        'anneeScolaire': organisation_id.anneeScolaire,
        'etabId': organisation_id.etabId,
        'numAdmFormation': organisation_id.numAdmFormation,
        'numOrganisation': organisation_id.numOrganisation,
    }
```

**After**:

1. Add the import at the top of the file:
   ```python
   from ._helpers import organisation_request_id
   ```

2. Replace every call from `self._organisation_id_dict(org_id)` to `organisation_request_id(org_id)`.

3. **Delete** the `_organisation_id_dict` static method from the class.

### Per-file checklist

**`pyetnic/services/organisation.py`**:
- [ ] Add import
- [ ] Replace calls in: `lire_organisation`, `modifier_organisation`, `supprimer_organisation`
- [ ] Delete `_organisation_id_dict` method
- [ ] Note: `creer_organisation` does NOT use `_organisation_id_dict` — it builds its own dict WITH `implId`. Leave it alone.

**`pyetnic/services/document1.py`**:
- [ ] Add import
- [ ] Replace calls in: `lire_document_1`, `modifier_document_1`, `approuver_document_1`
- [ ] Delete `_organisation_id_dict` method

**`pyetnic/services/document2.py`**:
- [ ] Add import
- [ ] Replace calls in: `lire_document_2`, `modifier_document_2`
- [ ] Delete `_organisation_id_dict` method

**`pyetnic/services/document3.py`**:
- [ ] Add import
- [ ] Replace calls in: `lire_document_3`, `modifier_document_3`
- [ ] Delete `_organisation_id_dict` method

### 3. Verify

```bash
pytest tests/regression/ tests/unit/ -v
```

**Critical check**: the regression tests from Sprint 0 phase 0.3 include tests like `test_lire_organisation_sends_correct_request` that verify the exact dict shape sent to `call_service`. These tests MUST pass without modification — they prove the migration is behaviorally transparent.

Specifically, every test that asserts `implId` is absent from the request dict must still pass. If it doesn't, the migration introduced a bug.

## Constraints

- **Do NOT modify the regression tests.** They are the proof that the migration is correct.
- **Do NOT change `creer_organisation`** — it legitimately includes `implId` and uses its own dict construction.
- **Do NOT add `organisation_request_id` to the public API.**
- **Separate commit from phase 2.1.** The helpers were created in 2.1; this phase only wires them in.

## Validation

- [ ] `grep -rn "_organisation_id_dict" pyetnic/services/` returns **zero** results
- [ ] `grep -rn "organisation_request_id" pyetnic/services/` shows imports + call sites in 4 files
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green, zero test modifications
- [ ] The `implId` exclusion tests in `tests/regression/test_public_api_eprom.py` still pass
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.2 as complete. Commit message:

```
refactor(sprint-2): phase 2.2 — deduplicate _organisation_id_dict (D5)

- Replace 4 copy-pasted _organisation_id_dict static methods with
  shared organisation_request_id() from _helpers.py
- 4 files touched: organisation.py, document1.py, document2.py, document3.py
- creer_organisation unchanged (legitimately includes implId)
- Zero regression test modifications — all implId-exclusion tests pass

Closes audit defect D5.
```

Next phase: **Phase 2.3 — Migrate to_soap_dict in EPROM document services (D2)**.
