"""Centralized configuration for ETNIC services."""

import logging
import os
from typing import NamedTuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _load_dotenv_compat() -> None:
    """Load .env without crashing on legacy Windows encodings."""
    try:
        load_dotenv(encoding="utf-8")
        return
    except UnicodeDecodeError:
        logger.warning("Could not decode .env as UTF-8. Retrying with cp1252.")

    try:
        load_dotenv(encoding="cp1252")
    except UnicodeDecodeError:
        logger.warning("Could not decode .env as cp1252. Skipping .env loading.")


_load_dotenv_compat()


class ServiceConfig(NamedTuple):
    endpoint: str
    wsdl_path: str
    binding_name: str
    auth_type: str = "username_token"  # "username_token" | "x509_pfx"


class Config:
    """Centralized application configuration."""

    ENV = os.getenv("ENV", "dev")

    USERNAME = os.getenv(f"{ENV.upper()}_USERNAME")
    PASSWORD = os.getenv(f"{ENV.upper()}_PASSWORD")

    ANNEE_SCOLAIRE = os.getenv("DEFAULT_SCHOOLYEAR", "2023-2024")
    ETAB_ID = os.getenv("DEFAULT_ETABID")
    IMPL_ID = os.getenv("DEFAULT_IMPLID")

    # Certificat X509 pour les services SEPS (chemin relatif au répertoire courant)
    SEPS_PFX_PATH = os.getenv("SEPS_PFX_PATH")
    SEPS_PFX_PASSWORD = os.getenv("SEPS_PFX_PASSWORD")

    SERVICES = {
        "LISTE_FORMATIONS": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formations/liste/v2",
            wsdl_path="EPROM_Formations_Liste_2.0/EpromFormationsListeService_external_v2.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formations/liste/v2}EPROMFormationsListeExternalV2Binding",
        ),
        "ORGANISATION": ServiceConfig(
            endpoint=f"https://ws{'-tq' if ENV == 'dev' else ''}.etnic.be/eprom/formation/organisation/v7",
            wsdl_path="EPROM_Formation_Organisation_7.0/EpromFormationOrganisationService_v7.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/organisation/v7}EPROMFormationOrganisationV7Binding",
        ),
        "DOCUMENT1": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/document1/v1",
            wsdl_path="EPROM_Formation_Population_1.0/EpromFormationDocument1Service_external_v1.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/document1/v1}EPROMFormationDocument1ExternalV1Binding",
        ),
        "DOCUMENT2": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/document2/v1",
            wsdl_path="EPROM_Formation_Périodes_1.0/EpromFormationDocument2Service_external_v1.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/document2/v1}EPROMFormationDocument2ExternalV1Binding",
        ),
        "DOCUMENT3": ServiceConfig(
            endpoint=f"https://services-web.{'tq.' if ENV == 'dev' else ''}etnic.be:11443/eprom/formation/document3/v1",
            wsdl_path="EPROM_Document_3_1.0/EpromFormationDocument3Service_external_v1.wsdl",
            binding_name="{http://services-web.etnic.be/eprom/formation/document3/v1}EPROMFormationDocument3ExternalV1Binding",
        ),
        "SEPS_RECHERCHE_ETUDIANTS": ServiceConfig(
            endpoint=f"https://ws{'-tq' if ENV == 'dev' else ''}.etnic.be/seps/rechercheEtudiants/v1",
            wsdl_path="SEPS_Recherche_Étudiants_2.1/SEPSRechercheEtudiantsService_external_v1.wsdl",
            binding_name="{http://ws.etnic.be/seps/rechercheEtudiants/v1}SEPSRechercheEtudiantsV1ExternalBinding",
            auth_type="x509_pfx",
        ),
    }

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


if not Config.validate():
    logger.warning("Configuration is incomplete. Some features may not work.")
