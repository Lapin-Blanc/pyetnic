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


class CodeStatut(str, Enum):
    """Statut d'une inscription (CodeStatutType).

    Used in ``Inscription.statut`` / ``InscriptionInputSave.statut``.
    Values pinned against XSD ``CodeStatutType``.
    """

    DEFINITIVE = "DE"
    ANNULEE = "AN"


class Indicateur(str, Enum):
    """Indicateur booléen ETNIC (IndicateurType) : oui / non.

    Pilote les nombreux champs ``"O"`` / ``"N"`` du contrat inscription
    (``regulier1`` / ``regulier5``, ``enfantACharge``, ``fse``, les
    indicateurs DI/DIS…). Values pinned against XSD ``IndicateurType``.
    """

    OUI = "O"
    NON = "N"


class IndicateurX(str, Enum):
    """Indicateur ternaire (IndicateurXType) : oui / non / n'accepte pas de préciser.

    Distinct de :class:`Indicateur` (qui n'accepte pas ``"X"``). Utilisé par
    ``SepsSpecificite.difficulteHandicap`` et ``difficulteAutre``. Values
    pinned against XSD ``IndicateurXType``.
    """

    OUI = "O"
    NON = "N"
    NON_PRECISE = "X"


class MotifExemption(str, Enum):
    """Motif d'exemption du droit d'inscription (MotifExemptionType, DI).

    Used in ``SepsExempteDroitInscription.motifExemption``. Libellés : cf.
    circulaire 9593 (spec 14). Values pinned against XSD ``MotifExemptionType``.
    """

    MINEUR = "C01"                  # Mineur soumis à l'obligation scolaire
    CHOMEUR_INDEMNISE = "C02"       # Chômeur complet indemnisé
    HANDICAP = "C03"                # Étudiant avec handicap reconnu
    RIS = "C04"                     # Bénéficiaire du revenu d'intégration (RIS)
    PERSONNEL_ENSEIGNANT = "C05"    # Personnel enseignant en formation continuée
    AUTORITE_PUBLIQUE = "C06"       # Obligation d'une autorité publique
    AUTRE = "C07"                   # Autre


class MotifExemptionSpec(str, Enum):
    """Motif d'exemption du droit d'inscription spécifique (MotifExemptionSpecType, DIS).

    Réservé aux étudiants de nationalité hors CEE (sinon erreur 30023).
    Used in ``SepsExempteDroitInscriptionSpec.motifExemptionSpec``. Members are
    the raw codes; the 13 motifs (manuel §3.1.11) are:

    - C01 Soumis à l'obligation scolaire
    - C02 Ressortissant d'un État membre UE
    - C03 Parents/tuteur belges
    - C04 Parents/tuteur (non belges) résidant en Belgique
    - C05 Marié/cohabitant avec conjoint résidant en Belgique
    - C06 Résidant en Belgique avec activité prof. ou revenu de remplacement
    - C07 Réfugié ou candidat réfugié reconnu
    - C08 Pris en charge par le CPAS
    - C09 Admis à séjourner > 3 mois (loi 15/12/1980)
    - C10 Demande de régularisation (loi 15/12/1980)
    - C11 Placé par le juge de la jeunesse
    - C12 Sous tutelle officieuse (Code civil)
    - C13 Visé par l'art. 42bis du décret du 30/06/1998

    Values pinned against XSD ``MotifExemptionSpecType``. ⚠️ Préfixe ``C0x``
    partagé avec :class:`MotifExemption` mais sémantique différente.
    """

    C01 = "C01"
    C02 = "C02"
    C03 = "C03"
    C04 = "C04"
    C05 = "C05"
    C06 = "C06"
    C07 = "C07"
    C08 = "C08"
    C09 = "C09"
    C10 = "C10"
    C11 = "C11"
    C12 = "C12"
    C13 = "C13"


class TypeEnseignement(str, Enum):
    """Type d'enseignement (TypeEnseignementType).

    Used in ``SepsAdmission.typeEnseignement`` (obligatoire si
    ``codeAdmission == "TITREBEL"``). PRI primaire ; SIPE/SSPE secondaire
    inf./sup. plein exercice ; SIPS/SSPS secondaire inf./sup. promotion
    sociale ; SCPE/SLPE supérieur court/long plein exercice ; SCPS/SLPS
    supérieur court/long promotion sociale. Pinned against XSD
    ``TypeEnseignementType``.
    """

    PRI = "PRI"
    SIPE = "SIPE"
    SSPE = "SSPE"
    SIPS = "SIPS"
    SSPS = "SSPS"
    SCPE = "SCPE"
    SLPE = "SLPE"
    SCPS = "SCPS"
    SLPS = "SLPS"


