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
- [x] **Sprint 3** — Quality and hygiene (H2, H5, H8, H11, Q8, Q5, Q6, Q3, Q7) _(completed 2026-06-01)_
- [x] **Sprint 4** — Publication (correctness fixes, CHANGELOG, bump, PyPI) _(completed 2026-06-02 — `0.1.0b1` live on PyPI)_

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

**Empirically resolved (2026-06-01) — `typeInterventionExterieure` Enum is wrong:**
- A live write/echo probe against `ws-tq.etnic.be` (create→read→delete, `/tmp/probe_tie.py`) is
  decisive: `typeInterventionExterieure="Convention"` (current Enum value) is **rejected with code
  `30004`** ("Le type d'intervention extérieure est incorrect"); `"C"` is **accepted and echoed back**.
  ETNIC wants the single-letter code, not the long label. The v7 manual was right; the H9 Enum is wrong.
- Authoritative full nomenclature: `specs/02_formation_organisation_v7.md` §"Valeurs de
  typeInterventionExterieure" (validated 2025-06-10): 13 active single-letter codes
  (A,B,C,D,E,F,I,J,K,P,Q,U,V) + 2 removed (R,S). All 13 current Enum members keep their *names*
  but need their *values* swapped from labels to letters (e.g. `CONVENTION = "C"`, `AGENCE_QUALITE = "Q"`).
- **Not a real breaking change**: the old label values never worked against ETNIC, and we are pre-release
  (0.0.12). Fixing before 0.1.0 avoids shipping a broken Enum in the first public release.
- Also fix the now-falsified `nomenclatures.py` docstring ("these labels are what ETNIC expects verbatim").
- **Bonus discovery**: code `30004` was masked by the generic "response was empty or success=False"
  message — concrete evidence for the error-mapping phase (Q-A). The v7 spec also catalogues the full
  Organisation error set (20005-20038, 30001-30009, 00009/00025/00999) incl. `20025`/`20016`/`20034`.

**Latent bugs (backlog / fold into the relevant phase):**
- `lister_formations_organisables` passes a `dict` where `FormationsListeResult.messages` is typed `List[str]` (`formations_liste.py`).
- `creer/modifier_organisation` still build dicts with `None` values (never migrated to `to_soap_dict` — out of the original D2 scope; latent partial-update risk).
- `Doc2ActiviteEnseignementLine` read-field order diverges from the XSD and has misleading `=0` defaults on required fields (positional-construction hazard).
- Common_v2 (Organisation v7) puts `requestId`/`transactionId` as XML attributes; `extract_error_info` reads `header['requestId']` only — `request_id` may always be `None` for that service. To test.

### Open questions

- **Error-mapping phase**: where to wire the ~60 specs-catalogued error codes into
  `map_etnic_error_code_to_class` — a Sprint 3 phase 3.6 (reopens a closed, hygiene-themed sprint),
  a dedicated pre-0.1.0 mini-sprint, or deferred post-0.1.0 (the enrichment is non-breaking)?
  Reinforced by the probe: code `30004` is currently masked behind a generic message.
- **`typeInterventionExterieure`**: ~~resolve labels-vs-letters empirically~~ **RESOLVED 2026-06-01**
  (single-letter codes; see Findings above). Remaining decision: schedule the Enum value fix —
  bundle it with the error-mapping work in a pre-0.1.0 correctness phase, or its own small fix.

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

Completed on: 2026-06-01

**What went well**:
- All 9 targeted defects closed across 5 phases (H2, H5, H8, H11, Q8, Q5, Q6, Q3, Q7).
  One-commit-per-phase discipline held for the 4th sprint running; CI green history intact.
- Phase 3.3 (Q8): the empirical-TDD loop paid off — single-element fixtures written first,
  confirmed failing on pre-migration code, then migrated. `_as_list()` unified 11 scattered
  zeep list|dict sites behind one helper and incidentally covered the latent
  `lister_formations_organisables` bug.
- Phase 3.1 was net-negative (+120/-431): the 413-line `.claude/CLAUDE.md` was deleted only
  after an adversarial completeness check confirmed its content survived in `docs/`.
