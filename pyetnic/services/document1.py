from dataclasses import asdict
from typing import Optional
from ..exceptions import signal_business_error
from ..soap_client import SoapClientManager
from .models import (
    FormationDocument1, OrganisationId,
    Doc1PopulationList, Doc1PopulationLine,
    Doc1PopulationListSave,
)
import logging
from pprint import pformat

logger = logging.getLogger(__name__)


class Document1Service:
    """Service pour gérer les opérations sur le document 1."""

    def __init__(self):
        self.client_manager = SoapClientManager("DOCUMENT1")

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

    def _parse_document1_response(
        self,
        result: dict,
        organisation_id: OrganisationId,
    ) -> Optional[FormationDocument1]:
        """Parse la réponse SOAP et retourne un objet FormationDocument1."""
        if not (
            result
            and 'body' in result
            and result['body'].get('response')
            and 'document1' in result['body']['response']
        ):
            return signal_business_error(
                result,
                message="Document1 response was empty or success=False",
            )

        doc_data = result['body']['response']['document1']
        logger.debug(f"document1 : {pformat(doc_data)}")

        population_liste = None
        if doc_data.get('populationListe'):
            population_liste = Doc1PopulationList(
                population=[
                    Doc1PopulationLine(
                        coAnnEtude=p['coAnnEtude'],
                        nbEleveA=p['nbEleveA'],
                        nbEleveEhr=p['nbEleveEhr'],
                        nbEleveFse=p['nbEleveFse'],
                        nbElevePi=p['nbElevePi'],
                        nbEleveB=p['nbEleveB'],
                        nbEleveTot2a5=p['nbEleveTot2a5'],
                        nbEleveDem=p['nbEleveDem'],
                        nbEleveMin=p['nbEleveMin'],
                        nbEleveExm=p['nbEleveExm'],
                        nbElevePl=p['nbElevePl'],
                        nbEleveTot6et8=p['nbEleveTot6et8'],
                        nbEleveTotFse=p['nbEleveTotFse'],
                        nbEleveTotPi=p['nbEleveTotPi'],
                        nbEleveTotHom=p['nbEleveTotHom'],
                        nbEleveTotFem=p['nbEleveTotFem'],
                        swAppPopD1=p['swAppPopD1'],
                        swAppD1=p['swAppD1'],
                        tsMaj=p.get('tsMaj'),
                        teUserMaj=p.get('teUserMaj'),
                    )
                    for p in doc_data['populationListe'].get('population', [])
                ]
            )

        return FormationDocument1(
            id=organisation_id,
            populationListe=population_liste,
        )

    # ------------------------------------------------------------------
    # Opérations WSDL
    # ------------------------------------------------------------------

    def lire_document_1(self, organisation_id: OrganisationId) -> Optional[FormationDocument1]:
        """Lit les informations d'un document 1."""
        logger.info(f"Lecture du document 1 pour l'organisation : {organisation_id}")
        result = self.client_manager.call_service(
            "LireDocument1",
            id=self._organisation_id_dict(organisation_id),
        )
        return self._parse_document1_response(result, organisation_id)

    def modifier_document_1(
        self,
        organisation_id: OrganisationId,
        population_liste: Optional[Doc1PopulationListSave] = None,
    ) -> Optional[FormationDocument1]:
        """Modifie le document 1 (populations par année d'étude).

        Seules les lignes de population fournies sont envoyées au serveur.
        """
        logger.info(f"Modification du document 1 pour l'organisation : {organisation_id}")
        request_data: dict = {'id': self._organisation_id_dict(organisation_id)}
        if population_liste is not None:
            request_data['populationListe'] = asdict(population_liste)
        result = self.client_manager.call_service("ModifierDocument1", **request_data)
        return self._parse_document1_response(result, organisation_id)

    def approuver_document_1(
        self,
        organisation_id: OrganisationId,
        population_liste: Optional[Doc1PopulationListSave] = None,
    ) -> Optional[FormationDocument1]:
        """Approuve le document 1.

        Une liste de populations peut optionnellement être fournie pour
        mettre à jour les données au moment de l'approbation.
        """
        logger.info(f"Approbation du document 1 pour l'organisation : {organisation_id}")
        request_data: dict = {'id': self._organisation_id_dict(organisation_id)}
        if population_liste is not None:
            request_data['populationListe'] = asdict(population_liste)
        result = self.client_manager.call_service("ApprouverDocument1", **request_data)
        return self._parse_document1_response(result, organisation_id)
