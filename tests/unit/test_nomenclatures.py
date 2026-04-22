"""Unit tests for nomenclature Enums (H9)."""

from __future__ import annotations

from pyetnic.nomenclatures import (
    CodeAdmission,
    CodeSanction,
    DureeInoccupation,
    MotifAbandon,
    SituationMenage,
    TYPES_INTERVENTION_EXTERIEURE,
    TypeInterventionExterieure,
)


class TestTypeInterventionExterieure:

    def test_enum_value_is_verbatim_string(self):
        assert TypeInterventionExterieure.CONVENTION.value == "Convention"
        assert TypeInterventionExterieure.EHR.value == "EHR"

    def test_enum_member_is_a_str_subclass(self):
        assert isinstance(TypeInterventionExterieure.CONVENTION, str)

    def test_bidirectional_string_comparison(self):
        """(str, Enum) members must compare equal to raw strings both ways."""
        assert TypeInterventionExterieure.CONVENTION == "Convention"
        assert "Convention" == TypeInterventionExterieure.CONVENTION

    def test_covers_all_legacy_values(self):
        """Every label in the legacy constant must be representable as an Enum member."""
        enum_values = {m.value for m in TypeInterventionExterieure}
        assert set(TYPES_INTERVENTION_EXTERIEURE) == enum_values


class TestCodeAdmission:

    def test_xsd_values_present(self):
        values = {m.value for m in CodeAdmission}
        assert values == {"REUSSITE", "TITREBEL", "TITREETR", "AUTRE"}

    def test_string_comparison(self):
        assert CodeAdmission.TITRE_BELGE == "TITREBEL"


class TestCodeSanction:

    def test_xsd_values_present(self):
        values = {m.value for m in CodeSanction}
        assert values == {"RE", "AB", "EH"}


class TestMotifAbandon:

    def test_xsd_values_present(self):
        values = {m.value for m in MotifAbandon}
        assert values == {"TPS", "PRO", "FAM", "SAN", "ATT", "MEM", "FMJ", "NUM", "AUT", "INC"}


class TestDureeInoccupation:

    def test_xsd_values_present(self):
        values = {m.value for m in DureeInoccupation}
        assert values == {"C00", "C06", "C12", "C24"}


class TestSituationMenage:

    def test_xsd_values_present(self):
        values = {m.value for m in SituationMenage}
        assert values == {"ISOL", "SSEM", "A1EM", "X"}


class TestLegacyConstant:

    def test_still_exists(self):
        assert TYPES_INTERVENTION_EXTERIEURE is not None
        assert len(TYPES_INTERVENTION_EXTERIEURE) == 13

    def test_is_a_list(self):
        """Shape must stay the same: a plain list of strings."""
        assert isinstance(TYPES_INTERVENTION_EXTERIEURE, list)
        assert all(isinstance(v, str) for v in TYPES_INTERVENTION_EXTERIEURE)

    def test_importable_from_eprom_namespace(self):
        from pyetnic.eprom import TYPES_INTERVENTION_EXTERIEURE as exported
        assert exported == TYPES_INTERVENTION_EXTERIEURE
