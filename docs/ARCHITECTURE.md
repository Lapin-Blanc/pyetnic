# pyetnic — Architecture

This document records the architectural decisions made across Sprints 0-2. For the
business rules and ETNIC contracts, see `docs/SPEC.md`. For the defect catalogue, see
`docs/AUDIT.md`.

## Layering

```
config → soap_client → services → public namespaces (eprom, seps)
```

- `config.py` — lazy `Config` (credentials, endpoints, env).
- `soap_client.py` — `SoapClientManager` (one zeep client per service, WSSE/X509 auth).
- `services/` — internal service classes + dataclasses (`models.py`). Not imported directly.
- `eprom/`, `seps/` — public namespaces re-exporting the stable API.

## Key Decisions

### Lazy Config via metaclass (Sprint 0)
`Config` uses a `_ConfigMeta` metaclass so attributes resolve on *access*, not at import.
`__getattr__` checks programmatic overrides first, then loads `.env` lazily, then reads
`os.environ`. This lets integrators (e.g. Django) set `Config.USERNAME = ...` before the
first SOAP call without manipulating `os.environ`. No side effects at `import pyetnic`.

### SOAP client manager + cache key (Sprint 1)
`SoapClientManager` caches one zeep client per `(service_name, ENV, USERNAME)` tuple, so a
runtime change of environment or credentials yields a fresh client instead of a stale one
(audit D1). `PASSWORD` is deliberately excluded from the key (no secrets in cache keys);
`reset_cache()` covers password rotation. `call_service()` returns
`serialize_object(result, dict)` with a fixed shape: `{header: {requestId}, body: {success,
messages: {error/warning/info}, response}}`.

### Read/Save model split
Each document has separate dataclasses per XSD direction: read types (received, all fields)
vs `*Save` types (sent, only the modifiable subset). They are intentionally not merged —
they map to distinct XSD contracts (e.g. `Doc1PopulationLine` vs `Doc1PopulationLineSave`).

### Namespace split: eprom vs seps
Two public namespaces with different auth and maturity: `eprom` (WSSE UsernameToken, dev+prod)
and `seps` (X509 PFX, prod-only). They evolved separately; SEPS pioneered typed exceptions.

### Strict error mode via ContextVar (Sprint 1)
EPROM services return `None` / result objects on business errors by default, or raise the typed
hierarchy (`EtnicError` …) when `Config.RAISE_ON_ERROR` is on, toggled by the `strict_errors()`
context manager. The flag is backed by a `contextvars.ContextVar` (not a class attribute) so it
is isolated per thread and per asyncio task. `signal_business_error()` centralizes the
raise-or-return decision so every `_parse_*_response` stays small and uniform.

### Private helpers module (Sprint 2)
`services/_helpers.py` holds `to_soap_dict()` (recursive, `exclude_none=True` — strips `None`
so partial updates don't send empty XML tags, audit D2) and `organisation_request_id()` (builds
the 4-field request id without `implId`, audit D5). Free functions, not methods, and private
(underscore) rather than public — to avoid locking in an API that the D6 `OrganisationKey` split
will obsolete at 1.0.0.

### Dataclasses over Pydantic (Sprint 0 decision)
Models stay on stdlib dataclasses through 0.1.0. A Pydantic migration is a separate decision
deferred to post-0.1.0.

## Known Limitations

- `SoapClientManager._client_cache` is class-level (shared across instances) — fine for
  single-threaded scripts; revisit for concurrent use.
- `Organisation.statutDocument*` fields are always `None` when the object comes from
  `lire_organisation()` — they are only populated on the `lister_formations()` aperçu.
- SSL verification is disabled in `dev` (EPROM TQ endpoints) — never deploy with `ENV=dev`.

## Not Yet Decided

- **`OrganisationKey` split (D6)** — separate key/full types to make the `implId` rule
  type-enforced. Breaking change, deferred to 1.0.0.
- **Pydantic migration** — deferred to post-0.1.0.
- **SEPS/EPROM exception unification** — the SEPS (`SepsEtnicError`) and EPROM (`EtnicError`)
  hierarchies remain separate for now.
- **Default-mode switch to raise** — making strict mode the default is a 0.2.0 change, not
  scheduled in Sprints 1-4.
