"""
Package de services ETNIC.

Ce package contient les classes et fonctions pour interagir avec les
différents services SOAP d'ETNIC.
"""

# Importation et exposition des fonctions pour la liste des formations
from .formations_liste import (
    lister_formations,
    lister_formations_organisables,
    FormationsListeService
)

# Importation et exposition des fonctions pour le service d'organisation
from .organisation import (
    creer_organisation,
    modifier_organisation,
    lire_organisation,
    supprimer_organisation
)

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