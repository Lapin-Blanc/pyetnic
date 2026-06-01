# Phase 3.5 — Logger formatting: f-strings → lazy %s (Q7)

## Context

Read first:

- `CLAUDE.md` — coding conventions section mentions "f-strings forbidden in logger.debug()"
- `docs/AUDIT.md` — section **Q7**
- `plan.md`

This is the last phase of Sprint 3. It's a mechanical substitution across ~20 call sites, but needs care to avoid breaking string formatting.

## Objective

Replace all f-string usage in `logger.debug()`, `logger.info()`, `logger.warning()`, and `logger.error()` calls with `%s`-style lazy formatting. For calls involving `pformat()` on potentially large objects, add a `logger.isEnabledFor()` guard.

## Tasks

### 1. Inventory all f-string logger calls

```bash
grep -rn 'logger\.\(debug\|info\|warning\|error\)(f"' pyetnic/
```

Expected ~20 occurrences across:
- `soap_client.py` (2 — but one was already fixed in phase 3.4)
- `services/formations_liste.py` (3)
- `services/organisation.py` (5)
- `services/document1.py` (4)
- `services/document2.py` (3)
- `services/document3.py` (3)

### 2. Apply the substitution pattern

**Simple case** (most occurrences):

```python
# Before:
logger.info(f"Lecture de l'organisation {organisation_id}")

# After:
logger.info("Lecture de l'organisation %s", organisation_id)
```

**Case with `pformat`** (heavy evaluation):

```python
# Before:
logger.debug(f"Organisation : {pformat(org_data)}")

# After:
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Organisation : %s", pformat(org_data))
```

The guard prevents `pformat()` from being called when DEBUG is not enabled. This is the performance fix — `pformat` on a large zeep dict can take milliseconds.

**Case with multiple variables**:

```python
# Before:
logger.error(f"{error_msg} (request_id: {request_id})")

# After:
logger.error("%s (request_id: %s)", error_msg, request_id)
```

Note: the `soap_client.py` error-path line was already fixed in phase 3.4. Verify it's done and skip it.

### 3. Remove unused `pprint` imports

After adding the `logging.DEBUG` guard pattern, some files may no longer need `from pprint import pformat` at the top level (if it's only used inside the guard). However, **keep the import** — removing it would change behavior if anyone adds a new debug log later. The import is cheap.

Actually, check: if `pprint` or `pformat` is imported but never used (some files import `pprint` but only use `pformat`), clean up the unused import.

```bash
grep -rn "from pprint import" pyetnic/services/
# Check each file: is pformat actually used?
```

### 4. Per-file checklist

For each file, apply the substitution and verify:

**`pyetnic/soap_client.py`**:
- [ ] Check that phase 3.4 already fixed the error-path log
- [ ] Fix remaining f-string logs (if any — the `logger.debug` in `_initialize_client`)
- [ ] Add `import logging` at top if not already present (it is)

**`pyetnic/services/formations_liste.py`**:
- [ ] `logger.info(f"Appel de lister_formations")` → `logger.info("Appel de lister_formations")` (no variable — just remove the f-prefix)
- [ ] `logger.debug(f"Résultat : {pformat(result)}")` → guarded
- [ ] `logger.debug(f"Formation : {pformat(f)}")` → guarded
- [ ] Remove unused `pprint` import if applicable

**`pyetnic/services/organisation.py`**:
- [ ] `logger.info(f"Lecture de l'organisation {organisation_id}")` → `%s`
- [ ] `logger.debug(f"Organisation : {pformat(org_data)}")` → guarded
- [ ] (repeat for all ~5 occurrences)

**`pyetnic/services/document1.py`**:
- [ ] Same pattern, ~4 occurrences

**`pyetnic/services/document2.py`**:
- [ ] Same pattern, ~3 occurrences

**`pyetnic/services/document3.py`**:
- [ ] Same pattern, ~3 occurrences

### 5. Verify no f-strings remain

```bash
grep -rn 'logger\.\(debug\|info\|warning\|error\)(f"' pyetnic/
# Must return ZERO results
```

### 6. Run tests

```bash
pytest tests/regression/ tests/unit/ -v
```

This is a purely cosmetic change — all tests should pass unchanged. If a test fails, it means the string substitution introduced a formatting error (e.g., wrong number of `%s` placeholders vs arguments). Fix the formatting, don't change the test.

### 7. Quick smoke test for log output

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from pyetnic.config import Config
Config.ENV = "dev"
Config.USERNAME = "test"
Config.PASSWORD = "test"

from pyetnic.services.organisation import OrganisationService
svc = OrganisationService()
# This will fail (no SOAP connection), but check that the logger.info
# at the start of lire_organisation prints correctly with %s formatting
try:
    svc.lire_organisation(None)
except:
    pass
```

Check that the log output looks correct (no `%s` literals in the output, no `TypeError: not enough arguments for format string`).

## Constraints

- **Mechanical substitution only.** Don't refactor the log messages, don't change log levels, don't add new log statements.
- **Don't remove `pformat` usage** — just guard it with `isEnabledFor`.
- **One commit for the whole file set.** This is a single logical change (style fix) across multiple files.
- **The `soap_client.py` error-path fix from phase 3.4** should already be done. Don't duplicate work.

## Validation

- [ ] `grep -rn 'logger\.\(debug\|info\|warning\|error\)(f"' pyetnic/` returns zero
- [ ] All `pformat` calls are inside `if logger.isEnabledFor(logging.DEBUG)` guards
- [ ] No unused `pprint`/`pformat` imports
- [ ] All tests green (no formatting errors)
- [ ] CI green
- [ ] Quick smoke test: log output looks correct

## Next

Update `plan.md`: mark Phase 3.5 as complete. Commit message:

```
style(sprint-3): phase 3.5 — replace f-strings with lazy %s in loggers (Q7)

- Convert ~20 logger calls from f"..." to "%s", args
- Add isEnabledFor(DEBUG) guards around pformat() calls
  (prevents expensive serialization when DEBUG is disabled)
- Clean up unused pprint imports

Closes audit defect Q7. Concludes Sprint 3.
```

After this phase, **open a new conversation in Atelier Analyse** for the Sprint 3 retrospective and Sprint 3 → Sprint 4 transition. Same process as previous sprints: PR, merge, branch creation, retrospective in `plan.md`.
