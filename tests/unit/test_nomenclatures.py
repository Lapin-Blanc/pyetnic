"""Unit tests for nomenclature Enums (H9)."""

from __future__ import annotations

import pytest

from pyetnic.nomenclatures import _TYPES_INTERVENTION_EXTERIEURE as TYPES_INTERVENTION_EXTERIEURE
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
    ModeEnregistrement,
    Sexe,
    SituationMenage,
    StatutFinFormation,
    TitreDelivre,
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

        Authoritative source: specs/02_formation_organisation_v8.md
        §"Valeurs de typeInterventionExterieure" (Organisation v8 manual rev. 6.0,
        list dated 2026-04-27; G is new in v8). Codes R and S are struck through
        in the manual and have no member here.
        """
        expected = {
            "PERSONNEL_NON_CHARGE_DE_COURS": "A",
            "OCTROI_PERIODES_SUPPLEMENTAIRES_BONUS": "B",
            "CONVENTION": "C",
            "DISCRIMINATIONS_POSITIVES": "D",
            "EHR": "E",
            "FONDS_EUROPEENS": "F",
            "BES": "G",
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
        assert values == {"REUSSITE", "TITREBEL", "TITREETR", "AUTRE", "AUCUN"}

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
    (MotifExemptionSpec, {f"C{n:02d}" for n in range(1, 14)} | {"C50"}),
    (TypeEnseignement, {"PRI", "SIPE", "SSPE", "SIPS", "SSPS", "SCPE", "SLPE", "SCPS", "SLPS"}),
    (TitreDelivre, {
        "CEB", "CE1D", "CESI", "CE2D", "CQ4", "CESSG", "CESST", "CESSQ", "CESSP",
        "CESSA", "CE6P", "CQ6", "CQ7", "DAES", "BES", "BACH", "MAST", "CESS",
        "CQSUP", "CQINF", "MASTSPE", "DOC", "BACHSPE",
    }),
    (Equivalence, {"C01", "C02", "C03", "C04"}),
    (ValorisationAcquis, {"C01", "C02", "C03", "C04", "C10", "C20", "C30", "C40", "C50"}),
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
        assert len(TYPES_INTERVENTION_EXTERIEURE) == 14

    def test_is_a_list(self):
        """Shape must stay the same: a plain list of strings."""
        assert isinstance(TYPES_INTERVENTION_EXTERIEURE, list)
        assert all(isinstance(v, str) for v in TYPES_INTERVENTION_EXTERIEURE)

    @pytest.mark.parametrize("module", ["pyetnic.eprom", "pyetnic.nomenclatures", "pyetnic.services"])
    def test_public_name_warns_until_1_0(self, module):
        import importlib

        namespace = importlib.import_module(module)
        with pytest.deprecated_call(match="TypeInterventionExterieure"):
            exported = namespace.TYPES_INTERVENTION_EXTERIEURE
        assert exported is TYPES_INTERVENTION_EXTERIEURE
        assert "TYPES_INTERVENTION_EXTERIEURE" not in getattr(namespace, "__all__", [])


# ---------------------------------------------------------------------------
# Every SEPS enum equals its enumeration in the embedded (live) inscription XSD
# ---------------------------------------------------------------------------

_XSD_TYPE_OF_ENUM = [
    (CodeStatut, "CodeStatutType"),
    (DureeInoccupation, "DureeInoccupationType"),
    (SituationMenage, "SituationMenageType"),
    (MotifExemption, "MotifExemptionType"),
    (MotifExemptionSpec, "MotifExemptionSpecType"),
    (CodeAdmission, "CodeAdmissionType"),
    (TypeEnseignement, "TypeEnseignementType"),
    (TitreDelivre, "TitreDelivreType"),
    (Equivalence, "EquivalenceType"),
    (ValorisationAcquis, "ValorisationAcquisType"),
    (CodeSanction, "CodeSanctionType"),
    (ValorisationAcquisSanction, "ValorisationAcquisSanctionType"),
    (MotifAbandon, "MotifAbandonType"),
    (StatutFinFormation, "StatutFinFormationType"),
    (CodeNiveau, "CodeNiveauType"),
    (Indicateur, "IndicateurType"),
    (IndicateurX, "IndicateurXType"),
]


def _xsd_enumerations(
    xsd: str = "SEPS_Enregistrer_Inscription_2.1/xsd/inscription_v1.xsd",
) -> dict:
    from xml.etree import ElementTree as ET

    from pyetnic.soap_client import get_wsdl_path

    path = get_wsdl_path("pyetnic.resources", xsd)
    xs = "{http://www.w3.org/2001/XMLSchema}"
    return {
        st.get("name"): {e.get("value") for e in st.iter(xs + "enumeration")}
        for st in ET.parse(path).getroot().findall(xs + "simpleType")
    }


@pytest.mark.parametrize("enum_cls, xsd_type", _XSD_TYPE_OF_ENUM, ids=lambda x: getattr(x, "__name__", x))
def test_enum_matches_embedded_xsd(enum_cls, xsd_type):
    """A contract refresh that adds or removes a code fails here (#22)."""
    assert {m.value for m in enum_cls} == _xsd_enumerations()[xsd_type]


# ---------------------------------------------------------------------------
# Student enums (#50), pinned against the EnregistrerEtudiant and
# RechercheEtudiants contracts
# ---------------------------------------------------------------------------

_STUDENT_ENUM_XSD = [
    (Sexe, "SexeType", "SEPS_Enregistrer_Etudiant_2.1/xsd/etudiantDetails_v1.xsd"),
    (Sexe, "SexeType", "SEPS_Recherche_Etudiants_2.1/xsd/etudiantDetails_v1.xsd"),
    (
        ModeEnregistrement,
        "ModeEnregistrement",
        "SEPS_Enregistrer_Etudiant_2.1/xsd/SEPSEnregistrerEtudiantMessages_external_v1.xsd",
    ),
]


@pytest.mark.parametrize(
    "enum_cls, xsd_type, xsd",
    _STUDENT_ENUM_XSD,
    ids=[f"{e.__name__}-{x.split('/')[0]}" for e, _, x in _STUDENT_ENUM_XSD],
)
def test_student_enum_matches_embedded_xsd(enum_cls, xsd_type, xsd):
    assert {m.value for m in enum_cls} == _xsd_enumerations(xsd)[xsd_type]


def test_student_enums_compare_to_raw_strings():
    assert Sexe.FEMININ == "F"
    assert ModeEnregistrement.DETAILS == "DETAILS"


def test_student_enums_exported_from_seps_namespace():
    import pyetnic.seps as seps

    for name in ("Sexe", "ModeEnregistrement"):
        assert getattr(seps, name) is not None
        assert name in seps.__all__

