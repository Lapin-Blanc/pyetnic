# Sprint 4 — Publication checklist (phases 4.3 → 4.5)

Per the hybrid plan: phases 4.1/4.2 have full recipes; the publication mechanics (4.3-4.5) are
driven by this checklist rather than rigid recipes (they are environment-dependent and partly
exploratory).

> **Key sequencing**: publish from **`main`, post-merge**, not from the feature branch. Land
> 4.1-4.4 on `refactor/sprint-4` → PR → merge → then cut the release (4.5) from `main`, so the
> `v0.1.0b1` tag points at the merge commit.

---

## Prerequisites (gather before 4.5)

- [x] `pyetnic` on PyPI is **ours** (already published at `0.0.12`) — so 4.5 is an *update*.
- [x] `pyetnic` is **free on TestPyPI** (claim it for the dry-run).
- [ ] **Regenerate a PyPI API token** scoped to the `pyetnic` project (the 0.0.12-era token may be stale).
- [ ] **Create a TestPyPI account + token** (separate credentials from PyPI).
- [ ] Choose token storage: `~/.pypirc` (`[pypi]` / `[testpypi]` sections) **or** env
      (`TWINE_USERNAME=__token__`, `TWINE_PASSWORD=pypi-…`). **Never commit tokens.**
- [ ] Install build tooling in the venv: `.venv/bin/pip install build twine` (neither is present).

---

## Phase 4.3 — CHANGELOG.md

- [ ] Create `CHANGELOG.md` (Keep a Changelog format: Added / Changed / Fixed / Removed).
- [ ] The `0.1.0b1` entry covers the **whole `0.0.12` → `0.1.0` delta** (Sprints 0→4 — `0.0.12` is
      the pre-refactor baseline). Emphasize what a user sees:
  - **Added**: strict error mode (`RAISE_ON_ERROR`), typed nomenclature Enums, typed exception
    hierarchy + code routing (4.2), `py.typed`, `[seps]`/`[excel]` extras.
  - **Changed**: `Config.ETAB_ID`/`IMPL_ID` return `int`; `_helpers` serialization.
  - **Fixed**: `typeInterventionExterieure` Enum values (4.1); zeep list|dict normalization (Q8).
  - **Removed**: `requirements.txt`, `Codes_Pays.xls`, `openpyxl` from base deps.
- [ ] Note the pre-release install: `pip install --pre pyetnic`.

## Phase 4.4 — Version bump + packaging metadata

- [ ] Bump version in **both** places: `pyproject.toml:7` **and** `pyetnic/__init__.py:27`
      (`0.0.12` → `0.1.0b1`). Consider deduplicating to one source (`dynamic = ["version"]`) later.
- [ ] `classifiers`: `Development Status :: 3 - Alpha` → `4 - Beta`.
- [ ] **Decide**: move `cryptography` from base `dependencies` into the `[seps]` extra (it is
      SEPS-only per `CLAUDE.md`) — lightens the base install — or keep it (document why).
- [ ] Enrich `[project.urls]`: add `Repository`, `Issues`, `Changelog` (only `Homepage` today).
- [ ] Verify `README.md` (484 lines) renders as the PyPI long description; check no broken local links.
- [ ] Build + check: `.venv/bin/python -m build` then `.venv/bin/twine check dist/*`.

## Phase 4.5 — Publish (from `main`, post-merge)

- [ ] TestPyPI dry-run: `twine upload --repository testpypi dist/*`.
- [ ] Verify a **clean install in a fresh venv**:
      `pip install --pre --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyetnic[seps]`
      then smoke-import and a no-network sanity call.
- [ ] Real upload: `twine upload dist/*`.
- [ ] Tag and push: `git tag v0.1.0b1 && git push origin v0.1.0b1` (tag on the `main` merge commit).
- [ ] Post-check: `pip install --pre pyetnic` from PyPI in a fresh venv.

---

## Notes

- **Irreversibility**: PyPI uploads cannot be overwritten or deleted (only *yanked*). The TestPyPI
  dry-run + `twine check` are the safety net.
- **Beta semantics**: `0.1.0b1` is a pre-release — existing `0.0.12` users are **not** auto-upgraded
  (`--pre` required). Intentional: lets the refactored library be beta-tested without disrupting them.
