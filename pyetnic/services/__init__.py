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
]
