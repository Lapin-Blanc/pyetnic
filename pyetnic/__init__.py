"""Pyetnic — client Python pour les services web SOAP d'ETNIC.

Usage :
    import pyetnic
    pyetnic.eprom.lister_formations(annee_scolaire="2024-2025")
    pyetnic.seps.rechercher_etudiants(nom="DUPONT")

    # ou import explicite
    from pyetnic.eprom import lire_organisation, OrganisationId
    from pyetnic.seps import lire_etudiant
"""

from . import eprom
from . import seps
from .config import Config
from .exceptions import (
    EtnicError,
    EtnicTransportError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
)
from .soap_client import SoapError  # legacy alias for EtnicTransportError

__version__ = "0.0.12"
__author__ = "Fabien Toune"
__all__ = [
    "eprom",
    "seps",
    "Config",
    "EtnicError",
    "EtnicTransportError",
    "EtnicBusinessError",
    "EtnicDocumentNotAccessibleError",
    "EtnicNotFoundError",
    "EtnicValidationError",
    "SoapError",
]


def run_cli() -> None:
    from .cli import main as cli_main
    cli_main()
