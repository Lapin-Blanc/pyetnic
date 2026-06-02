# Information sources — how the pyetnic docs fit together

> **Purpose**: this file exists because the project accumulated several overlapping
> documents (audit, plans, briefs, specs) produced at different times by different
> "actors" (the author, Claude Code, a Claude web analysis session). Read this first
> if you are unsure where a piece of information comes from or which document to trust.

---

## The mental model: two parallel tracks

| | **Track A — Incremental refactoring** | **Track B — v2 specifications** |
|---|---|---|
| **Goal** | Improve the existing **0.0.12** code → **0.1.0b1** beta | Prepare a future **v2 rewrite** (clean architecture, stateful SOAP mock server) |
| **Driven by** | `docs/AUDIT.md` → `plan.md` (recipes were in `docs/phases/`) | `specs/` (per-service WSDL + PDF analysis sessions) |
| **Horizon** | Done — Sprints 0–4 shipped | Now / later |
| **Status** | ✅ **Complete** — `0.1.0b1` published to PyPI (2026-06-02) | 🟢 **6/6 EPROM services specified** |

The two tracks fed each other (the `specs/` content enriched Track A — e.g. the
error-code catalogue routed in Sprint 4 phase 4.2), but they have distinct goals.
Track A is now closed; Track B is the live work going forward.

> **Note — `docs/phases/` removed.** The per-phase prompt files (Track A scaffolding for
> Sprints 0–4) were deleted once Track A shipped. They are consumed material; the full
> history remains recoverable from git if ever needed. The narrative record of what each
> phase did lives in `plan.md` (phase entries + retrospectives).

---

## Source map (provenance + authority)

| File / folder | Origin | Role | Authority | Freshness |
|---|---|---|---|---|
| `docs/AUDIT.md` | Initial architecture-review session | **Defines** the defects (D/Q/H ids) | 🟢 Immutable reference | OK |
| **`plan.md`** | Author + Claude Code, updated per phase | **Track A refactoring record** | 🟢 **Single source of truth (Track A)** | Sprints 0–4 complete |
| `CHANGELOG.md` | Sprint 4 phase 4.3 | User-facing release notes (Keep a Changelog) | 🟢 Reference | Current (`0.1.0b1`) |
| `docs/PUBLIC_API_SURFACE.md` | Sprint 0 | Stable-vs-construction API contract | 🟢 Reference | OK |
| `docs/BACKWARDS_COMPAT.md` | Sprint 0 | Backwards-compatibility policy | 🟢 Reference | OK |
| `docs/SPEC.md` | Sprint 0, enriched in phase 3.1 | Business rules / ETNIC contracts (current code) | 🟢 Reference | OK |
| `docs/ARCHITECTURE.md` | Sprint 3 phase 3.1 | Architecture decisions (layering, lazy config, strict mode) | 🟢 Reference | OK |
| `CLAUDE.md` (root) | Sprint 0 | Pointer to `docs/` + conventions | 🟢 Current | OK |
| `specs/` | Claude web sessions 1–5 (Track B) | Exhaustive ETNIC service spec for the v2 rewrite | 🟢 Rich business reference | 6/6 services |
| `docs/SOURCES.md` | This file | Orientation map | 🟢 Meta | — |

---

## Which document answers which question

- **"What is the defect X / what does D2 mean?"** → `docs/AUDIT.md` (the defect dictionary).
- **"What was done across the refactoring, in which sprint?"** → `plan.md` (the Track A record).
- **"What changed in the last release?"** → `CHANGELOG.md`.
- **"Can I rename / change this public symbol?"** → `docs/PUBLIC_API_SURFACE.md` + `docs/BACKWARDS_COMPAT.md`.
- **"What does ETNIC error code 30007 mean / what fields does this XSD have?"** → `specs/` (richest), then `docs/SPEC.md`.
- **"What are the project conventions for Claude Code?"** → `CLAUDE.md` (root).

---

## Business-knowledge consolidation (defect H2 — done in Sprint 3 phase 3.1)

The business knowledge used to be scattered across `.claude/CLAUDE.md`, `docs/SPEC.md`
and `specs/`. Sprint 3 phase 3.1 consolidated it: the business rules and the XSD-verification
procedure moved into `docs/SPEC.md`, the architecture decisions into `docs/ARCHITECTURE.md`,
and the legacy `.claude/CLAUDE.md` was deleted. The authoritative business-rules sources are
now `docs/SPEC.md` (for the current code) and `specs/` (the richer v2 reference).
