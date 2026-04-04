"""Centralized configuration for ETNIC services.

Config attributes are resolved lazily (on access, not at import time).
This allows integrators (e.g. Django) to set credentials programmatically
before the first SOAP call, without manipulating os.environ before import.

Usage:
    from pyetnic.config import Config

    # Override credentials programmatically
    Config.ENV = "prod"
    Config.USERNAME = "my_user"
    Config.PASSWORD = "my_pass"

    # Or rely on .env / os.environ (loaded lazily on first access)
"""

from __future__ import annotations

import logging
import os
from typing import Any, NamedTuple

logger = logging.getLogger(__name__)


def _load_dotenv_compat() -> None:
    """Load .env without crashing on legacy Windows encodings."""
    from dotenv import load_dotenv

    try:
        load_dotenv(encoding="utf-8")
        return
    except UnicodeDecodeError:
        logger.warning("Could not decode .env as UTF-8. Retrying with cp1252.")

    try:
        load_dotenv(encoding="cp1252")
    except UnicodeDecodeError:
        logger.warning("Could not decode .env as cp1252. Skipping .env loading.")


class ServiceConfig(NamedTuple):
    endpoint: str
    wsdl_path: str
    binding_name: str
    auth_type: str = "username_token"  # "username_token" | "x509_pfx"


# ---------------------------------------------------------------------------
# Mapping: Config attribute name → (env var name, default value)
# USERNAME and PASSWORD are dynamic (depend on ENV) and handled separately.
# ---------------------------------------------------------------------------
_SIMPLE_ENV_MAP: dict[str, tuple[str, str | None]] = {
    "ENV": ("ENV", "dev"),
    "ANNEE_SCOLAIRE": ("DEFAULT_SCHOOLYEAR", "2023-2024"),
    "ETAB_ID": ("DEFAULT_ETABID", None),
    "IMPL_ID": ("DEFAULT_IMPLID", None),
    "SEPS_PFX_PATH": ("SEPS_PFX_PATH", None),
    "SEPS_PFX_PASSWORD": ("SEPS_PFX_PASSWORD", None),
}

_ALL_CONFIG_ATTRS = {*_SIMPLE_ENV_MAP, "USERNAME", "PASSWORD", "SERVICES"}


class _ConfigMeta(type):
    """Metaclass enabling lazy resolution of Config attributes.

    Attribute reads go through __getattr__ (since no class-level attrs exist).
    Writes via ``Config.FOO = val`` store into ``_overrides`` so the next read
    returns the override instead of hitting os.environ.
    """

    _overrides: dict[str, Any] = {}
    _dotenv_loaded: bool = False

    # -- dotenv handling ----------------------------------------------------

    def _ensure_dotenv(cls) -> None:
        """Load .env lazily on first attribute access."""
        if not _ConfigMeta._dotenv_loaded:
            _load_dotenv_compat()
            _ConfigMeta._dotenv_loaded = True

    # -- attribute protocol -------------------------------------------------

    def __getattr__(cls, name: str) -> Any:
        if name not in _ALL_CONFIG_ATTRS:
            raise AttributeError(f"type object 'Config' has no attribute {name!r}")

        # 1. Explicit override wins
        if name in _ConfigMeta._overrides:
            return _ConfigMeta._overrides[name]

        # 2. Ensure .env is loaded
        cls._ensure_dotenv()

        # 3. Dynamic attrs
        if name == "USERNAME":
            return os.getenv(f"{cls.ENV.upper()}_USERNAME")
        if name == "PASSWORD":
            return os.getenv(f"{cls.ENV.upper()}_PASSWORD")
        if name == "SERVICES":
            return cls._build_services()

        # 4. Simple env lookup
        env_var, default = _SIMPLE_ENV_MAP[name]
        return os.getenv(env_var, default)

    def __setattr__(cls, name: str, value: Any) -> None:
        if name in _ALL_CONFIG_ATTRS:
            _ConfigMeta._overrides[name] = value
        else:
            type.__setattr__(cls, name, value)


