"""
Module pour le service de liste des formations.

Ce module fournit des fonctions pour lister les formations organisables
et les formations existantes avec leurs organisations.
"""

from typing import Any, Optional
from ..soap_client import SoapClientManager, SoapError
from ..config import Config
from .models import Formation, FormationsListeResult, Organisation, OrganisationId, StatutDocument
import logging
from pprint import pprint, pformat

# Configuration du logging
logger = logging.getLogger(__name__)


class FormationsListeService:
    """Service pour gérer les listes de formations."""
    
    def __init__(self):
        """Initialise le service de liste des formations."""
        self.client_manager = SoapClientManager("LISTE_FORMATIONS")
    
    def lister_formations_organisables(
        self,
        annee_scolaire: str = Config.ANNEE_SCOLAIRE,
        etab_id: int = Config.ETAB_ID,
        impl_id: int = Config.IMPL_ID
    ) -> FormationsListeResult:
        try:
            request_data = {
                "anneeScolaire": annee_scolaire,
                "etabId": etab_id,
                "implId": impl_id,
            }
            
            result = self.client_manager.call_service("ListerFormationsOrganisables", **request_data)
            
            if result['body']['success']:
                formations = []
                for f in result['body']['response'].get('formation', []):
                    formations.append(Formation(
                        numAdmFormation=f['numAdmFormation'],
                        libelleFormation=f['libelleFormation'],
                        codeFormation=f['codeFormation'],
                        organisations=[]  # Liste vide car pas d'organisations pour les formations organisables
                    ))
                return FormationsListeResult(True, formations)
            else:
                return FormationsListeResult(False, [], messages=result['body'].get('messages', []))
        
        except SoapError as e:
            return FormationsListeResult(False, [], messages=[str(e)])
        except Exception as e:
            return FormationsListeResult(False, [], messages=[f"Une erreur inattendue s'est produite : {str(e)}"])

    def lister_formations(
        self,
        annee_scolaire: str = Config.ANNEE_SCOLAIRE,
        etab_id: int = Config.ETAB_ID,
        impl_id: int = Config.IMPL_ID
    ) -> FormationsListeResult:
        logger.info("Appel de lister_formations")
        try:
            request_data = {
                "anneeScolaire": annee_scolaire,
                "etabId": etab_id,
                "implId": impl_id,
            }
            
            result = self.client_manager.call_service("ListerFormations", **request_data)
            if result['body']['success']:
                logger.debug(f"Résultat : {pformat(result)}")
                formations = []
                for f in result['body']['response']['formation']:
                    logger.debug(f"Formation : {pformat(f)}")
                    organisations = []
                    for org_data in f.get('organisation', []):
                        logger.debug(f"Organisation : {pformat(org_data)}")
                        org_id = OrganisationId(
                            anneeScolaire=annee_scolaire,
                            etabId=etab_id,
                            numAdmFormation=f['numAdmFormation'],
                            numOrganisation=org_data['numOrganisation'],
                        )
                        organisation = Organisation(
                            id=org_id,
                            dateDebutOrganisation=org_data['dateDebutOrganisation'],
                            dateFinOrganisation=org_data['dateFinOrganisation'],
                            nombreSemaineFormation=org_data.get('nombreSemaineFormation'),
                            organisationPeriodesSupplOuEPT=org_data.get('organisationPeriodesSupplOuEPT'),
                            valorisationAcquis=org_data.get('valorisationAcquis'),
                            enPrison=org_data.get('enPrison'),
                            activiteFormation=org_data.get('activiteFormation'),
                            conseillerPrevention=org_data.get('conseillerPrevention'),
                            enseignementHybride=org_data.get('enseignementHybride'),
                            numOrganisation2AnneesScolaires=org_data.get('numOrganisation2AnneesScolaires'),
                            typeInterventionExterieure=org_data.get('typeInterventionExterieure'),
                            interventionExterieure50p=org_data.get('interventionExterieure50p'),
                            statutDocumentOrganisation=StatutDocument(**org_data['statutDocumentOrganisation']) if org_data.get('statutDocumentOrganisation') else None,
                            statutDocumentPopulationPeriodes=StatutDocument(**org_data['statutDocumentPopulationPeriodes']) if org_data.get('statutDocumentPopulationPeriodes') else None,
                            statutDocumentDroitsInscription=StatutDocument(**org_data['statutDocumentDroitsInscription']) if org_data.get('statutDocumentDroitsInscription') else None,
                            statutDocumentAttributions=StatutDocument(**org_data['statutDocumentAttributions']) if org_data.get('statutDocumentAttributions') else None
                        )
                        organisations.append(organisation)
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
        except Exception as e:
            return FormationsListeResult(False, [], messages=[f"Une erreur inattendue s'est produite : {str(e)}"])

