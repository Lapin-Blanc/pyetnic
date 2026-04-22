"""
Module pour le service de liste des formations.

Ce module fournit des fonctions pour lister les formations organisables
et les formations existantes avec leurs organisations.
"""

from __future__ import annotations

from typing import Any, Optional
from ..soap_client import SoapClientManager, SoapError
from ..config import Config
from ..exceptions import extract_error_info, map_etnic_error_code_to_class
from .models import Formation, FormationsListeResult, OrganisationApercu, OrganisationId, StatutDocument
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
        annee_scolaire: str | None = None,
        etab_id: int | None = None,
        impl_id: int | None = None,
    ) -> FormationsListeResult:
        try:
            request_data = {
                "anneeScolaire": annee_scolaire if annee_scolaire is not None else Config.ANNEE_SCOLAIRE,
                "etabId": etab_id if etab_id is not None else Config.ETAB_ID,
                "implId": impl_id if impl_id is not None else Config.IMPL_ID,
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
                if Config.RAISE_ON_ERROR:
                    code, description, request_id = extract_error_info(result)
                    cls = map_etnic_error_code_to_class(code)
                    raise cls(
                        f"ListerFormationsOrganisables failed (code={code}, description={description})",
                        code=code,
                        description=description,
                        request_id=request_id,
                    )
                return FormationsListeResult(False, [], messages=result['body'].get('messages', []))

        except SoapError as e:
            if Config.RAISE_ON_ERROR:
                raise
            return FormationsListeResult(False, [], messages=[str(e)])

    def lister_formations(
        self,
        annee_scolaire: str | None = None,
        etab_id: int | None = None,
        impl_id: int | None = None,
    ) -> FormationsListeResult:
        logger.info("Appel de lister_formations")
        if annee_scolaire is None:
            annee_scolaire = Config.ANNEE_SCOLAIRE
        if etab_id is None:
            etab_id = Config.ETAB_ID
        if impl_id is None:
            impl_id = Config.IMPL_ID
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
                for f in result['body']['response'].get('formation', []):
                    logger.debug(f"Formation : {pformat(f)}")
                    organisations = []
                    for org_data in f.get('organisation', []):
                        logger.debug(f"Organisation : {pformat(org_data)}")
                        org_id = OrganisationId(
                            anneeScolaire=annee_scolaire,
                            etabId=etab_id,
                            numAdmFormation=f['numAdmFormation'],
                            numOrganisation=org_data['numOrganisation'],
                            implId=org_data.get('implId'),
                        )
                        organisation = OrganisationApercu(
                            id=org_id,
                            dateDebutOrganisation=org_data['dateDebutOrganisation'],
                            dateFinOrganisation=org_data['dateFinOrganisation'],
                            statutDocumentOrganisation=StatutDocument(**org_data['statutDocumentOrganisation']) if org_data.get('statutDocumentOrganisation') else None,
                            statutDocumentPopulationPeriodes=StatutDocument(**org_data['statutDocumentPopulationPeriodes']) if org_data.get('statutDocumentPopulationPeriodes') else None,
                            statutDocumentDroitsInscription=StatutDocument(**org_data['statutDocumentDroitsInscription']) if org_data.get('statutDocumentDroitsInscription') else None,
                            statutDocumentAttributions=StatutDocument(**org_data['statutDocumentAttributions']) if org_data.get('statutDocumentAttributions') else None,
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
                if Config.RAISE_ON_ERROR:
                    code, description, request_id = extract_error_info(result)
                    cls = map_etnic_error_code_to_class(code)
                    raise cls(
                        f"ListerFormations failed (code={code}, description={description})",
                        code=code,
                        description=description,
                        request_id=request_id,
                    )
                return FormationsListeResult(False, [], messages=result['body'].get('messages', []))

        except SoapError as e:
            if Config.RAISE_ON_ERROR:
                raise
            return FormationsListeResult(False, [], messages=[str(e)])

