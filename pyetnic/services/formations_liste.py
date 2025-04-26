"""
Module pour le service de liste des formations.

Ce module fournit des fonctions pour lister les formations organisables
et les formations existantes avec leurs organisations.
"""

from typing import Dict, List, Any, Optional
import logging
from ..soap_client import SoapClientManager, generate_request_id, SoapError
from zeep.helpers import serialize_object
from ..config import Config, anneeScolaire, etabId, implId
from .models import Formation, Organisation, FormationsListeResult

# Configuration du logging
logger = logging.getLogger(__name__)

class FormationsListeService:
    """Service pour gérer les listes de formations."""
    
    def __init__(self):
        """Initialise le service de liste des formations."""
        self.client_manager = SoapClientManager("LISTE_FORMATIONS")
    
    def lister_formations_organisables(
        self,
        annee_scolaire: Optional[str] = anneeScolaire,
        etab_id: Optional[int] = etabId,
        impl_id: Optional[int] = None
    ) -> Dict[str, Any]:
        request_data = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id
        }
        if impl_id:
            request_data["implId"] = impl_id
        
        return self.client_manager.call_service("ListerFormationsOrganisables", **request_data)
    
    def lister_formations(self, annee_scolaire: Optional[str] = anneeScolaire, etab_id: Optional[int] = etabId, impl_id: Optional[int] = None) -> FormationsListeResult:
        try:
            result = self.client_manager.call_service("ListerFormations", anneeScolaire=annee_scolaire, etabId=etab_id, implId=impl_id)
            
            if result['body']['success']:
                formations = []
                for f in result['body']['response']['formation']:
                    organisations = [
                        Organisation(**org) 
                        for org in f.get('organisation', [])
                    ]
                    formations.append(Formation(
                        numAdmFormation=f['numAdmFormation'],
                        libelleFormation=f['libelleFormation'],
                        codeFormation=f['codeFormation'],
                        organisations=organisations
                    ))
                return FormationsListeResult(True, formations)
            else:
                return FormationsListeResult(False, [], messages=result['body'].get('messages', []))
        
        except SoapError as e:
            return FormationsListeResult(False, [], messages=[str(e)])

