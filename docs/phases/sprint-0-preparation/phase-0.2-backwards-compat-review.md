# Phase 0.2 — Backwards compatibility policy review

## Context

Read first:

- `CLAUDE.md`
- `docs/BACKWARDS_COMPAT.md`
- `docs/PUBLIC_API_SURFACE.md`
- `plan.md`

This phase is a light validation/review phase. The main documents (`BACKWARDS_COMPAT.md` and `PUBLIC_API_SURFACE.md`) were installed in phase 0.1. This phase ensures they are accurate and internally consistent before we start writing regression tests against them in phase 0.3.

## Objective

Verify the `PUBLIC_API_SURFACE.md` classification against the actual exports of `pyetnic.eprom` and `pyetnic.seps`, and reconcile any discrepancies.

## Tasks

### 1. Enumerate actual exports

Run a Python introspection to list all names currently exported by the public namespaces. Do this WITHOUT importing the package normally — use `ast` parsing to avoid triggering SOAP client initialization:

```python
import ast
from pathlib import Path

def extract_all(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        ]
    return []

eprom_all = extract_all(Path("pyetnic/eprom/__init__.py"))
seps_all = extract_all(Path("pyetnic/seps/__init__.py"))
```

Alternatively use grep:

```bash
grep -A 200 '__all__' pyetnic/eprom/__init__.py
grep -A 200 '__all__' pyetnic/seps/__init__.py
```

### 2. Cross-reference with PUBLIC_API_SURFACE.md

For each exported name, verify it appears in `PUBLIC_API_SURFACE.md` with a classification (stable or construction). Flag any discrepancies:

- **Missing from surface doc**: exported but not classified → must be added
- **In surface doc but not exported**: listed but code doesn't export → either a typo or the doc is ahead of reality
- **Misclassified**: e.g. a function is listed as stable but its docstring says "experimental"

Produce a report in a temporary file `/tmp/api_surface_report.md` listing any discrepancies found. If there are none, the report should state "No discrepancies found."

### 3. Reconcile

If discrepancies are found, update `docs/PUBLIC_API_SURFACE.md` to match reality. When in doubt:

- An export that exists in code but isn't documented → classify as **construction** (safer default)
- A symbol listed as stable but not actually exported → remove from the doc

Do NOT modify `pyetnic/eprom/__init__.py` or `pyetnic/seps/__init__.py` in this phase. Any drift between the code and the doc is resolved on the doc side only.

### 4. Validate internal consistency of BACKWARDS_COMPAT.md

Read `docs/BACKWARDS_COMPAT.md` end to end. Check that:

- All rules are concrete and testable
- The deprecation process is clear and has a concrete example
- The version bumping rules are consistent with the target (0.0.12 → 0.1.0)

If anything is unclear or inconsistent, add a clarifying paragraph. Do not rewrite the document — just fix what's broken.

## Constraints

- **Do not modify any Python code.**
- **Do not run any ETNIC calls** (no network).
- Any reconciliation happens on the documentation side, not the code side.

## Validation

Before completing, verify:

- [ ] `/tmp/api_surface_report.md` exists and is readable
- [ ] If discrepancies were found, `docs/PUBLIC_API_SURFACE.md` has been updated and the report notes the resolutions
- [ ] `docs/BACKWARDS_COMPAT.md` is internally consistent
- [ ] No code files have been modified (`git diff pyetnic/` is empty)

## Next

Update `plan.md`: mark Phase 0.2 as complete. Commit with message:

```
refactor(sprint-0): phase 0.2 — backwards compat policy review

- Cross-reference PUBLIC_API_SURFACE.md with actual __all__ exports
- Reconcile discrepancies (doc side only)
- Validate BACKWARDS_COMPAT.md internal consistency
```

Include the content of `/tmp/api_surface_report.md` in the commit message body if non-trivial.

Next phase: **Phase 0.3 — Regression tests**.
