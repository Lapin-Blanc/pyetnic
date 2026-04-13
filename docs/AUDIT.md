# pyetnic — Code Audit

> **Status**: Reference document, immutable.
> **Date**: 2026-04-13
> **Version audited**: 0.0.12
> **Auditor**: Architecture review session

This document captures the audit findings of the pyetnic codebase at version 0.0.12. It serves as the reference for all subsequent refactoring phases. Each defect is assigned an identifier (D*, Q*, H*) that is referenced in the phase prompts.

---

## Overview

- **Lines of code**: ~3,900 Python
- **Services**: 10 (5 EPROM + 5 SEPS)
- **Tests**: ~40 (mock + integration)
- **WSDL embedded**: 9 (5 EPROM + 4 SEPS)
- **Version**: 0.0.12 — classified "Alpha"

General impression: the code is clean and readable, architectural intent is sound (clear layering `config` → `soap_client` → `services` → public namespaces `eprom`/`seps`), typed dataclasses, read/save separation following XSD contracts, custom exception hierarchy on SEPS side. The gap is between "works for one school" and "publishable and maintainable library".

---

## 🔴 Core defects (high priority)

### D1 — SOAP client cache not invalidated on environment change

In `soap_client.py`, `SoapClientManager._client_cache` is a **class-level dict** keyed only by `service_name`:

```python
class SoapClientManager:
    _client_cache = {}

    def _initialize_client(self):
        if self.service_name in self._client_cache:
            return self._client_cache[self.service_name]
        ...
```

**Breaking scenario**: A Django integrator does `Config.ENV = "dev"`, calls `lire_organisation(...)`, then does `Config.ENV = "prod"` and calls again. On the second call, the cached dev client is returned — dev endpoint, dev credentials, SSL disabled — silently.

Same issue if `Config.USERNAME` is reassigned: the zeep client retains the old `UsernameToken`.

**Fix**: key the cache by `(service_name, ENV, USERNAME)` or invalidate the cache on Config mutations.

### D2 — `asdict()` sends `None` fields into SOAP requests

In `document1.py` / `document2.py` / `document3.py` / `enregistrer_etudiant.py`:

```python
request_data['populationListe'] = asdict(population_liste)
```

`dataclasses.asdict()` recursively serializes **all** fields, including `None` ones. zeep injects them as empty XML elements. For `nillable="false"` XSD fields, ETNIC rejects. For other fields, the server may interpret "empty tag" as "erase this value" — which differs from "field absent = do not touch".

This is a likely root cause of silent ETNIC rejects on partial updates.

**Fix**: strip `None` fields before serialization. Either a recursive helper `to_soap_dict(exclude_none=True)` or migrate models to Pydantic v2 which provides `model_dump(exclude_none=True)` natively.

### D3 — Three different error handling philosophies

| Service | Business error (success=False) | Network/SOAP error | Invalid argument |
|---|---|---|---|
| `OrganisationService` | returns `None` | raises `SoapError` | returns `None` |
| `FormationsListeService` | returns `FormationsListeResult(False, ...)` | `except Exception`, wrapped in result | same |
| `Document*Service` | returns `None` | raises `SoapError` | returns `None` |
| `RechercheEtudiantsService` | **raises typed exceptions** | raises `SoapError` | raises `ValueError` |

Consumers must memorize each function's convention. Worse, `FormationsListeService` has `except Exception as e:` that swallows everything, including genuine bugs in the parsing code: a `KeyError` in local code becomes a `result.success=False` without a stack trace.

**Recommendation**: pick one philosophy, apply everywhere. The SEPS approach (typed exceptions) is the right one. Introduce `EtnicServiceError`, `EtnicBusinessError`, `EtnicDocumentNotAccessibleError`, etc. Current `None` returns conflate "document not yet accessible in workflow" with "ETNIC error". A clear distinction helps integrators.

### D4 — Tight coupling to zeep's dict format via `serialize_object(result, dict)`

In `soap_client.call_service`:
```python
from zeep.helpers import serialize_object
return serialize_object(result, dict)
```

Then each service re-parses these dicts into dataclasses. This is **double work**: zeep instantiates typed objects from the XSD, we flatten them to dict, then reconstruct dataclasses from the dict.

Result: `_parse_*` methods are 50-100 lines of field copying. Inconsistency emerges — `document1.py` uses `p['coAnnEtude']` (KeyError on missing), `document3.py` uses `a.get('coNumBranche')` (silent None). Mixing both styles in the same module is a classic sign of code written in multiple passes without a style guide.

