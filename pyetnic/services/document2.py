from ..soap_client import SoapClientManager
from dataclasses import asdict
from .models import (
    FormationDocument2, OrganisationId, 
    Doc2ActiviteEnseignementDetail, Doc2ActiviteEnseignementList, Doc2ActiviteEnseignementLine,
    Doc2InterventionExtList, Doc2InterventionExtLine, Doc2PeriodeExtList, Doc2PeriodeExtLine
)
import logging
from typing import Optional

# Configuration du logging
logger = logging.getLogger(__name__)

class Document2Service:
    """Service pour gérer les opérations sur le document 2."""

    def __init__(self):
        """Initialise le service pour le document 2."""
        self.client_manager = SoapClientManager("DOCUMENT2")

    def lire_document_2(self, organisation_id: OrganisationId) -> Optional[FormationDocument2]:
        """Lire les informations d'un document 2."""
        logger.info(f"Lecture du document 2 pour l'organisation: {organisation_id}")
        result = self.client_manager.call_service("LireDocument2", id=asdict(organisation_id))
        
        if result and 'body' in result and 'response' in result['body'] and 'document2' in result['body']['response']:
            doc_data = result['body']['response']['document2']
            logger.debug(f"Structure de doc_data : {doc_data.keys()}")

            # Traitement des activités d'enseignement
            activite_enseignement_detail = None
            if 'activiteEnseignementDetail' in doc_data:
                ae_detail = doc_data['activiteEnseignementDetail']
                logger.debug(f"Structure de activiteEnseignementDetail : {ae_detail.keys()}")
                
                activite_enseignement_list = Doc2ActiviteEnseignementList(
                    activiteEnseignement=[
                        Doc2ActiviteEnseignementLine(
                            coNumBranche=line['coNumBranche'],
                            coCategorie=line['coCategorie'],
                            teNomBranche=line['teNomBranche'],
                            coAnnEtude=line['coAnnEtude'],
                            nbEleveC1=line['nbEleveC1'],
                            nbPeriodeBranche=line['nbPeriodeBranche'],
                            nbPeriodePrevueAn1=line['nbPeriodePrevueAn1'],
                            nbPeriodePrevueAn2=line['nbPeriodePrevueAn2'],
                            nbPeriodeReelleAn1=line['nbPeriodeReelleAn1'],
                            nbPeriodeReelleAn2=line['nbPeriodeReelleAn2'],
                            coAdmReg=line['coAdmReg'],
                            coOrgReg=line['coOrgReg'],
                            coBraReg=line['coBraReg'],
                            coEtuReg=line['coEtuReg']
                        )
                        for line in ae_detail.get('activiteEnseignementListe', {}).get('activiteEnseignement', [])
                    ]
                )
                
                activite_enseignement_detail = Doc2ActiviteEnseignementDetail(
                    activiteEnseignementListe=activite_enseignement_list,
                    nbTotPeriodePrevueAn1=ae_detail['nbTotPeriodePrevueAn1'],
                    nbTotPeriodePrevueAn2=ae_detail['nbTotPeriodePrevueAn2'],
                    nbTotPeriodeReelleAn1=ae_detail['nbTotPeriodeReelleAn1'],
                    nbTotPeriodeReelleAn2=ae_detail['nbTotPeriodeReelleAn2']
                )

            # Traitement des interventions extérieures
            intervention_exterieure_liste = None
            if 'interventionExterieureListe' in doc_data:
                ie_list = doc_data['interventionExterieureListe']
                logger.debug(f"Type de interventionExterieureListe : {type(ie_list)}")
                
                if ie_list is not None:
                    intervention_exterieure_liste = Doc2InterventionExtList(
                        interventionExterieure=[
                            Doc2InterventionExtLine(
                                coNumIex=ie['coNumIex'],
                                coCatCol=ie['coCatCol'],
                                teTypeInterventionExt=ie['teTypeInterventionExt'],
                                coObjFse=ie['coObjFse'],
                                teSousTypeInterventionExt=ie['teSousTypeInterventionExt'],
                                coRefPro=ie['coRefPro'],
                                coCriCee=ie['coCriCee'],
                                periodeListe=Doc2PeriodeExtList(
                                    periode=[
                                        Doc2PeriodeExtLine(
                                            coCodePar=p['coCodePar'],
                                            teLibPeriode=p['teLibPeriode'],
                                            nbPerAn1=p['nbPerAn1'],
                                            nbPerAn2=p['nbPerAn2']
                                        )
                                        for p in ie.get('periodeListe', {}).get('periode', [])
                                    ]
                                ) if 'periodeListe' in ie else None
                            )
                            for ie in ie_list.get('interventionExterieure', [])
                        ]
                    )
                else:
                    logger.debug("interventionExterieureListe est None")

            # Création de l'objet FormationDocument2
            document = FormationDocument2(
                id=organisation_id,
                activiteEnseignementDetail=activite_enseignement_detail,
                interventionExterieureListe=intervention_exterieure_liste,
                swAppD2=doc_data.get('swAppD2', False),
                tsMaj=doc_data.get('tsMaj'),
                teUserMaj=doc_data.get('teUserMaj')
            )

            logger.debug(f"Document 2 lu avec succès: {document}")
            return document
        
        logger.warning(f"Aucun document 2 trouvé pour l'organisation: {organisation_id}")
        return None

def lire_document_2(organisation_id: OrganisationId) -> Optional[FormationDocument2]:
    """Fonction utilitaire pour lire le document 2."""
    service = Document2Service()
    return service.lire_document_2(organisation_id)