# pyetnic — Refactoring Plan

> **Current sprint**: Sprint 0 — Preparation
> **Target version**: 0.1.0 beta (end of Sprint 4)
> **Current branch**: `refactor/sprint-0` → merges to `main` at end of sprint

This document is the single source of truth for refactoring progress. It is updated by Claude Code at the end of each phase. Read it first before starting any new phase.

---

## Global progress

- [ ] **Sprint 0** — Preparation (structure, regression tests, CI)
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

- [ ] **Phase 0.3** — Regression tests
  - Create `tests/regression/` directory
  - Create `tests/regression/conftest.py` with mock fixtures for `SoapClientManager`
  - Write `tests/regression/test_public_api_eprom.py` covering all stable EPROM symbols
  - Write `tests/regression/test_public_api_seps_read.py` covering stable SEPS read symbols
  - Migrate existing tests to `tests/unit/` and `tests/integration/`
  - **Validation**: `pytest tests/regression/` green without network; existing tests still green

- [ ] **Phase 0.4** — CI setup
  - Create `.github/workflows/tests.yml`
  - Workflow runs `pytest tests/regression/ tests/unit/` on push and PR
  - Matrix: Python 3.10, 3.11, 3.12, 3.13 on ubuntu-latest
  - **Validation**: push a commit, check Actions tab is green

- [ ] **Phase 0.5** — Branch setup and sprint 0 merge
  - Review all sprint 0 changes
  - Squash/organize commits if needed
  - Open PR `refactor/sprint-0` → `main`
  - Self-review, merge
  - Tag the merge commit as `sprint-0-complete` (optional)
  - Create branch `refactor/sprint-1` from new `main`
  - **Validation**: sprint 0 merged, sprint 1 branch ready

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

## Changelog of this file

- **[Sprint 0, phase 0.1]** Initial creation.
