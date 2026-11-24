import logging
from pprint import pprint
from pyetnic.eprom import EtnicBusinessError, EtnicDocumentNotAccessibleError, lister_formations, lire_document_3

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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
    try:
        result = lister_formations()
    except EtnicBusinessError as exc:
        logger.error("Erreur lors de la liste des formations : %s", exc)
        raise SystemExit(1) from exc

    for formation in result:
        for organisation in formation.organisations:
            logger.info("Formation %s, organisation %s", organisation.id.numAdmFormation, organisation.id.numOrganisation)
            try:
                doc3 = lire_document_3(organisation.id)
            except EtnicDocumentNotAccessibleError:
                logger.info("Document 3 pas encore accessible (Doc A ou Doc 2 non approuvé)")
                continue
            pprint(extraire_noms_prenoms(doc3))
