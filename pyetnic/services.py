import os
from pathlib import Path
from dotenv import load_dotenv

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object
from importlib import resources

load_dotenv()

env = os.getenv('ENV', 'dev')
username = os.getenv(f"{env.upper()}_USERNAME")
password = os.getenv(f"{env.upper()}_PASSWORD")
etabId = os.getenv("DEFAULT_ETABID")
implId = os.getenv("DEFAULT_IMPLID")
anneeScolaire = os.getenv("DEFAULT_SCHOOLYEAR")


def get_wsdl_path(package, resource):
    """
    Récupère le chemin d'accès d'un fichier WSDL dans le package de ressources.
    
    Parameters:
        package (str): Le nom du package où se trouve le fichier WSDL.
        resource (str): Le nom du fichier WSDL à charger.
    
    Returns:
        str: Le chemin d'accès au fichier WSDL.
    """
    with resources.path(package, resource) as wsdl_path:
        return str(wsdl_path)


class SoapClientManager:
    def __init__(self, wsdl_subpath, service_name):
        package = 'pyetnic.resources'
        self.wsdl_path = get_wsdl_path(package, wsdl_subpath)
        endpoint = os.getenv(f"{service_name.upper()}_{env.upper()}_ENDPOINT")
        self.client = Client(self.wsdl_path, wsse=UsernameToken(username, password))
        binding_name = next(iter(self.client.wsdl.bindings))
        self.service = self.client.create_service(binding_name, endpoint)

    def get_service(self):
        return self.service


def lister_formations_organisables(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    wsdl_subpath = "EpromFormationsListeService_external_v2.wsdl"
    manager = SoapClientManager(wsdl_subpath, "LISTE_FORMATIONS")
    service = manager.get_service()
    result = service.ListerFormationsOrganisables(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return serialize_object(result['body']['response']['formation'], dict)


def lister_formations(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    wsdl_subpath = "EpromFormationsListeService_external_v2.wsdl"
    manager = SoapClientManager(wsdl_subpath, "LISTE_FORMATIONS")
    service = manager.get_service()
    result = service.ListerFormations(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return serialize_object(result['body']['response']['formation'], dict)


def lire_organisation(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationOrganisationService_external_v6.wsdl"
    manager = SoapClientManager(wsdl_subpath, "ORGANISATION")
    service = manager.get_service()
    result = service.LireOrganisation(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )
    return serialize_object(result['body']['response'], dict)

def lire_document_1(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationDocument1Service_external_v1.wsdl"
    manager = SoapClientManager(wsdl_subpath, "DOCUMENT1")
    service = manager.get_service()
    result = service.LireDocument1(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )
    return serialize_object(result['body']['response'], dict)

def lire_document_2(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationDocument2Service_external_v1.wsdl"
    manager = SoapClientManager(wsdl_subpath, "DOCUMENT2")
    service = manager.get_service()
    result = service.LireDocument2(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )
    return serialize_object(result['body']['response']['document2'], dict)