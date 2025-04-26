"""
Module de base pour les clients SOAP.

Ce module fournit les classes et fonctions nécessaires pour créer et gérer
les connexions aux services SOAP d'ETNIC.
"""

import uuid
import logging
import urllib3
from importlib.resources import files, as_file

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.transports import Transport
from zeep.exceptions import Fault, TransportError
from requests import Session
from requests.exceptions import RequestException

from .config import Config

# Configuration du logging
logger = logging.getLogger(__name__)

# Désactivation des avertissements SSL pour le développement
if not Config.get_verify_ssl():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger.warning("Vérification SSL désactivée (mode développement). Ne pas utiliser en production.")

def get_wsdl_path(package, resource):
    """Obtient le chemin absolu d'un fichier WSDL depuis les ressources du package."""
    with as_file(files(package) / resource) as wsdl_path:
        return str(wsdl_path)

def generate_request_id():
    """Génère un identifiant unique pour les requêtes SOAP."""
    return str(uuid.uuid4())

class SoapError(Exception):
    """Exception personnalisée pour les erreurs SOAP."""
    
    def __init__(self, message, soap_fault=None, request_id=None):
        self.message = message
        self.soap_fault = soap_fault
        self.request_id = request_id
        super().__init__(self.message)

class SoapClientManager:
    """
    Gestionnaire de clients SOAP pour les services ETNIC.
    
    Cette classe s'occupe de créer et configurer les clients SOAP,
    en gérant l'authentification, le transport et les bindings.
    """
    
    _client_cache = {}
    
    def __init__(self, service_name):
        """
        Initialise un gestionnaire de client SOAP pour un service spécifique.
        
        Args:
            service_name (str): Nom du service (LISTE_FORMATIONS, ORGANISATION, DOCUMENT1, DOCUMENT2)
        
        Raises:
            ValueError: Si le service n'est pas reconnu
        """
        self.service_name = service_name
        self.service_config = Config.SERVICES.get(service_name)
        
        if not self.service_config:
            raise ValueError(f"Configuration manquante pour le service: {service_name}")

    def _initialize_client(self):
        if self.service_name in self._client_cache:
            return self._client_cache[self.service_name]

        logger.debug(f"Création d'un nouveau client SOAP pour {self.service_name}")
        session = Session()
        session.verify = Config.get_verify_ssl()
        transport = Transport(session=session)

        wsdl_path = get_wsdl_path('pyetnic.resources', self.service_config.wsdl_path)
        client = Client(wsdl_path, wsse=UsernameToken(Config.USERNAME, Config.PASSWORD), transport=transport)
        service = client.create_service(self.service_config.binding_name, self.service_config.endpoint)

        self._client_cache[self.service_name] = service
        return service

    def call_service(self, method_name, **kwargs):
        """
        Appelle une méthode du service SOAP avec gestion des erreurs.
        
        Args:
            method_name (str): Nom de la méthode à appeler
            **kwargs: Arguments à passer à la méthode
            
        Returns:
            dict: Réponse du service, sérialisée en dictionnaire
            
        Raises:
            SoapError: Si l'appel au service échoue
        """
        service = self._initialize_client()
        try:
            request_id = generate_request_id()
            method = getattr(service, method_name)
            result = method(_soapheaders={"requestId": request_id}, **kwargs)
            
            from zeep.helpers import serialize_object
            return serialize_object(result, dict)
            
        except (Fault, TransportError, RequestException, AttributeError) as e:
            error_msg = f"Erreur lors de l'appel à {method_name} sur {self.service_name}: {str(e)}"
            logger.error(f"{error_msg} (request_id: {request_id})")
            raise SoapError(error_msg, soap_fault=e, request_id=request_id)

    def get_service(self):
        """Retourne le service SOAP configuré."""
        return self._initialize_client()