- The 2026-05-31 codebase+specs audit (unplanned) caught real issues — the 2-of-~60 error-code
  mapping gap, `typeInterventionExterieure` labels-vs-letters, and four latent bugs — and fed
  the Open questions cleanly instead of letting them rot.
- Conversation segmentation (A: 3.1+3.2 docs/files, B: 3.3 alone, C: 3.4+3.5 soap_client/loggers)
  kept context clean; `/clear` between segments worked as intended.

**What took longer than expected**:
- The 2026-05-31 audit was out-of-plan scope: verifying the documented plan against the actual
  code and cross-referencing `specs/` took real time, but surfaced the Open questions now driving
  the Sprint 3→4 transition.
- Phase 3.4 (Q6): `serialize_object` had to be hoisted from a local to a module-level import
  purely to make it patchable — a test-seam constraint discovered mid-phase, not anticipated.

**Surprises / discoveries**:
- D2 was never applied to `creer/modifier_organisation` — they still serialize `None` fields
  (out of the original D2 scope; now a tracked latent partial-update risk).
- `map_etnic_error_code_to_class` maps only 2 codes (20102, 00009) while `specs/` catalogues ~60
  across 4 services, and `EtnicValidationError` exists but is never routed — high-value phase candidate.
- `typeInterventionExterieure`: the code Enum uses long labels (`"Convention"`), the v7 PDF manual
  single letters (`"C"`); the XSD is a free `xs:string`, so neither is contract-validated.
- Further latent bugs logged: `formations_liste` dict-where-`List[str]`, `Doc2` read-field order vs
  XSD, Common_v2 `requestId` as an XML attribute (`extract_error_info` may always return `None`).
- `specs/` (+2574) and `docs/phases/` (+1414) reference material lives on the branch and inflates
  the raw diff ~6×; the real sprint footprint is much smaller.

**Metrics**:
- Commits: 8 (5 phases 3.1–3.5 + 3 prep: phase-prompts, SOURCES.md, specs/ reference).
- Diff (excluding `specs/`): 29 files, +2182 / -616 — of which ~+1414 is phase-prompt scaffolding
  under `docs/phases/`; the core sprint work is ≈ +768 / -616 (net-negative, as befits a hygiene
  sprint). Full tree including the `specs/` v2 reference is +4756 / -616 — to be rationalized post-merge.
- Tests: 177 → 190 (+13: phase 3.3 +9 via `_as_list` fixtures, phase 3.4 +4 soap_client unit).
- Total local suite: 190 passed in ~0.26 s.
- CI runtime: pending first push (not yet run on this branch).

**Notes for Sprint 4**:
- Rationalize the `specs/` and `docs/phases/` reference material so it stops inflating the diff
  (decision deferred to post-publication, per the Sprint 3 retro discussion).
- Both Open questions resolved in the transition: the `typeInterventionExterieure` Enum fix and the
  error-code mapping land as Sprint 4 phases 4.1 / 4.2, before the version bump.
- CI confirmed green on the 3.10–3.13 matrix at push; PR #5 merged to main (merge commit, no squash).
- Latent-bug backlog (`formations_liste`, `creer/modifier_organisation` None-serialization, `Doc2`
  field order, Common_v2 `requestId`) to triage into Sprint 4 or a 0.1.x backlog.

---

## Sprint 4 — Publication

**Goal**: Make the public contract correct, then ship `0.1.0b1` (beta) to PyPI.

**Branch**: `refactor/sprint-4`

**Scope**: the two correctness fixes surfaced by the 2026-05-31 audit + the 2026-06-01 empirical
probe (`typeInterventionExterieure` Enum, error-code mapping), then the publication mechanics
(CHANGELOG, version bump, packaging, PyPI).

**Key design decisions** (Atelier Analyse, Sprint 3 → Sprint 4 transition, 2026-06-01):
- **Version scheme**: `0.0.12` → `0.1.0b1` (PEP 440 beta), not `0.1.0` + Beta classifier only.
- **4.2 scope**: wire the full ~60-code catalogue now (red→green), not a minimal subset — the first
  public release is the right moment to stabilize the exception hierarchy (it is public contract).
- **PyPI**: TestPyPI dry-run (verify a clean install) before the real PyPI upload — safety net.
- **Correctness before publication**: 4.1 and 4.2 land before the version bump (4.4).

