# pyetnic — Refactoring Plan

> **Current sprint**: Sprint 3 — Quality and hygiene
> **Target version**: 0.1.0 beta (end of Sprint 4)
> **Current branch**: `refactor/sprint-3`

This document is the single source of truth for refactoring progress. It is updated by Claude Code at the end of each phase. Read it first before starting any new phase.

---

## Global progress

- [x] **Sprint 0** — Preparation (structure, regression tests, CI) _(completed 2026-04-13)_
- [x] **Sprint 1** — Robustness (D1, D3, Q1, Q2, H3, H1) _(completed 2026-04-22)_
- [x] **Sprint 2** — Structural refactoring (D2, D5, Q4, H9) _(completed 2026-04-23)_
- [ ] **Sprint 3** — Quality and hygiene (H2, H5, H8, H11, Q8, Q5, Q6, Q3, Q7)
- [ ] **Sprint 4** — Publication (CHANGELOG, bump, PyPI)

---

## Sprint 0 — Preparation

**Branch**: `refactor/sprint-0` — [x] All 5 phases completed 2026-04-13.

## Sprint 1 — Robustness

**Branch**: `refactor/sprint-1` — [x] All 6 phases completed 2026-04-22.

---

## Notes and decisions

### Decisions made in Sprint 0 discussion

- **Pydantic vs dataclasses**: stay on dataclasses for Sprints 1-4. Pydantic migration is a separate decision to be made after 0.1.0.
- **`OrganisationKey` split (D6)**: deferred to 1.0.0 (breaking change).
- **SEPS write operations**: classified as "construction" API per `PUBLIC_API_SURFACE.md`. Free to refactor without backwards compatibility constraints.
- **Git workflow**: one branch per sprint, commits per phase, PR merge at end of sprint.
- **Target version**: 0.0.12 → 0.1.0 beta at end of Sprint 4.

### Decisions made in Sprint 1 → Sprint 2 transition

- **D2 helper form**: free function `to_soap_dict()` in private module `pyetnic/services/_helpers.py`.
- **D5 helper form**: free function `organisation_request_id()` in same module (not public).
- **H9 Enums**: `(str, Enum)` base for transparent string comparison. Dataclass fields unchanged.

### Decisions made in Sprint 2 → Sprint 3 transition

