"""Pyetnic package public API."""

from importlib import import_module
from typing import Any

__version__ = "0.0.5"
__author__ = "Fabien Toune"

_SERVICE_EXPORTS = {
    "lister_formations",
    "lister_formations_organisables",
    "OrganisationApercu",
    "lire_organisation",
    "creer_organisation",
    "modifier_organisation",
    "supprimer_organisation",
    "lire_document_1",
    "modifier_document_1",
    "approuver_document_1",
    "lire_document_2",
    "modifier_document_2",
    "lire_document_3",
    "modifier_document_3",
}

__all__ = sorted([*_SERVICE_EXPORTS, "Config", "run_cli"])


def __getattr__(name: str) -> Any:
    if name in _SERVICE_EXPORTS:
        services = import_module(".services", __name__)
        return getattr(services, name)
    if name == "Config":
        return import_module(".config", __name__).Config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def run_cli() -> None:
    from .cli import main as cli_main

    cli_main()