### Phases

- [x] **Phase 4.1** — Fix `typeInterventionExterieure` Enum (correctness) _(completed 2026-06-01)_
  - Swapped the 13 Enum values from long labels to single-letter codes
    (A, B, C, D, E, F, I, J, K, P, Q, U, V) per `specs/02_formation_organisation_v7.md`
    §"Valeurs de typeInterventionExterieure" (validated 2025-06-10); member names unchanged
  - Fixed the falsified module + class docstrings (dropped "labels are what ETNIC expects verbatim";
    documented the removed R/S codes and the legacy-read behaviour)
  - `TYPES_INTERVENTION_EXTERIEURE` auto-derives the letters (verified, not hand-edited)
  - Updated 3 `test_nomenclatures.py` assertions to `"C"` (red→green); renamed the now-misleading
    `test_enum_value_is_verbatim_string`; added a `test_values_are_the_exact_letter_codes` drift guard
    pinning the full name→letter mapping. 190 → 191 tests green
  - Integration-probe promotion (optional step 5) skipped — empirical basis already established
  - Empirical basis: live dev-server probe — `"Convention"` → `30004`, `"C"` accepted (Sprint 3 Findings)

- [x] **Phase 4.2** — Error-code mapping enrichment (correctness) _(completed 2026-06-01)_
  - Added two exception classes (`EtnicAlreadyApprovedError` 1530/1545, `EtnicConcurrencyError` 00011),
    exported from the top-level + `eprom` namespaces (4.2a)
  - Replaced the 2-code if-chain with a table-driven `map_etnic_error_code_to_class` wiring the full
    `specs/00_REGISTRE.md` §4 catalogue: discrete dict + inclusive numeric ranges (4004-4012,
    1527-1528, 1598-1604, 20015-20036, 30016-30017). `EtnicValidationError` now routed (30001/30002/
    30004/30005/30007/30008/30009 + 20xxx, 1113/1114, 2106/2118); `EtnicDocumentNotAccessibleError`
    extended to 30003/30006; 00025 (security) and 00999 (SQL) deliberately left on the base class (4.2b)
  - Unmasked the real ETNIC message: `signal_business_error` auto-builds `"ETNIC error {code}:
    {description}"`; the four parse helpers + `supprimer_organisation` dropped their static `message=`.
    `30004` now reads "ETNIC error 30004: Le type d'intervention extérieure est incorrect" (4.2c)
  - 191 → 230 tests green; `docs/PUBLIC_API_SURFACE.md` updated with the two new classes
  - Common_v2 `requestId` (step 4): investigated by reasoning (serialized v7 carries requestId as an
    XML attribute on the body root, not a SOAP header, so `extract_error_info` likely returns `None`
    there) but **not empirically confirmed** without a live v7 error response — kept as a 0.1.x backlog
    item rather than shipping an unverified speculative fix, per the recipe's "log it as backlog" rule

- [x] **Phase 4.3** — CHANGELOG.md (publication) _(completed 2026-06-02)_
  - Created `CHANGELOG.md` (Keep a Changelog 1.1.0 format: Added / Changed / Fixed / Removed /
    Deprecated), in English to match `docs/` and the standard headings; one `0.1.0b1` entry
    covering the whole `0.0.12` → `0.1.0` delta (Sprints 0→4)
  - Emphasized the public-surface changes: `TypeInterventionExterieure` letter codes (4.1),
    enriched exception hierarchy + the two new classes + ~60-code routing (4.2), opt-in strict
    mode (`strict_errors()` / `RAISE_ON_ERROR`), the 6 `(str, Enum)` nomenclatures, `py.typed`,
    the `[seps]` / `[excel]` extras, and the deprecated `SoapError` alias + flat namespace
  - Noted the pre-release install (`pip install --pre pyetnic`); added Keep a Changelog compare
    links (`v0.0.12...v0.1.0b1`) + an empty `[Unreleased]` section
  - Did **not** bump the version (that is phase 4.4); the dated `0.1.0b1` header is authored-on
    today — 4.5 adjusts if the publish slips
  - Adversarially fact-checked every entry against the source (exceptions.py, __init__.py,
    nomenclatures.py, pyproject.toml, _helpers.py, soap_client.py, config.py): all claims confirmed

