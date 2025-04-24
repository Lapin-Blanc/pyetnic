from pyetnic.services import *
from pprint import pprint

def extraire_noms_prenoms(data):
    enseignants_info = []

    try:
        activites = data['body']['response']['document3']['activiteListe']['activite']
        for activite in activites:
            enseignants = activite.get('enseignantListe', {}).get('enseignant', [])
            for ens in enseignants:
                nom = ens.get('teNomEns')
                prenom = ens.get('tePrenomEns')
                if nom or prenom:
                    enseignants_info.append({'Nom': nom, 'Prénom': prenom})
    except (KeyError, TypeError):
        print("Données non conformes")

    return enseignants_info

formations = [f for f in lister_formations()["body"]["response"]["formation"] if f["organisation"]]

organisations = []
for formation in formations:
    for orga in formation["organisation"]:
        num_adm = formation["numAdmFormation"]
        num_orga = orga["numOrganisation"]
        print(num_adm, num_orga)
        print(type(num_adm), type(num_orga))
        doc3 = lire_document_3(num_adm, num_orga)
        noms_prenoms = extraire_noms_prenoms(doc3)
        pprint(noms_prenoms)