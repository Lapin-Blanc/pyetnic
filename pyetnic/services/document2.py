from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId

class Document2Service:
    """Service pour gérer les opérations sur le document 2."""

    def __init__(self):
        """Initialise le service pour le document 2."""
        self.client_manager = SoapClientManager("DOCUMENT2")

    def lire_document_2(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
        """Lire le document 2."""
        document_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        return self.client_manager.call_service("LireDocument2", id=document_id)

    def modifier_document_2(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId, activite_enseignement_liste=None, intervention_exterieure_liste=None):
        """Modifier le document 2."""
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

        return self.client_manager.call_service("ModifierDocument2", **document_data)