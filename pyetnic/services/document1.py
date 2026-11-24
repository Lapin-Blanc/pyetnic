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
            return signal_business_error(result, service=self.client_manager.service_name)

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
        (tested on TQ, 2026-11-10): ``EtnicDocumentNotAccessibleError``.
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
        """Write the Doc 1 population (per year of study).

        Only the lines given are sent, and in each line only the fields that
        are not ``None``. What the server does with the lines and fields left
        out is not established (spec 03).
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
        population_liste: Doc1PopulationListSave,
    ) -> Optional[FormationDocument1]:
        """Validate the Doc 1 population (``swAppPopD1``, the "Validé" box).

        ``population_liste`` is required, although the XSD makes it optional:
        the server compares it with what it stores and refuses with error
        20104 (``EtnicConcurrencyError``) when it differs or is missing
        (observed in production, 2026-09-18). Send back the lines just read::

            doc = lire_document_1(org_id)
            approuver_document_1(org_id, Doc1PopulationListSave.from_document(doc))

        The administration's own approval (``swAppD1``) is out of the
        school's reach.
        """
        if population_liste is None:
            raise TypeError(
                "approuver_document_1() needs population_liste: the server refuses an "
                "approval without the population (error 20104). Use "
                "Doc1PopulationListSave.from_document(lire_document_1(organisation_id))."
            )
        logger.info("Approbation du document 1 pour l'organisation : %s", organisation_id)
        request_data: dict = {
            'id': organisation_request_id(organisation_id),
            'populationListe': to_soap_dict(population_liste),
        }
        result = self.client_manager.call_service("ApprouverDocument1", **request_data)
        return self._parse_document1_response(result, organisation_id)
