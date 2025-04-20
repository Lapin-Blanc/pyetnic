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


# Note: Les autres services (organisation, document1, document2) seront importés
# de manière similaire lorsque leurs modules seront implémentés.