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
    rechercher_inscriptions,
    enregistrer_inscription,
    modifier_inscription,
)

# Exceptions
from ..services.seps import SepsEtnicError, SepsAuthError, NissMutationError, TropDeResultatsError

# Nomenclatures — typed Enums (H9)
from ..nomenclatures import (
    CodeAdmission,
    CodeSanction,
    MotifAbandon,
    DureeInoccupation,
    SituationMenage,
)

# Modèles
from ..services.models import (
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
    # Exceptions (base → spécialisées)
    "SepsEtnicError",
    "SepsAuthError",
    "NissMutationError",
    "TropDeResultatsError",
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
]