class TitreDelivre(str, Enum):
    """Titre délivré (TitreDelivreType, 23 valeurs).

    Used in ``SepsAdmission.titreDelivre`` (obligatoire si
    ``codeAdmission == "TITREBEL"``, applicabilité selon ``typeEnseignement``).
    Members are the canonical ETNIC codes. Pinned against XSD
    ``TitreDelivreType``.
    """

    CEB = "CEB"
    CE1D = "CE1D"
    CESI = "CESI"
    CE2D = "CE2D"
    CQ4 = "CQ4"
    CESSG = "CESSG"
    CESST = "CESST"
    CESSQ = "CESSQ"
    CESSP = "CESSP"
    CESSA = "CESSA"
    CE6P = "CE6P"
    CQ6 = "CQ6"
    CQ7 = "CQ7"
    DAES = "DAES"
    BES = "BES"
    BACH = "BACH"
    MAST = "MAST"
    CESS = "CESS"
    CQSUP = "CQSUP"
    CQINF = "CQINF"
    MASTSPE = "MASTSPE"
    DOC = "DOC"
    BACHSPE = "BACHSPE"


class Equivalence(str, Enum):
    """Équivalence d'un titre étranger (EquivalenceType).

    Used in ``SepsAdmission.equivalence`` (obligatoire si
    ``codeAdmission == "TITREETR"``). Pinned against XSD ``EquivalenceType``.
    """

    SECONDAIRE_INFERIEUR = "C01"
    SECONDAIRE_SUPERIEUR = "C02"
    SUPERIEUR = "C03"
    CEB = "C04"


class ValorisationAcquis(str, Enum):
    """Valorisation des acquis à l'admission (ValorisationAcquisType).

    Used in ``SepsAdmission.valorisationAcquis`` (obligatoire si
    ``codeAdmission == "AUTRE"``). C01-C04 valorisation formelle V1-V4 ;
    C10 VANFI Test/Épreuve ; C20 VANFI Dossier ; C30 Autres ; C40 Aucun titre
    requis. Distinct de :class:`ValorisationAcquisSanction`. Pinned against
    XSD ``ValorisationAcquisType``.
    """

    C01 = "C01"
    C02 = "C02"
    C03 = "C03"
    C04 = "C04"
    C10 = "C10"
    C20 = "C20"
    C30 = "C30"
    C40 = "C40"


class ValorisationAcquisSanction(str, Enum):
    """Valorisation des acquis en sanction (ValorisationAcquisSanctionType).

    Used in ``SepsSanction.valorisationAcquisSanction`` (obligatoire si
    ``codeSanction == "RE"``). C00 Réussite ; C01-C04 valorisation formelle
    V1-V4 ; C05 VANFI Test/Épreuves. Distinct de :class:`ValorisationAcquis`
    (pas de C00/C05, mais C10-C40). Pinned against XSD
    ``ValorisationAcquisSanctionType``.
    """

    C00 = "C00"
    C01 = "C01"
    C02 = "C02"
    C03 = "C03"
    C04 = "C04"
    C05 = "C05"


class StatutFinFormation(str, Enum):
    """Statut de fin de formation (StatutFinFormationType, FSE).

    Used in ``SepsSanction.statutFinFormation`` (obligatoire si UE FSE).
    ⚠️ Le XSD impose ``C01``-``C06`` ; le manuel PDF écrit ``01``-``06`` (sans
    « C ») — **le XSD fait foi**.

    - C01 Mise à l'emploi après la formation
    - C02 Poursuite d'une formation dans le cadre du PI
    - C03 Poursuite d'une formation hors du cadre du PI
    - C04 Aide à la recherche d'emploi après la formation
    - C05 Réorientation vers un autre type d'action
    - C06 Fin de formation sans suite connue
    """

    C01 = "C01"
    C02 = "C02"
    C03 = "C03"
    C04 = "C04"
    C05 = "C05"
    C06 = "C06"


class CodeNiveau(str, Enum):
    """Code niveau d'une UE (CodeNiveauType).

    Used in ``SepsUE.codeNiveau`` (lecture). Pinned against XSD
    ``CodeNiveauType``.
    """

    SI = "SI"
    SS = "SS"
    SC = "SC"
    SL = "SL"


# ---------------------------------------------------------------------------
# Backwards compatibility: preserve the legacy list constant.
# Derived from TypeInterventionExterieure so the two never drift.
# Will be deprecated in 0.2.0 and removed in 1.0.0.
# ---------------------------------------------------------------------------

TYPES_INTERVENTION_EXTERIEURE: list = [member.value for member in TypeInterventionExterieure]
