from pprint import pformat
from pyetnic.services import *
from pyetnic.services.models import FormationDocument2, OrganisationId
from pyetnic.config import Config
from dataclasses import fields

from pyetnic.log_config import configure_logging
import logging

# Configurez le logging en utilisant la fonction du fichier log_config.py
configure_logging()

# Obtenez le logger pour ce script
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Début du script de test")
logger.info("Tentative de lister les formations")

Config.ANNEE_SCOLAIRE = "2023-2024"

result = lister_formations(annee_scolaire=Config.ANNEE_SCOLAIRE, etab_id=Config.ETAB_ID, impl_id=Config.IMPL_ID)

if result:
    for formation in result:
        if formation.organisations:
            for org in formation.organisations:
                org_id = OrganisationId(anneeScolaire=Config.ANNEE_SCOLAIRE,
                                        etabId=Config.ETAB_ID, 
                                        numAdmFormation=formation.numAdmFormation, 
                                        numOrganisation=org.id.numOrganisation,) 
                orga_detail = lire_organisation(org_id)
                for field in fields(Organisation):
                    if getattr(orga_detail, field.name) is not None:
                        setattr(org, field.name, getattr(orga_detail, field.name))
                logger.debug(f"    - Organisation {org.id.numOrganisation} : {pformat(vars(org))}")
                
else:
    logger.error("Erreur lors de la récupération des formations:")
    for message in result.messages:
        logger.error(f"  - {message}")