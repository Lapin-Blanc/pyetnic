"""ETNIC nomenclature codes as typed Enums.

These Enums document the valid values for various ETNIC code fields.
They can be used for autocompletion and readability but are NOT enforced
at the dataclass level — the raw string value is always accepted.

Every Enum uses ``(str, Enum)`` so members compare equal to raw strings:

    >>> CodeSanction.REUSSITE == "RE"
    True

Values for SEPS enums are pinned against the XSD enumerations in
``pyetnic/resources/SEPS_Enregistrer_Inscription_2.1/xsd/inscription_v1.xsd``.
Values for ``TypeInterventionExterieure`` are the single-letter codes from
the Organisation v7 manual (validated 2025-06-10); the XSD type is a
free-form ``xs:string`` so they are not contract-validated, but they are the
values ETNIC actually accepts.

Usage:
    from pyetnic.nomenclatures import TypeInterventionExterieure, CodeSanction

    # Using the Enum (recommended for new code):
    org.typeInterventionExterieure = TypeInterventionExterieure.CONVENTION.value

    # Using the raw string (still works, always will):
    org.typeInterventionExterieure = "C"
"""

from __future__ import annotations

from enum import Enum


class TypeInterventionExterieure(str, Enum):
    """Types d'intervention extérieure pour une organisation.

    Used in ``Organisation.typeInterventionExterieure``. The XSD defines
    the field as ``xs:string`` — ETNIC expects the single-letter codes
    below (Organisation v7 manual, validated 2025-06-10), not the long
    French labels. Codes ``R`` (Récupération périodes) and ``S`` (CISCO
    Système) were removed by ETNIC and have no member here; reading a
    legacy organisation that still carries them works (the dataclass keeps
    the raw string, the Enum simply has no matching member).
    """

    AGENCE_QUALITE = "Q"
    CONVENTION = "C"
    DISCRIMINATIONS_POSITIVES = "D"
    EHR = "E"
    FONDS_EUROPEENS = "F"
    FORMATION_PUBLICS_INFRA_SCOLARISES = "I"
    FORMATIONS_CONTINUEES = "P"
    OCTROI_PERIODES_CABINET_PROJETS_TRANSVER = "K"
    OCTROI_PERIODES_SUPPLEMENTAIRES_BONUS = "B"
    PERSONNEL_NON_CHARGE_DE_COURS = "A"
    REORIENTATION_7TQ_7P = "J"
    UNION_EUROPEENNE = "U"
    VALIDATION_DES_COMPETENCES = "V"


class CodeAdmission(str, Enum):
    """Codes d'admission pour une inscription SEPS.

    Used in ``SepsAdmission.codeAdmission``. Values pinned against XSD
    ``CodeAdmissionType``.
    """

    REUSSITE = "REUSSITE"
    TITRE_BELGE = "TITREBEL"
    TITRE_ETRANGER = "TITREETR"
    AUTRE = "AUTRE"


class CodeSanction(str, Enum):
    """Codes de sanction de formation.

    Used in ``SepsSanction.codeSanction``. Values pinned against XSD
    ``CodeSanctionType``.
    """

    REUSSITE = "RE"
    ABANDON = "AB"
    EN_HORAIRE = "EH"


class MotifAbandon(str, Enum):
    """Motifs d'abandon.

    Used in ``SepsSanction.motifAbandon`` when ``codeSanction == "AB"``.
    Values pinned against XSD ``MotifAbandonType``.
    """

    TEMPS = "TPS"
    PROFESSIONNEL = "PRO"
    FAMILIAL = "FAM"
    SANTE = "SAN"
    ATTENTES = "ATT"
    MEMOIRE = "MEM"
    FORMATION_JEUNES = "FMJ"
    NUMERIQUE = "NUM"
    AUTRE = "AUT"
    INCONNU = "INC"


class DureeInoccupation(str, Enum):
    """Durée d'inoccupation.

    Used in ``SepsSpecificite.dureeInoccupation``. Values pinned against
    XSD ``DureeInoccupationType``.
    """

    ZERO = "C00"
    SIX_MOIS = "C06"
    DOUZE_MOIS = "C12"
    VINGT_QUATRE_MOIS = "C24"


class SituationMenage(str, Enum):
    """Situation de ménage.

    Used in ``SepsSpecificite.situationMenage``. Values pinned against
    XSD ``SituationMenageType``.
    """

    ISOLE = "ISOL"
    SANS_EMPLOI = "SSEM"
    UN_EMPLOI = "A1EM"
    INCONNU = "X"


# ---------------------------------------------------------------------------
# Backwards compatibility: preserve the legacy list constant.
# Derived from TypeInterventionExterieure so the two never drift.
# Will be deprecated in 0.2.0 and removed in 1.0.0.
# ---------------------------------------------------------------------------

TYPES_INTERVENTION_EXTERIEURE: list = [member.value for member in TypeInterventionExterieure]
