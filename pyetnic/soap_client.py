"""
Module de base pour les clients SOAP.

Ce module fournit les classes et fonctions nécessaires pour créer et gérer
les connexions aux services SOAP d'ETNIC.
"""

import uuid
import logging
import urllib3
from importlib.resources import files, as_file
from functools import lru_cache

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
    request_id = str(uuid.uuid4())
    logger.debug(f"ID de requête généré: {request_id}")
    return request_id

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
    
    # Cache pour les clients SOAP (évite de recréer des instances pour les mêmes services)
    _client_cache = {}
    
    def __init__(self, service_name):
        """
        Initialise un gestionnaire de client SOAP pour un service spécifique.
        
        Args:
            service_name (str): Nom du service (LISTE_FORMATIONS, ORGANISATION, DOCUMENT1, DOCUMENT2)
        
        Raises:
            ValueError: Si le service n'est pas reconnu
            SoapError: Si la création du client échoue
        """
        self.service_name = service_name
        
        # Vérification que le service est valide
        if service_name not in Config.WSDL_PATHS:
            raise ValueError(f"Service inconnu: {service_name}")
        
        # Récupération du chemin WSDL et de l'endpoint
        wsdl_subpath = Config.WSDL_PATHS[service_name]
        self.endpoint = Config.ENDPOINTS[service_name]
        
        if not self.endpoint:
            logger.warning(f"Endpoint non défini pour le service {service_name}")
        
        # Création ou récupération du client SOAP depuis le cache
        cache_key = f"{service_name}_{Config.ENV}"
        
        if cache_key in self._client_cache:
            logger.debug(f"Utilisation du client SOAP en cache pour {service_name}")
            self.client = self._client_cache[cache_key]['client']
            self.service = self._client_cache[cache_key]['service']
        else:
            logger.debug(f"Création d'un nouveau client SOAP pour {service_name}")
            try:
                # Configuration de la session HTTP
                session = Session()
                session.verify = Config.get_verify_ssl()
                transport = Transport(session=session)
                
                # Chemin vers le fichier WSDL
                package = 'pyetnic.resources'
                wsdl_path = get_wsdl_path(package, wsdl_subpath)
                
                # Création du client avec authentification
                self.client = Client(
                    wsdl_path,
                    wsse=UsernameToken(Config.USERNAME, Config.PASSWORD),
                    transport=transport
                )
                
                # Détermination du binding
                binding_name = self._get_binding_name(wsdl_subpath)
                
                # Création du service avec le binding et l'endpoint appropriés
                self.service = self.client.create_service(binding_name, self.endpoint)
                
                # Mise en cache du client et du service
                self._client_cache[cache_key] = {
                    'client': self.client,
                    'service': self.service
                }
                
            except (Fault, TransportError, RequestException) as e:
                error_msg = f"Erreur lors de la création du client SOAP pour {service_name}: {str(e)}"
                logger.error(error_msg)
                raise SoapError(error_msg, soap_fault=e)
    
    def _get_binding_name(self, wsdl_subpath):
        """
        Détermine le nom du binding approprié en fonction du service.
        
        Args:
            wsdl_subpath (str): Chemin du fichier WSDL
            
        Returns:
            str: Nom du binding à utiliser
        """
        # Détermination du binding par analyse du nom du fichier WSDL
        if 'Document1' in wsdl_subpath:
            return "{http://services-web.etnic.be/eprom/formation/document1/v1}EPROMFormationDocument1ExternalV1Binding"
        elif 'Document2' in wsdl_subpath:
            return "{http://services-web.etnic.be/eprom/formation/document2/v1}EPROMFormationDocument2ExternalV1Binding"
        elif 'Organisation' in wsdl_subpath:
            return "{http://services-web.etnic.be/eprom/formation/organisation/v6}EPROMFormationOrganisationExternalV6Binding"
        elif 'FormationsListe' in wsdl_subpath:
            return "{http://services-web.etnic.be/eprom/formations/liste/v2}EPROMFormationsListeExternalV2Binding"
        else:
            # Fallback: utiliser le premier binding défini dans le WSDL
            return next(iter(self.client.wsdl.bindings))
    
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
        # Génération d'un ID de requête pour le traçage
        request_id = generate_request_id()
        
        try:
            # Récupération de la méthode à partir du nom
            method = getattr(self.service, method_name)
            
            # Appel de la méthode avec l'en-tête SOAP
            result = method(_soapheaders={"requestId": request_id}, **kwargs)
            
            # Sérialisation du résultat en dictionnaire
            from zeep.helpers import serialize_object
            return serialize_object(result, dict)
            
        except (Fault, TransportError, RequestException, AttributeError) as e:
            error_msg = f"Erreur lors de l'appel à {method_name} sur {self.service_name}: {str(e)}"
            logger.error(f"{error_msg} (request_id: {request_id})")
            raise SoapError(error_msg, soap_fault=e, request_id=request_id)
    
    def get_service(self):
        """Retourne le service SOAP configuré."""
        return self.service