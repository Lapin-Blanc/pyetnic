# pyetnic — Refactoring Plan

> **Current sprint**: Sprint 2 — Structural refactoring
> **Target version**: 0.1.0 beta (end of Sprint 4)
> **Current branch**: `refactor/sprint-2`

This document is the single source of truth for refactoring progress. It is updated by Claude Code at the end of each phase. Read it first before starting any new phase.

---

## Global progress

- [x] **Sprint 0** — Preparation (structure, regression tests, CI) _(completed 2026-04-13)_
- [x] **Sprint 1** — Robustness (D1, D3, Q1, Q2, H3, H1) _(completed 2026-04-22)_
- [ ] **Sprint 2** — Structural refactoring (D2, D5, Q4, H9)
- [ ] **Sprint 3** — Quality and hygiene (H2, H5, H8, Q5, Q6, Q7, Q8, H11)
- [ ] **Sprint 4** — Publication (CHANGELOG, bump, PyPI)

---

## Sprint 0 — Preparation

**Goal**: Put the scaffolding in place so that all subsequent sprints can proceed safely. No refactoring yet.

**Branch**: `refactor/sprint-0`

### Phases

- [x] **Phase 0.1** — Structure setup _(completed 2026-04-13)_
- [x] **Phase 0.2** — Backwards compatibility policy _(completed 2026-04-13)_
- [x] **Phase 0.3** — Regression tests _(completed 2026-04-13)_
- [x] **Phase 0.4** — CI setup _(completed 2026-04-13)_
- [x] **Phase 0.5** — Branch setup and sprint 0 merge _(completed 2026-04-13)_

---

## Notes and decisions

### Decisions made in Sprint 0 discussion

- **Pydantic vs dataclasses**: stay on dataclasses for Sprints 1-4. Pydantic migration is a separate decision to be made after 0.1.0.
- **`OrganisationKey` split (D6)**: deferred to 1.0.0 (breaking change).
- **SEPS write operations**: classified as "construction" API per `PUBLIC_API_SURFACE.md`. Free to refactor without backwards compatibility constraints.
- **Git workflow**: one branch per sprint, commits per phase, PR merge at end of sprint.
- **Target version**: 0.0.12 → 0.1.0 beta at end of Sprint 4.

### Decisions made in Sprint 1 → Sprint 2 transition

- **D2 helper form**: free function `to_soap_dict()` in private module `pyetnic/services/_helpers.py` (not a method on dataclass, not Pydantic).
- **D5 helper form**: free function `organisation_request_id()` in the same private module (not a public method `as_request_key()` on `OrganisationId`). Avoids adding to the public API surface a method that would become obsolete when D6 is implemented in 1.0.0.
- **Single private module**: both helpers in `pyetnic/services/_helpers.py` (underscore prefix = internal, not exported).
- **H9 Enums**: use `(str, Enum)` base so Enum members compare equal to raw strings. Dataclass field types remain `Optional[str]` — Enums are convenience, not enforcement. `TYPES_INTERVENTION_EXTERIEURE` legacy constant preserved.

### Open questions

- (none at this point)

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
- Lines removed: 1316
- Tests added: 69 regression (50 EPROM + 19 SEPS read)
- Tests migrated: 26 unit + 14 integration
- Total local suite: 95 passed in 0.19s + 14 skipped
- CI runtime: ~33-37 s per Python version

---

## Sprint 1 — Robustness

**Goal**: Make the EPROM error handling consistent and predictable. Fix the silent SOAP cache bug. Clean up the catch-all exception handlers and the hardcoded establishment IDs.

**Branch**: `refactor/sprint-1`

**Audit defects addressed**: D1, D3, Q1, Q2, H3, H1.

### Phases

- [x] **Phase 1.1** — Cache invalidation on Config change (D1) _(completed 2026-04-22)_
- [x] **Phase 1.2** — Create EPROM exception hierarchy (D3a) _(completed 2026-04-22)_
- [x] **Phase 1.3** — Migrate EPROM services to typed exceptions (D3b) _(completed 2026-04-22)_
- [x] **Phase 1.4** — Remove AttributeError from call_service catch (Q1) _(completed 2026-04-22)_
- [x] **Phase 1.5** — Remove except Exception from formations_liste (Q2) _(completed 2026-04-22)_
- [x] **Phase 1.6** — De-hardcode CLI and update README (H3 + H1) _(completed 2026-04-22)_

---

## Sprint 1 retrospective

Completed on: 2026-04-22

**What went well**:
- The "one commit per phase" discipline held cleanly: each of 1.1→1.6 is a single, reviewable diff, and CI stayed green on every push across the 3.10-3.13 matrix.
- Phase 1.1 → 1.3 sequencing paid off: cache invalidation first (D1), then the typed hierarchy as a pure-additive module (D3a), then the opt-in strict switch (D3b). Nothing had to be revisited.
- `contextvars.ContextVar` for `RAISE_ON_ERROR` turned out to be the right choice for both thread and asyncio isolation, with no extra plumbing in the metaclass.
- Centralizing the raise/return-None decision in `signal_business_error()` kept every `_parse_*_response` small and uniform.
- The Sprint 0 regression harness did its job: the default-mode contract was never broken by accident.

