from typing import Optional
from ._helpers import _as_list, organisation_request_id, to_soap_dict
from ..exceptions import signal_business_error
from ..soap_client import SoapClientManager
from .models import (
    FormationDocument3, OrganisationId,
    Doc3ActiviteListe, Doc3ActiviteDetail, Doc3EnseignantList, Doc3EnseignantDetail,
    Doc3ActiviteListeSave,
)
import logging
from pprint import pformat

logger = logging.getLogger(__name__)


class Document3Service:
    """Service pour gérer les opérations sur le document 3."""

    def __init__(self):
        self.client_manager = SoapClientManager("DOCUMENT3")

    # ------------------------------------------------------------------
    # Méthodes privées
    # ------------------------------------------------------------------

    def _parse_document3_response(
        self,
        result: dict,
        organisation_id: OrganisationId,
    ) -> Optional[FormationDocument3]:
        """Parse la réponse SOAP et retourne un objet FormationDocument3."""
        if not (
            result
            and 'body' in result
            and result['body'].get('response')
            and 'document3' in result['body']['response']
        ):
            # Let signal_business_error surface the real ETNIC code + description.
            return signal_business_error(result)

        doc_data = result['body']['response']['document3']
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("document3 : %s", pformat(doc_data))

        activite_liste = None
        if doc_data.get('activiteListe'):
            activite_liste = Doc3ActiviteListe(
                activite=[
                    Doc3ActiviteDetail(
                        coNumBranche=a.get('coNumBranche'),
                        coCategorie=a.get('coCategorie'),
                        teNomBranche=a.get('teNomBranche'),
                        noAnneeEtude=a.get('noAnneeEtude'),
                        nbPeriodesDoc8=a.get('nbPeriodesDoc8'),
                        nbPeriodesPrevuesDoc2=a.get('nbPeriodesPrevuesDoc2'),
                        nbPeriodesReellesDoc2=a.get('nbPeriodesReellesDoc2'),
                        enseignantListe=Doc3EnseignantList(
                            enseignant=[
                                Doc3EnseignantDetail(
                                    coNumAttribution=e.get('coNumAttribution'),
                                    noMatEns=e.get('noMatEns'),
                                    teNomEns=e.get('teNomEns'),
                                    tePrenomEns=e.get('tePrenomEns'),
                                    teAbrEns=e.get('teAbrEns'),
                                    teEnseignant=e.get('teEnseignant'),
                                    coDispo=e.get('coDispo'),
                                    teStatut=e.get('teStatut'),
                                    nbPeriodesAttribuees=e.get('nbPeriodesAttribuees'),
                                    tsMaj=e.get('tsMaj'),
                                    teUserMaj=e.get('teUserMaj'),
                                )
                                for e in _as_list(a['enseignantListe'].get('enseignant'))
                            ]
                        ) if a.get('enseignantListe') else None,
                    )
                    for a in _as_list(doc_data['activiteListe'].get('activite'))
                ]
            )

        return FormationDocument3(
            id=organisation_id,
            activiteListe=activite_liste,
        )

    # ------------------------------------------------------------------
    # Opérations WSDL
    # ------------------------------------------------------------------

    def lire_document_3(self, organisation_id: OrganisationId) -> Optional[FormationDocument3]:
        """Read Doc 3 (teacher attributions).

        Not reachable until "Doc A" (the organisation) and Doc 2 are approved:
        error 20102, ``None`` by default, ``EtnicDocumentNotAccessibleError``
        under :func:`strict_errors`.

        A Doc 3 that is reachable but was never written reads as a skeleton:
        one line per branch, ``coNumAttribution`` 1, empty staff number and
        status, 0 period. ``statutDocumentAttributions`` stays absent until
        the first write, then reads "Encodé école" (observed in production,
        2025-2026): the document's existence does not mean it was encoded.
        """
        logger.info("Lecture du document 3 pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "LireDocument3",
            id=organisation_request_id(organisation_id),
        )
        return self._parse_document3_response(result, organisation_id)

    def modifier_document_3(
        self,
        organisation_id: OrganisationId,
        activite_liste: Doc3ActiviteListeSave,
    ) -> Optional[FormationDocument3]:
        """Write the teacher attributions of Doc 3.

        .. warning::
           For every branch present in ``activite_liste``, the server
           **replaces** the branch's teacher list with the one sent; it does
           not add to it. Sending only the attribution to add deletes the other
           attributions of that branch. Always send the complete list of each
           branch touched (branches left out are not modified), and read the
           whole document back afterwards: a check limited to the lines sent
           cannot see what was deleted.

        ``activite_liste`` is required by the XSD. ``coNumAttribution`` is a
        server-side counter; freed numbers are not reused. It does not target an
        existing attribution: lines sent without it are accepted and numbered by
        the server. A branch may carry several lines with the same ``noMatEns``
        (different ``teStatut`` or ``coDispo``, even identical triples): the
        server keeps them apart, so a read-back cannot match on the staff number
        alone (observed in production, 2026-09).

        The total of the lines without ``coDispo`` is capped by the real periods
        of Doc 2 (error 1574); a line carrying a ``coDispo`` does not count
        toward it (observed in production, 2026-09).
        """
        logger.info("Modification du document 3 pour l'organisation : %s", organisation_id)
        result = self.client_manager.call_service(
            "ModifierDocument3",
            id=organisation_request_id(organisation_id),
            activiteListe=to_soap_dict(activite_liste),
        )
        return self._parse_document3_response(result, organisation_id)
