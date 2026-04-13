# pyetnic — Claude Code Instructions

## Overview

Python client for ETNIC SOAP web services (Belgian promotion sociale education). Provides typed access to EPROM (formations/organisations/documents) and SEPS (student registry) services.

## Tech Stack

- Python 3.12+ (minimum 3.8 for packaging)
- `zeep` — SOAP client
- `requests` — HTTP transport
- `python-dotenv` — config loading
- `cryptography` + `xmlsec` (extra `[seps]`) — X509 signing for SEPS

## Project Structure

```
pyetnic/
├── eprom/               # Public namespace for EPROM services
├── seps/                # Public namespace for SEPS services
├── services/            # Service implementations (internal)
├── resources/           # Embedded WSDL and XSD files
├── config.py            # Lazy Config with metaclass
├── soap_client.py       # SoapClientManager (zeep + WSSE)
└── cli.py               # `pyetnic init-config` command
```

## Development Commands

- Run tests (mock only): `pytest tests/regression/ tests/unit/`
- Run tests (integration, needs `.env`): `pytest tests/integration/`
- Install dev: `pip install -e ".[seps]"`
- Build wheel: `python -m build`

## Key Documentation

All specification and architecture details live in `docs/`:

- **`docs/SPEC.md`** — full functional and technical specification (ETNIC workflow rules, implId gotchas, error codes)
- **`docs/AUDIT.md`** — reference audit (defect IDs D1-D6, Q1-Q10, H1-H11)
- **`docs/ARCHITECTURE.md`** — target architecture post-refactoring
- **`docs/BACKWARDS_COMPAT.md`** — backwards compatibility policy
- **`docs/PUBLIC_API_SURFACE.md`** — authoritative list of stable vs construction symbols
- **`docs/phases/`** — phased implementation prompts per sprint
- **`plan.md`** — current refactoring progress

## Architecture Decisions

- **Layered**: `config` → `soap_client` → `services` → public namespaces
- **Lazy config**: `Config` resolves attributes on access, allowing programmatic override (Django integration)
- **Read/Save model split**: separate dataclasses per XSD contract (e.g. `Doc1PopulationLine` vs `Doc1PopulationLineSave`)
- **Two namespaces**: `eprom` (username/password auth) and `seps` (X509 PFX auth)

## Current Status

See `plan.md` for refactoring progress. Currently in: **Sprint 0 — Preparation**.

## Coding Conventions

- Exchange language with user: French
- Code, docstrings, commit messages: English
- Type hints mandatory on all public functions
- Dataclasses for data models (not Pydantic, for now)
- No `except Exception` in library code
- Logging via named loggers, never `basicConfig` in library code
- f-strings forbidden in `logger.debug()` — use `%s` formatting
