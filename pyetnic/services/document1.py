from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId

class Document1Service:
    """Service pour gérer les opérations sur le document 1."""

    def __init__(self):
        """Initialise le service pour le document 1."""
        self.client_manager = SoapClientManager("DOCUMENT1")

    def lire_document_1(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
        """Lire le document 1."""
        document_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        return self.client_manager.call_service("LireDocument1", id=document_id)

    def modifier_document_1(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId, populations_liste=None):
        """Modifier le document 1."""
        document_data = {
            "id": {
                "anneeScolaire": annee_scolaire,
                "etabId": etab_id,
                "numAdmFormation": num_adm_formation,
                "numOrganisation": num_organisation
            }
        }
        
        if populations_liste:
            document_data["populationsListe"] = populations_liste

        return self.client_manager.call_service("ModifierDocument1", **document_data)

    def approuver_document_1(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
        """Approuver le document 1."""
        document_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        return self.client_manager.call_service("ApprouverDocument1", id=document_id)