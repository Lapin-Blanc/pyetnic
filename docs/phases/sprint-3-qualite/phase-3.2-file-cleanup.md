# Phase 3.2 — File cleanup: requirements.txt, Codes_Pays.xls, py.typed (H5 + H8 + H11)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — sections **H5**, **H8**, **H11**
- `plan.md`
- `pyproject.toml` — current dependency declarations

Three small, independent file-level fixes grouped into one phase because each is trivial on its own.

## Objective

1. **H5**: Delete `requirements.txt` (pyproject.toml is the source of truth) and move `openpyxl` from main deps to an `[excel]` extra
2. **H8**: Delete `pyetnic/resources/Codes_Pays.xls` (unused binary bloating the wheel)
3. **H11**: Create `pyetnic/py.typed` marker and add it to package-data

## Tasks

### 1. H5 — Delete requirements.txt and clean up pyproject.toml deps

```bash
# Verify no CI or script references requirements.txt
grep -rn "requirements.txt" .github/ Makefile* Dockerfile* scripts/ 2>/dev/null
# Should be empty. If anything references it, update that file instead of keeping requirements.txt.

git rm requirements.txt
```

Then open `pyproject.toml` and fix the dependencies:

**Current** (main deps):
```toml
dependencies = [
    "zeep",
    "python-dotenv",
    "requests",
    "openpyxl",
    "cryptography",
]
```

**After**:
```toml
dependencies = [
    "zeep",
    "python-dotenv",
    "requests",
    "cryptography",
]

[project.optional-dependencies]
seps = ["xmlsec"]
excel = ["openpyxl"]
```

`openpyxl` is not used anywhere in the current codebase (no `import openpyxl` in `pyetnic/`). It was listed as a dependency for a future Excel export feature that hasn't been implemented yet. Moving it to an `[excel]` extra makes it available when needed (`pip install pyetnic[excel]`) without forcing every user to download it.

**Verify** no code imports openpyxl:
```bash
grep -rn "import openpyxl" pyetnic/
# Must be empty
```

### 2. H8 — Delete Codes_Pays.xls

```bash
# Verify no code references this file
grep -rn "Codes_Pays" pyetnic/ tests/
# Must be empty

git rm pyetnic/resources/Codes_Pays.xls
```

Also check `MANIFEST.in` if it exists — it may reference `*.xls` patterns. If so, remove the pattern.

Check `pyproject.toml` package-data:
```toml
[tool.setuptools.package-data]
pyetnic = [
    "resources/*/*.wsdl",
    "resources/*/xsd/*.xsd",
]
```

No `.xls` pattern here, so nothing to change. Good.

### 3. H11 — Create py.typed marker

```bash
touch pyetnic/py.typed
```

Update `pyproject.toml` package-data to include it:

```toml
[tool.setuptools.package-data]
pyetnic = [
    "py.typed",
    "resources/*/*.wsdl",
    "resources/*/xsd/*.xsd",
]
```

**Verify** the marker will be in the wheel:
```bash
pip install -e ".[seps]"
python -c "import pyetnic; import pathlib; p = pathlib.Path(pyetnic.__file__).parent / 'py.typed'; print('py.typed exists:', p.exists())"
# Should print: py.typed exists: True
```

### 4. Verify

```bash
# Files deleted
ls requirements.txt 2>/dev/null            # should fail
ls pyetnic/resources/Codes_Pays.xls 2>/dev/null  # should fail

# py.typed created
ls pyetnic/py.typed                         # should exist

# No broken imports
python -c "import pyetnic; print('OK')"

# Tests
pytest tests/regression/ tests/unit/ -v     # all green

# Optional: build test
python -m build 2>/dev/null && unzip -l dist/pyetnic-*.whl | grep py.typed
# Should show pyetnic/py.typed in the wheel
```

## Constraints

- **Do not add new dependencies.**
- **Do not modify any Python source code** (only pyproject.toml and file deletions/creations).
- **Preserve `openpyxl` availability** via the `[excel]` extra — don't remove it entirely.

## Validation

- [ ] `requirements.txt` deleted
- [ ] `pyetnic/resources/Codes_Pays.xls` deleted
- [ ] `pyetnic/py.typed` exists (empty file)
- [ ] `pyproject.toml`: `openpyxl` moved to `[excel]` extra
- [ ] `pyproject.toml`: `py.typed` in package-data
- [ ] No `import openpyxl` in `pyetnic/`
- [ ] All tests green
- [ ] CI green

## Next

Update `plan.md`: mark Phase 3.2 as complete. Commit message:

```
chore(sprint-3): phase 3.2 — file cleanup (H5 + H8 + H11)

- Delete requirements.txt (pyproject.toml is source of truth)
- Move openpyxl from main deps to [excel] optional extra
- Delete pyetnic/resources/Codes_Pays.xls (unused binary, wheel bloat)
- Create pyetnic/py.typed marker (PEP 561) and add to package-data

Closes audit defects H5, H8, H11.
```

Next phase: **Phase 3.3 — _as_list() helper and parser migration (Q8)**.
