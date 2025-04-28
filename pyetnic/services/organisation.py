from datetime import datetime
from .models import Organisation
from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId, implId, Config

class OrganisationService:
    """Service pour gérer les organisations de formation."""

    def __init__(self):
        """Initialise le service d'organisation."""
        self.client_manager = SoapClientManager("ORGANISATION")

    def lire_organisation(self, 
                          num_adm_formation, 
                          num_organisation, 
                          annee_scolaire=Config.ANNEE_SCOLAIRE, 
                          etab_id=Config.ETAB_ID):
        """Lit les informations d'une organisation de formation existante."""
        organisation_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        
        result = self.client_manager.call_service("LireOrganisation", id=organisation_id)
        
        if result and 'body' in result and 'response' in result['body'] and 'organisation' in result['body']['response']:
            org_data = result['body']['response']['organisation']
            print(org_data)
            return
            return Organisation(
                anneeScolaire=org_data['id']['anneeScolaire'],
                etabId=org_data['id']['etabId'],
                implId=org_data['id']['implId'],
                numAdmFormation=org_data['id']['numAdmFormation'],
                numOrganisation=org_data['id']['numOrganisation'],
                dateDebutOrganisation=datetime.strptime(org_data['dateDebutOrganisation'], '%Y-%m-%d').date(),
                dateFinOrganisation=datetime.strptime(org_data['dateFinOrganisation'], '%Y-%m-%d').date(),
                nombreSemaineFormation=org_data['nombreSemaineFormation'],
                statut=org_data['statut'],
                organisationPeriodesSupplOuEPT=org_data.get('organisationPeriodesSupplOuEPT'),
                valorisationAcquis=org_data.get('valorisationAcquis'),
                enPrison=org_data.get('enPrison'),
                activiteFormation=org_data.get('activiteFormation'),
                conseillerPrevention=org_data.get('conseillerPrevention'),
                enseignementHybride=org_data.get('enseignementHybride'),
                numOrganisation2AnneesScolaires=org_data.get('numOrganisation2AnneesScolaires'),
                typeInterventionExterieure=org_data.get('typeInterventionExterieure'),
                interventionExterieure50p=org_data.get('interventionExterieure50p')
            )
        
        return None
