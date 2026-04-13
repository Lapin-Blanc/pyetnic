# Phase 0.5 — Sprint 0 merge

## Context

Read first:

- `CLAUDE.md`
- `plan.md`
- All Sprint 0 phase files under `docs/phases/sprint-0-preparation/`

By this point:

- Phase 0.1: structure created, scripts moved, docs installed
- Phase 0.2: API surface reconciled
- Phase 0.3: regression tests in place, existing tests migrated
- Phase 0.4: CI running green on the `refactor/sprint-0` branch

This final phase of Sprint 0 closes the sprint cleanly, merges it to `main`, and prepares the branch for Sprint 1.

## Objective

Wrap up Sprint 0 with a clean git history, a merged `main`, and a ready-to-use `refactor/sprint-1` branch.

## Tasks

### 1. Review the sprint diff

```bash
git diff main...refactor/sprint-0 --stat
```

Expect to see:

- New files in `docs/`
- New files in `tests/regression/`
- Files moved from `tests/` to `tests/unit/` or `tests/integration/`
- Files moved from repo root to `examples/`
- New file `.github/workflows/tests.yml`
- New file `CLAUDE.md` at root
- New file `plan.md` at root
- `.gitignore` updated

Files that should **NOT** appear in the diff:

- Anything under `pyetnic/` (no code changes in Sprint 0)
- `pyproject.toml` (except possibly the Python version bump from phase 0.4)

If you see unexpected changes to `pyetnic/`, stop and investigate. Sprint 0 is scaffolding-only — any code change is a bug.

### 2. Review commit history

```bash
git log main..refactor/sprint-0 --oneline
```

Expect roughly 5 commits (one per phase). If the history is messy (many fixup commits, WIP commits), clean it up:

```bash
git rebase -i main
# Squash fixups into their parent commits
# Keep one commit per phase
```

Target: one commit per phase, clearly labeled:

```
refactor(sprint-0): phase 0.1 — structure setup
refactor(sprint-0): phase 0.2 — backwards compat policy review
refactor(sprint-0): phase 0.3 — regression test suite
refactor(sprint-0): phase 0.4 — CI setup
refactor(sprint-0): phase 0.5 — sprint merge (will be created by this phase)
```

### 3. Run all tests one last time

```bash
# Full local suite
pytest tests/regression/ tests/unit/ -v

# If credentials are configured, also:
pytest tests/integration/eprom/ -v
```

All must pass. If integration tests fail and you believe the failure is pre-existing (not caused by Sprint 0 changes), document it in `plan.md` under "Known issues" before proceeding. Sprint 0 does not touch code, so any code-level failure is pre-existing and should be flagged but not block the merge.

### 4. Update `plan.md`

Mark Sprint 0 as complete at the top of the file:

```markdown
## Global progress

- [x] **Sprint 0** — Preparation (structure, regression tests, CI)
- [ ] **Sprint 1** — Robustness (D1, D3, Q1, Q2, H3, H1)
- ...
```

Add a "Sprint 0 retrospective" section at the bottom:

```markdown
## Sprint 0 retrospective

Completed on: YYYY-MM-DD

**What went well**:
- (fill in)

**What took longer than expected**:
- (fill in)

**Surprises / discoveries**:
- (fill in)

**Metrics**:
- Lines added: (git diff stat)
- Tests added: (count in tests/regression/)
- CI runtime: (from GitHub Actions)

**Notes for Sprint 1**:
- (anything that came up during Sprint 0 that changes the plan for Sprint 1)
```

### 5. Open a PR from `refactor/sprint-0` to `main`

Use the GitHub CLI or web UI:

```bash
gh pr create \
  --base main \
  --head refactor/sprint-0 \
  --title "Sprint 0 — Preparation" \
  --body-file - <<EOF
This PR wraps up Sprint 0 of the pyetnic refactoring plan.

## What's in this PR

No code changes under \`pyetnic/\`. This sprint is pure scaffolding:

- New documentation under \`docs/\`: AUDIT, BACKWARDS_COMPAT, PUBLIC_API_SURFACE, SPEC, phase prompts
- New short \`CLAUDE.md\` at repo root (the old 413-line \`.claude/CLAUDE.md\` is kept as-is pending Sprint 3 cleanup)
- New \`plan.md\` tracking refactoring progress
- Regression test suite under \`tests/regression/\` covering all stable API symbols
- Existing tests migrated to \`tests/unit/\` and \`tests/integration/eprom/\`
- One-off scripts moved from repo root to \`examples/\`
- GitHub Actions CI running regression + unit tests on Python 3.10-3.13

## Validation

- [x] CI green on all Python versions
- [x] Regression tests cover every stable symbol in \`PUBLIC_API_SURFACE.md\`
- [x] No changes to \`pyetnic/\` code
- [x] \`examples/\` scripts still runnable (tested manually)

## Next

Sprint 1 — Robustness. Phase prompts will be generated after this PR is merged.
EOF
```

### 6. Self-review and merge

Go through the PR diff one more time in the GitHub UI. Look for:

- Accidental changes to code files
- Typos in documentation
- Inconsistencies between documents (e.g., SPEC.md saying one thing, CLAUDE.md another)
- Missing `.gitkeep` files in empty directories
- `.env` or other secrets accidentally committed

When satisfied, merge with "Merge commit" strategy (not squash — we want to keep the per-phase commit history):

```bash
gh pr merge --merge
```

### 7. Create `refactor/sprint-1` branch

```bash
git checkout main
git pull
git checkout -b refactor/sprint-1
git push -u origin refactor/sprint-1
```

### 8. Update `plan.md` on the new branch

At the top of `plan.md`, update:

```markdown
> **Current sprint**: Sprint 1 — Robustness
> **Current branch**: refactor/sprint-1
```

Commit this update:

```bash
git add plan.md
git commit -m "chore: start sprint 1"
git push
```

This is the only commit on `refactor/sprint-1` until Sprint 1 phase 1.1 begins. It serves as the branching point.

## Constraints

- **Do not start Sprint 1 work in this phase.** The objective is to close Sprint 0 cleanly, not to begin the next one.
- **Do not force-push `main`.** If the PR can't be merged for any reason, investigate and fix, don't bypass.
- **Do not delete the `refactor/sprint-0` branch** immediately after merge — keep it for a week or two in case a post-mortem review is needed.

## Validation

Before completing, verify:

- [ ] `main` contains all Sprint 0 changes (`git log main --oneline | head -10` shows the merge commit)
- [ ] CI is green on `main` after the merge
- [ ] `refactor/sprint-1` branch exists on origin and is checked out locally
- [ ] `plan.md` on `refactor/sprint-1` shows Sprint 0 as complete and Sprint 1 as current
- [ ] The retrospective section in `plan.md` is filled in (even briefly)

## Next

Sprint 1 begins. The phase prompts for Sprint 1 will be produced in a separate atelier session with the user, once this sprint's retrospective is available to inform the planning.

**Do not start Sprint 1 phases without the phase prompts.** Stop here and report completion.