- [x] **Phase 4.4** — Version bump + packaging metadata (publication) _(completed 2026-06-02)_
  - Bumped `0.0.12` → `0.1.0b1` in **both** `pyproject.toml` and `pyetnic/__init__.py`
    (dedup to `dynamic = ["version"]` deliberately deferred — "later" per the checklist)
  - `classifiers`: `Development Status :: 3 - Alpha` → `4 - Beta`
  - **Decision (asked Fabien): moved `cryptography` from base `dependencies` into `[seps]`**
    (`["xmlsec", "cryptography"]`) — it is SEPS-only (lazy-imported in `_build_x509_wsse`,
    guarded by `_x509_available`); lightens the base install, matches CLAUDE.md and the
    existing X509 error message
  - Enriched `[project.urls]`: added `Repository`, `Issues`, `Changelog` (only `Homepage` before)
  - Verified README (484 lines) renders as long_description: no relative/local links, the one
    image is an absolute GitHub CI badge, `Description-Content-Type: text/markdown`
  - Built sdist + wheel; `twine check dist/*` → both **PASSED**. Confirmed in the wheel:
    `py.typed`, 9 WSDL + 73 XSD, no `Codes_Pays.xls`; base deps = zeep/python-dotenv/requests,
    `[seps]` = xmlsec+cryptography, `[excel]` = openpyxl
  - **Not** uploaded and **not** merged (TestPyPI/PyPI = 4.5; merge before publishing)
  - Backlog note: `CHANGELOG.md` is not in the sdist (MANIFEST.in omits it); the Changelog
    Project-URL covers PyPI discoverability — consider `include CHANGELOG.md` in 4.5

- [x] **Phase 4.5** — PyPI publication (publication) _(completed 2026-06-02)_
  - Decision (asked Fabien): **did not** add `include CHANGELOG.md` to `MANIFEST.in` — the
    `Changelog` Project-URL covers PyPI discoverability; kept as a 0.1.x backlog item
  - Merged `refactor/sprint-4` → `main` via **PR #6** (merge commit `ccdb8a9`, parents `79ddad5` +
    `b0b8247`, **no squash** — consistent with PR #5); `tests.yml` green on the 3.10–3.13 matrix
    for the `pull_request` event before merging
  - Date reconciliation unneeded: published on 2026-06-02, matching the `CHANGELOG.md` header
  - Clean build from up-to-date `main`: `twine check` → both sdist + wheel **PASSED**; wheel carries
    `py.typed`, 9 WSDL + 73 XSD, no `Codes_Pays.xls`
  - **Local install rehearsal (piste A, no upload)**: installed both the wheel and the sdist with
    `[seps]` in throwaway venvs — `xmlsec` resolved as a prebuilt cp313 wheel (no compile),
    `import pyetnic` → `0.1.0b1`, `TypeInterventionExterieure.CONVENTION == "C"`, `pyetnic --help` OK
  - **Published via OIDC**: pushed annotated tag `v0.1.0b1` on `ccdb8a9` → `publish-pypi.yml`
    rebuilt in a clean room, re-ran `twine check`, and published to **prod PyPI** through Trusted
    Publishing (run `26810820326`, 37 s, green; no API token). No manual `twine upload`.
  - **Post-check**: `pip install --pre pyetnic` from PyPI in a fresh venv → `0.1.0b1`; the base
    install pulls **neither** `xmlsec` **nor** `cryptography` (confirming the 4.4 move of
    `cryptography` into `[seps]` lightened the base); smoke import + new exceptions + CLI all OK;
    `https://pypi.org/project/pyetnic/0.1.0b1/` returns HTTP 200

---

## Sprint 4 retrospective

Completed on: 2026-06-02 — **`0.1.0b1` published to PyPI.**

**What went well**:
- The sprint did what it set out to: land the two audit-surfaced correctness fixes _before_ the
  bump (4.1 Enum letter-codes, 4.2 ~60-code error routing), then ship. One-commit-per-phase and
  green-CI discipline held for the 5th sprint running.
