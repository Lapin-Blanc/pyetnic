"""Namespace public pour les services SEPS (Registre national / CFWB).

Authentification par certificat X509 (PFX). Fonctionne uniquement en production.
Prérequis : pip install pyetnic[seps]
"""

# Fonctions de service — singleton géré dans services/
from ..services import (
    lire_etudiant,
    rechercher_etudiants,
    enregistrer_etudiant,
    modifier_etudiant,
    mettre_a_jour_etudiant,
    rechercher_inscriptions,
    enregistrer_inscription,
    modifier_inscription,
    mettre_a_jour_inscription,
    lire_notifications,
)

# Exceptions
from ..services.seps_errors import (
    SepsEtnicError,
    SepsAuthError,
    NissMutationError,
    TropDeResultatsError,
    SepsValidationError,
    SepsNotFoundError,
    SepsUeInconnueError,
    SepsEtudiantInconnuError,
    SepsConflictError,
    SepsInscriptionExisteError,
    SepsEtudiantExisteError,
    SepsDoublonsError,
    SepsAucuneModificationError,
)

# Nomenclatures — typed Enums (H9)
from ..nomenclatures import (
    CodeAdmission,
    CodeSanction,
    MotifAbandon,
    DureeInoccupation,
    SituationMenage,
    # Énumérations inscription (inscription_v1.xsd)
    CodeStatut,
    Indicateur,
    IndicateurX,
    MotifExemption,
    MotifExemptionSpec,
    TypeEnseignement,
    TitreDelivre,
    Equivalence,
    ValorisationAcquis,
    ValorisationAcquisSanction,
    StatutFinFormation,
    CodeNiveau,
    CodeNotification,
)

# Modèles
from ..services.models import (
    # Résultats des écritures
    SepsMessage,
    SepsEcritureResult,
    EnregistrerEtudiantResult,
    ModifierEtudiantResult,
    InscriptionResult,
    # Étudiant
    Etudiant,
    EtudiantDetails,
    EtudiantDetailsSave,
    SepsAdresse,
    SepsAdresseSave,
    SepsLocalite,
    SepsNaissance,
    SepsNaissanceSave,
    SepsDeces,
    # Inscription (lecture)
    Inscription,
    SepsUE,
    SepsLieuCours,
    SepsSpecificite,
    SepsDroitInscription,
    SepsExempteDroitInscription,
    SepsDroitInscriptionSpecifique,
    SepsExempteDroitInscriptionSpec,
    SepsAdmission,
    SepsSanction,
    SepsAudit,
    SepsNotification,
    # Inscription (envoi)
    InscriptionInputDataSave,
    InscriptionInputSave,
    SepsUESave,
    SepsSpecificiteSave,
)

__all__ = [
    # Fonctions
    "lire_etudiant",
    "rechercher_etudiants",
    "enregistrer_etudiant",
    "modifier_etudiant",
    "mettre_a_jour_etudiant",
    # Exceptions (base → spécialisées)
    "SepsEtnicError",
    "SepsAuthError",
    "NissMutationError",
    "TropDeResultatsError",
    "SepsValidationError",
    "SepsNotFoundError",
    "SepsUeInconnueError",
    "SepsEtudiantInconnuError",
    "SepsConflictError",
    "SepsInscriptionExisteError",
    "SepsEtudiantExisteError",
    "SepsDoublonsError",
    "SepsAucuneModificationError",
    # Résultats des écritures
    "SepsMessage",
    "SepsEcritureResult",
    "EnregistrerEtudiantResult",
    "ModifierEtudiantResult",
    "InscriptionResult",
    # Modèles (lecture)
    "Etudiant",
    "EtudiantDetails",
    "SepsAdresse",
    "SepsLocalite",
    "SepsNaissance",
    "SepsDeces",
    # Modèles étudiant (envoi)
    "EtudiantDetailsSave",
    "SepsAdresseSave",
    "SepsNaissanceSave",
    # Fonctions inscription
    "rechercher_inscriptions",
    "enregistrer_inscription",
    "modifier_inscription",
    "mettre_a_jour_inscription",
    # Notifications
    "lire_notifications",
    "SepsNotification",
    "CodeNotification",
    # Modèles inscription (lecture)
    "Inscription",
    "SepsUE",
    "SepsLieuCours",
    "SepsSpecificite",
    "SepsDroitInscription",
    "SepsExempteDroitInscription",
    "SepsDroitInscriptionSpecifique",
    "SepsExempteDroitInscriptionSpec",
    "SepsAdmission",
    "SepsSanction",
    "SepsAudit",
    # Modèles inscription (envoi)
    "InscriptionInputDataSave",
    "InscriptionInputSave",
    "SepsUESave",
    "SepsSpecificiteSave",
    # Nomenclatures
    "CodeAdmission",
    "CodeSanction",
    "MotifAbandon",
    "DureeInoccupation",
    "SituationMenage",
    # Nomenclatures inscription (inscription_v1.xsd)
    "CodeStatut",
    "Indicateur",
    "IndicateurX",
    "MotifExemption",
    "MotifExemptionSpec",
    "TypeEnseignement",
    "TitreDelivre",
    "Equivalence",
    "ValorisationAcquis",
    "ValorisationAcquisSanction",
    "StatutFinFormation",
    "CodeNiveau",
]
