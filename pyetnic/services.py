import os
import uuid
import urllib3
from dotenv import load_dotenv
from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object
from zeep.transports import Transport
from requests import Session
from importlib.resources import files, as_file

# Désactiver les warnings de sécurité
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

env = os.getenv('ENV', 'dev')
username = os.getenv(f"{env.upper()}_USERNAME")
password = os.getenv(f"{env.upper()}_PASSWORD")
anneeScolaire = os.getenv("DEFAULT_SCHOOLYEAR")
etabId = os.getenv("DEFAULT_ETABID")
implId = os.getenv("DEFAULT_IMPLID")


def get_wsdl_path(package, resource):
    with as_file(files(package) / resource) as wsdl_path:
        return str(wsdl_path)


class SoapClientManager:
    def __init__(self, wsdl_subpath, service_name):
        package = 'pyetnic.resources'
        self.wsdl_path = get_wsdl_path(package, wsdl_subpath)
        endpoint = os.getenv(f"{service_name}_{env.upper()}_ENDPOINT")
        
        session = Session()
        if env == "dev":
            session.verify = False  # Pour le développement seulement, à supprimer en production
        transport = Transport(session=session)
        
        self.client = Client(self.wsdl_path, wsse=UsernameToken(username, password), transport=transport)
        
        # Déterminer le binding correct en fonction du service
        if 'Document1' in wsdl_subpath:
            binding_name = "{http://services-web.etnic.be/eprom/formation/document1/v1}EPROMFormationDocument1ExternalV1Binding"
        elif 'Document2' in wsdl_subpath:
            binding_name = "{http://services-web.etnic.be/eprom/formation/document2/v1}EPROMFormationDocument2ExternalV1Binding"
        elif 'Organisation' in wsdl_subpath:
            binding_name = "{http://services-web.etnic.be/eprom/formation/organisation/v6}EPROMFormationOrganisationExternalV6Binding"
        elif 'FormationsListe' in wsdl_subpath:
            binding_name = "{http://services-web.etnic.be/eprom/formations/liste/v2}EPROMFormationsListeExternalV2Binding"
        else:
            binding_name = next(iter(self.client.wsdl.bindings))
        
        self.service = self.client.create_service(binding_name, endpoint)

    def get_service(self):
        return self.service

def generate_request_id():
    return str(uuid.uuid4())

# Fonctions pour EpromFormationOrganisation

def creer_organisation(num_adm_formation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=implId, **kwargs):
    """
    Crée une nouvelle organisation de formation.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        date_debut (str): Date de début de l'organisation de la formation (format 'YYYY-MM-DD').
        date_fin (str): Date de fin de l'organisation de la formation (format 'YYYY-MM-DD').
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        impl_id (int, optional): Identifiant FASE de l'implantation. Par défaut, utilise la valeur de implId.
        **kwargs: Arguments optionnels supplémentaires.

    Keyword Args:
        organisationPeriodesSupplOuEPT (bool): Flag autorisant l'organisation de périodes supplémentaires ou pour de l'expertise pédagogique et technique.
        valorisationAcquis (bool): Flag indiquant que la formation est pour la valorisation des acquis.
        enPrison (bool): Flag indiquant que la formation est donnée en prison.
        activiteFormation (bool): Flag indiquant que la formation est organisée dans le cadre des activités de formation.
        conseillerPrevention (bool): Flag indiquant si la formation est organisée uniquement dans le cadre de la mission de conseiller en prévention ou de DPO.
        enseignementHybride (bool): Flag indiquant que la formation est donnée en enseignement hybride.
        numOrganisation2AnneesScolaires (int): Numéro de l'organisation de la formation de l'année précédente qui est organisée sur deux années scolaires consécutives.
        typeInterventionExterieure (str): Code type d'intervention extérieure pour l'organisation de la formation.
        interventionExterieure50p (bool): Intervention d'un tiers de 50% ou plus dans l'organisation de la formation.

    Returns:
        dict: Un dictionnaire contenant les informations de l'organisation créée, incluant :
            - id (dict): Identifiant de l'organisation
            - dateDebutOrganisation (str): Date de début de l'organisation
            - dateFinOrganisation (str): Date de fin de l'organisation
            - nombreSemaineFormation (int): Nombre de semaines de formation
            - statut (dict): Statut de l'organisation
            - Autres champs optionnels selon les arguments fournis

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - La date de début d'organisation ne peut être inférieure à une date spécifique (voir documentation).
        - La date de fin d'organisation ne peut être supérieure à une date spécifique (voir documentation).
        - La date de fin d'organisation ne peut être supérieure d'un an à la date de début d'organisation.
    """
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "implId": impl_id,
            "numAdmFormation": num_adm_formation
        },
        "dateDebutOrganisation": date_debut,
        "dateFinOrganisation": date_fin
    }
    
    organisation_data.update(kwargs)
    
    headers = {"requestId": generate_request_id()}
    result = service.CreerOrganisation(_soapheaders=headers, **organisation_data)
    return serialize_object(result, dict)

