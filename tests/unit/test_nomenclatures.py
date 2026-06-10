"""Unit tests for nomenclature Enums (H9)."""

from __future__ import annotations

import pytest

from pyetnic.nomenclatures import (
    CodeAdmission,
    CodeNiveau,
    CodeSanction,
    CodeStatut,
    DureeInoccupation,
    Equivalence,
    Indicateur,
    IndicateurX,
    MotifAbandon,
    MotifExemption,
    MotifExemptionSpec,
    SituationMenage,
    StatutFinFormation,
    TitreDelivre,
    TYPES_INTERVENTION_EXTERIEURE,
    TypeEnseignement,
    TypeInterventionExterieure,
    ValorisationAcquis,
    ValorisationAcquisSanction,
)


class TestTypeInterventionExterieure:

    def test_enum_value_is_letter_code(self):
        assert TypeInterventionExterieure.CONVENTION.value == "C"
        assert TypeInterventionExterieure.EHR.value == "E"

    def test_enum_member_is_a_str_subclass(self):
        assert isinstance(TypeInterventionExterieure.CONVENTION, str)

    def test_bidirectional_string_comparison(self):
        """(str, Enum) members must compare equal to raw strings both ways."""
        assert TypeInterventionExterieure.CONVENTION == "C"
        assert "C" == TypeInterventionExterieure.CONVENTION

    def test_covers_all_legacy_values(self):
        """Every value in the legacy constant must be representable as an Enum member."""
        enum_values = {m.value for m in TypeInterventionExterieure}
        assert set(TYPES_INTERVENTION_EXTERIEURE) == enum_values

    def test_values_are_the_exact_letter_codes(self):
        """Drift guard: pin the full name->letter mapping so a future edit cannot
        silently reintroduce the long French labels (which ETNIC rejects, code 30004).

        Authoritative source: specs/02_formation_organisation_v7.md
        §"Valeurs de typeInterventionExterieure" (validated 2025-06-10).
        Codes R and S were removed by ETNIC and have no member here.
        """
        expected = {
            "PERSONNEL_NON_CHARGE_DE_COURS": "A",
            "OCTROI_PERIODES_SUPPLEMENTAIRES_BONUS": "B",
            "CONVENTION": "C",
            "DISCRIMINATIONS_POSITIVES": "D",
            "EHR": "E",
            "FONDS_EUROPEENS": "F",
            "FORMATION_PUBLICS_INFRA_SCOLARISES": "I",
            "REORIENTATION_7TQ_7P": "J",
            "OCTROI_PERIODES_CABINET_PROJETS_TRANSVER": "K",
            "FORMATIONS_CONTINUEES": "P",
            "AGENCE_QUALITE": "Q",
            "UNION_EUROPEENNE": "U",
            "VALIDATION_DES_COMPETENCES": "V",
        }
        assert {m.name: m.value for m in TypeInterventionExterieure} == expected


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


# ---------------------------------------------------------------------------
# Inscription enums — drift guards pinned against inscription_v1.xsd
# ---------------------------------------------------------------------------

# (enum, exact set of XSD enumeration values)
_INSCRIPTION_ENUM_XSD_VALUES = [
    (CodeStatut, {"DE", "AN"}),
    (Indicateur, {"O", "N"}),
    (IndicateurX, {"O", "N", "X"}),
    (MotifExemption, {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}),
    (MotifExemptionSpec, {f"C{n:02d}" for n in range(1, 14)}),
    (TypeEnseignement, {"PRI", "SIPE", "SSPE", "SIPS", "SSPS", "SCPE", "SLPE", "SCPS", "SLPS"}),
    (TitreDelivre, {
        "CEB", "CE1D", "CESI", "CE2D", "CQ4", "CESSG", "CESST", "CESSQ", "CESSP",
        "CESSA", "CE6P", "CQ6", "CQ7", "DAES", "BES", "BACH", "MAST", "CESS",
        "CQSUP", "CQINF", "MASTSPE", "DOC", "BACHSPE",
    }),
    (Equivalence, {"C01", "C02", "C03", "C04"}),
    (ValorisationAcquis, {"C01", "C02", "C03", "C04", "C10", "C20", "C30", "C40"}),
    (ValorisationAcquisSanction, {"C00", "C01", "C02", "C03", "C04", "C05"}),
    (StatutFinFormation, {"C01", "C02", "C03", "C04", "C05", "C06"}),
    (CodeNiveau, {"SI", "SS", "SC", "SL"}),
]


@pytest.mark.parametrize(
    "enum_cls, expected",
    _INSCRIPTION_ENUM_XSD_VALUES,
    ids=[e.__name__ for e, _ in _INSCRIPTION_ENUM_XSD_VALUES],
)
def test_inscription_enum_values_match_xsd(enum_cls, expected):
    """Each inscription enum must carry exactly the XSD enumeration values."""
    assert {m.value for m in enum_cls} == expected


@pytest.mark.parametrize(
    "enum_cls",
    [e for e, _ in _INSCRIPTION_ENUM_XSD_VALUES],
    ids=[e.__name__ for e, _ in _INSCRIPTION_ENUM_XSD_VALUES],
)
def test_inscription_enum_members_are_str(enum_cls):
    """Every member must be a str subclass that compares to its raw value."""
    for m in enum_cls:
        assert isinstance(m, str)
        assert m == m.value


def test_titre_delivre_has_23_members():
    assert len(TitreDelivre) == 23


def test_statut_fin_formation_uses_c_prefix_not_bare_digits():
    """XSD imposes C01-C06; the PDF's bare 01-06 must never sneak in."""
    assert {m.value for m in StatutFinFormation} == {f"C{n:02d}" for n in range(1, 7)}
    assert "01" not in {m.value for m in StatutFinFormation}


def test_indicateur_and_indicateurx_are_distinct():
    assert "X" not in {m.value for m in Indicateur}
    assert "X" in {m.value for m in IndicateurX}


def test_new_inscription_enums_exported_from_seps_namespace():
    import pyetnic.seps as seps

    for name in (
        "CodeStatut", "Indicateur", "IndicateurX", "MotifExemption",
        "MotifExemptionSpec", "TypeEnseignement", "TitreDelivre", "Equivalence",
        "ValorisationAcquis", "ValorisationAcquisSanction", "StatutFinFormation",
        "CodeNiveau",
    ):
        assert hasattr(seps, name), f"missing seps export: {name}"
        assert name in seps.__all__


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
