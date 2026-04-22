# pyetnic — Refactoring Plan

> **Current sprint**: Sprint 1 — Robustness
> **Target version**: 0.1.0 beta (end of Sprint 4)
> **Current branch**: `refactor/sprint-1`

This document is the single source of truth for refactoring progress. It is updated by Claude Code at the end of each phase. Read it first before starting any new phase.

---

## Global progress

- [x] **Sprint 0** — Preparation (structure, regression tests, CI) _(completed 2026-04-13)_
- [ ] **Sprint 1** — Robustness (D1, D3, Q1, Q2, H3, H1)
- [ ] **Sprint 2** — Structural refactoring (D2, D5, Q4, H9)
- [ ] **Sprint 3** — Quality and hygiene (H2, H5, H8, Q5, Q6, Q7, Q8, H11)
- [ ] **Sprint 4** — Publication (CHANGELOG, bump, PyPI)

---

## Sprint 0 — Preparation

**Goal**: Put the scaffolding in place so that all subsequent sprints can proceed safely. No refactoring yet.

**Branch**: `refactor/sprint-0`

### Phases

- [x] **Phase 0.1** — Structure setup _(completed 2026-04-13)_
  - Create `docs/`, `docs/phases/`, `examples/`
  - Move scripts `extrait_profs.py`, `print_doc2.py`, `print_doc3.py` to `examples/`
  - Import `AUDIT.md` to `docs/`
  - Extract `SPEC.md` from current `.claude/CLAUDE.md` (413 lines)
  - Install new short `CLAUDE.md` at repo root
  - Do NOT modify any code under `pyetnic/`
  - **Validation**: `tree -L 2` shows new structure; `pytest tests/` still green

- [x] **Phase 0.2** — Backwards compatibility policy _(completed 2026-04-13)_
  - Install `docs/BACKWARDS_COMPAT.md`
  - Install `docs/PUBLIC_API_SURFACE.md`
  - **Validation**: documents present and internally consistent

- [x] **Phase 0.3** — Regression tests _(completed 2026-04-13)_
  - Create `tests/regression/` directory
  - Create `tests/regression/conftest.py` with mock fixtures for `SoapClientManager`
  - Write `tests/regression/test_public_api_eprom.py` covering all stable EPROM symbols
  - Write `tests/regression/test_public_api_seps_read.py` covering stable SEPS read symbols
  - Migrate existing tests to `tests/unit/` and `tests/integration/`
  - **Validation**: `pytest tests/regression/` green without network; existing tests still green

- [x] **Phase 0.4** — CI setup _(completed 2026-04-13)_
  - Create `.github/workflows/tests.yml`
  - Workflow runs `pytest tests/regression/ tests/unit/` on push and PR
  - Matrix: Python 3.10, 3.11, 3.12, 3.13 on ubuntu-latest
  - **Validation**: push a commit, check Actions tab is green

- [x] **Phase 0.5** — Branch setup and sprint 0 merge _(completed 2026-04-13)_
  - Review all sprint 0 changes
  - Squash/organize commits if needed
  - Open PR `refactor/sprint-0` → `main`
  - Self-review, merge
  - Tag the merge commit as `sprint-0-complete` (optional)
  - Create branch `refactor/sprint-1` from new `main`
  - **Validation**: sprint 0 merged, sprint 1 branch ready

---

## Sprint 1 — Robustness

**Goal**: close the robustness defects flagged in `docs/AUDIT.md` (D1, D3, Q1, Q2, H3, H1) without breaking the stable API.

**Branch**: `refactor/sprint-1`

### Phases

- [x] **Phase 1.1** — Cache invalidation on Config change (D1) _(completed 2026-04-13)_
  - Cache keyed on `(service_name, Config.ENV, Config.USERNAME)`
  - New `SoapClientManager.reset_cache()` classmethod
  - 5 regression tests in `tests/regression/test_cache_invalidation.py`

- [x] **Phase 1.2** — EPROM exception hierarchy _(completed 2026-04-13)_
- [x] **Phase 1.3** — Strict-mode migration (opt-in raise-on-error) _(completed 2026-04-22)_
  - `Config.RAISE_ON_ERROR` backed by a `ContextVar` (thread/asyncio-safe)
  - `strict_errors()` context manager in `pyetnic/error_mode.py`
  - `signal_business_error()` + `map_etnic_error_code_to_class()` helpers in `pyetnic/exceptions.py`
  - All EPROM `_parse_*_response` methods migrated; `supprimer_organisation` and `lister_formations*` raise in strict mode
  - 18 regression tests in `tests/regression/test_strict_mode.py`; default-mode contract unchanged
