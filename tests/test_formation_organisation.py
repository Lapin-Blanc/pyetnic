# test_formation_organisation.py

import pytest
from pyetnic.services import creer_organisation, lire_organisation, modifier_organisation, supprimer_organisation
from datetime import datetime

def get_previous_school_year():
    current_year = datetime.now().year
    if datetime.now().month < 9:  # Si nous sommes avant septembre
        return f"{current_year-2}-{current_year-1}"
    else:
        return f"{current_year-1}-{current_year}"

@pytest.fixture
def nouvelle_organisation():
    annee_scolaire = get_previous_school_year()
    date_debut = f"{annee_scolaire.split('-')[0]}-09-01"
    date_fin = f"{annee_scolaire.split('-')[1]}-06-30"
    
    org = creer_organisation(403, date_debut, date_fin, annee_scolaire=annee_scolaire)
    yield org
    supprimer_organisation(403, org['body']['response']['organisation']['id']['numOrganisation'], annee_scolaire=annee_scolaire)

def test_creer_lire_organisation(nouvelle_organisation):
    assert nouvelle_organisation['body']['success'] == True
    
    num_org = nouvelle_organisation['body']['response']['organisation']['id']['numOrganisation']
    annee_scolaire = nouvelle_organisation['body']['response']['organisation']['id']['anneeScolaire']
    
    org_lue = lire_organisation(403, num_org, annee_scolaire=annee_scolaire)
    assert org_lue['body']['success'] == True
    assert org_lue['body']['response']['organisation']['id']['numAdmFormation'] == 403
    assert org_lue['body']['response']['organisation']['id']['anneeScolaire'] == annee_scolaire

def test_modifier_organisation(nouvelle_organisation):
    num_org = nouvelle_organisation['body']['response']['organisation']['id']['numOrganisation']
    annee_scolaire = nouvelle_organisation['body']['response']['organisation']['id']['anneeScolaire']
    nouvelle_date_fin = f"{annee_scolaire.split('-')[1]}-05-31"  # On modifie la date de fin au 31 mai
    
    org_modifiee = modifier_organisation(403, num_org,
                                         nouvelle_organisation['body']['response']['organisation']['dateDebutOrganisation'],
                                         nouvelle_date_fin,
                                         annee_scolaire=annee_scolaire)
    
    assert org_modifiee['body']['success'] == True
    
    # Convertir la date retournée en chaîne de caractères pour la comparaison
    date_fin_retournee = org_modifiee['body']['response']['organisation']['dateFinOrganisation']
    date_fin_str = date_fin_retournee.strftime('%Y-%m-%d')
    
    assert date_fin_str == nouvelle_date_fin

    # Ou, alternativement, convertir la chaîne en objet date pour la comparaison
    # nouvelle_date_fin_obj = datetime.strptime(nouvelle_date_fin, '%Y-%m-%d').date()
    # assert org_modifiee['body']['response']['organisation']['dateFinOrganisation'] == nouvelle_date_fin_obj
    
def test_lire_organisation_existante():
    annee_scolaire = get_previous_school_year()
    org = lire_organisation(328, 1, annee_scolaire=annee_scolaire)
    assert org['body']['success'] == True
    assert org['body']['response']['organisation']['id']['numAdmFormation'] == 328
    assert org['body']['response']['organisation']['id']['numOrganisation'] == 1
    assert org['body']['response']['organisation']['id']['anneeScolaire'] == annee_scolaire