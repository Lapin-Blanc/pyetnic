"""Unit tests for pyetnic.services._helpers."""

from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from pyetnic.services._helpers import organisation_request_id, to_soap_dict
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
        """A dataclass where every field is None produces an empty dict."""
        @dataclass
        class _AllOptional:
            a: Optional[int] = None
            b: Optional[str] = None

        result = to_soap_dict(_AllOptional())
        assert result == {}

    def test_preserves_zero_and_empty_string(self):
        """Zero, empty string, and False are NOT None — they must be preserved."""
        @dataclass
        class _FalsyValues:
            count: int = 0
            name: str = ""
            flag: bool = False

        result = to_soap_dict(_FalsyValues())
        assert result == {'count': 0, 'name': '', 'flag': False}

    def test_with_real_doc1_save_model(self):
        """Smoke test with an actual pyetnic model."""
        from pyetnic.services.models import (
            Doc1PopulationLineSave,
            Doc1PopulationListSave,
        )

        line = Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12)
        liste = Doc1PopulationListSave(population=[line])
        result = to_soap_dict(liste)

        assert result == {
            'population': [
                {'coAnnEtude': 1, 'nbEleveA': 12},
            ],
        }
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
            implId=6050,
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