- **Q7 strategy**: mechanical `f"..." → "%s", args` substitution. `pformat()` calls guarded with `isEnabledFor(DEBUG)`. No `LazyPformat` wrapper (over-engineering for 20 sites).
- **Q8 helper**: `_as_list()` goes in `_helpers.py` (not a new file).
- **H5**: delete `requirements.txt` entirely. Move `openpyxl` from main deps to `[excel]` extra.
- **H8**: delete `Codes_Pays.xls` directly (no DeprecationWarning — unused binary).
- **Q5**: SSL flag → class attribute on `SoapClientManager` (not ContextVar — process-wide flag doesn't need per-thread isolation).
- **Q3**: include as documentation-only fix in the soap_client cleanup phase.
- **H7** (lazy PEP 562): deferred post-1.0 (low impact, non-trivial risk).
- **H2**: create `docs/ARCHITECTURE.md` (60-80 lines, minimal, records existing decisions).

### Findings from codebase + specs audit (2026-05-31)

A full codebase state-audit (verifying the documented plan against the actual code) and a cross-reference of the new `specs/` business specifications (see `docs/SOURCES.md`, Piste B) surfaced items not in the original Sprint 3 brief.

**Two out-of-sprint bugfixes — already merged to `main`** (commit `3f2a195`, before this branch):
- `fix(readme)`: the SEPS Inscriptions example imported three non-existent Save symbols (`SepsDroitInscriptionSave`, `SepsAdmissionSave`, `SepsSanctionSave`) → `ImportError` on copy-paste.
- `test(regression)`: `Config._reset()` re-read the developer's on-disk `.env`, so `test_etab_id_returns_none_when_unset` passed in CI but failed locally. An autouse `block_dotenv` fixture now isolates the regression suite.

**Candidate Sprint 3 addition (high value) — error-code mapping enrichment:**
- `map_etnic_error_code_to_class` (`exceptions.py:116`) maps only 2 codes (20102, 00009). The `specs/` files catalogue ~60 codes across 4 services with labels and operation scope, and `EtnicValidationError` already exists but is never routed. Proposed new phase: wire 30001/30002/30007/1113/1114/2106/4004-4012/20015-17 → `EtnicValidationError`; 1530/1545 → new `EtnicAlreadyApprovedError`; 00011 → new `EtnicConcurrencyError`; 30003/30006 → `EtnicDocumentNotAccessibleError`. Red→green, one commit per code group. **Not yet scheduled — see Open questions.**

**Needs empirical resolution:**
- `typeInterventionExterieure`: the code's `TypeInterventionExterieure` Enum (`nomenclatures.py`) uses long French labels (`"Convention"`); the Organisation v7 PDF manual lists single-letter codes (`"C"`). The XSD is a free `xs:string`, so neither is contract-validated. One real `lire_organisation` call on an org with this field populated decides which is correct. The H9 Enum may be wrong for this field.

**Latent bugs (backlog / fold into the relevant phase):**
- `lister_formations_organisables` passes a `dict` where `FormationsListeResult.messages` is typed `List[str]` (`formations_liste.py`).
- `creer/modifier_organisation` still build dicts with `None` values (never migrated to `to_soap_dict` — out of the original D2 scope; latent partial-update risk).
- `Doc2ActiviteEnseignementLine` read-field order diverges from the XSD and has misleading `=0` defaults on required fields (positional-construction hazard).
- Common_v2 (Organisation v7) puts `requestId`/`transactionId` as XML attributes; `extract_error_info` reads `header['requestId']` only — `request_id` may always be `None` for that service. To test.

### Open questions

- **Error-mapping phase**: add a Sprint 3 phase 3.6 to wire the ~60 specs-catalogued error codes into `map_etnic_error_code_to_class`, or keep Sprint 3 scoped to the original 9 defects and defer error-mapping to its own mini-sprint? (High value, but widens Sprint 3.)
- **`typeInterventionExterieure`**: resolve labels-vs-letters empirically before any further nomenclature work touches it.

---

## Sprint 0 retrospective

Completed on: 2026-04-13

**What went well**:
- Phases 0.1 and 0.2 were quasi-mechanical thanks to the bundled documents and a clear scope.
- Phase 0.3 regression suite came together cleanly: class-level patching of `SoapClientManager.call_service` lets every singleton be intercepted without per-service plumbing.
- 4-version Python matrix on CI passed first try with no fixups.
- Zero changes to `pyetnic/` code — Sprint 0 stayed pure scaffolding.

**What took longer than expected**:
- Phase 0.3 reconciliation between SOAP response shapes and parsers.
- Test-file migration lost git similarity threshold (`git log --follow -M30%` needed).

**Metrics**:
- Lines: +4812 / -1316. Tests: 69 regression + 26 unit + 14 integration = 95 total.
- CI: ~33-37 s per Python version.

---

## Sprint 1 retrospective

Completed on: 2026-04-22

**What went well**:
- One commit per phase discipline held. CI green on every push.
- Phase 1.1 → 1.3 sequencing paid off. `ContextVar` for `RAISE_ON_ERROR` was the right choice.
- `signal_business_error()` centralized the raise/return-None decision cleanly.
- Sprint 0 regression harness did its job — default-mode contract never broken.

**What took longer than expected**:
- Phase 1.3 design iteration (plain class attr → ContextVar).
- Phase 1.5 regression fixtures needed rework for the `except Exception` removal.
- README documentation in phase 1.6.

**Metrics**:
- Commits: 8 (2 chore + 6 phases). Diff: 27 files, +2918 / -48.
- Tests: 95 → 138 (+43). Local suite: ~0.19 s.

---

## Sprint 2 — Structural refactoring

**Branch**: `refactor/sprint-2` — [x] All 6 phases completed 2026-04-23.

**Audit defects addressed**: D2, D5, Q4, H9.

### Phases

- [x] **Phase 2.1** — Create private helpers module (D2 + D5 foundations) _(completed)_
- [x] **Phase 2.2** — Migrate organisation_request_id across services (D5) _(completed)_
- [x] **Phase 2.3** — Migrate to_soap_dict in EPROM document services (D2) _(completed)_
- [x] **Phase 2.4** — Migrate to_soap_dict in SEPS write services (D2) _(completed)_
- [x] **Phase 2.5** — Config int casting for ETAB_ID / IMPL_ID (Q4) _(completed)_
- [x] **Phase 2.6** — Nomenclature Enums (H9) _(completed)_

---

## Sprint 2 retrospective

Completed on: 2026-04-23

**What went well**:
- `_helpers.py` (107 lines) cleanly centralizes `to_soap_dict()` and `organisation_request_id()`. Replaced 4 copies of `_organisation_id_dict` + 7 `asdict()` call sites.
- H9: `nomenclatures.py` promoted to top-level with 6 `(str, Enum)` classes; legacy constant preserved. Clean addition to public surface.
- Q4: `_SIMPLE_ENV_MAP` caster extension was minimal and clean — `int()` wrappers removed from callers.
- No regression test from S0/S1 was modified (only Config type change was natural).
- One commit per phase discipline maintained.

**What took longer than expected**:
- (to be filled by Fabien after Sprint 2 retrospective)

**Surprises / discoveries**:
- `nomenclatures.py` needed to be at top-level (`pyetnic/nomenclatures.py`) rather than under `services/` because both `eprom` and `seps` namespaces export from it.
- `openpyxl` is in main deps but unused — flagged for cleanup in Sprint 3 (H5).
- **(post-audit 2026-05-31)** D2 was applied to document1/2/3 + SEPS writes but **not** to `creer/modifier_organisation`, which still serialize `None` fields. See "Findings from codebase + specs audit".

**Metrics**:
- Diff: 34 files changed, +2518 / -252.
- Tests added: ~45 (test_helpers, test_nomenclatures, test_seps_write_unit, test_config, test_soap_payload_shape).
- CI: green on every push, 3.10-3.13 matrix.

**Notes for Sprint 3**:
- Strict-mode semantics are load-bearing across all EPROM services.
- `PASSWORD` exclusion from cache key needs a docstring comment (noted in Sprint 1 retro, still pending — can do in Sprint 3 alongside Q5/Q6 soap_client work).
- Default-mode switch to raise (0.2.0) NOT scheduled in Sprints 1-4.

---

## Sprint 3 — Quality and hygiene

**Goal**: Clean up documentation, remove dead files, fix parser inconsistencies, and standardize logging across the codebase.

**Branch**: `refactor/sprint-3`

**Audit defects addressed**: H2, H5, H8, H11, Q8, Q5, Q6, Q3, Q7.

**Key design decisions** (made in Atelier Analyse before sprint start):
- **Q7**: mechanical f-string → `%s` substitution. `pformat()` guarded with `isEnabledFor(DEBUG)`. No LazyPformat wrapper.
- **Q8**: `_as_list()` helper in `_helpers.py` (existing private module, no new file).
- **H5**: delete `requirements.txt`. Move `openpyxl` to `[excel]` extra.
- **H8**: delete `Codes_Pays.xls` directly (unused, no deprecation period).
- **Q5**: SSL flag → class attribute on `SoapClientManager` (not ContextVar).
- **Q3**: documentation-only fix (docstring on `verify()` no-op), bundled with Q5/Q6.
- **H2**: create `docs/ARCHITECTURE.md` (60-80 lines). Delete `.claude/CLAUDE.md`.
- **H7**: deferred post-1.0 (lazy PEP 562).

### Phases

- [x] **Phase 3.1** — Split .claude/CLAUDE.md, create ARCHITECTURE.md (H2) _(completed 2026-05-31)_
  - Created docs/ARCHITECTURE.md (77 lines); migrated the XSD-verification procedure to docs/SPEC.md
  - Deleted .claude/CLAUDE.md (413 lines); content confirmed present in docs/ by an adversarial completeness check
  - Fixed two stale doc facts: Python floor 3.8 → 3.10; removed 3 non-existent SEPS inscription Save types from SPEC.md
  - Updated docs/SOURCES.md to reflect the consolidation
  - No code changes; 177 tests green
  - **Conversation A** (with phase 3.2)

- [x] **Phase 3.2** — File cleanup (H5 + H8 + H11) _(completed 2026-05-31)_
  - Deleted requirements.txt; moved openpyxl from main deps to the [excel] extra
  - Deleted pyetnic/resources/Codes_Pays.xls (83 KB unused binary)
  - Created pyetnic/py.typed (PEP 561); added to package-data and MANIFEST.in
  - No Python source changes; 177 tests green
  - **Conversation A** (with phase 3.1)

- [x] **Phase 3.3** — _as_list() helper and parser migration (Q8) _(completed 2026-05-31)_
  - Added `_as_list()` to `_helpers.py` (None → [], dict → [dict], list → list)
  - Migrated 11 collection-iteration sites: document1 (1), document2 (3), document3 (2),
    formations_liste (3 — incl. `lister_formations_organisables`, same latent bug), seps (1),
    inscriptions (1). Dropped the now-redundant `, []` getter defaults.
  - Replaced the inline `isinstance(.., dict)` result guards in seps.py and inscriptions.py
  - Added 5 unit tests (`TestAsList`) + 4 regression tests with single-element fixtures
    (document1/2/3 + lister_formations); empirically confirmed they fail on the pre-migration code
  - **Out of scope (deliberate):** the `isinstance(errors, list)` error-message guards in
    seps.py/inscriptions.py (error path, not result parsing) and the two
    `messages=...get('messages', [])` defaults in formations_liste.py (separate latent bug —
    dict-where-`List[str]`-expected, tracked in the audit findings)
  - 177 → 186 tests green
  - **Conversation B** (alone — touches many parser files)

- [x] **Phase 3.4** — soap_client.py cleanup (Q5 + Q6 + Q3) _(completed 2026-06-01)_
  - Q5: moved `_ssl_warnings_suppressed` from module global to a `SoapClientManager`
    class attribute; `reset_cache()` now resets it too
  - Q6: log `request_id` on success at DEBUG level; rewrote the error-path log to `%s`
    formatting; hoisted `serialize_object` to a module-level import (needed to patch it)
  - Q3: documented `_EtnicBinarySignature.verify()` rationale (TLS makes the WS-Security
    response signature check redundant)
  - Added `tests/unit/test_soap_client_unit.py` (4 unit tests)
  - 186 → 190 tests green
  - **Conversation C** (with phase 3.5)

- [x] **Phase 3.5** — Logger formatting: f-strings → lazy %s (Q7) _(completed 2026-06-01)_
  - Converted all 20 f-string logger calls to `%s` lazy formatting across soap_client,
    organisation, document1/2/3 and formations_liste
  - Wrapped the 7 `pformat()` debug calls in `if logger.isEnabledFor(logging.DEBUG)` guards
  - Removed the unused `pprint` import in formations_liste.py (kept `pformat`)
  - No new tests (cosmetic); 190 tests still green; smoke-tested log interpolation
  - **Conversation C** (with phase 3.4)

### Conversation segmentation

- **Conversation A** — Phases 3.1 + 3.2 (docs and files, zero code logic)
- **Conversation B** — Phase 3.3 alone (Q8 parser migration, many files)
- **Conversation C** — Phases 3.4 + 3.5 (soap_client + loggers, related cleanup)

---

## Sprint 3 retrospective

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

**Notes for Sprint 4**:
- (anything that came up during Sprint 3 that changes the plan for Sprint 4)

---

## Changelog of this file

- **[Sprint 0, phase 0.1]** Initial creation.
- **[Sprint 0, phase 0.5]** Sprint 0 marked complete; retrospective added.
- **[Sprint 1, pre-start]** Sprint 1 section added.
- **[Sprint 1, post-merge]** Sprint 1 marked complete; retrospective added.
- **[Sprint 2, pre-start]** Sprint 2 section added.
- **[Sprint 2, post-merge]** Sprint 2 marked complete; retrospective added.
- **[Sprint 3, pre-start]** Sprint 3 section added with design decisions and phase breakdown.
- **[2026-05-31]** Saved Sprint 3 plan to disk; added "Findings from codebase + specs audit" and two new Open questions; recorded two out-of-sprint bugfixes merged to main. See `docs/SOURCES.md`.
- **[Sprint 3, phase 3.1]** Created `docs/ARCHITECTURE.md`; migrated XSD procedure into `docs/SPEC.md`; deleted `.claude/CLAUDE.md` (413 lines, content preserved in docs/). Fixed two stale doc facts. H2 closed.
- **[Sprint 3, phase 3.2]** Deleted `requirements.txt` and `Codes_Pays.xls`; moved `openpyxl` to `[excel]` extra; added `pyetnic/py.typed` (PEP 561) to package-data and MANIFEST.in. H5, H8, H11 closed.
- **[Sprint 3, phase 3.3]** Added `_as_list()` to `_helpers.py`; migrated 11 zeep collection-iteration sites (document1/2/3, formations_liste, seps, inscriptions) and replaced the inline `isinstance(dict)` result guards. Added 5 unit + 4 single-element regression tests (177 → 186). Q8 closed.
- **[Sprint 3, phase 3.4]** Moved `_ssl_warnings_suppressed` to a `SoapClientManager` class attribute reset by `reset_cache()` (Q5); logged `request_id` on success + rewrote the error log to `%s` (Q6); documented `_EtnicBinarySignature.verify()` (Q3). Added `test_soap_client_unit.py` (190 tests). Q5, Q6, Q3 closed.
- **[Sprint 3, phase 3.5]** Converted all 20 f-string logger calls to lazy `%s`; guarded the 7 `pformat()` debug calls with `isEnabledFor(DEBUG)`; dropped the unused `pprint` import. Q7 closed — **all 9 Sprint 3 defects addressed** (H2, H5, H8, H11, Q8, Q5, Q6, Q3, Q7). Retrospective + PR/merge pending in the transition conversation.
