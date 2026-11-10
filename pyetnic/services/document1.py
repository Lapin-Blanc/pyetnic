from typing import Optional
from ._helpers import _as_list, organisation_request_id, to_soap_dict
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
            # Let signal_business_error surface the real ETNIC code + description.
            return signal_business_error(result)

        doc_data = result['body']['response']['document1']
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("document1 : %s", pformat(doc_data))

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
                    for p in _as_list(doc_data['populationListe'].get('population'))
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
        """Read Doc 1 (population per year of study).

        Before anything is encoded, the server already returns a population
        line at zero (``swAppPopD1`` false; observed in production,
        2026-09-16, confirmed on TQ, 2026-11-10): its presence does not mean
        the Doc 1 was encoded.

        Before the Doc A is approved the server refuses with error 20101
        (tested on TQ, 2026-11-10). The code is not mapped to a specific
        exception: ``None`` by default, a plain ``EtnicBusinessError`` under
        :func:`strict_errors`.
        """
        logger.info("Lecture du document 1 pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "LireDocument1",
            id=organisation_request_id(organisation_id),
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
        logger.info("Modification du document 1 pour l'organisation : %s", organisation_id)
        request_data: dict = {'id': organisation_request_id(organisation_id)}
        if population_liste is not None:
            request_data['populationListe'] = to_soap_dict(population_liste)
        result = self.client_manager.call_service("ModifierDocument1", **request_data)
        return self._parse_document1_response(result, organisation_id)

    def approuver_document_1(
        self,
        organisation_id: OrganisationId,
        population_liste: Optional[Doc1PopulationListSave] = None,
    ) -> Optional[FormationDocument1]:
        """Validate the Doc 1 population (``swAppPopD1``, the "Validé" box).

        Although the XSD makes ``population_liste`` optional, the server
        compares it with what it stores and refuses with error 20104 when it
        differs or is missing: pass back the lines just read with
        :func:`lire_document_1`. The administration's own approval
        (``swAppD1``) is out of the school's reach.
        """
        logger.info("Approbation du document 1 pour l'organisation : %s", organisation_id)
        request_data: dict = {'id': organisation_request_id(organisation_id)}
        if population_liste is not None:
            request_data['populationListe'] = to_soap_dict(population_liste)
        result = self.client_manager.call_service("ApprouverDocument1", **request_data)
        return self._parse_document1_response(result, organisation_id)
