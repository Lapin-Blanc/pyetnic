"""EPROM Formation Document 1D: population at 5/10 and enrolment fees.

The "droits d'inscription" service (``/eprom/formation/document1D/v1``) carries,
per year of study, the population counted at 5/10 of the unit
(``nbEleves5ieme``) and the enrolment fee (``mtDroitsInscription``). Its status
is ``statutDocumentDroitsInscription`` in :func:`lister_formations`.

A line goes through two phases (manual §3.1.4.1): the population is writable
until the school approves it with :func:`approuver_document_1d`
(``swAppPopD1D``), the fee only afterwards (error 20112 before; the manual
numbers it 1546). Once the
administration approves the document (``swAppD1D``), nothing is writable
(error 1530). pyetnic does not check these phases itself: the server decides,
and its refusal surfaces as a typed exception.
"""

from __future__ import annotations

import logging
from pprint import pformat
from typing import Optional

from ..exceptions import signal_business_error
from ..soap_client import SoapClientManager
from ._helpers import _as_list, organisation_request_id, to_soap_dict
from .models import (
    Doc1DDroitInscriptionLine,
    Doc1DDroitInscriptionList,
    Doc1DDroitInscriptionListAppr,
    Doc1DDroitInscriptionListSave,
    FormationDocument1D,
    OrganisationId,
)

logger = logging.getLogger(__name__)


class Document1DService:
    """Operations of the Document 1D (droits d'inscription)."""

    def __init__(self) -> None:
        self.client_manager = SoapClientManager("DOCUMENT1D")

    def _parse_document1d_response(
        self,
        result: dict,
        organisation_id: OrganisationId,
    ) -> Optional[FormationDocument1D]:
        if not (
            result
            and 'body' in result
            and result['body'].get('response')
            and 'document1D' in result['body']['response']
        ):
            return signal_business_error(result, service=self.client_manager.service_name)

        doc_data = result['body']['response']['document1D']
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("document1D : %s", pformat(doc_data))

        droit_inscription_liste = None
        if doc_data.get('droitInscriptionListe'):
            droit_inscription_liste = Doc1DDroitInscriptionList(
                droitInscription=[
                    Doc1DDroitInscriptionLine(
                        coAnnEtude=line['coAnnEtude'],
                        nbEleves5ieme=line['nbEleves5ieme'],
                        mtDroitsInscription=line['mtDroitsInscription'],
                        mtDroitsInscriptionOccupationnel=line['mtDroitsInscriptionOccupationnel'],
                        swAppPopD1D=line['swAppPopD1D'],
                        swAppD1D=line['swAppD1D'],
                        tsMaj=line.get('tsMaj'),
                        teUserMaj=line.get('teUserMaj'),
                    )
                    for line in _as_list(doc_data['droitInscriptionListe'].get('droitInscription'))
                ]
            )

        return FormationDocument1D(id=organisation_id, droitInscriptionListe=droit_inscription_liste)

    def lire_document_1d(self, organisation_id: OrganisationId) -> Optional[FormationDocument1D]:
        """Read the Document 1D: one line per year of study."""
        logger.info("Lecture du document 1D pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "LireDocument1D",
            id=organisation_request_id(organisation_id),
        )
        return self._parse_document1d_response(result, organisation_id)

    def modifier_document_1d(
        self,
        organisation_id: OrganisationId,
        droit_inscription_liste: Doc1DDroitInscriptionListSave,
    ) -> Optional[FormationDocument1D]:
        """Write the population at 5/10 or the enrolment fee of some years of study.

        A line targets its year by ``coAnnEtude`` and carries only the fields
        to write: ``nbEleves5ieme`` until the population is approved,
        ``mtDroitsInscription`` after (error 20112 before, tested on TQ on
        2026-11-24, the manual's 1546; ``EtnicDocumentNotAccessibleError``). After the administration's
        approval the server refuses any write (error 1530,
        ``EtnicAlreadyApprovedError``).
        """
        logger.info("Modification du document 1D pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "ModifierDocument1D",
            id=organisation_request_id(organisation_id),
            droitInscriptionListe=to_soap_dict(droit_inscription_liste),
        )
        return self._parse_document1d_response(result, organisation_id)

    def approuver_document_1d(
        self,
        organisation_id: OrganisationId,
        droit_inscription_liste: Doc1DDroitInscriptionListAppr,
    ) -> Optional[FormationDocument1D]:
        """Approve the population at 5/10 (``swAppPopD1D``, the school's approval).

        Send back, per year of study, the ``nbEleves5ieme`` just read: the
        server checks that nothing changed since (error 20104, tested on TQ on
        2026-11-24; ``EtnicConcurrencyError``). Build the list from a read with
        :meth:`Doc1DDroitInscriptionListAppr.from_document`. After the
        approval the population is frozen and the fees become writable;
        approving again is refused (error 1545, ``EtnicAlreadyApprovedError``).
        """
        logger.info("Approbation du document 1D pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "ApprouverDocument1D",
            id=organisation_request_id(organisation_id),
            droitInscriptionListe=to_soap_dict(droit_inscription_liste),
        )
        return self._parse_document1d_response(result, organisation_id)
