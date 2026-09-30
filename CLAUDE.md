# pyetnic - Claude Code Instructions

## Overview

Python client for the ETNIC SOAP web services of the Belgian adult education
("Enseignement pour adultes", formerly "promotion sociale"). Typed access to EPROM
(formations, organisations, documents 1/2/3) and SEPS (student registry) services.

## Scope

pyetnic implements and documents **the ETNIC SOAP contracts, nothing else**. Regulatory
material (circulars, allocation and staffing computations, staff codes), derived
computations and school-specific reports belong to the consuming applications: see
"Scope Boundary" in `docs/ARCHITECTURE.md`. Do not add them back, in code or in docs.

## Tech Stack

- Python 3.10+ (CI matrix 3.10-3.13)
- `zeep` - SOAP client
- `requests` - HTTP transport
- `python-dotenv` - config loading
- `cryptography` + `xmlsec` (extra `[seps]`) - X509 signing for SEPS
- `openpyxl` (extra `[excel]`) - only for the Excel examples

## Project Structure

```
pyetnic/
├── eprom/               # Public namespace for EPROM services
├── seps/                # Public namespace for SEPS services
├── services/            # Service implementations (internal)
├── resources/           # Embedded WSDL and XSD files, one folder per service
├── config.py            # Lazy Config with metaclass
├── soap_client.py       # SoapClientManager (zeep + WSSE)
└── cli.py               # `pyetnic init-config` command
```

## Development Commands

- Install dev: `pip install -e ".[seps]"`
- Run tests (mock only): `pytest tests/regression/ tests/unit/`
- Run tests (integration, needs `.env`): `pytest tests/integration/`
- Build and check: `python -m build` then `python -m twine check dist/*`

## Key Documentation

Start with `docs/SOURCES.md`, the map of what answers which question.

- **`docs/SPEC.md`** - business rules and ETNIC contracts as implemented (workflow, `implId` rule, error codes)
- **`docs/ARCHITECTURE.md`** - layering, scope boundary, key decisions, known limitations
- **`docs/PUBLIC_API_SURFACE.md`** - stable vs construction symbols
- **`docs/BACKWARDS_COMPAT.md`** - backwards compatibility policy
- **`specs/`** - exhaustive per-service reference, built from the WSDL/XSD and the ETNIC manuals in `documentation/`
- **GitHub issues** - the backlog

Audit ids (`D2`, `Q4`, `H9`...) and sprint numbers in comments resolve in tag
`refactoring-records`: see "History" in `docs/SOURCES.md`.

## Production

`ENV=prod` reaches the real data of a school. Exploratory tests run on TQ (`ENV=dev`)
first: create, read, then delete an organisation there to settle a wire value. Ask before
any write against production, and record what a production test teaches in the matching
`specs/` file.

## Release

1. Bump the version in **both** `pyproject.toml` and `pyetnic/__init__.py`.
2. Move the `[Unreleased]` entries of `CHANGELOG.md` under the new version.
3. Build and `twine check`, then push an annotated tag `vX.Y.Z` (or `vX.Y.ZbN`).
4. `.github/workflows/publish-pypi.yml` publishes through PyPI Trusted Publishing (OIDC):
   no API token is involved. Pre-releases need `pip install --pre`.

## Coding Conventions

- Exchange language with user: French. README and `specs/` are in French.
- Code, docstrings, commit messages: English, Conventional Commits.
- Type hints mandatory on all public functions
- Dataclasses for data models (not Pydantic, for now)
- No `except Exception` in library code
- Logging via named loggers, never `basicConfig` in library code
- f-strings forbidden in `logger.debug()` - use `%s` formatting
- `serialize_object` stays a module-level import in `soap_client.py`: the tests patch it there.
- Small fixes may go straight to `main`; anything structural goes through a branch and a
  pull request, merged with a merge commit (no squash).
