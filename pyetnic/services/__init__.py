"""
Package de services ETNIC.

Ce package contient les classes et fonctions pour interagir avec les
différents services SOAP d'ETNIC.
"""
import logging
logger = logging.getLogger(__name__)
logger.debug("Initialisation du package services")

from .formations_liste import FormationsListeService
from .organisation import OrganisationService
from .models import OrganisationApercu
from .document1 import Document1Service
from .document2 import Document2Service
from .document3 import Document3Service
from .seps import RechercheEtudiantsService
from .enregistrer_etudiant import EnregistrerEtudiantService
from .inscriptions import InscriptionsService
from ..nomenclatures import TYPES_INTERVENTION_EXTERIEURE

# Importation et exposition des fonctions pour la liste des formations
# Instanciation du service
formations_service = FormationsListeService()
# Exposition des méthodes du service
lister_formations_organisables = formations_service.lister_formations_organisables
lister_formations = formations_service.lister_formations

# Instanciation du service
organisation_service = OrganisationService()
# Exposition des méthodes du service
lire_organisation = organisation_service.lire_organisation
creer_organisation = organisation_service.creer_organisation
modifier_organisation = organisation_service.modifier_organisation
supprimer_organisation = organisation_service.supprimer_organisation

# instanciation du service
document2_service = Document2Service()
# Exposition des méthodes du service
lire_document_2 = document2_service.lire_document_2
modifier_document_2 = document2_service.modifier_document_2

# instanciation du service
document3_service = Document3Service()
# Exposition des méthodes du service
lire_document_3 = document3_service.lire_document_3
modifier_document_3 = document3_service.modifier_document_3

# instanciation du service
document1_service = Document1Service()
# Exposition des méthodes du service
lire_document_1 = document1_service.lire_document_1
modifier_document_1 = document1_service.modifier_document_1
approuver_document_1 = document1_service.approuver_document_1

# instanciation du service SEPS
seps_service = RechercheEtudiantsService()
# Exposition des méthodes du service
lire_etudiant = seps_service.lire_etudiant
rechercher_etudiants = seps_service.rechercher_etudiants

# instanciation du service SEPS EnregistrerEtudiant
enregistrer_etudiant_service = EnregistrerEtudiantService()
# Exposition des méthodes du service
enregistrer_etudiant = enregistrer_etudiant_service.enregistrer_etudiant
modifier_etudiant = enregistrer_etudiant_service.modifier_etudiant

# instanciation des services SEPS Inscriptions
inscriptions_service = InscriptionsService()
# Exposition des méthodes du service
rechercher_inscriptions = inscriptions_service.rechercher_inscriptions
enregistrer_inscription = inscriptions_service.enregistrer_inscription
modifier_inscription = inscriptions_service.modifier_inscription

__all__ = [
    'FormationsListeService',
    'OrganisationService',
    'OrganisationApercu',
    'Document1Service',
    'Document2Service',
    'Document3Service',
    'lister_formations_organisables',
    'lister_formations',
    'lire_organisation',
    'creer_organisation',
    'modifier_organisation',
    'supprimer_organisation',
    'lire_document_1',
    'modifier_document_1',
    'approuver_document_1',
    'lire_document_2',
    'modifier_document_2',
    'lire_document_3',
    'modifier_document_3',
    'RechercheEtudiantsService',
    'lire_etudiant',
    'rechercher_etudiants',
    'EnregistrerEtudiantService',
    'enregistrer_etudiant',
    'modifier_etudiant',
    'InscriptionsService',
    'rechercher_inscriptions',
    'enregistrer_inscription',
    'modifier_inscription',
    'TYPES_INTERVENTION_EXTERIEURE',
]
