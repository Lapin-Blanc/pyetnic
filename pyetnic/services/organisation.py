from ..soap_client import SoapClientManager, generate_request_id
from zeep.helpers import serialize_object
from ..config import anneeScolaire, etabId, implId

class OrganisationService:
    """Service pour gérer les organisations de formation."""

    def __init__(self):
        """Initialise le service d'organisation."""
        self.client_manager = SoapClientManager("ORGANISATION")

    def creer_organisation(self, num_adm_formation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, impl_id=implId, **kwargs):
        """
        Crée une nouvelle organisation de formation.

        Args:
            num_adm_formation (int): Numéro administratif de la formation.
            date_debut (str): Date de début de l'organisation de la formation (format 'YYYY-MM-DD').
            date_fin (str): Date de fin de l'organisation de la formation (format 'YYYY-MM-DD').
            annee_scolaire (str, optional): Année scolaire au format 'YYYY-YYYY'. Par défaut, utilise la valeur de anneeScolaire.
            etab_id (int, optional): Identifiant FASE de l'établissement. Par défaut, utilise la valeur de etabId.
            impl_id (int, optional): Identifiant FASE de l'implantation. Par défaut, utilise la valeur de implId.
            **kwargs: Arguments optionnels supplémentaires.

        Keyword Args:
            organisationPeriodesSupplOuEPT (bool): Flag autorisant l'organisation de périodes supplémentaires ou pour de l'expertise pédagogique et technique.
            valorisationAcquis (bool): Flag indiquant que la formation est pour la valorisation des acquis.
            enPrison (bool): Flag indiquant que la formation est donnée en prison.
            activiteFormation (bool): Flag indiquant que la formation est organisée dans le cadre des activités de formation.
            conseillerPrevention (bool): Flag indiquant si la formation est organisée uniquement dans le cadre de la mission de conseiller en prévention ou de DPO.
            enseignementHybride (bool): Flag indiquant que la formation est donnée en enseignement hybride.
            numOrganisation2AnneesScolaires (int): Numéro de l'organisation de la formation de l'année précédente qui est organisée sur deux années scolaires consécutives.
            typeInterventionExterieure (str): Code type d'intervention extérieure pour l'organisation de la formation.
            interventionExterieure50p (bool): Intervention d'un tiers de 50% ou plus dans l'organisation de la formation.

        Returns:
            dict: Un dictionnaire contenant les informations de l'organisation créée, incluant :
                - id (dict): Identifiant de l'organisation
                - dateDebutOrganisation (str): Date de début de l'organisation
                - dateFinOrganisation (str): Date de fin de l'organisation
                - nombreSemaineFormation (int): Nombre de semaines de formation
                - statut (dict): Statut de l'organisation
                - Autres champs optionnels selon les arguments fournis

        """

        organisation_data = {
            "id": {
                "anneeScolaire": annee_scolaire,
                "etabId": etab_id,
                "implId": impl_id,
                "numAdmFormation": num_adm_formation
            },
            "dateDebutOrganisation": date_debut,
            "dateFinOrganisation": date_fin
        }
        organisation_data.update(kwargs)
        
        return self.client_manager.call_service("CreerOrganisation", **organisation_data)

    def lire_organisation(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
        """Lit les informations d'une organisation de formation existante."""
        organisation_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        
        return self.client_manager.call_service("LireOrganisation", id=organisation_id)

    def modifier_organisation(self, num_adm_formation, num_organisation, date_debut, date_fin, annee_scolaire=anneeScolaire, etab_id=etabId, **kwargs):
        """Modifie une organisation de formation existante."""
        organisation_data = {
            "id": {
                "anneeScolaire": annee_scolaire,
                "etabId": etab_id,
                "numAdmFormation": num_adm_formation,
                "numOrganisation": num_organisation
            },
            "dateDebutOrganisation": date_debut,
            "dateFinOrganisation": date_fin
        }
        organisation_data.update(kwargs)
        
        return self.client_manager.call_service("ModifierOrganisation", **organisation_data)

    def supprimer_organisation(self, num_adm_formation, num_organisation, annee_scolaire=anneeScolaire, etab_id=etabId):
        """Supprime une organisation de formation existante."""
        organisation_id = {
            "anneeScolaire": annee_scolaire,
            "etabId": etab_id,
            "numAdmFormation": num_adm_formation,
            "numOrganisation": num_organisation
        }
        
        return self.client_manager.call_service("SupprimerOrganisation", id=organisation_id)

# Fonctions pour EpromFormationDocument1

