from dataclasses import asdict
from typing import Optional
from ..soap_client import SoapClientManager
from .models import (
    FormationDocument2, OrganisationId,
    Doc2ActiviteEnseignementDetail, Doc2ActiviteEnseignementList, Doc2ActiviteEnseignementLine,
    Doc2ActiviteEnseignementListSave,
    Doc2InterventionExtList, Doc2InterventionExtLine,
    Doc2InterventionExtListSave,
    Doc2PeriodeExtList, Doc2PeriodeExtLine,
)
import logging
from pprint import pformat

logger = logging.getLogger(__name__)


class Document2Service:
    """Service pour gérer les opérations sur le document 2."""

    def __init__(self):
        self.client_manager = SoapClientManager("DOCUMENT2")

    # ------------------------------------------------------------------
    # Méthodes privées
    # ------------------------------------------------------------------

    @staticmethod
    def _organisation_id_dict(organisation_id: OrganisationId) -> dict:
        """Retourne les champs attendus par OrganisationReqIdCT (sans implId)."""
        return {
            'anneeScolaire': organisation_id.anneeScolaire,
            'etabId': organisation_id.etabId,
            'numAdmFormation': organisation_id.numAdmFormation,
            'numOrganisation': organisation_id.numOrganisation,
        }

    def _parse_document2_response(
        self,
        result: dict,
        organisation_id: OrganisationId,
    ) -> Optional[FormationDocument2]:
        """Parse la réponse SOAP et retourne un objet FormationDocument2."""
        if not (
            result
            and 'body' in result
            and result['body'].get('response')
            and 'document2' in result['body']['response']
        ):
            return None

        doc_data = result['body']['response']['document2']
        logger.debug(f"document2 : {pformat(doc_data)}")

        activite_enseignement_detail = None
        if doc_data.get('activiteEnseignementDetail'):
            ae = doc_data['activiteEnseignementDetail']
            activite_enseignement_detail = Doc2ActiviteEnseignementDetail(
                activiteEnseignementListe=Doc2ActiviteEnseignementList(
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
                            coEtuReg=line['coEtuReg'],
                        )
                        for line in ae.get('activiteEnseignementListe', {}).get('activiteEnseignement', [])
                    ]
                ),
                nbTotPeriodePrevueAn1=ae['nbTotPeriodePrevueAn1'],
                nbTotPeriodePrevueAn2=ae['nbTotPeriodePrevueAn2'],
                nbTotPeriodeReelleAn1=ae['nbTotPeriodeReelleAn1'],
                nbTotPeriodeReelleAn2=ae['nbTotPeriodeReelleAn2'],
            )

        intervention_exterieure_liste = None
        if doc_data.get('interventionExterieureListe'):
            ie_list = doc_data['interventionExterieureListe']
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
                                    nbPerAn2=p['nbPerAn2'],
                                )
                                for p in ie.get('periodeListe', {}).get('periode', [])
                            ]
                        ) if ie.get('periodeListe') else None,
                    )
                    for ie in ie_list.get('interventionExterieure', [])
                ]
            )

        return FormationDocument2(
            id=organisation_id,
            activiteEnseignementDetail=activite_enseignement_detail,
            interventionExterieureListe=intervention_exterieure_liste,
            swAppD2=doc_data.get('swAppD2', False),
            tsMaj=doc_data.get('tsMaj'),
            teUserMaj=doc_data.get('teUserMaj'),
        )

    # ------------------------------------------------------------------
    # Opérations WSDL
    # ------------------------------------------------------------------

    def lire_document_2(self, organisation_id: OrganisationId) -> Optional[FormationDocument2]:
        """Lit les informations d'un document 2."""
        logger.info(f"Lecture du document 2 pour l'organisation : {organisation_id}")
        result = self.client_manager.call_service(
            "LireDocument2",
            id=self._organisation_id_dict(organisation_id),
        )
        return self._parse_document2_response(result, organisation_id)

    def modifier_document_2(
        self,
        organisation_id: OrganisationId,
        activite_enseignement_liste: Optional[Doc2ActiviteEnseignementListSave] = None,
        intervention_exterieure_liste: Optional[Doc2InterventionExtListSave] = None,
    ) -> Optional[FormationDocument2]:
        """Modifie le document 2 (périodes de formation).

        Seuls les champs fournis sont envoyés au serveur ; les champs absents ne
        sont pas modifiés.
        """
        logger.info(f"Modification du document 2 pour l'organisation : {organisation_id}")
        request_data: dict = {'id': self._organisation_id_dict(organisation_id)}
        if activite_enseignement_liste is not None:
            request_data['activiteEnseignementListe'] = asdict(activite_enseignement_liste)
        if intervention_exterieure_liste is not None:
            request_data['interventionExterieureListe'] = asdict(intervention_exterieure_liste)
        result = self.client_manager.call_service("ModifierDocument2", **request_data)
        return self._parse_document2_response(result, organisation_id)
