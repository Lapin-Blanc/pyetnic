# pyetnic/config.py

"""
Configuration centralisée pour les services ETNIC.

Ce module gère le chargement et la validation des variables d'environnement
nécessaires pour l'authentification et les paramètres par défaut.
"""

import os
import logging
from dotenv import load_dotenv
from typing import NamedTuple

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class ServiceConfig(NamedTuple):
    endpoint: str
    wsdl_path: str
    binding_name: str

class Config:
    """Classe centralisée pour la configuration de l'application."""
    
    # Environnement (dev, prod, etc.)
    ENV = os.getenv('ENV', 'dev')
    
    # Identifiants d'authentification
    USERNAME = os.getenv(f"{ENV.upper()}_USERNAME")
    PASSWORD = os.getenv(f"{ENV.upper()}_PASSWORD")
    
    # Paramètres par défaut
    ANNEE_SCOLAIRE = os.getenv("DEFAULT_SCHOOLYEAR", "2023-2024")
    ETAB_ID = os.getenv("DEFAULT_ETABID")
    IMPL_ID = os.getenv("DEFAULT_IMPLID")
    
    # Configuration unifiée des services
    SERVICES = {
        "LISTE_FORMATIONS": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formations/liste/v2",
            wsdl_path="EpromFormationsListeService_external_v2.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formations/liste/v2}EPROMFormationsListeExternalV2Binding"
        ),
        "ORGANISATION": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/organisation/v6",
            wsdl_path="EpromFormationOrganisationService_external_v6.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/organisation/v6}EPROMFormationOrganisationExternalV6Binding"
        ),
        "DOCUMENT1": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/document1/v1",
            wsdl_path="EpromFormationDocument1Service_external_v1.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/document1/v1}EPROMFormationDocument1ExternalV1Binding"
        ),
        "DOCUMENT2": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/document2/v1",
            wsdl_path="EpromFormationDocument2Service_external_v1.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/document2/v1}EPROMFormationDocument2ExternalV1Binding"
        )
    }
    
    @classmethod
    def validate(cls):
        """Valide que toutes les variables d'environnement nécessaires sont définies."""
        missing = []
        
        if not cls.USERNAME:
            missing.append(f"{cls.ENV.upper()}_USERNAME")
        if not cls.PASSWORD:
            missing.append(f"{cls.ENV.upper()}_PASSWORD")
        
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