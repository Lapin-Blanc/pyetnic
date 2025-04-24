from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId

def lire_document_3(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """Lire le document 3."""
    manager = SoapClientManager("DOCUMENT3")
    service = manager.get_service()
    
    document_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.LireDocument3(_soapheaders=headers, id=document_id)
    return serialize_object(result, dict)

