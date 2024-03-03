import os
from pathlib import Path
from dotenv import load_dotenv

from zeep import Client
from zeep.wsse.username import UsernameToken
from importlib import resources


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

# PROD = serveur en production de l'ETNIC
PROD = False

load_dotenv("pyetnic.env")
if PROD:
    username = os.environ.get("USERNAME_PROD")
    password = os.environ.get("PASSWORD_PROD")
else:
    username = os.environ.get("USERNAME_DEV")
    password = os.environ.get("PASSWORD_DEV")

etabId = os.environ.get("DEFAULT_ETAB_ID")
implId = os.environ.get("DEFAULT_IMPL_ID")
anneeScolaire = os.environ.get("DEFAULT_SCHOOL_YEAR")


class SoapClientManager:
    def __init__(self, wsdl_subpath):
        package = 'pyetnic.resources'
        self.wsdl_path = get_wsdl_path(package, wsdl_subpath)
        self.client = None

    def get_client(self):
        if not self.client:
            self.client = Client(self.wsdl_path, wsse=UsernameToken(username, password))
        return self.client


def lister_formations_organisables(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    wsdl_subpath = "EpromFormationsListeService_external_v2.wsdl"
    manager = SoapClientManager(wsdl_subpath)
    client = manager.get_client()
    result = client.service.ListerFormationsOrganisables(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return result['body']['response']['formation']

def lister_formations(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    wsdl_subpath = "EpromFormationsListeService_external_v2.wsdl"
    manager = SoapClientManager(wsdl_subpath)
    client = manager.get_client()
    result = client.service.ListerFormations(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return result['body']['response']['formation']

def lire_organisation(num_adm_formation, num_organisation, annee_scolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationOrganisationService_external_v6.wsdl"
    manager = SoapClientManager(wsdl_subpath)
    client = manager.get_client()
    return client.service.LireOrganisation(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )

def lire_document_1(num_adm_formation, num_organisation, annee_scolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationDocument1Service_external_v1.wsdl"
    manager = SoapClientManager(wsdl_subpath)
    client = manager.get_client()
    return client.service.LireDocument1(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )

def lire_document_2(num_adm_formation, num_organisation, annee_scolaire, etab_id=etabId):
    wsdl_subpath = "EpromFormationDocument2Service_external_v1.wsdl"
    manager = SoapClientManager(wsdl_subpath)
    client = manager.get_client()
    return client.service.LireDocument2(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )