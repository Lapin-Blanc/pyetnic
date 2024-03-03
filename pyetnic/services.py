import os
from pathlib import Path
from dotenv import load_dotenv

from zeep import Client
from zeep.wsse.username import UsernameToken

current_directory = Path(__file__).resolve().parent

# PROD = serveur en production de l'ETNIC
PROD = False

load_dotenv()
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
        self.wsdl_path = str(current_directory / wsdl_subpath)
        self.client = None

    def get_client(self):
        if not self.client:
            self.client = Client(self.wsdl_path, wsse=UsernameToken(username, password))
        return self.client

def lister_formations_organisables(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    manager = SoapClientManager("resources/EPROM_Formations_Liste_2.0/EpromFormationsListeService_external_v2.wsdl")
    client = manager.get_client()
    result = client.service.ListerFormationsOrganisables(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return result['body']['response']['formation']


def lister_formations(annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=None):
    manager = SoapClientManager("resources/EPROM_Formations_Liste_2.0/EpromFormationsListeService_external_v2.wsdl")
    client = manager.get_client()
    result = client.service.ListerFormations(
        anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id
    )
    return result['body']['response']['formation']


def lire_organisation(num_adm_formation, num_organisation, annee_scolaire, etab_id=etabId):
    manager = SoapClientManager("resources/EPROM_Formation_Organisation_6.0/EpromFormationOrganisationService_external_v6.wsdl")
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
    manager = SoapClientManager("resources/EPROM_Formation_Population_1.0/EpromFormationDocument1Service_external_v1.wsdl")
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
    manager = SoapClientManager("resources/EPROM_Formation_Periodes_1.0/EpromFormationDocument2Service_external_v1.wsdl")
    client = manager.get_client()
    return client.service.LireDocument2(
        id={
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation,
        }
    )
