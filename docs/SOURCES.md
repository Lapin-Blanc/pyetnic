# Information sources — how the pyetnic docs fit together

> **Purpose**: this file exists because the project accumulated several overlapping
> documents (audit, plans, briefs, specs) produced at different times by different
> "actors" (the author, Claude Code, a Claude web analysis session). Read this first
> if you are unsure where a piece of information comes from or which document to trust.

---

## The mental model: two parallel tracks

| | **Track A — Incremental refactoring** | **Track B — v2 specifications** |
|---|---|---|
| **Goal** | Improve the existing **0.0.12** code → 0.1.0 beta | Prepare a future **v2 rewrite** (clean architecture, stateful SOAP mock server) |
| **Driven by** | `docs/AUDIT.md` → `plan.md` → `docs/phases/` | `specs/` (per-service WSDL + PDF analysis sessions) |
| **Horizon** | Now (Sprints 0–4) | Later |
| **Status** | Sprints 0–2 done, Sprint 3 to start | 4/6 EPROM services specified |

The two tracks feed each other (the `specs/` content can enrich Track A — e.g. the
error-code catalogue), but they have distinct goals. Keep them mentally separate.

---

## Source map (provenance + authority)

| File / folder | Origin | Role | Authority | Freshness |
|---|---|---|---|---|
| `docs/AUDIT.md` | Initial architecture-review session | **Defines** the defects (D/Q/H ids) | 🟢 Immutable reference | OK |
| **`plan.md`** | Author + Claude Code, updated per phase | **Refactoring progress** | 🟢 **Single source of truth (Track A)** | Current (Sprint 3) |
| `docs/phases/sprint-N/*.md` | Per-phase prompt files | Step-by-step recipe for one phase | 🟡 Derived from `plan.md` | Current |
| `docs/phases/sprint-3-qualite/00-brief-input.md` | Generated 2026-04-23 as **input** to a Claude web session | The brief that produced the Sprint 3 plan + phase prompts | 🔴 Consumed scaffolding (contains some stale claims) | Archived |
| `docs/PUBLIC_API_SURFACE.md` | Sprint 0 | Stable-vs-construction API contract | 🟢 Reference | OK |
| `docs/BACKWARDS_COMPAT.md` | Sprint 0 | Backwards-compatibility policy | 🟢 Reference | OK |
| `docs/SPEC.md` | Sprint 0 | Business rules / ETNIC contracts (**target** of the H2 consolidation) | 🟡 Incomplete | To enrich (phase 3.1) |
| `CLAUDE.md` (root, 66 lines) | Sprint 0 | Pointer to `docs/` + conventions | 🟢 Current | OK |
| `specs/` | Claude web sessions 1–3 (Track B) | Exhaustive ETNIC service spec for the v2 rewrite | 🟢 Rich business reference | 4/6 services |
| `docs/SOURCES.md` | This file | Orientation map | 🟢 Meta | — |

---

## Which document answers which question

- **"What is the defect X / what does D2 mean?"** → `docs/AUDIT.md` (the defect dictionary).
- **"What is done, what is next, on which branch?"** → `plan.md` (the only progress tracker).
- **"How exactly do I implement phase 3.N?"** → `docs/phases/sprint-3-qualite/phase-3.N-*.md`.
- **"Can I rename / change this public symbol?"** → `docs/PUBLIC_API_SURFACE.md` + `docs/BACKWARDS_COMPAT.md`.
- **"What does ETNIC error code 30007 mean / what fields does this XSD have?"** → `specs/` (richest), then `docs/SPEC.md`.
- **"What are the project conventions for Claude Code?"** → `CLAUDE.md` (root). (The legacy `.claude/CLAUDE.md` was retired in Sprint 3 phase 3.1 — its content now lives in `docs/SPEC.md` and `docs/ARCHITECTURE.md`.)

---

## Business-knowledge consolidation (defect H2 — done in Sprint 3 phase 3.1)

The business knowledge used to be scattered across `.claude/CLAUDE.md`, `docs/SPEC.md`
and `specs/`. Sprint 3 phase 3.1 consolidated it: the business rules and the XSD-verification
procedure moved into `docs/SPEC.md`, the architecture decisions into `docs/ARCHITECTURE.md`,
and the legacy `.claude/CLAUDE.md` was deleted. The authoritative business-rules sources are
now `docs/SPEC.md` (for the current code) and `specs/` (the richer v2 reference).