**What took longer than expected**:
- Phase 1.3 design iteration: the first sketch used a plain class attribute on `Config`; realizing it had to survive `_reset()`, not be stored in `_overrides`, and still be thread-safe forced the move to `ContextVar`.
- Phase 1.5: removing `except Exception` in `formations_liste` required updating regression fixtures to assert the absence of the wrapping behavior for non-`SoapError` exceptions.
- Documenting the 0.2.0 default-switch plan in README (phase 1.6) took more drafting than the code change itself.

**Surprises / discoveries**:
- `formations_liste` is structurally a special case and cannot be normalized without a breaking change.
- `PASSWORD` intentionally excluded from the cache key (no secrets in loggable structures) — worth a docstring comment.
- `AttributeError` removal (phase 1.4) changed two lines of production code and zero pre-existing test lines.
- The typed-hierarchy module was used by tests before any production code raised from it — pure API surface first is a pattern worth reusing.

**Metrics**:
- Commits on branch: 8 (2 chore + 6 phases), linear.
- Diff vs main: 27 files, +2918 / -48 lines.
- Tests: 95 → 138 passed (+43).
- Local suite runtime: ~0.19 s, unchanged from Sprint 0.
- CI: green on every push, 3.10-3.13 matrix.

**Notes for Sprint 2**:
- D5 has 5 call sites. Migration mechanical but keep separate commits from signal_business_error changes.
- D2 touches 7 call sites: 3 EPROM (stable), 2+2 SEPS write (construction).
- Strict-mode semantics are load-bearing: D2/D5 must preserve both default-mode None and strict-mode raise.
- Default-mode switch to raise (0.2.0) is NOT scheduled in Sprints 1-4.

---

## Sprint 2 — Structural refactoring

**Goal**: Eliminate code duplication and improve serialization safety. Deduplicate the `_organisation_id_dict` pattern, replace `asdict()` with None-stripping serialization, add proper typing to Config numeric attributes, and introduce nomenclature Enums.

**Branch**: `refactor/sprint-2`

**Audit defects addressed**: D2, D5, Q4, H9.

**Key design decisions** (made in Atelier Analyse before sprint start):
- **D2**: `to_soap_dict()` free function in `pyetnic/services/_helpers.py`.
- **D5**: `organisation_request_id()` free function in same module. Not a public method.
- **H9**: `(str, Enum)` base. Dataclass fields unchanged. Legacy constant preserved.
- **No Pydantic**: Sprint 0 decision holds.

### Phases

- [x] **Phase 2.1** — Create private helpers module (D2 + D5 foundations) _(completed 2026-04-22)_
  - `pyetnic/services/_helpers.py` with `to_soap_dict` and `organisation_request_id`
  - ~14 unit tests
  - No service code modified
  - **Conversation A** (with phase 2.2)

- [ ] **Phase 2.2** — Migrate organisation_request_id across services (D5)
  - Replace 4 copy-pasted `_organisation_id_dict` with shared helper
  - Zero regression test modifications
  - **Conversation A** (with phase 2.1)

- [ ] **Phase 2.3** — Migrate to_soap_dict in EPROM document services (D2)
  - Replace `asdict()` in document1.py, document2.py, document3.py
  - Add ~3 payload-shape regression tests
  - Stable API — existing tests must pass unmodified
  - **Conversation B** (with phase 2.4)

- [ ] **Phase 2.4** — Migrate to_soap_dict in SEPS write services (D2)
  - Replace `asdict()` in enregistrer_etudiant.py and inscriptions.py
  - Construction API — free to refactor
  - **Conversation B** (with phase 2.3)

- [ ] **Phase 2.5** — Config int casting for ETAB_ID / IMPL_ID (Q4)
  - Extend `_SIMPLE_ENV_MAP` with optional caster
  - ~7 regression tests
  - **Conversation C** (with phase 2.6)

- [ ] **Phase 2.6** — Nomenclature Enums (H9)
  - 6 `(str, Enum)` classes in `nomenclatures.py`
  - Legacy constant preserved
  - Update `PUBLIC_API_SURFACE.md`
  - ~7 unit tests
  - **Conversation C** (with phase 2.5)

### Conversation segmentation

- **Conversation A** — Phases 2.1 + 2.2 (create helpers, then wire in)
- **Conversation B** — Phases 2.3 + 2.4 (to_soap_dict migration)
- **Conversation C** — Phases 2.5 + 2.6 (Config casting + Enums)

---

## Sprint 2 retrospective

Completed on: TBD

**What went well**:
- (fill in)

**What took longer than expected**:
- (fill in)

**Surprises / discoveries**:
- (fill in)

**Metrics**:
- Lines added: (git diff stat)
- Tests added: (count)
- Total local suite: (X passed in Y seconds)
- CI runtime: (from GitHub Actions)

**Notes for Sprint 3**:
- (anything that came up during Sprint 2 that changes the plan for Sprint 3)

---

## Changelog of this file

- **[Sprint 0, phase 0.1]** Initial creation.
- **[Sprint 0, phase 0.5]** Sprint 0 marked complete; retrospective added.
- **[Sprint 1, pre-start]** Sprint 1 section and retrospective template added.
- **[Sprint 1, post-merge]** Sprint 1 marked complete; retrospective added.
- **[Sprint 2, pre-start]** Sprint 2 section added with design decisions and phase breakdown.
- **[Sprint 2, phase 2.1]** `_helpers.py` module created (D2 + D5 foundations); 14 unit tests added.