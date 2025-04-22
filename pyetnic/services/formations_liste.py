"""
Module pour le service de liste des formations.

Ce module fournit des fonctions pour lister les formations organisables
et les formations existantes avec leurs organisations.
"""

from typing import Dict, List, Any, Optional
import logging
from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import Config, anneeScolaire, etabId, implId

# Configuration du logging
logger = logging.getLogger(__name__)

class FormationsListeService:
    """Service pour gérer les listes de formations."""
    
    def __init__(self):
        """Initialise le service de liste des formations."""
        self.client_manager = SoapClientManager("LISTE_FORMATIONS")
    
    def lister_formations_organisables(
        self,
        annee_scolaire: Optional[str] = anneeScolaire,
        etab_id: Optional[int] = etabId,
        impl_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Liste les formations organisables dans l'établissement.

        Args:
            annee_scolaire: Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de Config.
            etab_id: Identifiant FASE de l'établissement. Par défaut, utilise la valeur de Config.
            impl_id: Identifiant FASE de l'implantation. Si non fourni, liste pour toutes les implantations.

        Returns:
            Un dictionnaire contenant la liste des formations organisables, avec pour chaque formation :
                - numAdmFormation (int): Numéro administratif de la formation
                - libelleFormation (str): Libellé de la formation
                - codeFormation (str): Code de la formation

        Raises:
            SoapError: Si la requête échoue ou si les paramètres sont invalides.

        Notes:
            Si impl_id n'est pas fourni, la liste retournée concernera l'ensemble des implantations de l'établissement.
        """
        # Validation des paramètres
        if not annee_scolaire:
            logger.warning("Année scolaire non spécifiée, utilisation de la valeur par défaut")
        if not etab_id:
            logger.warning("Identifiant d'établissement non spécifié, utilisation de la valeur par défaut")
        
        # Préparation des paramètres de la requête
        request_data = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id
        }
        if impl_id:
            request_data["implId"] = impl_id
        
        # Appel au service
        return self.client_manager.call_service("ListerFormationsOrganisables", **request_data)
    
    def lister_formations(
        self,
        annee_scolaire: Optional[str] = anneeScolaire,
        etab_id: Optional[int] = etabId,
        impl_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Liste les formations organisables dans l'établissement, ainsi que les organisations avec le statut des différents documents.

        Args:
            annee_scolaire: Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de Config.
            etab_id: Identifiant FASE de l'établissement. Par défaut, utilise la valeur de Config.
            impl_id: Identifiant FASE de l'implantation. Si non fourni, liste pour toutes les implantations.

        Returns:
            Un dictionnaire contenant la liste des formations et leurs organisations, avec pour chaque formation :
                - numAdmFormation (int): Numéro administratif de la formation
                - libelleFormation (str): Libellé de la formation
                - codeFormation (str): Code de la formation
                - organisation (list): Liste des organisations de la formation
                  (voir documentation complète pour les détails)

        Raises:
            SoapError: Si la requête échoue ou si les paramètres sont invalides.

        Notes:
            Si impl_id n'est pas fourni, la liste retournée concernera l'ensemble des implantations de l'établissement.
        """
        # Validation des paramètres
        if not annee_scolaire:
            logger.warning("Année scolaire non spécifiée, utilisation de la valeur par défaut")
        if not etab_id:
            logger.warning("Identifiant d'établissement non spécifié, utilisation de la valeur par défaut")
        
        # Préparation des paramètres de la requête
        request_data = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id
        }
        if impl_id:
            request_data["implId"] = impl_id
        
        # Appel au service
        return self.client_manager.call_service("ListerFormations", **request_data)

# Fonctions compatibles avec l'API originale
def lister_formations_organisables(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    """Lister les formations organisables."""
    manager = SoapClientManager("LISTE_FORMATIONS")
    service = manager.get_service()
    
    request_data = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id
    }
    if impl_id:
        request_data["implId"] = impl_id
    
    headers = {"requestId": generate_request_id()}
    result = service.ListerFormationsOrganisables(_soapheaders=headers, **request_data)
    return serialize_object(result, dict)

def lister_formations(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    """Lister les formations avec organisations."""
    manager = SoapClientManager("LISTE_FORMATIONS")
    service = manager.get_service()
    
    request_data = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id
    }
    if impl_id:
        request_data["implId"] = impl_id
    
    headers = {"requestId": generate_request_id()}
    result = service.ListerFormations(_soapheaders=headers, **request_data)
    return serialize_object(result, dict)