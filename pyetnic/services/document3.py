from dataclasses import asdict
from typing import Optional
from ._helpers import organisation_request_id
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
            return signal_business_error(
                result,
                message="Document3 response was empty or success=False",
            )

        doc_data = result['body']['response']['document3']
        logger.debug(f"document3 : {pformat(doc_data)}")

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
                                for e in a['enseignantListe'].get('enseignant', [])
                            ]
                        ) if a.get('enseignantListe') else None,
                    )
                    for a in doc_data['activiteListe'].get('activite', [])
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
        """Lit les informations d'un document 3."""
        logger.info(f"Lecture du document 3 pour l'organisation : {organisation_id}")
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
        """Modifie le document 3 (attributions d'enseignants).

        activite_liste est obligatoire (contrat XSD : activiteListe requis).
        """
        logger.info(f"Modification du document 3 pour l'organisation : {organisation_id}")
        result = self.client_manager.call_service(
            "ModifierDocument3",
            id=organisation_request_id(organisation_id),
            activiteListe=asdict(activite_liste),
        )
        return self._parse_document3_response(result, organisation_id)