- **Piste A paid off**: the OIDC Trusted Publishing handshake worked first try (run 37 s, no token,
  no manual `twine upload`) — the tag push was the only release action. Dropping TestPyPI in favour
  of a local fresh-venv install rehearsal (wheel _and_ sdist, with `[seps]`) caught nothing broken
  and removed a whole token/account surface.
- The pre-publish safety net stacked cleanly — `twine check` (metadata/README) + local install
  (deps/extras/import/CLI) + the post-publish `--pre` install from PyPI — so the irreversible step
  was reached with high confidence.
- The 4.4 decision to move `cryptography` into `[seps]` was empirically vindicated at post-check:
  the base `pip install --pre pyetnic` pulls neither `xmlsec` nor `cryptography`.

**What took longer than expected**:
- Nothing of note — the sprint ran to plan. The two correctness fixes (4.1/4.2) and the whole
  publication chain (merge → clean build → local install rehearsal → OIDC tag publish → post-check)
  each landed without friction, and the OIDC Trusted-Publishing handshake worked first try.

**Surprises / discoveries**:
- `xmlsec` now ships a prebuilt cp313 manylinux wheel, so the `[seps]` install needed no
  `libxml2-dev`/`libxmlsec1-dev` compile locally — the documented compile fallback was a no-op here.
- CI annotation: `actions/checkout@v4` + `actions/setup-python@v5` run on Node.js 20, deprecated
  from 2026-06-16. Non-blocking now; bump the action versions in a 0.1.x chore.
- `CHANGELOG.md` is still absent from the sdist (MANIFEST.in omits it) — decided _not_ to add it in
  4.5; the `Changelog` Project-URL covers discoverability. 0.1.x backlog.

**Metrics**:
- Phases: 5 (4.1–4.5). Commits to `main`: 11 via PR #6 (merge commit `ccdb8a9`, no squash).
- Tests: 190 → 230 (+40, all from 4.1 Enum drift-guard + 4.2 error-mapping suite). No new tests
  in the publication phases (4.3–4.5).
- Release: `0.0.12` → `0.1.0b1` (PEP 440 beta), tag `v0.1.0b1`, published via OIDC.

**Notes / backlog after publication** (not done in Sprint 4):
- Rationalize `specs/` and `docs/phases/` so they stop inflating the diff ~6×.
- Four latent bugs: `formations_liste` dict-where-`List[str]`; `creer/modifier_organisation`
  `None`-serialization; `Doc2` read-field order vs XSD; Common_v2 `requestId` as an XML attribute.
