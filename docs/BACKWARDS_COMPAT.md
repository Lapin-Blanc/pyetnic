# Backwards Compatibility Policy

> **Status**: Active policy for versions 0.1.0 through 0.x.x
> **Target**: Freeze stable API at 1.0.0

This document defines which parts of pyetnic are considered stable and cannot be broken without a major version bump, and which parts are "in construction" and may evolve freely.

---

## Principle

pyetnic is in pre-1.0 development. Not all public-looking symbols are actually in production use. We distinguish between:

- **Stable API** — used in production (by the author or known dependents), must be preserved across minor versions
- **Construction API** — exported but not in production use, may change without notice until 1.0.0

The authoritative list lives in [`PUBLIC_API_SURFACE.md`](./PUBLIC_API_SURFACE.md). This document describes the rules that apply to each category.

---

## Stable API rules

For any symbol listed as **stable** in `PUBLIC_API_SURFACE.md`:

### Functions

- **Names** are frozen. Renaming requires a deprecation alias and a major version bump.
- **Parameter names** are frozen. Renaming a parameter is a breaking change.
- **Parameter order** for positional args is frozen.
- **Adding new parameters** is allowed only if they have default values.
- **Return types** are frozen. The concrete dataclass returned may gain new optional fields but cannot remove or rename existing ones.
- **Exception types raised** may be refined (a function may start raising a more specific subclass), but the base type expected by callers must remain compatible.

### Dataclasses

- **Existing fields** cannot be removed or renamed.
- **New fields** must have defaults (so existing constructor calls still work).
- **Field types** may be widened (e.g. `int` → `int | None`) but not narrowed.

### Configuration

- `Config` attribute names are frozen.
- Environment variable names (`DEV_USERNAME`, `PROD_PASSWORD`, `DEFAULT_ETABID`, etc.) are frozen.
- `.env` file format is frozen.

### Error handling contract

When a stable function changes its error handling behavior (e.g. starts raising instead of returning `None`), the new behavior must be:

1. **Opt-in** via a parameter defaulting to the old behavior, OR
2. **Backward compatible** in the sense that old callers' error paths still work (e.g. the raised exception subclasses a type they were already handling)

## Construction API rules

For any symbol listed as **construction** in `PUBLIC_API_SURFACE.md`:

- No rétrocompatibility guarantee.
- May be renamed, refactored, rewritten, or removed at any minor version.
- Should still be tested (unit tests at minimum), but not via regression tests of the public API.
- Documentation should make clear the API is unstable (docstrings, README warnings).

---

## Deprecation process

When we want to change a stable symbol, the process is:

1. **Introduce the new behavior** alongside the old one, typically via a new parameter or a new function.
2. **Mark the old behavior as deprecated** using `warnings.warn(DeprecationWarning, ...)` with a clear message including the target removal version.
3. **Update documentation** (README, docstrings, CHANGELOG) to point to the new way.
4. **Wait at least one minor version** before removing the old behavior.
5. **Remove in the next major version** (e.g. deprecated in 0.2.0, removed in 1.0.0).

Example from Sprint 1 phase 1.3:

```python
def lire_organisation(
    self,
    organisation_id: OrganisationId,
    raise_on_error: bool = False,  # NEW
) -> Optional[Organisation]:
    """
    ...
    Args:
        raise_on_error: If True, raises EtnicBusinessError on server failure.
                        If False (default, deprecated), returns None on failure.
                        Default will change to True in 0.2.0.
    """
```

Callers who want the new behavior opt in by passing `raise_on_error=True`. Callers who do nothing keep the old behavior until 0.2.0.

---

## Version bumping rules

This project follows [Semantic Versioning](https://semver.org/) with pre-1.0 semantics:

| Version | Meaning |
|---|---|
| `0.x.y` | Pre-1.0. Minor bumps MAY contain breaking changes to construction APIs but NOT to stable APIs. Patch bumps are bug fixes only. |
| `1.0.0` | First stable release. Stable API frozen. Construction APIs either promoted to stable or removed. |
| `1.x.y` | Stable API frozen. Breaking changes require a major bump to `2.0.0`. |

Current trajectory:
- **0.0.12** → **0.1.0**: end of Sprint 4, stable beta.
- **0.1.0** → **0.2.0**: when deprecated behaviors introduced in 0.1.0 are removed.
- **0.2.0** → **1.0.0**: when we're ready to freeze the API and promote construction APIs.

---

## Testing rétrocompatibility

Stable API symbols are covered by regression tests in `tests/regression/`:

- `test_public_api_eprom.py` — all EPROM stable symbols
- `test_public_api_seps_read.py` — SEPS lecture stable symbols

These tests are mock-based (no network), run in CI on every push, and serve as the automated enforcement mechanism for this policy. If a refactoring breaks a regression test, either the refactoring is wrong, or the regression test captures outdated behavior and needs explicit review before being updated.

Construction API symbols are covered only by unit tests. No regression coverage.

---

## What to do when you want to break something stable

1. **Double-check** it's actually on the stable list. If not, go ahead.
2. If it is, document the proposed change in a phase prompt under `docs/phases/`.
3. Introduce the change via the deprecation process above.
4. Update `PUBLIC_API_SURFACE.md` if the symbol's classification changes.
5. Add a CHANGELOG entry.
