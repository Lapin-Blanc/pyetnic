"""
Configuration centralisée pour les services ETNIC.

Ce module gère le chargement et la validation des variables d'environnement
nécessaires pour l'authentification et les paramètres par défaut.
"""

import os
import logging
from dotenv import load_dotenv

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Classe centralisée pour la configuration de l'application."""
    
    # Environnement (dev, prod, etc.)
    ENV = os.getenv('ENV', 'dev')
    
    # Identifiants d'authentification
    USERNAME = os.getenv(f"{ENV.upper()}_USERNAME")
    PASSWORD = os.getenv(f"{ENV.upper()}_PASSWORD")
    
    # Paramètres par défaut
    ANNEE_SCOLAIRE = os.getenv("DEFAULT_SCHOOLYEAR")
    ETAB_ID = os.getenv("DEFAULT_ETABID")
    IMPL_ID = os.getenv("DEFAULT_IMPLID")
    
    # Endpoints des services
    ENDPOINTS = {
        "LISTE_FORMATIONS": os.getenv(f"LISTE_FORMATIONS_{ENV.upper()}_ENDPOINT"),
        "ORGANISATION": os.getenv(f"ORGANISATION_{ENV.upper()}_ENDPOINT"),
        "DOCUMENT1": os.getenv(f"DOCUMENT1_{ENV.upper()}_ENDPOINT"),
        "DOCUMENT2": os.getenv(f"DOCUMENT2_{ENV.upper()}_ENDPOINT"),
        "DOCUMENT3": os.getenv(f"DOCUMENT3_{ENV.upper()}_ENDPOINT"),
    }
    
    # Mapping des services vers leurs fichiers WSDL
    WSDL_PATHS = {
        "LISTE_FORMATIONS": "EpromFormationsListeService_external_v2.wsdl",
        "ORGANISATION": "EpromFormationOrganisationService_external_v6.wsdl",
        "DOCUMENT1": "EpromFormationDocument1Service_external_v1.wsdl",
        "DOCUMENT2": "EpromFormationDocument2Service_external_v1.wsdl",
        "DOCUMENT3": "EpromFormationDocument3Service_external_v1.wsdl",
    }
    
    @classmethod
    def validate(cls):
        """Valide que toutes les variables d'environnement nécessaires sont définies."""
        missing = []
        
        if not cls.USERNAME:
            missing.append(f"{cls.ENV.upper()}_USERNAME")
        if not cls.PASSWORD:
            missing.append(f"{cls.ENV.upper()}_PASSWORD")
        
        # Vérification des endpoints
        for service, endpoint in cls.ENDPOINTS.items():
            if not endpoint:
                missing.append(f"{service}_{cls.ENV.upper()}_ENDPOINT")
        
        if missing:
            logger.warning(f"Variables d'environnement manquantes : {', '.join(missing)}")
            return False
        
        return True
    
    @classmethod
    def get_verify_ssl(cls):
        """Retourne si la vérification SSL doit être activée."""
        return cls.ENV != "dev"

# Variables exposées pour la compatibilité avec le code existant
anneeScolaire = Config.ANNEE_SCOLAIRE
etabId = Config.ETAB_ID
implId = Config.IMPL_ID

# Validation initiale de la configuration
if not Config.validate():
    logger.warning("Configuration incomplète. Certaines fonctionnalités pourraient ne pas fonctionner correctement.")