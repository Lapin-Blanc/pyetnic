"""
Package de services ETNIC.

Ce package contient les classes et fonctions pour interagir avec les
différents services SOAP d'ETNIC.
"""
from .formations_liste import FormationsListeService
from .organisation import OrganisationService
# Importation et exposition des fonctions pour la liste des formations
# Instanciation du service
formations_service = FormationsListeService()
# Exposition des méthodes du service
lister_formations_organisables = formations_service.lister_formations_organisables
lister_formations = formations_service.lister_formations

# Instanciation du service
organisation_service = OrganisationService()
# Exposition des méthodes du service
creer_organisation = organisation_service.creer_organisation
modifier_organisation = organisation_service.modifier_organisation
lire_organisation = organisation_service.lire_organisation
supprimer_organisation = organisation_service.supprimer_organisation


# Importation et exposition des fonctions pour le service document1
from .document1 import (
    lire_document_1,
    modifier_document_1,
    approuver_document_1
)

# Importation et exposition des fonctions pour le service document2
from .document2 import (
    lire_document_2,
    modifier_document_2
)