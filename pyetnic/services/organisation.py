from datetime import datetime
from dataclasses import asdict
from .models import Organisation, OrganisationId, StatutDocument
from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId, implId, Config

class OrganisationService:
    """Service pour gérer les organisations de formation."""

    def __init__(self):
        """Initialise le service d'organisation."""
        self.client_manager = SoapClientManager("ORGANISATION")

    def lire_organisation(self, 
                          organisation_id: OrganisationId) -> Organisation:
        """Lit les informations d'une organisation de formation existante."""
        result = self.client_manager.call_service("LireOrganisation", id=asdict(organisation_id))
        
        if result and 'body' in result and 'response' in result['body'] and 'organisation' in result['body']['response']:
            org_data = result['body']['response']['organisation']
            
            return Organisation(
                id=organisation_id,
                dateDebutOrganisation=org_data['dateDebutOrganisation'],
                dateFinOrganisation=org_data['dateFinOrganisation'],
                nombreSemaineFormation=org_data['nombreSemaineFormation'],
                statutDocumentOrganisation=StatutDocument(**org_data['statut']) if org_data.get('statut') else None,
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
