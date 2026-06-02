# Sprint 4 — Publication checklist (phases 4.3 → 4.5)

Per the hybrid plan: phases 4.1/4.2 have full recipes; the publication mechanics (4.3-4.5) are
driven by this checklist rather than rigid recipes (they are environment-dependent and partly
exploratory).

> **Key sequencing**: publish from **`main`, post-merge**, not from the feature branch. Land
> 4.1-4.4 on `refactor/sprint-4` → PR → merge → then cut the release (4.5) from `main`, so the
> `v0.1.0b1` tag points at the merge commit.

---

## Prerequisites (gather before 4.5)

> **Publishing model (piste A)**: prod **PyPI upload is automated** by
> `.github/workflows/publish-pypi.yml` — it fires on a `v*` tag and authenticates with
> **OIDC Trusted Publishing** (no API token). We keep that for prod; the **TestPyPI dry-run is
> manual** (local `twine`). See the OIDC check in Phase 4.5 before tagging.

- [x] `pyetnic` on PyPI is **ours** (already published at `0.0.12`) — so 4.5 is an *update*.
- [x] `pyetnic` is **free on TestPyPI** (claim it for the dry-run).
- [x] Build tooling installed in the venv (`build` 1.5.0 + `twine` 6.2.0 — done in phase 4.4).
- [ ] **Verify the PyPI Trusted Publisher** is registered for this repo (see "OIDC check" in
      Phase 4.5). With OIDC in place a prod **PyPI API token is NOT needed** — the 0.0.12-era
      token can be retired rather than regenerated.
- [ ] **Create a TestPyPI account + token** (still required: the TestPyPI dry-run uses manual twine).
- [ ] Store the TestPyPI token: `~/.pypirc` (`[testpypi]` section) **or** env
      (`TWINE_USERNAME=__token__`, `TWINE_PASSWORD=pypi-…`). **Never commit tokens.**

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

## Phase 4.5 — Publish (piste A: manual TestPyPI dry-run → tag → CI publishes to PyPI)

> **Split of responsibility (piste A)**: the **TestPyPI** upload is **manual** (local twine);
> the **prod PyPI** upload is performed **by the workflow** when the `v0.1.0b1` tag is pushed.
> Do **not** `twine upload` to prod yourself — that would collide with the tag-triggered run
> (PyPI rejects the duplicate, whichever lands second).

### OIDC Trusted Publishing — verify once before tagging

- [ ] **PyPI side** — open `https://pypi.org/manage/project/pyetnic/settings/publishing/`. Under
      "Trusted Publishers", confirm a **GitHub** publisher with **exactly**: owner `Lapin-Blanc`,
      repository `pyetnic`, workflow **filename** `publish-pypi.yml` (not the workflow's `name:`),
      environment `pypi`. If absent → "Add a new publisher" with those four fields.
- [ ] **GitHub side** — repo **Settings → Environments**: an environment named **`pypi`** exists
      (case-sensitive; must match `environment: name: pypi` in the workflow). Optional hardening:
      required reviewer and/or restrict deployments to the `v*` tag pattern.
- [ ] Confirm **no stale `PYPI_API_TOKEN` secret** is wired into the publish step — OIDC needs none.
- [ ] Safe failure mode: if OIDC is misconfigured the publish step fails at the auth handshake and
      **nothing is uploaded** — fix the publisher registration, then re-run the job / re-push the tag.

### Release steps

- [ ] Merge `refactor/sprint-4` → `main` (PR), so the tag lands on the merge commit.
- [ ] From `main`: clean build — `rm -rf dist/ && .venv/bin/python -m build`, then
      `.venv/bin/twine check dist/*`.
- [ ] **TestPyPI dry-run (manual)**: `.venv/bin/twine upload --repository testpypi dist/*`.
- [ ] Verify a **clean install in a fresh venv** from TestPyPI:
      `pip install --pre --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyetnic[seps]`
      then smoke-import and a no-network sanity call.
- [ ] **Tag → triggers the prod publish**: `git tag v0.1.0b1 && git push origin v0.1.0b1`
      (on the `main` merge commit). The workflow rebuilds in a clean room, re-runs `twine check`,
      and publishes to **prod PyPI** via OIDC. **No manual prod `twine upload`.**
- [ ] Watch the Actions run go green, then post-check: `pip install --pre pyetnic` from PyPI in a
      fresh venv.

---

## Notes

- **Irreversibility**: PyPI uploads cannot be overwritten or deleted (only *yanked*). The TestPyPI
  dry-run + `twine check` are the safety net.
- **Beta semantics**: `0.1.0b1` is a pre-release — existing `0.0.12` users are **not** auto-upgraded
  (`--pre` required). Intentional: lets the refactored library be beta-tested without disrupting them.
