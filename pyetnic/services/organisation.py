from datetime import date
from pprint import pformat
from typing import Optional
from .models import Organisation, OrganisationId, StatutDocument
from ..soap_client import SoapClientManager
import logging

# Configuration du logging
logger = logging.getLogger(__name__)


class OrganisationService:
    """Service pour gérer les organisations de formation."""

    def __init__(self):
        """Initialise le service d'organisation."""
        self.client_manager = SoapClientManager("ORGANISATION")

    # ------------------------------------------------------------------
    # Méthodes privées
    # ------------------------------------------------------------------

    def _parse_organisation_response(
        self,
        result: dict,
        organisation_id: Optional[OrganisationId] = None,
    ) -> Optional[Organisation]:
        """Parse la réponse SOAP et retourne un objet Organisation.

        Si organisation_id est fourni, il est utilisé directement.
        Sinon, l'id est reconstruit depuis les données de la réponse
        (utile après CreerOrganisation dont le numOrganisation est attribué par le serveur).
        """
        if (
            result
            and 'body' in result
            and result['body'].get('response')
            and 'organisation' in result['body']['response']
        ):
            org_data = result['body']['response']['organisation']
            logger.debug(f"Organisation : {pformat(org_data)}")

            if organisation_id is None:
                id_data = org_data.get('id', {})
                organisation_id = OrganisationId(
                    anneeScolaire=id_data['anneeScolaire'],
                    etabId=id_data['etabId'],
                    numAdmFormation=id_data['numAdmFormation'],
                    numOrganisation=id_data['numOrganisation'],
                    implId=id_data.get('implId'),
                )

            return Organisation(
                id=organisation_id,
                dateDebutOrganisation=org_data['dateDebutOrganisation'],
                dateFinOrganisation=org_data['dateFinOrganisation'],
                nombreSemaineFormation=org_data.get('nombreSemaineFormation'),
                statutDocumentOrganisation=StatutDocument(**org_data['statut']) if org_data.get('statut') else None,
                organisationPeriodesSupplOuEPT=org_data.get('organisationPeriodesSupplOuEPT'),
                valorisationAcquis=org_data.get('valorisationAcquis'),
                enPrison=org_data.get('enPrison'),
                eLearning=org_data.get('eLearning'),
                activiteFormation=org_data.get('activiteFormation'),
                conseillerPrevention=org_data.get('conseillerPrevention'),
                partiellementDistance=org_data.get('partiellementDistance'),
                enseignementHybride=org_data.get('enseignementHybride'),
                numOrganisation2AnneesScolaires=org_data.get('numOrganisation2AnneesScolaires'),
                typeInterventionExterieure=org_data.get('typeInterventionExterieure'),
                interventionExterieure50p=org_data.get('interventionExterieure50p'),
            )

        return None

    @staticmethod
    def _organisation_id_dict(organisation_id: OrganisationId) -> dict:
        """Retourne uniquement les champs attendus par Lire/Modifier/Supprimer.

        Ces opérations n'incluent pas implId dans leur schéma d'ID.
        """
        return {
            'anneeScolaire': organisation_id.anneeScolaire,
            'etabId': organisation_id.etabId,
            'numAdmFormation': organisation_id.numAdmFormation,
            'numOrganisation': organisation_id.numOrganisation,
        }

    # ------------------------------------------------------------------
    # Opérations WSDL
    # ------------------------------------------------------------------

    def lire_organisation(self, organisation_id: OrganisationId) -> Optional[Organisation]:
        """Lit les informations d'une organisation de formation existante."""
        logger.info(f"Lecture de l'organisation {organisation_id}")
        result = self.client_manager.call_service(
            "LireOrganisation",
            id=self._organisation_id_dict(organisation_id),
        )
        return self._parse_organisation_response(result, organisation_id)

    def creer_organisation(
        self,
        annee_scolaire: str,
        etab_id: int,
        impl_id: int,
        num_adm_formation: int,
        date_debut: date,
        date_fin: date,
        organisationPeriodesSupplOuEPT: Optional[bool] = None,
        valorisationAcquis: Optional[bool] = None,
        enPrison: Optional[bool] = None,
        activiteFormation: Optional[bool] = None,
        conseillerPrevention: Optional[bool] = None,
        enseignementHybride: Optional[bool] = None,
        numOrganisation2AnneesScolaires: Optional[int] = None,
        typeInterventionExterieure: Optional[str] = None,
        interventionExterieure50p: Optional[bool] = None,
    ) -> Optional[Organisation]:
        """Crée une nouvelle organisation de formation.

        Le numOrganisation est attribué par le serveur et renvoyé dans la réponse.
        """
        logger.info(f"Création d'une organisation pour la formation {num_adm_formation}")
        request_data = {
            'id': {
                'anneeScolaire': annee_scolaire,
                'etabId': etab_id,
                'implId': impl_id,
                'numAdmFormation': num_adm_formation,
            },
            'dateDebutOrganisation': date_debut,
            'dateFinOrganisation': date_fin,
            'organisationPeriodesSupplOuEPT': organisationPeriodesSupplOuEPT,
            'valorisationAcquis': valorisationAcquis,
            'enPrison': enPrison,
            'activiteFormation': activiteFormation,
            'conseillerPrevention': conseillerPrevention,
            'enseignementHybride': enseignementHybride,
            'numOrganisation2AnneesScolaires': numOrganisation2AnneesScolaires,
            'typeInterventionExterieure': typeInterventionExterieure,
            'interventionExterieure50p': interventionExterieure50p,
        }
        result = self.client_manager.call_service("CreerOrganisation", **request_data)
        # L'id complet (avec numOrganisation) est dans la réponse
        return self._parse_organisation_response(result)

    def modifier_organisation(self, organisation: Organisation) -> Optional[Organisation]:
        """Modifie une organisation de formation existante."""
        logger.info(f"Modification de l'organisation {organisation.id}")
        request_data = {
            'id': self._organisation_id_dict(organisation.id),
            'dateDebutOrganisation': organisation.dateDebutOrganisation,
            'dateFinOrganisation': organisation.dateFinOrganisation,
            'organisationPeriodesSupplOuEPT': organisation.organisationPeriodesSupplOuEPT,
            'valorisationAcquis': organisation.valorisationAcquis,
            'enPrison': organisation.enPrison,
            'activiteFormation': organisation.activiteFormation,
            'conseillerPrevention': organisation.conseillerPrevention,
            'enseignementHybride': organisation.enseignementHybride,
            'numOrganisation2AnneesScolaires': organisation.numOrganisation2AnneesScolaires,
            'typeInterventionExterieure': organisation.typeInterventionExterieure,
            'interventionExterieure50p': organisation.interventionExterieure50p,
        }
        result = self.client_manager.call_service("ModifierOrganisation", **request_data)
        return self._parse_organisation_response(result, organisation.id)

    def supprimer_organisation(self, organisation_id: OrganisationId) -> bool:
        """Supprime une organisation de formation.

        Retourne True si la suppression a réussi, False sinon.
        """
        logger.info(f"Suppression de l'organisation {organisation_id}")
        result = self.client_manager.call_service(
            "SupprimerOrganisation",
            id=self._organisation_id_dict(organisation_id),
        )
        return bool(result and result.get('body', {}).get('success', False))
