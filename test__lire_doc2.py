from dataclasses import fields
from pprint import pformat
from pyetnic.services import lire_document_2
from pyetnic.services.models import OrganisationId
from pyetnic.config import Config
from pprint import pprint
from pyetnic.log_config import configure_logging
import logging
from pyetnic.services.models import (FormationDocument2,
                                     Doc2ActiviteEnseignementDetail,
                                     Doc2ActiviteEnseignementList, 
                                     Doc2ActiviteEnseignementLine)

# Configurez le logging en utilisant la fonction du fichier log_config.py
configure_logging()

# Obtenez le logger pour ce script
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info("Tentative de lire un document2")

Config.ANNEE_SCOLAIRE = "2023-2024"

orga_id = OrganisationId(anneeScolaire=Config.ANNEE_SCOLAIRE, 
                         etabId=Config.ETAB_ID, 
                         numAdmFormation=455, numOrganisation=1) # Intro info 328/1
doc2 = lire_document_2(orga_id)

if doc2 and doc2.activiteEnseignementDetail and doc2.activiteEnseignementDetail.activiteEnseignementListe:
    logger.debug("Lignes d'activités d'enseignement:")
    
    # En-tête du tableau
    header = f"{'N°':^4}|{'Branche':^6}|{'Catégorie':^10}|{'Nom':^40}|{'Année':^6}|{'Élèves':^7}|{'Prévues':^8}|{'Réelles':^8}"
    logger.debug("-" * len(header))
    logger.debug(header)
    logger.debug("-" * len(header))
    
    # Lignes du tableau
    for idx, activite in enumerate(doc2.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement, 1):
        logger.debug(f"{idx:4}|{activite.coNumBranche:^6}|{activite.coCategorie:^10}|{activite.teNomBranche[:40]:40}|{activite.coAnnEtude:^6}|{activite.nbEleveC1:^7}|{activite.nbPeriodePrevueAn1:^8.1f}|{activite.nbPeriodeReelleAn1:^8.1f}")
    
    logger.debug("-" * len(header))
else:
    logger.warning("Aucune activité d'enseignement trouvée dans le document 2")
