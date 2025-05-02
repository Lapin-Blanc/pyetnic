from ..soap_client import SoapClientManager
from dataclasses import asdict
from .models import (
    FormationDocument3, OrganisationId, 
    Doc3ActiviteListe, Doc3ActiviteDetail, Doc3EnseignantList, Doc3EnseignantDetail,
    Doc3ActiviteListeSave, Doc3ActiviteDetailSave, Doc3EnseignantListSave, Doc3EnseignantDetailSave
)
import logging
from typing import Optional

# Configuration du logging
logger = logging.getLogger(__name__)

class Document3Service:
    """Service pour gérer les opérations sur le document 3."""

    def __init__(self):
        """Initialise le service pour le document 3."""
        self.client_manager = SoapClientManager("DOCUMENT3")

    def lire_document_3(self, organisation_id: OrganisationId) -> Optional[FormationDocument3]:
        """Lire les informations d'un document 3."""
        logger.info(f"Lecture du document 3 pour l'organisation: {organisation_id}")
        result = self.client_manager.call_service("LireDocument3", id=asdict(organisation_id))
        
        if result and 'body' in result and 'response' in result['body'] and 'document3' in result['body']['response']:
            doc_data = result['body']['response']['document3']
            logger.debug(f"Structure de doc_data : {doc_data.keys()}")

            # Traitement des activités d'enseignement
            activite_liste = None
            if 'activiteListe' in doc_data and doc_data['activiteListe'] is not None:
                activites = []
                
                for activite_data in doc_data['activiteListe'].get('activite', []):
                    # Traitement des enseignants pour cette activité
                    enseignant_liste = None
                    if 'enseignantListe' in activite_data and activite_data['enseignantListe'] is not None:
                        enseignants = []
                        
                        for ens_data in activite_data['enseignantListe'].get('enseignant', []):
                            enseignant = Doc3EnseignantDetail(
                                coNumAttribution=ens_data.get('coNumAttribution'),
                                noMatEns=ens_data.get('noMatEns'),
                                teNomEns=ens_data.get('teNomEns'),
                                tePrenomEns=ens_data.get('tePrenomEns'),
                                teAbrEns=ens_data.get('teAbrEns'),
                                teEnseignant=ens_data.get('teEnseignant'),
                                coDispo=ens_data.get('coDispo'),
                                teStatut=ens_data.get('teStatut'),
                                nbPeriodesAttribuees=ens_data.get('nbPeriodesAttribuees'),
                                tsMaj=ens_data.get('tsMaj'),
                                teUserMaj=ens_data.get('teUserMaj')
                            )
                            enseignants.append(enseignant)
                        
                        enseignant_liste = Doc3EnseignantList(enseignant=enseignants)
                    
                    # Création de l'activité d'enseignement
                    activite = Doc3ActiviteDetail(
                        coNumBranche=activite_data.get('coNumBranche'),
                        coCategorie=activite_data.get('coCategorie'),
                        teNomBranche=activite_data.get('teNomBranche'),
                        noAnneeEtude=activite_data.get('noAnneeEtude'),
                        nbPeriodesDoc8=activite_data.get('nbPeriodesDoc8'),
                        nbPeriodesPrevuesDoc2=activite_data.get('nbPeriodesPrevuesDoc2'),
                        nbPeriodesReellesDoc2=activite_data.get('nbPeriodesReellesDoc2'),
                        enseignantListe=enseignant_liste
                    )
                    activites.append(activite)
                
                activite_liste = Doc3ActiviteListe(activite=activites)
            
            # Création de l'objet FormationDocument3
            document = FormationDocument3(
                id=organisation_id,
                activiteListe=activite_liste,
                tsMaj=doc_data.get('tsMaj'),
                teUserMaj=doc_data.get('teUserMaj')
            )

            logger.debug(f"Document 3 lu avec succès: {document}")
            return document
        
        logger.warning(f"Aucun document 3 trouvé pour l'organisation: {organisation_id}")
        return None

    def modifier_document_3(self, document: FormationDocument3) -> Optional[FormationDocument3]:
        """Modifier les informations d'un document 3."""
        logger.info(f"Modification du document 3 pour l'organisation: {document.id}")
        
        # Préparation des données à envoyer
        data = {
            'id': asdict(document.id),
            'activiteListe': self._prepare_activite_liste_for_save(document.activiteListe)
        }
        
        result = self.client_manager.call_service("ModifierDocument3", **data)
        
        if result and 'body' in result and 'response' in result['body'] and 'document3' in result['body']['response']:
            # On récupère le document mis à jour
            return self.lire_document_3(document.id)
        
        logger.warning(f"Échec de modification du document 3 pour l'organisation: {document.id}")
        return None
    
    def _prepare_activite_liste_for_save(self, activite_liste: Optional[Doc3ActiviteListe]) -> dict:
        """Prépare la liste des activités pour la sauvegarde."""
        if not activite_liste:
            return {'activite': []}
        
        activites_save = []
        for activite in activite_liste.activite:
            # Prépare les enseignants pour cette activité
            enseignant_liste_save = None
            if activite.enseignantListe:
                enseignants_save = []
                for ens in activite.enseignantListe.enseignant:
                    enseignant_save = Doc3EnseignantDetailSave(
                        noMatEns=ens.noMatEns,
                        coDispo=ens.coDispo,
                        teStatut=ens.teStatut,
                        nbPeriodesAttribuees=ens.nbPeriodesAttribuees
                    )
                    enseignants_save.append(asdict(enseignant_save))
                
                enseignant_liste_save = {'enseignant': enseignants_save}
            
            # Création de l'activité pour la sauvegarde
            activite_save = Doc3ActiviteDetailSave(
                coNumBranche=activite.coNumBranche,
                noAnneeEtude=activite.noAnneeEtude,
                enseignantListe=enseignant_liste_save
            )
            activites_save.append(asdict(activite_save))
        
        return {'activite': activites_save}

def lire_document_3(organisation_id: OrganisationId) -> Optional[FormationDocument3]:
    """Fonction utilitaire pour lire le document 3."""
    service = Document3Service()
    return service.lire_document_3(organisation_id)

def modifier_document_3(document: FormationDocument3) -> Optional[FormationDocument3]:
    """Fonction utilitaire pour modifier le document 3."""
    service = Document3Service()
    return service.modifier_document_3(document)