- [x] **Phase 1.4** — AttributeError fix _(completed 2026-04-22)_
  - Removed `AttributeError` from `SoapClientManager.call_service` except tuple
  - 2 regression tests in `tests/regression/test_call_service_errors.py`
- [x] **Phase 1.5** — Replace `except Exception` blocks _(completed 2026-04-22)_
  - Removed broad `except Exception` from `lister_formations` and `lister_formations_organisables`
  - Unexpected errors (KeyError, etc.) now propagate with full traceback
  - 2 new regression tests in `tests/regression/test_unexpected_errors.py`
  - Updated 2 unit tests to the new contract; added 2 more for `SoapError` wrapping and `RuntimeError` propagation
- [ ] **Phase 1.6** — CLI and README hygiene

---

## Notes and decisions

### Decisions made in Sprint 0 discussion

- **Pydantic vs dataclasses**: stay on dataclasses for Sprints 1-4. Pydantic migration is a separate decision to be made after 0.1.0.
- **`OrganisationKey` split (D6)**: deferred to 1.0.0 (breaking change).
- **SEPS write operations**: classified as "construction" API per `PUBLIC_API_SURFACE.md`. Free to refactor without backwards compatibility constraints. No golden payloads, no manual validation gate. Simple unit tests with mocks suffice.
- **Git workflow**: one branch per sprint, commits per phase, PR merge at end of sprint.
- **Target version**: 0.0.12 → 0.1.0 beta at end of Sprint 4.

### Open questions

- (none at this point — all resolved during Sprint 0 planning discussion)

---

## Sprint 0 retrospective

Completed on: 2026-04-13

**What went well**:
- Phases 0.1 and 0.2 were quasi-mechanical thanks to the bundled documents and a clear scope.
- Phase 0.3 regression suite came together cleanly: class-level patching of `SoapClientManager.call_service` lets every singleton be intercepted without per-service plumbing, and the `mock_soap_call` + `isolate_config` pair keeps tests fully hermetic.
- 4-version Python matrix on CI passed first try with no fixups.
- Zero changes to `pyetnic/` code — Sprint 0 stayed pure scaffolding as intended.

**What took longer than expected**:
- Phase 0.3 reconciliation between SOAP response shapes and parsers required reading every service module to build canonical fixtures rich enough to detect future regressions silently dropping fields.
- Test-file migration (`git mv` + heavy edits) lost the default 50 % similarity threshold, so `git log --follow` now needs `-M30%` to trace the unit-side history. Documented as a footnote.

**Surprises / discoveries**:
- The metaclass-driven lazy `Config` is friendly to tests: `Config._reset()` + a few attribute writes give you a clean, dotenv-free environment.
- `rechercher_etudiants` uses a regex to extract the new NISS from the error description (code 30401). The regression test pins this contract explicitly.
- `_CT.serialize_object(result, dict)` shape sometimes returns a single dict where a list was expected (one match in `rechercherEtudiants`); a regression test guards against this corner case.

**Metrics**:
- Lines added: 4812 (mostly tests + docs)
- Lines removed: 1316 (old `tests/test_formation_*.py` deleted in favor of unit/integration split)
- Tests added: 69 regression (50 EPROM + 19 SEPS read), with full coverage of every stable symbol in `PUBLIC_API_SURFACE.md`
- Tests migrated: 26 unit + 14 integration
- Total local suite: 95 passed in 0.19s + 14 skipped (integration without `.env`)
- CI runtime: ~33-37 s per Python version (4 jobs in parallel)

**Notes for Sprint 1**:
- Sprint 1 will introduce new error-handling behavior (raising vs returning None). Each contract change must update the corresponding regression test in the same commit, otherwise the safety net fails for the wrong reason.
- The Node.js 20 deprecation warning on `actions/checkout@v4` and `actions/setup-python@v5` is non-blocking until June 2026 — track for Sprint 3 hygiene.
- `.claude/CLAUDE.md` (413 lines) is still on disk pending Sprint 3 phase 3.1 cleanup; do not delete it before then.

---

## Changelog of this file

- **[Sprint 0, phase 0.1]** Initial creation.
- **[Sprint 0, phase 0.5]** Sprint 0 marked complete; retrospective added.
