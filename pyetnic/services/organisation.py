from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId, implId

def creer_organisation(num_adm_formation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=implId, **kwargs):
    """Créer une organisation."""
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "implId": impl_id,
            "numAdmFormation": num_adm_formation
        },
        "dateDebutOrganisation": date_debut,
        "dateFinOrganisation": date_fin
    }
    
    organisation_data.update(kwargs)
    
    headers = {"requestId": generate_request_id()}
    result = service.CreerOrganisation(_soapheaders=headers, **organisation_data)
    return serialize_object(result, dict)

def modifier_organisation(num_adm_formation, num_organisation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, **kwargs):
    """Modifier une organisation."""
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_data = {
        "id": {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        },
        "dateDebutOrganisation": date_debut,
        "dateFinOrganisation": date_fin
    }
    
    organisation_data.update(kwargs)
    
    headers = {"requestId": generate_request_id()}
    result = service.ModifierOrganisation(_soapheaders=headers, **organisation_data)
    return serialize_object(result, dict)

def lire_organisation(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """Lire une organisation."""
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.LireOrganisation(_soapheaders=headers, id=organisation_id)
    return serialize_object(result, dict)

def supprimer_organisation(num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
    """Supprimer une organisation."""
    manager = SoapClientManager("EpromFormationOrganisationService_external_v6.wsdl", "ORGANISATION")
    service = manager.get_service()
    
    organisation_id = {
        "anneeScolaire": annee_scolaire,
        "etabId": etab_id,
        "numAdmFormation": num_adm_formation,
        "numOrganisation": num_organisation
    }
    
    headers = {"requestId": generate_request_id()}
    result = service.SupprimerOrganisation(_soapheaders=headers, id=organisation_id)
    return serialize_object(result, dict)