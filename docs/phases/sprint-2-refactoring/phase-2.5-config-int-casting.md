# Phase 2.5 — Config int casting for ETAB_ID / IMPL_ID (Q4)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **Q4**
- `plan.md`
- `pyetnic/config.py` — the `_SIMPLE_ENV_MAP` and `_ConfigMeta.__getattr__`

## Objective

Make `Config.ETAB_ID` and `Config.IMPL_ID` return `int` (or `None`) instead of `str` (or `None`). Currently `os.getenv()` returns strings, and callers have to do `int(Config.ETAB_ID)` manually — or worse, pass strings to zeep which silently converts them because the XSD says `xs:int`.

## Tasks

### 1. Extend `_SIMPLE_ENV_MAP` with a caster

Currently:

```python
_SIMPLE_ENV_MAP: dict[str, tuple[str, str | None]] = {
    "ENV": ("ENV", "dev"),
    "ANNEE_SCOLAIRE": ("DEFAULT_SCHOOLYEAR", "2023-2024"),
    "ETAB_ID": ("DEFAULT_ETABID", None),
    "IMPL_ID": ("DEFAULT_IMPLID", None),
    "SEPS_PFX_PATH": ("SEPS_PFX_PATH", None),
    "SEPS_PFX_PASSWORD": ("SEPS_PFX_PASSWORD", None),
}
```

Add a third element to each tuple — the caster function (default: `str` or identity):

```python
_SIMPLE_ENV_MAP: dict[str, tuple[str, Any, type | None]] = {
    "ENV": ("ENV", "dev", None),               # str, no cast needed
    "ANNEE_SCOLAIRE": ("DEFAULT_SCHOOLYEAR", "2023-2024", None),
    "ETAB_ID": ("DEFAULT_ETABID", None, int),   # cast to int
    "IMPL_ID": ("DEFAULT_IMPLID", None, int),   # cast to int
    "SEPS_PFX_PATH": ("SEPS_PFX_PATH", None, None),
    "SEPS_PFX_PASSWORD": ("SEPS_PFX_PASSWORD", None, None),
}
```

### 2. Update `__getattr__` to apply the caster

In the "Simple env lookup" branch of `_ConfigMeta.__getattr__`:

```python
# 4. Simple env lookup
env_var, default, caster = _SIMPLE_ENV_MAP[name]
value = os.getenv(env_var, default)
if value is not None and caster is not None:
    try:
        value = caster(value)
    except (ValueError, TypeError):
        # If the env value can't be cast (e.g. empty string for int),
        # return None rather than crashing at import time
        value = None
return value
```

The `try/except` is important: if someone has `DEFAULT_ETABID=` (empty string) in their `.env`, `int("")` would raise `ValueError`. Returning `None` in that case is the safest default — `Config.validate()` will then report the missing value.

### 3. Handle overrides with the caster

When someone does `Config.ETAB_ID = "3052"` (string), should we cast? Currently overrides go straight into `_overrides` and are returned as-is.

**Decision**: do NOT auto-cast overrides. If someone explicitly writes `Config.ETAB_ID = "3052"`, they get a string. If they write `Config.ETAB_ID = 3052`, they get an int. The caster only applies to `.env` file values (which are always strings).

This is consistent with the existing behavior for `USERNAME` and `PASSWORD` (never cast) and avoids surprising behavior on explicit assignments.

### 4. Update callers that do manual `int()` conversion

```bash
grep -rn "int(Config.ETAB_ID)" pyetnic/ tests/
grep -rn "int(Config.IMPL_ID)" pyetnic/ tests/
```

For each found:
- In `pyetnic/` code: remove the `int()` wrapper (now redundant)
- In `tests/`: update if the test was explicitly testing the string behavior. These are unit tests, not regression tests, so they can be updated.

Check `pyetnic/services/formations_liste.py` especially — it passes `Config.ETAB_ID` directly without casting, relying on zeep to handle the conversion. This will now work correctly by type.

### 5. Add a regression test

Add to `tests/regression/test_config.py` (or create if it doesn't exist):

```python
"""Regression tests for Config attribute types."""

import os
import pytest
from pyetnic.config import Config


@pytest.fixture(autouse=True)
def clean_config():
    Config._reset()
    yield
    Config._reset()


def test_etab_id_returns_int_from_env(monkeypatch):
    """Config.ETAB_ID should return an int when set via env var."""
    monkeypatch.setenv("DEFAULT_ETABID", "3052")
    Config._reset()  # force re-read
    result = Config.ETAB_ID
    assert result == 3052
    assert isinstance(result, int)


def test_impl_id_returns_int_from_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_IMPLID", "6050")
    Config._reset()
    result = Config.IMPL_ID
    assert result == 6050
    assert isinstance(result, int)


def test_etab_id_returns_none_when_unset():
    """Config.ETAB_ID should return None when the env var is absent."""
    Config._reset()
    # Don't set DEFAULT_ETABID
    result = Config.ETAB_ID
    assert result is None


def test_etab_id_returns_none_for_empty_string(monkeypatch):
    """An empty env value should return None, not raise ValueError."""
    monkeypatch.setenv("DEFAULT_ETABID", "")
    Config._reset()
    result = Config.ETAB_ID
    assert result is None


def test_etab_id_override_preserves_type():
    """Explicit override is returned as-is (no auto-casting)."""
    Config.ETAB_ID = 9999
    assert Config.ETAB_ID == 9999
    assert isinstance(Config.ETAB_ID, int)

    Config.ETAB_ID = "9999"  # string override
    assert Config.ETAB_ID == "9999"
    assert isinstance(Config.ETAB_ID, str)


def test_env_returns_str():
    """Config.ENV should still return a string (no caster)."""
    Config._reset()
    result = Config.ENV
    assert isinstance(result, str)
```

### 6. Verify

```bash
pytest tests/regression/ tests/unit/ -v
```

Check specifically for any test that was doing `assert Config.ETAB_ID == "3052"` (string comparison) — it will now need to compare against `3052` (int) if it reads from env. This is a legitimate test update, not a regression.

## Constraints

- **Do NOT change the type of `Config.ENV`, `Config.ANNEE_SCOLAIRE`, etc.** Only `ETAB_ID` and `IMPL_ID` get the int caster.
- **Do NOT auto-cast overrides.** Only env-sourced values are cast.
- **The `try/except` on the caster is mandatory** — don't let a bad `.env` value crash at import time.
- **`Config._reset()` must clear the cast cache** (it already clears overrides, which is sufficient since env values are re-read each time).

## Validation

- [ ] `Config.ETAB_ID` returns `int` when set via env, `None` when absent
- [ ] `Config.IMPL_ID` same behavior
- [ ] `Config.ENV` still returns `str` (no regression)
- [ ] No `int(Config.ETAB_ID)` left in `pyetnic/` code (redundant wrapper removed)
- [ ] `tests/regression/test_config.py` exists with 7+ tests
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.5 as complete. Commit message:

```
fix(sprint-2): phase 2.5 — Config.ETAB_ID/IMPL_ID return int (Q4)

- Extend _SIMPLE_ENV_MAP with optional caster (third tuple element)
- ETAB_ID and IMPL_ID now return int (from env) or None (absent/empty)
- Graceful handling of empty string values (returns None, not ValueError)
- Explicit overrides are NOT auto-cast (preserves caller intent)
- Remove redundant int() wrappers in callers
- Add 7 regression tests for Config type behavior

Closes audit defect Q4.
```

Next phase: **Phase 2.6 — Nomenclature Enums (H9)**.
