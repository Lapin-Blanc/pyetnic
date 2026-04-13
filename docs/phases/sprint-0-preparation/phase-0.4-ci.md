# Phase 0.4 — CI setup

## Context

Read first:

- `CLAUDE.md`
- `plan.md`
- `docs/phases/sprint-0-preparation/phase-0.3-regression-tests.md` (the previous phase)

By this point, the regression test suite from phase 0.3 is in place. This phase wires it into GitHub Actions so that every push and every PR automatically runs the test suite.

## Objective

Create a minimal, reliable CI workflow that:

1. Runs on every push to any branch AND on every PR to `main`
2. Executes regression tests and unit tests (no integration tests, no network, no secrets)
3. Runs on a matrix of supported Python versions
4. Fails fast if any test fails
5. Reports clearly in the GitHub Actions tab

## Tasks

### 1. Create `.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches:
      - main
      - 'refactor/**'
  pull_request:
    branches:
      - main

jobs:
  test:
    name: pytest (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install system dependencies for xmlsec
        run: |
          sudo apt-get update
          sudo apt-get install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[seps]"
          pip install pytest pytest-cov

      - name: Run regression tests
        run: pytest tests/regression/ -v --tb=short

      - name: Run unit tests
        run: pytest tests/unit/ -v --tb=short

      - name: Check that no test is at the root of tests/
        run: |
          if ls tests/test_*.py 2>/dev/null | grep -q test; then
            echo "ERROR: test files found directly under tests/. They must be under tests/{regression,unit,integration}/"
            ls tests/test_*.py
            exit 1
          fi
```

**Notes on this workflow**:

- **`libxml2-dev libxmlsec1-dev`** are required for `xmlsec` Python package (SEPS X509 signing). Without these, `pip install pyetnic[seps]` fails on GitHub runners. They're standard on ubuntu-latest but need apt-get.
- **`pkg-config`** is sometimes needed for `xmlsec` to find its headers.
- **`-e ".[seps]"`** installs with the `seps` extra because the regression tests cover SEPS read paths which import from `pyetnic/seps/__init__.py`, which may pull in xmlsec-dependent code.
- **Integration tests are NOT run** — they require credentials and hit live ETNIC services. They remain manual.
- **Python 3.10 to 3.13** covers the range declared in `pyproject.toml`. Python 3.8 and 3.9 are still listed in the classifiers but consider whether to drop them (see optional task below).
- **No coverage reporting** yet — keep the workflow minimal and add coverage in Sprint 3 if desired.

### 2. Add a status badge to README.md

Insert near the top of `README.md`, right after the title:

```markdown
# pyetnic

[![Tests](https://github.com/Lapin-Blanc/pyetnic/actions/workflows/tests.yml/badge.svg)](https://github.com/Lapin-Blanc/pyetnic/actions/workflows/tests.yml)

Bibliothèque Python d'accès aux services web SOAP d'ETNIC...
```

### 3. Verify locally before pushing

Simulate the CI environment as much as possible locally:

```bash
# Clean install in a fresh venv
python -m venv /tmp/pyetnic-ci-check
source /tmp/pyetnic-ci-check/bin/activate
pip install -e ".[seps]"
pip install pytest pytest-cov

# Run the exact commands the CI will run
pytest tests/regression/ -v --tb=short
pytest tests/unit/ -v --tb=short
```

If anything fails locally, fix it before pushing. Deactivate the venv and remove it when done:

```bash
deactivate
rm -rf /tmp/pyetnic-ci-check
```

### 4. Push and verify

Push the branch and check the GitHub Actions tab:

```bash
git push origin refactor/sprint-0
```

Go to https://github.com/Lapin-Blanc/pyetnic/actions and verify:

- The workflow triggered
- All 4 Python versions pass
- No warnings about deprecated actions or missing features

If the workflow fails on CI but passed locally, the most common causes are:

- Missing system package (libxmlsec1-dev etc.) — add to the `apt-get install` step
- Python version not available (e.g., 3.13 might not be GA) — drop from matrix temporarily
- Path separator issues (unlikely since ubuntu-latest)

### Optional task: drop Python 3.8 and 3.9 from classifiers

Check `pyproject.toml`:

```toml
requires-python = ">=3.8"
classifiers = [
    ...
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    ...
]
```

Python 3.8 is EOL (October 2024) and 3.9 reaches EOL in October 2025. The CI matrix only tests 3.10+. **Decision** (confirm with user in commit message): either drop 3.8 and 3.9 from classifiers and bump `requires-python` to `>=3.10`, or keep them and add them to the CI matrix. Inconsistency between classifiers and CI is a red flag.

Recommended: drop 3.8 and 3.9. If you choose this, update:

```toml
requires-python = ">=3.10"
classifiers = [
    ...
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    ...
]
```

## Constraints

- **No secrets required** — the workflow must run on a forked PR without access to credentials.
- **No integration tests** in this workflow.
- **Don't enable auto-merge or branch protection** yet — that's user policy, not phase scope.
- **Don't add pre-commit hooks, linters, or formatters** in this phase. Keep the CI minimal. These can be added in Sprint 3 if desired.

## Validation

Before completing, verify:

- [ ] `.github/workflows/tests.yml` exists and is syntactically valid YAML
- [ ] Local verification: `pytest tests/regression/ tests/unit/` passes on a fresh venv
- [ ] Push to branch succeeds
- [ ] GitHub Actions workflow triggers within a few minutes of the push
- [ ] All matrix jobs pass (green checkmarks)
- [ ] Badge in README.md displays correctly (green, shows "passing")

If any matrix job fails, investigate before proceeding. Do not mark the phase complete with a red CI.

## Next

Update `plan.md`: mark Phase 0.4 as complete. Commit with message:

```
refactor(sprint-0): phase 0.4 — CI setup

- Add GitHub Actions workflow running regression + unit tests
- Matrix: Python 3.10 / 3.11 / 3.12 / 3.13 on ubuntu-latest
- Install libxmlsec1-dev for xmlsec dependency
- Enforce that no test file sits directly under tests/
- Add status badge to README.md
```

If you dropped 3.8 and 3.9 from classifiers, mention it in the commit body.

Next phase: **Phase 0.5 — Sprint 0 merge**.
