# Sprint 4 — Publication checklist (phases 4.3 → 4.5)

Per the hybrid plan: phases 4.1/4.2 have full recipes; the publication mechanics (4.3-4.5) are
driven by this checklist rather than rigid recipes (they are environment-dependent and partly
exploratory).

> **Key sequencing**: publish from **`main`, post-merge**, not from the feature branch. Land
> 4.1-4.4 on `refactor/sprint-4` → PR → merge → then cut the release (4.5) from `main`, so the
> `v0.1.0b1` tag points at the merge commit.

---

## Prerequisites (gather before 4.5)

> **Publishing model (piste A)**: prod **PyPI upload is fully automated** by
> `.github/workflows/publish-pypi.yml` — it fires on a `v*` tag and authenticates with
> **OIDC Trusted Publishing** (no API token, no manual upload). The pre-publish safety net is a
> local `twine check` + a fresh-venv install of the built artifact — **no TestPyPI**.

- [x] `pyetnic` on PyPI is **ours** (already published at `0.0.12`) — so 4.5 is an *update*.
- [x] Build tooling installed in the venv (`build` 1.5.0 + `twine` 6.2.0 — done in phase 4.4).
- [x] **PyPI Trusted Publisher verified** (checked 2026-06-02): GitHub · `Lapin-Blanc/pyetnic` ·
      workflow `publish-pypi.yml` · environment `pypi`; GitHub `pypi` environment exists; no stale
      token secret. OIDC fully configured — see the OIDC check in Phase 4.5.
- [x] **No tokens to manage**: OIDC handles prod; with TestPyPI dropped there is no token to store.
      The 0.0.12-era PyPI API token (if any) can be retired.

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

## Phase 4.5 — Publish (piste A: local install rehearsal → tag → CI publishes to PyPI)

> **How prod publishing works (piste A)**: the **prod PyPI** upload is performed **by the
> workflow** when the `v0.1.0b1` tag is pushed (clean-room rebuild + OIDC). Do **not** `twine
> upload` to prod yourself — that would collide with the tag-triggered run (PyPI rejects the
> duplicate, whichever lands second). The local rehearsal below uses **no upload**.

### OIDC Trusted Publishing — verified 2026-06-02 (re-check only if the workflow/repo/PyPI config changes)

- [x] **PyPI side** — `https://pypi.org/manage/project/pyetnic/settings/publishing/`: a **GitHub**
      publisher with owner `Lapin-Blanc`, repository `pyetnic`, workflow **filename**
      `publish-pypi.yml`, environment `pypi`.
- [x] **GitHub side** — repo **Settings → Environments**: the **`pypi`** environment exists
      (matches `environment: name: pypi` in the workflow). Optional hardening (required reviewer /
      `v*`-tag restriction) not yet applied.
- [x] **No stale token** — publish step has no `with:`/`password`; `gh secret list` (repo) and
      `gh secret list --env pypi` both empty.
- [ ] Safe failure mode (for reference): if OIDC ever breaks, the publish step fails at the auth
      handshake and **nothing is uploaded** — fix the publisher registration, then re-push the tag.

### Release steps

- [ ] Merge `refactor/sprint-4` → `main` (PR), so the tag lands on the merge commit.
- [ ] From `main`: clean build — `rm -rf dist/ && .venv/bin/python -m build`, then
      `.venv/bin/twine check dist/*`.
- [ ] **Local install rehearsal (standard, no upload)** — install the built artifact in a fresh
      throwaway venv and smoke-test it:
      ```
      python -m venv /tmp/pyetnic-rc && /tmp/pyetnic-rc/bin/pip install "dist/pyetnic-0.1.0b1-py3-none-any.whl[seps]"
      /tmp/pyetnic-rc/bin/python -c "import pyetnic; print(pyetnic.__version__)"
      /tmp/pyetnic-rc/bin/pyetnic --help    # entry point
      ```
      Exercises deps + the `[seps]` extra (needs `libxml2-dev`/`libxmlsec1-dev` for `xmlsec`),
      the import, and the CLI entry point. Repeat against the `.tar.gz` sdist to also test the
      source build.
- [ ] **Tag → triggers the prod publish**: `git tag v0.1.0b1 && git push origin v0.1.0b1`
      (on the `main` merge commit). The workflow rebuilds in a clean room, re-runs `twine check`,
      and publishes to **prod PyPI** via OIDC. **No manual prod `twine upload`.**
- [ ] Watch the Actions run go green, then post-check: `pip install --pre pyetnic` from PyPI in a
      fresh venv.

---

## Notes

- **Irreversibility**: PyPI uploads cannot be overwritten or deleted (only *yanked*). The
  `twine check` + the local fresh-venv install of the built artifact are the safety net. TestPyPI
  was dropped from piste A: it rehearses a manual upload path that prod no longer uses (prod is
  CI/OIDC), `twine check` already covers metadata/README, and the local install covers
  deps/extras/import/CLI — the parts that actually break.
- **Beta semantics**: `0.1.0b1` is a pre-release — existing `0.0.12` users are **not** auto-upgraded
  (`--pre` required). Intentional: lets the refactored library be beta-tested without disrupting them.
