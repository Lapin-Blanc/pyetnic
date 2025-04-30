from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId
from dataclasses import asdict
from .models import FormationDocument2, OrganisationId

class Document2Service:
    """Service pour gérer les opérations sur le document 2."""

    def __init__(self):
        """Initialise le service pour le document 2."""
        self.client_manager = SoapClientManager("DOCUMENT2")

    def lire_document_2(self, organisation_id: OrganisationId) -> FormationDocument2:
        """Lire les informations d'un document 2."""
        result = self.client_manager.call_service("LireDocument2", id=asdict(organisation_id))
        
        if result and 'body' in result and 'response' in result['body'] and 'document2' in result['body']['response']:
            doc_data = result['body']['response']['document2']
            
            # Conversion des données SOAP en objet FormationDocument2
            return FormationDocument2(
                id=organisation_id,
                activiteEnseignementDetail=doc_data.get('activiteEnseignementDetail'),
                interventionExterieureListe=doc_data.get('interventionExterieureListe'),
                swAppD2=doc_data.get('swAppD2', False),
                tsMaj=doc_data.get('tsMaj'),
                teUserMaj=doc_data.get('teUserMaj')
            )
        
        return None