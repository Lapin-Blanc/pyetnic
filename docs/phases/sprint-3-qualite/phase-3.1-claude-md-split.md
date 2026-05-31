# Phase 3.1 — Split .claude/CLAUDE.md and create ARCHITECTURE.md (H2)

## Context

Read first:

- `CLAUDE.md` (root — 66 lines, the short version)
- `.claude/CLAUDE.md` (413 lines — the legacy monolith to decompose)
- `docs/SPEC.md` (225 lines — partially extracted during Sprint 0 phase 0.1)
- `docs/AUDIT.md` — section **H2**
- `plan.md`

This is the first phase of **Sprint 3 — Quality and hygiene**. It addresses the long-standing H2 defect: `.claude/CLAUDE.md` is still 413 lines and contains a mix of Claude Code instructions, ETNIC business rules, architecture decisions, and coding conventions.

## Objective

1. Migrate all remaining specification content from `.claude/CLAUDE.md` to `docs/SPEC.md`
2. Create `docs/ARCHITECTURE.md` (referenced in root `CLAUDE.md` but doesn't exist yet)
3. Reduce `.claude/CLAUDE.md` to either a symlink to the root `CLAUDE.md` or delete it entirely
4. Verify that root `CLAUDE.md` is still under 80 lines and accurately points to all docs

## Tasks

### 1. Audit `.claude/CLAUDE.md` content

Read `.claude/CLAUDE.md` end to end. Categorize every section into one of:

| Category | Destination |
|---|---|
| What the project is, tech stack, structure | Already in root `CLAUDE.md` — verify, skip |
| Dev commands (run, test, lint, build) | Already in root `CLAUDE.md` — verify, skip |
| ETNIC business rules (implId, workflow Doc1→Doc2→Doc3, error codes, statut transitions) | `docs/SPEC.md` |
| Architecture decisions (layering, lazy config, read/save split, namespace strategy, strict mode) | `docs/ARCHITECTURE.md` (NEW) |
| Coding conventions specific to this project | Root `CLAUDE.md` if not already there |
| XSD checklist, WSDL details | `docs/SPEC.md` |
| Generic framework conventions (Django, Vue, etc.) | Not applicable to pyetnic — discard |

### 2. Enrich `docs/SPEC.md`

Take the ETNIC business rules, workflow descriptions, error codes, and XSD details from `.claude/CLAUDE.md` and merge them into `docs/SPEC.md`. The existing 225 lines are a starting point — add what's missing, don't duplicate what's already there.

Structure the enriched SPEC.md as:

```markdown
# pyetnic — Specification

## Overview
## ETNIC Services Coverage
## Authentication
  ### EPROM (UsernameToken)
  ### SEPS (X509 PFX)
## Business Workflow
  ### Organisation lifecycle
  ### Document approval workflow (Doc1 → Doc2 → Doc3)
  ### Blocking rules
## Critical Business Rules
  ### implId exclusion rule
  ### Error codes and their meaning
## Data Model
  ### Organisation and OrganisationId
  ### Documents 1, 2, 3
  ### SEPS Étudiant / Inscription
## Environment Configuration
  ### .env file format
  ### Config attributes
  ### Strict error mode
```

### 3. Create `docs/ARCHITECTURE.md`

This document records the architectural decisions that have been made across Sprints 0-2. Keep it concise (60-80 lines). Structure:

```markdown
# pyetnic — Architecture

## Layering

  config → soap_client → services → public namespaces (eprom, seps)

## Key Decisions

### Lazy Config via metaclass (Sprint 0)
One paragraph explaining why and how.

### Read/Save model split
Separate dataclasses per XSD contract direction.

### Namespace split: eprom vs seps
Different auth mechanisms, different error handling maturity.

### Strict error mode via ContextVar (Sprint 1)
Config.RAISE_ON_ERROR + strict_errors() context manager.
Why ContextVar instead of plain class attribute.

### Private helpers module (Sprint 2)
_helpers.py for to_soap_dict() and organisation_request_id().
Why free functions instead of methods on dataclasses.
Why private instead of public (D6 forward compatibility).

### Dataclasses over Pydantic (Sprint 0 decision)
Deferred to post-0.1.0.

## Not Yet Decided

### OrganisationKey split (D6) — deferred to 1.0.0
### Pydantic migration — deferred to post-0.1.0
### SEPS/EPROM exception unification — deferred
```

### 4. Delete `.claude/CLAUDE.md`

Once all content is migrated:

```bash
git rm .claude/CLAUDE.md
```

If `.claude/` becomes empty (only `settings.json` left), keep the directory — `settings.json` is needed for Claude Code permissions.

Verify that `.claude/settings.json` is still present:
```bash
ls -la .claude/
```

### 5. Verify root `CLAUDE.md`

Check that root `CLAUDE.md`:
- Is still under 80 lines (`wc -l CLAUDE.md`)
- References `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/AUDIT.md`, `docs/BACKWARDS_COMPAT.md`, `docs/PUBLIC_API_SURFACE.md`
- Has no stale references to `.claude/CLAUDE.md`

If needed, add the `docs/ARCHITECTURE.md` reference (it was already listed but the file didn't exist until now).

### 6. Verify

```bash
wc -l CLAUDE.md                    # < 80
wc -l docs/SPEC.md                 # enriched, probably 300-400 lines
wc -l docs/ARCHITECTURE.md         # 60-80 lines
ls .claude/CLAUDE.md 2>/dev/null    # should fail (deleted)
ls .claude/settings.json            # should exist
pytest tests/regression/ tests/unit/ -v   # all green (no code change)
```

## Constraints

- **No code changes** in this phase. Pure documentation.
- **Do not lose information.** Every significant piece of content in `.claude/CLAUDE.md` must end up somewhere — either SPEC.md, ARCHITECTURE.md, or confirmed already present in root CLAUDE.md.
- **Don't bloat root CLAUDE.md** beyond 80 lines. It's a signpost, not an encyclopedia.

## Validation

- [ ] `.claude/CLAUDE.md` deleted
- [ ] `.claude/settings.json` still exists
- [ ] `docs/SPEC.md` enriched with all business rules from old CLAUDE.md
- [ ] `docs/ARCHITECTURE.md` exists with architecture decisions
- [ ] Root `CLAUDE.md` under 80 lines and references all docs
- [ ] All tests still green (no code change)
- [ ] CI green

## Next

Update `plan.md`: mark Phase 3.1 as complete. Commit message:

```
docs(sprint-3): phase 3.1 — split .claude/CLAUDE.md, create ARCHITECTURE.md (H2)

- Migrate remaining business rules from .claude/CLAUDE.md to docs/SPEC.md
- Create docs/ARCHITECTURE.md documenting key architectural decisions
- Delete .claude/CLAUDE.md (413 lines → 0; content preserved in docs/)
- Root CLAUDE.md unchanged (66 lines, already points to docs/)

Closes audit defect H2.
```

Next phase: **Phase 3.2 — File cleanup (H5 + H8 + H11)**.
