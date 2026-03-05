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
)

# Exceptions
from ..services.seps import NissMutationError

# Modèles
from ..services.models import (
    Etudiant,
    EtudiantDetails,
    EtudiantDetailsSave,
    SepsAdresse,
    SepsAdresseSave,
    SepsLocalite,
    SepsNaissance,
    SepsNaissanceSave,
    SepsDeces,
)

__all__ = [
    # Fonctions
    "lire_etudiant",
    "rechercher_etudiants",
    "enregistrer_etudiant",
    "modifier_etudiant",
    # Exceptions
    "NissMutationError",
    # Modèles (lecture)
    "Etudiant",
    "EtudiantDetails",
    "SepsAdresse",
    "SepsLocalite",
    "SepsNaissance",
    "SepsDeces",
    # Modèles (envoi)
    "EtudiantDetailsSave",
    "SepsAdresseSave",
    "SepsNaissanceSave",
]
