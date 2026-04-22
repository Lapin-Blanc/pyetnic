# Phase 2.1 — Create private helpers module (D2 + D5 foundations)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — sections **D2** and **D5**
- `plan.md` — Sprint 2 section, especially design decisions
- `pyetnic/services/organisation.py` — to see `_organisation_id_dict` in action
- `pyetnic/services/document1.py` — to see `asdict()` usage in action

This is the first phase of **Sprint 2 — Structural refactoring**. It creates the two helper functions that the rest of Sprint 2 will use. No service code is modified yet — this phase is pure addition, like phase 1.2 was for the exception hierarchy.

**Design decisions (made in Atelier Analyse)**:
- Both helpers live in a **single private module** `pyetnic/services/_helpers.py`.
- `to_soap_dict()` is a **free function**, not a method on dataclasses.
- `organisation_request_id()` is a **free function**, not a method on `OrganisationId`.
- Neither function is exported from the public API. They are internal plumbing.

## Objective

Create `pyetnic/services/_helpers.py` containing:

1. `to_soap_dict(obj, *, exclude_none=True)` — recursively converts a dataclass to a dict, stripping `None` values (fixes D2)
2. `organisation_request_id(org_id)` — produces the 4-field dict for `OrganisationReqIdCT` without `implId` (fixes D5)

Both functions are tested in isolation before being wired into any service.

## Tasks

### 1. Create `pyetnic/services/_helpers.py`

```python
"""Private helpers for EPROM/SEPS service implementations.

These are internal utilities, NOT part of the public API.
Do not import from outside pyetnic.services.

Contents:
- to_soap_dict: None-stripping serialization for SOAP payloads (D2)
- organisation_request_id: OrganisationReqIdCT dict builder (D5)
"""

from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from typing import Any

from .models import OrganisationId


def _strip_none_recursive(d: dict) -> dict:
    """Recursively remove keys with None values from a nested dict.

    Also processes lists of dicts (common in SOAP payloads like
    population lists, activité lists, etc.).

    Returns a new dict — the input is not modified.
    """
    result = {}
    for key, value in d.items():
        if value is None:
            continue
        if isinstance(value, dict):
            stripped = _strip_none_recursive(value)
            if stripped:  # don't add empty dicts
                result[key] = stripped
        elif isinstance(value, list):
            result[key] = [
                _strip_none_recursive(item) if isinstance(item, dict) else item
                for item in value
                if item is not None
            ]
        else:
            result[key] = value
    return result


def to_soap_dict(obj: Any, *, exclude_none: bool = True) -> dict:
    """Convert a dataclass instance to a dict suitable for zeep SOAP calls.

    This replaces direct use of `dataclasses.asdict()` in service methods.
    The key difference: when `exclude_none=True` (default), fields with
    `None` values are recursively stripped from the output. This prevents
    zeep from injecting empty XML elements for absent optional fields,
    which can cause ETNIC to reject the request or misinterpret "empty tag"
    as "erase this value".

    Args:
        obj: A dataclass instance to serialize.
        exclude_none: If True (default), recursively remove None-valued keys.
            Set to False to get the same behavior as `dataclasses.asdict()`.

    Returns:
        A plain dict suitable for passing as **kwargs to zeep service calls.

    Examples:
        # Before (D2 defect — sends None fields as empty XML):
        request_data['populationListe'] = asdict(population_liste)

        # After:
        request_data['populationListe'] = to_soap_dict(population_liste)
    """
    if not is_dataclass(obj) or isinstance(obj, type):
        raise TypeError(f"to_soap_dict expects a dataclass instance, got {type(obj).__name__}")

    d = asdict(obj)
    if exclude_none:
        return _strip_none_recursive(d)
    return d


def organisation_request_id(org_id: OrganisationId) -> dict:
    """Build the request ID dict for Lire/Modifier/Supprimer operations.

    These WSDL operations use the `OrganisationReqIdCT` contract type,
    which contains exactly 4 fields. Critically, `implId` is NOT included
    — it exists on the response type but must NOT be sent in requests
    (except for CreerOrganisation, which uses a different contract type
    that includes implId).

    This function replaces the `_organisation_id_dict` static method that
    was copy-pasted across 4 service modules (D5).

    Args:
        org_id: An OrganisationId instance. The `implId` field, if present,
            is deliberately excluded from the output.

    Returns:
        A dict with exactly {anneeScolaire, etabId, numAdmFormation,
        numOrganisation} — suitable for the `id=` kwarg in SOAP calls.
    """
    return {
        'anneeScolaire': org_id.anneeScolaire,
        'etabId': org_id.etabId,
        'numAdmFormation': org_id.numAdmFormation,
        'numOrganisation': org_id.numOrganisation,
    }
```

### 2. Write unit tests

Create `tests/unit/test_helpers.py`:

```python
"""Unit tests for pyetnic.services._helpers."""

import pytest
from dataclasses import dataclass, field
from typing import Optional, List

from pyetnic.services._helpers import to_soap_dict, organisation_request_id
from pyetnic.services.models import OrganisationId


# ---------------------------------------------------------------------------
# to_soap_dict
# ---------------------------------------------------------------------------

@dataclass
class _SimpleModel:
    required_field: int
    optional_field: Optional[str] = None


@dataclass
class _NestedModel:
    name: str
    inner: Optional[_SimpleModel] = None


@dataclass
class _ListModel:
    items: List[_SimpleModel] = field(default_factory=list)


class TestToSoapDict:

    def test_strips_none_fields(self):
        obj = _SimpleModel(required_field=42, optional_field=None)
        result = to_soap_dict(obj)
        assert result == {'required_field': 42}
        assert 'optional_field' not in result

    def test_keeps_non_none_fields(self):
        obj = _SimpleModel(required_field=42, optional_field="hello")
        result = to_soap_dict(obj)
        assert result == {'required_field': 42, 'optional_field': 'hello'}

    def test_strips_none_recursively(self):
        obj = _NestedModel(
            name="outer",
            inner=_SimpleModel(required_field=1, optional_field=None),
        )
        result = to_soap_dict(obj)
        assert result == {'name': 'outer', 'inner': {'required_field': 1}}

    def test_strips_none_in_nested_none(self):
        obj = _NestedModel(name="outer", inner=None)
        result = to_soap_dict(obj)
        assert result == {'name': 'outer'}
        assert 'inner' not in result

    def test_strips_none_in_lists(self):
        obj = _ListModel(items=[
            _SimpleModel(required_field=1, optional_field=None),
            _SimpleModel(required_field=2, optional_field="yes"),
        ])
        result = to_soap_dict(obj)
        assert result == {
            'items': [
                {'required_field': 1},
                {'required_field': 2, 'optional_field': 'yes'},
            ],
        }

    def test_exclude_none_false_preserves_nones(self):
        obj = _SimpleModel(required_field=42, optional_field=None)
        result = to_soap_dict(obj, exclude_none=False)
        assert result == {'required_field': 42, 'optional_field': None}

    def test_rejects_non_dataclass(self):
        with pytest.raises(TypeError, match="to_soap_dict expects a dataclass"):
            to_soap_dict({"not": "a dataclass"})

    def test_rejects_class_instead_of_instance(self):
        with pytest.raises(TypeError, match="to_soap_dict expects a dataclass"):
            to_soap_dict(_SimpleModel)

    def test_empty_dataclass_all_none(self):
        """A dataclass where every field is None produces an empty dict
        (or at minimum, no None values)."""
        @dataclass
        class _AllOptional:
            a: Optional[int] = None
            b: Optional[str] = None
        
        result = to_soap_dict(_AllOptional())
        assert result == {}

    def test_preserves_zero_and_empty_string(self):
        """Zero and empty string are NOT None — they must be preserved."""
        @dataclass
        class _FalsyValues:
            count: int = 0
            name: str = ""
            flag: bool = False
        
        result = to_soap_dict(_FalsyValues())
        assert result == {'count': 0, 'name': '', 'flag': False}

    def test_with_real_doc1_save_model(self):
        """Smoke test with an actual pyetnic model."""
        from pyetnic.services.models import Doc1PopulationLineSave, Doc1PopulationListSave
        
        line = Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12)
        liste = Doc1PopulationListSave(population=[line])
        result = to_soap_dict(liste)
        
        assert result == {
            'population': [
                {'coAnnEtude': 1, 'nbEleveA': 12},
            ],
        }
        # Verify None fields are absent
        assert 'nbEleveEhr' not in result['population'][0]


# ---------------------------------------------------------------------------
# organisation_request_id
# ---------------------------------------------------------------------------

class TestOrganisationRequestId:

    def test_produces_4_field_dict(self):
        org_id = OrganisationId(
            anneeScolaire="2024-2025",
            etabId=3052,
            numAdmFormation=455,
            numOrganisation=1,
        )
        result = organisation_request_id(org_id)
        assert result == {
            'anneeScolaire': '2024-2025',
            'etabId': 3052,
            'numAdmFormation': 455,
            'numOrganisation': 1,
        }

    def test_excludes_implid(self):
        """The critical business rule: implId must NOT be in the output."""
        org_id = OrganisationId(
            anneeScolaire="2024-2025",
            etabId=3052,
            numAdmFormation=455,
            numOrganisation=1,
            implId=6050,  # explicitly set
        )
        result = organisation_request_id(org_id)
        assert 'implId' not in result

    def test_result_has_exactly_4_keys(self):
        """Guard against accidental additions to the output."""
        org_id = OrganisationId(
            anneeScolaire="2024-2025",
            etabId=3052,
            numAdmFormation=455,
            numOrganisation=1,
            implId=6050,
        )
        result = organisation_request_id(org_id)
        assert len(result) == 4
```

### 3. Verify

```bash
pytest tests/unit/test_helpers.py -v
pytest tests/regression/ tests/unit/ -v
```

All green. The helpers are tested in isolation without touching any service code.

## Constraints

- **Do NOT modify any service file** in this phase.
- **Do NOT add the helpers to the public API** (`__all__`, `pyetnic/__init__.py`, etc.).
- **Do NOT import from `_helpers.py` outside of `pyetnic/services/`** — the underscore prefix signals "internal".
- The file should be fully self-contained except for the `OrganisationId` import.

## Validation

- [ ] `pyetnic/services/_helpers.py` exists with `to_soap_dict` and `organisation_request_id`
- [ ] `tests/unit/test_helpers.py` exists with ~14 tests, all passing
- [ ] `pytest tests/regression/ tests/unit/ -v` — all green, no regressions
- [ ] No service file modified
- [ ] CI green

## Next

Update `plan.md`: mark Phase 2.1 as complete. Commit message:

```
feat(sprint-2): phase 2.1 — create _helpers module (D2 + D5 foundations)

- Add pyetnic/services/_helpers.py with:
  - to_soap_dict(obj, exclude_none=True): None-stripping serialization
  - organisation_request_id(org_id): OrganisationReqIdCT builder (no implId)
- Add tests/unit/test_helpers.py with 14 unit tests:
  - to_soap_dict: None stripping, recursion, lists, edge cases, real model
  - organisation_request_id: 4-field output, implId exclusion, key count guard

Pure addition — no service code touched. Foundations for phases 2.2-2.5.
```

Next phase: **Phase 2.2 — Migrate organisation_request_id across services (D5)**.
