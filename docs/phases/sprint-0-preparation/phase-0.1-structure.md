# Phase 0.1 — Structure setup

## Context

You are working on **pyetnic**, a Python SOAP client for ETNIC (Belgian education sector). This is the first phase of **Sprint 0 — Preparation**, a multi-sprint refactoring effort.

Read these files first to understand the project:

- `CLAUDE.md` (root — short overview)
- `docs/AUDIT.md` (the reference audit — defect IDs are referenced in phase prompts)
- `plan.md` (refactoring progress tracker)

**Do not modify any Python code in `pyetnic/` during this phase.** This phase is pure scaffolding.

## Objective

Put the documentation structure in place, relocate one-off scripts, and extract the existing 413-line `.claude/CLAUDE.md` into a proper specification document.

## Tasks

### 1. Create the target directory structure

```
docs/
├── phases/
│   ├── sprint-0-preparation/     (already exists, contains this file)
│   ├── sprint-1-robustesse/      (empty for now)
│   ├── sprint-2-refactoring/     (empty for now)
│   ├── sprint-3-qualite/         (empty for now)
│   └── sprint-4-publication/     (empty for now)
examples/
tests/
├── regression/                    (empty for now, populated in phase 0.3)
├── unit/                          (target for existing tests)
└── integration/                   (target for existing tests)
```

Use `mkdir -p` for all directories. Add a `.gitkeep` file to empty directories so git tracks them.

### 2. Move one-off scripts to `examples/`

The following files at the repo root are one-off operational scripts, not library code:

- `extrait_profs.py`
- `print_doc2.py`
- `print_doc3.py`

Move them to `examples/` using `git mv` (to preserve history).

Create `examples/README.md` with a short paragraph explaining that these are historical operational scripts kept as usage examples. Each script should be briefly documented in one sentence. Example:

```markdown
# Examples

These are operational scripts written during development. They demonstrate real-world usage of pyetnic against live ETNIC services.

## Contents

- **`extrait_profs.py`** — extracts the list of teachers from Document 3 for a given school year.
- **`print_doc2.py`** — prints a formatted view of Document 2 (periods of teaching activity).
- **`print_doc3.py`** — prints a formatted view of Document 3 (teacher assignments).

These scripts require a valid `.env` with ETNIC credentials. Adapt `etab_id`, `num_adm_formation`, etc. to your own establishment.
```

### 3. Install the Sprint 0 documentation files

The following files should be created at the paths shown. The content for each is provided as separate deliverables (see Sprint 0 bundle):

- `docs/AUDIT.md`
- `docs/BACKWARDS_COMPAT.md`
- `docs/PUBLIC_API_SURFACE.md`
- `CLAUDE.md` (new short version, at repo root — **replaces** the current `.claude/CLAUDE.md` as the primary Claude Code instructions file)
- `plan.md` (at repo root)

**Important about `CLAUDE.md`**: the current `.claude/CLAUDE.md` is 413 lines and will be partially migrated to `docs/SPEC.md` in task 4 below. For now, install the new short `CLAUDE.md` at the repo root. **Do not delete** `.claude/CLAUDE.md` yet — it will be cleaned up in Sprint 3 phase 3.1. Both files can coexist temporarily.

### 4. Extract SPEC.md from the existing `.claude/CLAUDE.md`

Read `.claude/CLAUDE.md` (413 lines) carefully. This file contains a mix of:

- Claude Code operational instructions (what belongs in `CLAUDE.md`)
- Project specification, business rules, ETNIC workflow, implId rules, error codes, data model details (what belongs in `SPEC.md`)
- Architecture notes (what belongs in `ARCHITECTURE.md`, to be created in a later phase)

Your task is to **extract the specification content** into a new `docs/SPEC.md`. The structure of `SPEC.md` should follow roughly:

```markdown
# pyetnic — Specification

## Overview
One paragraph describing what pyetnic does, who uses it, and why.

## ETNIC Services Coverage
- EPROM services (FormationsListe, Organisation, Document 1, Document 2, Document 3)
- SEPS services (RechercheEtudiants, and construction APIs for write operations)

## Authentication
- EPROM: WSSE UsernameToken (dev and prod credentials via `.env`)
- SEPS: X509 PFX certificate (prod only)

## Business Workflow
The Doc1 → Doc2 → Doc3 approval workflow, blocking rules, statut transitions.

## Critical Business Rules
- `implId` must NEVER be included in Lire/Modifier/Supprimer requests (OrganisationReqIdCT)
- Doc 1 inaccessible if organisation is "Encodé école"
- Doc 3 requires Doc 1 AND Doc 2 approved (error 20102)
- etc.

## Data Model
High-level description of the main entities (Organisation, Formation, Document 1/2/3, Étudiant, Inscription). Refer to `pyetnic/services/models.py` for the authoritative definitions.

## Error Codes
Known ETNIC error codes and their meaning.

## Environment Configuration
Full description of the `.env` file format and Config attributes.
```

Keep the SPEC.md focused and structured. Do NOT copy the 413 lines verbatim — reorganize and deduplicate. Aim for a clean, navigable document. If some content in `.claude/CLAUDE.md` is outdated or inconsistent with the actual code, note it with a `TODO` comment.

Do NOT delete `.claude/CLAUDE.md` in this phase — it will be replaced in Sprint 3 phase 3.1.

### 5. Update `.gitignore`

Add entries for:

```
# Test credentials (never committed)
.env
.env.test
.env.test.seps

# Build artifacts
build/
dist/
*.egg-info/
```

Check if these are already present before adding.

## Constraints

- **Do not modify any file under `pyetnic/`** in this phase.
- **Do not run any ETNIC tests** (no network calls).
- **Do not delete `.claude/CLAUDE.md`** yet.
- Use `git mv` to preserve history when moving files.

## Validation

Before completing, verify:

- [ ] `tree -L 2 -I '__pycache__|*.egg-info|.git|resources'` shows the new structure with `docs/`, `examples/`, `tests/regression/`, `tests/unit/`, `tests/integration/`
- [ ] `ls examples/` shows `extrait_profs.py`, `print_doc2.py`, `print_doc3.py`, `README.md`
- [ ] `wc -l CLAUDE.md` returns less than 80
- [ ] `ls docs/` shows `AUDIT.md`, `BACKWARDS_COMPAT.md`, `PUBLIC_API_SURFACE.md`, `SPEC.md`, `phases/`
- [ ] `ls plan.md` exists
- [ ] `pytest tests/ --collect-only` runs without error (tests not yet moved, just checking nothing is broken)
- [ ] `git status` shows the changes as expected (new files, moved files, no accidental deletions)

## Next

Update `plan.md`: mark Phase 0.1 as complete, add a "Completed" timestamp line under it. Commit with message:

```
refactor(sprint-0): phase 0.1 — structure setup

- Create docs/, examples/, tests/{regression,unit,integration}/ directories
- Move one-off scripts to examples/
- Install Sprint 0 documentation (AUDIT, BACKWARDS_COMPAT, PUBLIC_API_SURFACE, plan)
- Extract SPEC.md from .claude/CLAUDE.md (kept as-is for now)
- Install new short CLAUDE.md at repo root
```

Next phase: **Phase 0.2 — Backwards compatibility policy** (formalization only, already partly done). Actually, since `BACKWARDS_COMPAT.md` and `PUBLIC_API_SURFACE.md` were installed in this phase, phase 0.2 reduces to validation. You may proceed directly to **Phase 0.3 — Regression tests**.
