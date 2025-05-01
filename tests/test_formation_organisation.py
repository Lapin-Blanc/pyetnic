# test_formation_organisation.py

import pytest
import logging
from pyetnic.services.models import OrganisationId, Organisation
from pyetnic.config import Config
from pyetnic.services import lister_formations, lire_organisation
from dataclasses import fields

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def setup_logging():
    # Cette fixture sera automatiquement utilisée pour chaque test
    logger.setLevel(logging.DEBUG)
    yield
    # Vous pouvez remettre le niveau de logging à son état d'origine après le test si nécessaire
    logger.setLevel(logging.INFO)

def test_lister_formations_et_organisations():
    logger.info("Début du test de liste des formations et organisations")
    result = lister_formations(annee_scolaire=Config.ANNEE_SCOLAIRE, etab_id=Config.ETAB_ID, impl_id=Config.IMPL_ID)
    
    assert result is not None
    assert len(result) > 0, "Aucune formation trouvée"
    
    for formation in result:
        assert formation.numAdmFormation > 0
        assert formation.libelleFormation != ""
        assert formation.codeFormation != ""
        logger.debug(f"Formation: {formation.numAdmFormation} - {formation.libelleFormation} (Code: {formation.codeFormation})")

        if formation.organisations:
            logger.debug("  Organisations:")
            for org in formation.organisations:
                org_id = OrganisationId(
                    anneeScolaire=Config.ANNEE_SCOLAIRE,
                    etabId=Config.ETAB_ID,
                    numAdmFormation=formation.numAdmFormation,
                    numOrganisation=org.id.numOrganisation
                )
                orga_full = lire_organisation(org_id)
                
                assert orga_full is not None, f"Organisation {org.id.numOrganisation} non trouvée"
                
                # Vérifier que tous les champs de l'organisation complète sont présents
                for field in fields(Organisation):
                    assert hasattr(orga_full, field.name), f"Le champ {field.name} est manquant dans l'organisation"
                
                # Vérifier quelques champs spécifiques
                assert orga_full.dateDebutOrganisation is not None
                assert orga_full.dateFinOrganisation is not None
                assert orga_full.dateDebutOrganisation <= orga_full.dateFinOrganisation
                logger.debug(f"    - orga {org.id.numOrganisation} du {org.dateDebutOrganisation} au {org.dateFinOrganisation}")
    
    logger.info("Fin du test de liste des formations et organisations")