**Options**:
- **A (minimal)**: keep dicts but introduce a `from_dict()` helper on each dataclass with a strict rule (always `.get()`, except for required fields). Unifies style, removes ~30% of parsing code.
- **B (ambitious)**: replace dataclasses with Pydantic v2 models.

### D5 — `_organisation_id_dict` duplicated across 4 services

Identical static method copy-pasted in `organisation.py`, `document1.py`, `document2.py`, `document3.py`:

```python
@staticmethod
def _organisation_id_dict(organisation_id: OrganisationId) -> dict:
    return {
        'anneeScolaire': organisation_id.anneeScolaire,
        'etabId': organisation_id.etabId,
        'numAdmFormation': organisation_id.numAdmFormation,
        'numOrganisation': organisation_id.numOrganisation,
    }
```

If `OrganisationReqIdCT` evolves, you fix it in 4 places.

**Fix**: method on `OrganisationId` itself:
```python
def as_request_key(self) -> dict: ...
```

### D6 — `OrganisationId` type encodes a critical business rule by convention

The rule "never send `implId` in Lire/Modifier/Supprimer, only in Créer" is enforced today by the discipline of 4 `_organisation_id_dict` functions that deliberately omit the field. Your CLAUDE.md repeats this. It's fragile.

**Recommended refactor**: split into two distinct types.

```python
@dataclass(frozen=True)
class OrganisationKey:
    """Minimal organisation identifier (without implId). Used in read/modify/delete."""
    anneeScolaire: str
    etabId: int
    numAdmFormation: int
    numOrganisation: int

@dataclass
class Organisation:
    """Full organisation with all attributes."""
    key: OrganisationKey
    implId: Optional[int] = None
    ...
```

Benefit: the type system makes it **impossible** to get wrong. No more functions that "deliberately forget" a field.

**Note**: this is a breaking change on the public API. Deferred to a future major version (1.0.0).

---

## 🟠 Important quality issues

### Q1 — `except (Fault, TransportError, RequestException, AttributeError)` in `call_service`

`AttributeError` has no business here. It masks real bugs (typo in kwarg, nonexistent method) by converting them into unhelpful `SoapError`. Remove.

### Q2 — `FormationsListeService` has a catch-all `except Exception`

```python
except Exception as e:
    return FormationsListeResult(False, [], messages=[f"Une erreur inattendue s'est produite : {str(e)}"])
```

Classic antipattern. A `KeyError` in the parsing code is wrapped as "unexpected error" with no stack trace. At minimum, `logger.exception(...)` so the traceback reaches logs.

### Q3 — `_EtnicBinarySignature.verify()` is a silent no-op

```python
class _EtnicBinarySignature(_MemorySignature):
    def verify(self, envelope):
        return envelope
```