- Dedup the version to a single source (`dynamic = ["version"]`).
- Bump the deprecated Node 20 GitHub Actions; consider `include CHANGELOG.md` in MANIFEST.in.
- Default-mode flip to "raise" + `0.1.0` final / `0.2.0` planning.

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
- **[Sprint 3, post-merge]** Sprint 3 marked complete (9/9 defects); retrospective filled in. Empirically resolved `typeInterventionExterieure` via a live dev-server write/echo probe — ETNIC wants single-letter codes (`"Convention"` → `30004`, `"C"` accepted); the H9 Enum is wrong. Both the Enum value fix and the error-code mapping enrichment scheduled into Sprint 4 (phases 4.1 / 4.2, before the version bump). 190 tests green. PR #5 merged to main (merge commit `79ddad5`).
- **[Sprint 4, pre-start]** Sprint 4 section added with phase breakdown (4.1 Enum fix, 4.2 error-code mapping, 4.3 CHANGELOG, 4.4 bump to `0.1.0b1`, 4.5 PyPI). Decisions: `0.1.0b1` (PEP 440 beta), full ~60-code catalogue, TestPyPI dry-run before PyPI.
- **[Sprint 4, phase 4.1]** Corrected `TypeInterventionExterieure` Enum values from long French labels to the single-letter codes ETNIC accepts (A,B,C,D,E,F,I,J,K,P,Q,U,V); member names unchanged, `TYPES_INTERVENTION_EXTERIEURE` auto-derives. Fixed the falsified docstrings, updated 3 unit assertions to `"C"` and added a drift-guard test (190 → 191 green). Optional integration-probe promotion skipped (empirical basis already established).
- **[Sprint 4, phase 4.2]** Enriched the error-code mapping. Added `EtnicAlreadyApprovedError` (1530/1545) and `EtnicConcurrencyError` (00011); table-driven `map_etnic_error_code_to_class` wires the full `specs/00_REGISTRE.md` §4 catalogue (~60 codes: discrete dict + numeric ranges), routing `EtnicValidationError` (30xxx/20xxx, 1113/1114, 2106/2118, 4004-4012, …) and extending `EtnicDocumentNotAccessibleError` to 30003/30006; 00025/00999 stay on the base class. Unmasked the real ETNIC message (`signal_business_error` auto-builds `"ETNIC error {code}: {description}"`; static `message=` dropped from the 4 parse helpers + `supprimer_organisation`) — `30004` no longer reads "response was empty or success=False". 3 commits (4.2a/b/c), 191 → 230 green, `PUBLIC_API_SURFACE.md` updated. Common_v2 `requestId` attribute (step 4) reasoned-through but left as a 0.1.x backlog item (no live v7 error to confirm the serialized shape).
- **[Sprint 4, phase 4.3]** Created `CHANGELOG.md` (Keep a Changelog 1.1.0, English, sections Added/Changed/Fixed/Removed/Deprecated) with a single `0.1.0b1` entry spanning the whole `0.0.12` → `0.1.0` delta (Sprints 0→4). Emphasized public-surface changes: `TypeInterventionExterieure` letter codes, enriched exception hierarchy + `EtnicAlreadyApprovedError`/`EtnicConcurrencyError` + ~60-code routing, opt-in strict mode, the 6 `(str, Enum)` nomenclatures, `py.typed`, `[seps]`/`[excel]` extras, deprecated `SoapError` alias + flat namespace. Pre-release install noted (`pip install --pre`); compare links + empty `[Unreleased]` added. Version **not** bumped (phase 4.4); header dated 2026-06-02. Every entry adversarially fact-checked against the source — all claims confirmed.
- **[Sprint 4, phase 4.4]** Bumped `0.0.12` → `0.1.0b1` in both `pyproject.toml` and `pyetnic/__init__.py` (single-source dedup deferred per checklist); classifier `3 - Alpha` → `4 - Beta`. **Decision (with Fabien): moved `cryptography` from base deps to the `[seps]` extra** (`["xmlsec", "cryptography"]`) since it is SEPS-only (lazy-imported, guarded) — lighter base install. Enriched `[project.urls]` with Repository/Issues/Changelog. Verified README renders as long_description (no local links). Built sdist + wheel; `twine check dist/*` → both PASSED; wheel confirmed to carry `py.typed`, 9 WSDL + 73 XSD, no `Codes_Pays.xls`. No upload, no merge (4.5). Backlog: `CHANGELOG.md` absent from sdist (MANIFEST.in omits it).
- **[Sprint 4, phase 4.5]** **Published `0.1.0b1` to PyPI.** Decided (asked Fabien) _not_ to add `CHANGELOG.md` to the sdist (kept as backlog). Merged `refactor/sprint-4` → `main` via PR #6 (merge commit `ccdb8a9`, no squash; `tests.yml` green on `pull_request`). Clean build from `main`; `twine check` PASSED (sdist + wheel). Local install rehearsal (no upload): wheel + sdist with `[seps]` in fresh venvs — `xmlsec` resolved as a prebuilt cp313 wheel, `import pyetnic` → `0.1.0b1`, `CONVENTION == "C"`, CLI OK. Pushed annotated tag `v0.1.0b1` on `ccdb8a9` → `publish-pypi.yml` published to prod PyPI via OIDC Trusted Publishing (run `26810820326`, 37 s green, no token). Post-check: `pip install --pre pyetnic` → `0.1.0b1` (base install pulls neither `xmlsec` nor `cryptography`); project page HTTP 200.
- **[Sprint 4, post-publication]** Sprint 4 marked complete (Global progress); phase 4.5 detailed; Sprint 4 retrospective drafted (subjective sections pending Fabien). Backlog carried forward: rationalize `specs/`/`docs/phases/`, the four latent bugs, version single-source, Node 20 action bump, `CHANGELOG.md` in MANIFEST.in.
