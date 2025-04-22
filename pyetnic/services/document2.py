from ..services import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId

def lire_document_2(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """Lire le document 2."""
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
    """Modifier le document 2."""
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