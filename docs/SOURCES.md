# Information sources - how the pyetnic docs fit together

pyetnic is a client of the ETNIC SOAP contracts (EPROM and SEPS). Its documentation covers
those contracts and the library built on them, nothing else: regulatory material (circulars,
allocation and staffing computations, staff codes) and school-specific reports belong to the
applications that consume pyetnic.

## Source map

| File / folder | Role | Authority |
|---|---|---|
| `README.md` | User guide (French): installation, configuration, usage, troubleshooting | Current |
| `CHANGELOG.md` | User-facing release notes (Keep a Changelog) | Current |
| `docs/PUBLIC_API_SURFACE.md` | Stable vs construction API contract | Reference |
| `docs/BACKWARDS_COMPAT.md` | Backwards-compatibility policy | Reference |
| `docs/SPEC.md` | Business rules and ETNIC contracts as implemented by the current code | Reference |
| `docs/ARCHITECTURE.md` | Architecture decisions, scope boundary, known limitations | Reference |
| `specs/` | Exhaustive per-service reference (French), built from the WSDL/XSD and the ETNIC manuals; `00_REGISTRE.md` holds the shared types and the error-code table | Richest business reference |
| `documentation/` | The official ETNIC user manuals the specs are built from. The SEPS manual is kept out of the repository (one of its examples shows an unmasked NISS): ask ETNIC for it | Primary source |
| `pyetnic/resources/` | The embedded WSDL and XSD, one folder per service | Contract |
| GitHub issues | Backlog: open defects, deferred decisions, missing services | Current |
| `CLAUDE.md` | Conventions for Claude Code sessions | Current |

## Which document answers which question

- **"What changed in the last release?"** -> `CHANGELOG.md`.
- **"Can I rename / change this public symbol?"** -> `docs/PUBLIC_API_SURFACE.md` + `docs/BACKWARDS_COMPAT.md`.
- **"What does ETNIC error code 30007 mean / what fields does this XSD have?"** -> `specs/` (richest), then `docs/SPEC.md`.
- **"Does this operation exist?"** -> the WSDL in `pyetnic/resources/` decides.
- **"What is left to do?"** -> the GitHub issues.

## History

The 0.1.0b1 refactoring was driven by an architecture audit and recorded in a per-phase
plan; the specs were built across numbered analysis sessions. Those records were retired
once consumed. Code comments and tests still cite their identifiers: audit defect ids
(`D2`, `Q4`, `H9`...), sprint and phase numbers, "session N". They resolve in the tree of
tag `refactoring-records`:

```
git show refactoring-records:docs/AUDIT.md              # defect ids D/Q/H
git show refactoring-records:plan.md                    # sprints and phases
git show refactoring-records:specs/00_SUIVI_SESSIONS.md # analysis sessions
```
