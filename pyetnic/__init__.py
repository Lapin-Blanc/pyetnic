"""Pyetnic — client Python pour les services web SOAP d'ETNIC.

Usage :
    import pyetnic
    pyetnic.eprom.lister_formations(annee_scolaire="2024-2025")
    pyetnic.seps.rechercher_etudiants(nom="DUPONT")

    # ou import explicite
    from pyetnic.eprom import lire_organisation, OrganisationId
    from pyetnic.seps import lire_etudiant
"""

from typing import Any

from . import eprom
from . import seps
from .config import Config
from .error_mode import permissive_errors, strict_errors
from .exceptions import (
    EtnicError,
    EtnicTransportError,
    EtnicResponseError,
    EtnicBusinessError,
    EtnicDocumentNotAccessibleError,
    EtnicNotFoundError,
    EtnicValidationError,
    EtnicAlreadyApprovedError,
    EtnicConcurrencyError,
)
from ._deprecated import deprecated_name

__version__ = "0.3.0b3"
__author__ = "Fabien Toune"
__all__ = [
    "eprom",
    "seps",
    "Config",
    "strict_errors",
    "permissive_errors",
    "EtnicError",
    "EtnicTransportError",
    "EtnicResponseError",
    "EtnicBusinessError",
    "EtnicDocumentNotAccessibleError",
    "EtnicNotFoundError",
    "EtnicValidationError",
    "EtnicAlreadyApprovedError",
    "EtnicConcurrencyError",
]


def __getattr__(name: str) -> Any:
    """The deprecated names, served with a ``DeprecationWarning`` until 1.0."""
    if name in ("SoapError",):
        return deprecated_name(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def run_cli() -> None:
    from .cli import main as cli_main
    cli_main()