class Config(metaclass=_ConfigMeta):
    """Centralized application configuration.

    All attributes are resolved lazily on access.  You can override any
    attribute with a simple assignment (``Config.USERNAME = "foo"``).
    """

    @classmethod
    def load_from_dotenv(cls) -> None:
        """Explicitly load .env file.  Idempotent — safe to call multiple times."""
        cls._ensure_dotenv()

    @classmethod
    def validate(cls) -> bool:
        """Validate required environment variables."""
        missing = []

        if not cls.USERNAME:
            missing.append(f"{cls.ENV.upper()}_USERNAME")
        if not cls.PASSWORD:
            missing.append(f"{cls.ENV.upper()}_PASSWORD")

        if missing:
            logger.warning("Missing environment variables: %s", ", ".join(missing))
            return False

        return True

    @classmethod
    def get_verify_ssl(cls) -> bool:
        """Return whether SSL verification should be enabled."""
        return cls.ENV != "dev"

    @classmethod
    def _build_services(cls) -> dict[str, ServiceConfig]:
        """Build the SERVICES dict based on the current ENV value."""
        env = cls.ENV
        return {
            "LISTE_FORMATIONS": ServiceConfig(
                endpoint=f"https://services-web.{'tq.' if env == 'dev' else ''}etnic.be:11443/eprom/formations/liste/v2",
                wsdl_path="EPROM_Formations_Liste_2.0/EpromFormationsListeService_external_v2.wsdl",
                binding_name="{http://services-web.etnic.be/eprom/formations/liste/v2}EPROMFormationsListeExternalV2Binding",
            ),
            "ORGANISATION": ServiceConfig(
                endpoint=f"https://ws{'-tq' if env == 'dev' else ''}.etnic.be/eprom/formation/organisation/v7",
                wsdl_path="EPROM_Formation_Organisation_7.0/EpromFormationOrganisationService_v7.wsdl",
                binding_name="{http://services-web.etnic.be/eprom/formation/organisation/v7}EPROMFormationOrganisationV7Binding",
            ),
            "DOCUMENT1": ServiceConfig(
                endpoint=f"https://services-web.{'tq.' if env == 'dev' else ''}etnic.be:11443/eprom/formation/document1/v1",
                wsdl_path="EPROM_Formation_Population_1.0/EpromFormationDocument1Service_external_v1.wsdl",
                binding_name="{http://services-web.etnic.be/eprom/formation/document1/v1}EPROMFormationDocument1ExternalV1Binding",
            ),
            "DOCUMENT2": ServiceConfig(
                endpoint=f"https://services-web.{'tq.' if env == 'dev' else ''}etnic.be:11443/eprom/formation/document2/v1",
                wsdl_path="EPROM_Formation_Periodes_1.0/EpromFormationDocument2Service_external_v1.wsdl",
                binding_name="{http://services-web.etnic.be/eprom/formation/document2/v1}EPROMFormationDocument2ExternalV1Binding",
            ),
            "DOCUMENT3": ServiceConfig(
                endpoint=f"https://services-web.{'tq.' if env == 'dev' else ''}etnic.be:11443/eprom/formation/document3/v1",
                wsdl_path="EPROM_Document_3_1.0/EpromFormationDocument3Service_external_v1.wsdl",
                binding_name="{http://services-web.etnic.be/eprom/formation/document3/v1}EPROMFormationDocument3ExternalV1Binding",
            ),
            "SEPS_RECHERCHE_ETUDIANTS": ServiceConfig(
                endpoint=f"https://ws{'-tq' if env == 'dev' else ''}.etnic.be/seps/rechercheEtudiants/v1",
                wsdl_path="SEPS_Recherche_Etudiants_2.1/SEPSRechercheEtudiantsService_external_v1.wsdl",
                binding_name="{http://ws.etnic.be/seps/rechercheEtudiants/v1}SEPSRechercheEtudiantsV1ExternalBinding",
                auth_type="x509_pfx",
            ),
            "SEPS_ENREGISTRER_ETUDIANT": ServiceConfig(
                endpoint=f"https://ws{'-tq' if env == 'dev' else ''}.etnic.be/seps/enregistrerEtudiant/v1",
                wsdl_path="SEPS_Enregistrer_Etudiant_2.1/SEPSEnregistrerEtudiantService_external_v1.wsdl",
                binding_name="{http://ws.etnic.be/seps/enregistrerEtudiant/v1}SEPSEnregistrerEtudiantV1ExternalBinding",
                auth_type="x509_pfx",
            ),
            "SEPS_ENREGISTRER_INSCRIPTION": ServiceConfig(
                endpoint=f"https://ws{'-tq' if env == 'dev' else ''}.etnic.be/seps/enregistrerInscription/v1",
                wsdl_path="SEPS_Enregistrer_Inscription_2.1/SEPSEnregistrerInscriptionService_external_v1.wsdl",
                binding_name="{http://ws.etnic.be/seps/enregistrerInscription/v1}SEPSEnregistrerInscriptionV1ExternalBinding",
                auth_type="x509_pfx",
            ),
            "SEPS_RECHERCHE_INSCRIPTIONS": ServiceConfig(
                endpoint=f"https://ws{'-tq' if env == 'dev' else ''}.etnic.be/seps/rechercheInscriptions/v1",
                wsdl_path="SEPS_Recherche_Inscriptions_2.1/SEPSRechercheInscriptionsService_external_v1.wsdl",
                binding_name="{http://ws.etnic.be/seps/rechercheInscriptions/v1}SEPSRechercheInscriptionsV1ExternalBinding",
                auth_type="x509_pfx",
            ),
        }

    @classmethod
    def _reset(cls) -> None:
        """Reset all overrides and dotenv state.  For testing only."""
        _ConfigMeta._overrides.clear()
        _ConfigMeta._dotenv_loaded = False
