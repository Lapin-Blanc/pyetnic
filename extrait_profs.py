import logging
from pprint import pprint
from pyetnic.services import lister_formations, lire_document_3
from pyetnic.log_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def extraire_noms_prenoms(doc3):
    """Extrait les noms et prénoms des enseignants d'un document 3."""
    enseignants_info = []
    if not doc3 or not doc3.activiteListe:
        return enseignants_info
    for activite in doc3.activiteListe.activite:
        if not activite.enseignantListe:
            continue
        for ens in activite.enseignantListe.enseignant:
            if ens.teNomEns or ens.tePrenomEns:
                enseignants_info.append({'Nom': ens.teNomEns, 'Prénom': ens.tePrenomEns})
    return enseignants_info


if __name__ == "__main__":
    result = lister_formations()
    if not result:
        logger.error(f"Erreur lors de la liste des formations: {result.messages}")
        raise SystemExit(1)

    for formation in result:
        for organisation in formation.organisations:
            logger.info(f"Formation {organisation.id.numAdmFormation}, organisation {organisation.id.numOrganisation}")
            doc3 = lire_document_3(organisation.id)
            noms_prenoms = extraire_noms_prenoms(doc3)
            pprint(noms_prenoms)
