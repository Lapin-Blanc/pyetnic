from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId

def lire_document_1(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """Lire le document 1."""
    manager = SoapClientManager("DOCUMENT1")
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
    """Modifier le document 1."""
    manager = SoapClientManager("DOCUMENT1")
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
    """Approuver le document 1."""
    manager = SoapClientManager("DOCUMENT1")
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