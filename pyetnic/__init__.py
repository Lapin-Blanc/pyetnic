"""
Pyetnic - Bibliothèque d'accès aux services web ETNIC pour l'enseignement de promotion sociale.

Ce module permet d'interagir avec les services SOAP d'ETNIC pour gérer les formations,
les organisations, les documents administratifs, etc.
"""

__version__ = '0.0.3'
__author__ = 'Fabien Toune'

# Exposition des fonctions principales pour un accès direct
from .services import (
    # Formations liste
    lister_formations,
    lister_formations_organisables,
    
    # Organisation
    creer_organisation,
    modifier_organisation, 
    lire_organisation,
    supprimer_organisation,
    
    # Document 1
    lire_document_1,
    modifier_document_1,
    approuver_document_1,
    
    # Document 2
    lire_document_2,
    modifier_document_2
)

# Exposition des constantes de configuration
from .config import anneeScolaire, etabId, implId

from .cli import main as cli_main

def run_cli():
    cli_main()