def modifier_organisation(num_adm_formation, num_organisation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, **kwargs):
    """
    Modifie une organisation de formation existante.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        date_debut (str): Nouvelle date de début de l'organisation de la formation (format 'YYYY-MM-DD').
        date_fin (str): Nouvelle date de fin de l'organisation de la formation (format 'YYYY-MM-DD').
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        **kwargs: Arguments optionnels supplémentaires (voir creer_organisation pour la liste complète).

    Returns:
        dict: Un dictionnaire contenant les informations mises à jour de l'organisation.

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - Les mêmes restrictions sur les dates que pour creer_organisation s'appliquent.
        - La modification n'est pas possible si le statut des documents ne le permet pas.
    """
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        },
        "dateDebutOrganisation": date_debut,
        "dateFinOrganisation": date_fin
    }
    
    organisation_data.update(kwargs)
    
    headers = {"requestId": generate_request_id()}
    result = service.ModifierOrganisation(_soapheaders=headers, **organisation_data)
    return serialize_object(result, dict)

def lire_organisation(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """
    Lit les informations d'une organisation de formation existante.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.

    Returns:
        dict: Un dictionnaire contenant les informations de l'organisation, incluant :
            - id (dict): Identifiant de l'organisation
            - dateDebutOrganisation (str): Date de début de l'organisation
            - dateFinOrganisation (str): Date de fin de l'organisation
            - nombreSemaineFormation (int): Nombre de semaines de formation
            - Autres champs selon la configuration de l'organisation

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.
    """
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.LireOrganisation(_soapheaders=headers, id=organisation_id)
    return serialize_object(result, dict)

def supprimer_organisation(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """
    Supprime une organisation de formation existante.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.

    Returns:
        dict: Un dictionnaire indiquant le succès ou l'échec de l'opération.

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - La suppression n'est pas possible si le statut des documents ne le permet pas.
    """
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.SupprimerOrganisation(_soapheaders=headers, id=organisation_id)
    return serialize_object(result, dict)

# Fonctions pour EpromFormationDocument1

def lire_document_1(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """
    Lit les informations d'un document 1 (Doc 1D) pour une formation spécifique.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.

    Returns:
        dict: Un dictionnaire contenant les informations du document 1, incluant :
            - id (dict): Identifiant du document
            - (autres champs spécifiques au document 1, à compléter selon la documentation exacte)

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.
    """
    manager = SoapClientManager("EpromFormationDocument1Service_external_v1.wsdl", "DOCUMENT1")
    service = manager.get_service()
    
    document_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.LireDocument1(_soapheaders=headers, id=document_id)
    return serialize_object(result, dict)

def modifier_document_1(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId, populations_liste=None):
    """
    Modifie les informations d'un document 1 (Doc 1D) pour une formation spécifique.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        **kwargs: Arguments optionnels supplémentaires pour la modification du document 1.

    Returns:
        dict: Un dictionnaire contenant les informations mises à jour du document 1.

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - Les champs modifiables spécifiques doivent être précisés dans la documentation exacte du service.
    """
    manager = SoapClientManager("EpromFormationDocument1Service_external_v1.wsdl", "DOCUMENT1")
    service = manager.get_service()
    
    document_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
    }
    
    if populations_liste:
        document_data["populationListe"] = {
            "population": populations_liste
        }
       
    headers = {"requestId": generate_request_id()}
    result = service.ModifierDocument1(_soapheaders=headers, **document_data)
    return serialize_object(result, dict)

def approuver_document_1(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """
    Approuve un document 1 (Doc 1D) pour une formation spécifique.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.

    Returns:
        dict: Un dictionnaire indiquant le succès ou l'échec de l'opération d'approbation.

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - L'approbation peut être soumise à certaines conditions ou vérifications côté serveur.
    """
    manager = SoapClientManager("EpromFormationDocument1Service_external_v1.wsdl", "DOCUMENT1")
    service = manager.get_service()
    
    document_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.ApprouverDocument1(_soapheaders=headers, id=document_id)
    return serialize_object(result, dict)

# Fonctions pour EpromFormationsListe

def lister_formations_organisables(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    """
    Liste les formations organisables dans l'établissement.

    Args:
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        impl_id (int, optional): Identifiant FASE de l'implantation. Si non fourni, liste pour toutes les implantations.

    Returns:
        dict: Un dictionnaire contenant la liste des formations organisables, avec pour chaque formation :
            - numAdmFormation (int): Numéro administratif de la formation
            - libelleFormation (str): Libellé de la formation
            - codeFormation (str): Code de la formation

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - Si impl_id n'est pas fourni, la liste retournée concernera l'ensemble des implantations de l'établissement.
    """
    manager = SoapClientManager("EpromFormationsListeService_external_v2.wsdl", "LISTE_FORMATIONS")
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
    """
    Liste les formations organisables dans l'établissement, ainsi que les organisations avec le statut des différents documents.

    Args:
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        impl_id (int, optional): Identifiant FASE de l'implantation. Si non fourni, liste pour toutes les implantations.

    Returns:
        dict: Un dictionnaire contenant la liste des formations et leurs organisations, avec pour chaque formation :
            - numAdmFormation (int): Numéro administratif de la formation
            - libelleFormation (str): Libellé de la formation
            - codeFormation (str): Code de la formation
            - organisation (list): Liste des organisations de la formation, chacune contenant :
                - implId (int): Identifiant FASE de l'implantation (si recherche pour toutes les implantations)
                - numOrganisation (int): Numéro de l'organisation de la formation
                - dateDebutOrganisation (str): Date de début de l'organisation
                - dateFinOrganisation (str): Date de fin de l'organisation
                - statutDocumentOrganisation (dict): Statut du document d'organisation (Doc A)
                - statutDocumentPopulationPeriodes (dict): Statut du document des populations et périodes (Doc 2)
                - statutDocumentDroitsInscription (dict): Statut du document des droits d'inscription (Doc 1D)
                - statutDocumentAttributions (dict): Statut du document des attributions (Doc 3)

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        - Si impl_id n'est pas fourni, la liste retournée concernera l'ensemble des implantations de l'établissement.
        - Les statuts des documents sont représentés par un dictionnaire contenant 'statut' (str) et 'dateStatut' (str).
    """
    manager = SoapClientManager("EpromFormationsListeService_external_v2.wsdl", "LISTE_FORMATIONS")
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

# Fonctions pour EpromFormationDocument2

def lire_document_2(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """
    Lit les informations d'un document 2 (Doc 2) pour une formation spécifique.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.

    Returns:
        dict: Un dictionnaire contenant les informations du document 2, incluant :
            - id (dict): Identifiant du document
            - activiteEnseignementDetail (dict): Détails des activités d'enseignement
            - interventionExterieureListe (list): Liste des interventions extérieures
            - swAppD2 (bool): Indique si le document est approuvé par l'administration
            - tsMaj (str): Date de la dernière mise à jour
            - teUserMaj (str): Dernier utilisateur ayant modifié le document

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.
    """
    manager = SoapClientManager("EpromFormationDocument2Service_external_v1.wsdl", "DOCUMENT2")
    service = manager.get_service()
    
    document_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.LireDocument2(_soapheaders=headers, id=document_id)
    return serialize_object(result, dict)

def modifier_document_2(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId, activite_enseignement_liste=None, intervention_exterieure_liste=None):
    """
    Modifie les informations d'un document 2 (Doc 2) pour une formation spécifique.

    Args:
        num_adm_formation (int): Numéro administratif de la formation.
        num_organisation (int): Numéro de l'organisation de la formation.
        annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
        etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
        activite_enseignement_liste (list, optional): Liste des activités d'enseignement à modifier.
        intervention_exterieure_liste (list, optional): Liste des interventions extérieures à modifier.

    Returns:
        dict: Un dictionnaire contenant les informations mises à jour du document 2.

    Raises:
        Exception: Si la requête échoue ou si les paramètres sont invalides.

    Notes:
        Structure de activite_enseignement_liste:
        [
            {
                "coNumBranche": int,  # Numéro de l'activité d'enseignement (obligatoire)
                "nbEleveC1": int,  # Nombre d'élèves (facultatif)
                "nbPeriodePrevueAn1": float,  # Nombre de périodes prévues 1ère année (facultatif)
                "nbPeriodePrevueAn2": float,  # Nombre de périodes prévues 2ème année (facultatif)
                "nbPeriodeReelleAn1": float,  # Nombre de périodes réelles 1ère année (facultatif)
                "nbPeriodeReelleAn2": float,  # Nombre de périodes réelles 2ème année (facultatif)
                "coAdmReg": int,  # Numéro administratif Rgp (facultatif)
                "coOrgReg": int,  # Numéro d'organisation Rgp (facultatif)
                "coBraReg": int,  # Numéro d'activité d'enseignement Rgp (facultatif)
                "coEtuReg": str  # Année d'études Rgp (facultatif)
            },
            # ... autres activités d'enseignement
        ]

        Structure de intervention_exterieure_liste:
        [
            {
                "coNumIex": int,  # Numéro d'intervention (facultatif)
                "coCatCol": str,  # Code du type d'intervention extérieure (obligatoire)
                "coObjFse": str,  # Code du sous-type d'intervention extérieure (facultatif)
                "coRefPro": str,  # Code Projet global / Référence (facultatif)
                "coCriCee": str,  # Numéro agrément (facultatif)
                "periodeListe": {
                    "periode": [
                        {
                            "coCodePar": str,  # Code du type de périodes (obligatoire)
                            "nbPerAn1": float,  # Nombre de périodes pour l'année 1 (facultatif)
                            "nbPerAn2": float  # Nombre de périodes pour l'année 2 (facultatif)
                        },
                        # ... autres périodes
                    ]
                }
            },
            # ... autres interventions extérieures
        ]

    Important:
        - Le nombre maximum d'interventions extérieures est limité à 4.
        - Les codes pour coCatCol, coObjFse, et coCodePar doivent correspondre aux valeurs autorisées
          dans la documentation.
        - Le document ne peut pas être modifié s'il a déjà été approuvé par l'administration.
    """
    manager = SoapClientManager("EpromFormationDocument2Service_external_v1.wsdl", "DOCUMENT2")
    service = manager.get_service()
    
    document_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
    }
    
    if activite_enseignement_liste:
        document_data["activiteEnseignementListe"] = {
            "activiteEnseignement": activite_enseignement_liste
        }
    
    if intervention_exterieure_liste:
        document_data["interventionExterieureListe"] = {
            "interventionExterieure": intervention_exterieure_liste
        }

    headers = {"requestId": generate_request_id()}
    result = service.ModifierDocument2(_soapheaders=headers, **document_data)
    return serialize_object(result, dict)