Silently neutralizes response signature validation. Add an explicit comment explaining why (ETNIC doesn't sign responses? Signs them incompatibly?), and ideally log a warning on first call.

### Q4 — `Config.ETAB_ID` returns a string, but callers want an int

`os.getenv("DEFAULT_ETABID", None)` always returns `str | None`. Tests do `int(Config.ETAB_ID)`. `formations_liste.py` passes `Config.ETAB_ID` directly to `kwargs["etabId"]` — zeep converts it because the XSD says `xs:int`, but by luck.

**Fix**: `_SIMPLE_ENV_MAP` can include a caster.

### Q5 — `_ssl_warnings_suppressed` is a module-level mutable global

Module-level flag modified via `global`. Works, but non-testable (no clean reset) and not thread-safe.

### Q6 — `request_id` not logged on success

In `call_service`, on success the `request_id` is not logged. When reporting a bug to ETNIC support, you'd need to replay in debug mode.

### Q7 — f-strings in `logger.debug(f"... {pformat(x)}")`

Immediate evaluation even when the logger is at INFO. For `pformat` on large objects, this is a real cost.

```python
# Instead of:
logger.debug(f"Organisation : {pformat(org_data)}")
# Use:
logger.debug("Organisation : %s", pformat(org_data))
```

### Q8 — zeep `list|dict` parsing inconsistent

In `seps.py` you correctly do:
```python
if isinstance(etudiants_raw, dict):
    etudiants_raw = [etudiants_raw]
```
Because zeep sometimes returns a single dict instead of a list. **This trap exists elsewhere** but isn't handled systematically. In `document3.py`, `a['enseignantListe'].get('enseignant', [])` assumes a list — but with a single teacher, zeep may return a dict. Unify via an `_as_list(value)` helper.

### Q9 — No visible CI

Tests exist (~40) but no `.github/workflows/`. Adding a minimal workflow that runs mock tests is a quick win.

### Q10 — `log_config.py` in a library

By principle, **a library should never configure root logging**. It should create named loggers and leave configuration to the application. If `log_config.py` calls `logging.basicConfig()`, remove it.

---

## 🟡 Hygiene and structure

### H1 — README out of sync with code

README documents `pyetnic.lire_organisation(...)` (flat namespace) but actual API is `pyetnic.eprom.lire_organisation(...)`. All examples need updating.

### H2 — CLAUDE.md at 413 lines

5× the 80-line guideline. Grew by accretion. To split: business rules and `implId` / Doc1-Doc2-Doc3 workflow → SPEC.md; Claude Code instructions strictly → CLAUDE.md.

### H3 — `cli.py` hardcodes your establishment IDs

```python
DEFAULT_ETABID=3052
DEFAULT_IMPLID=6050
```

Leaks institutional info and makes the template useless for other schools.

### H4 — One-off scripts at repo root

`extrait_profs.py`, `print_doc2.py`, `print_doc3.py`. Move to `examples/`.

### H5 — `requirements.txt` duplicates `pyproject.toml` and contains commented-out code

40% of the file is commented. `xmlsec` is in main dependencies but `pyproject.toml` correctly places it in extra `seps` — inconsistency.

### H6 — "Alpha" classification inconsistent with production use

If used daily, it's at minimum **Beta**. `0.0.12` signals "unstable API, don't rely on it" — which doesn't match reality.

### H7 — `services/__init__.py` instantiates service singletons at import

Imports instantiate all services, including SEPS clients with X509 cert, even if only EPROM is used. Consider module-level `__getattr__` (PEP 562) for lazy loading.

### H8 — `pyetnic/resources/Codes_Pays.xls`

Binary `.xls` embedded in the package with no visible usage. Dead resource bloating the wheel.

### H9 — `nomenclatures.py` (17 lines)

Likely just a `TYPES_INTERVENTION_EXTERIEURE` constant. ETNIC nomenclature codes (`coEtuReg`, `codeAdmission`, `codeSanction`, `motifExemption` C01-C07, etc.) should be typed Enums, not free strings. Huge win for IDE autocompletion and error detection.

### H10 — No semantic versioning on embedded XSD

If ETNIC updates an XSD, how do we know? A `pyetnic doctor` command that hits each service and prints its WSDL version would help. And a CHANGELOG tracking ETNIC-side changes per release.

### H11 — No `py.typed` marker

Dataclasses are typed, but without `py.typed` (PEP 561), users don't get mypy support.

---

## 🟢 What's good (keep)

- **Read/Save separation per XSD**. Resist merging — matches the contracts.
- **Lazy config via metaclass**. Good pattern, well executed.
- **`_load_dotenv_compat`** with cp1252 fallback. Real-world terrain knowledge.
- **SEPS exception hierarchy with `ancien_niss`/`nouveau_niss` in `NissMutationError`**. Very clean, genuinely useful.
- **Namespace split `eprom`/`seps`**. Good structural decision.
- **`FormationsListeResult` with `__bool__`, `__iter__`, `__len__`**. Small touch that makes caller code elegant.
- **French comments** targeted on ETNIC subtleties (implId rule, error 20102). Useful documentation.

---

## Summary

The foundation is sound. No deep architectural debt to repay: no tangled layers, no toxic coupling, no impossible inheritance. Defects are concentrated and identifiable.

The two highest-leverage fixes:
1. **Fix cache invalidation (D1) + normalize error handling (D3)**: one day's work, massive impact on reliability and predictability.
2. **Replace `asdict()` with None-stripping serialization (D2)**: eliminates a whole class of silent bugs on partial updates.

The decision to migrate to Pydantic v2 is a heavier one, to be evaluated separately — it brings much (validation, clean serialization, JSON schema) but requires touching all models and reconverging tests. Keeping dataclasses with a `to_soap_dict(exclude_none=True)` helper captures 80% of the benefit for 20% of the effort.
