# test_formation_organisation.py

import pytest
from pyetnic.services import creer_organisation, lire_organisation, modifier_organisation, supprimer_organisation
from datetime import datetime, date
from pyetnic.services.organisation import OrganisationService

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

@pytest.fixture
def organisation_service():
    """Fixture to provide an instance of OrganisationService."""
    return OrganisationService()

@pytest.fixture
def organisation_data():
    """Fixture to provide default data for creating an organisation."""
    return {
        "num_adm_formation": 328,
        "date_debut": date(2023, 9, 1),
        "date_fin": date(2024, 6, 30),
        "annee_scolaire": "2023-2024",
        "etab_id": 3052,
        "impl_id": 6050
    }

def test_creer_organisation(organisation_service, organisation_data):
    """Test the creation of an organisation."""
    result = organisation_service.creer_organisation(**organisation_data)
    assert result['body']['success'] is True
    assert result['body']['response']['organisation']['id']['numAdmFormation'] == organisation_data['num_adm_formation']

def test_lire_organisation(organisation_service, organisation_data):
    """Test reading an existing organisation."""
    # First, create the organisation
    organisation_service.creer_organisation(**organisation_data)
    # Then, read the organisation
    result = organisation_service.lire_organisation(organisation_data['num_adm_formation'], 8)
    assert result['body']['success'] is True
    assert result['body']['response']['organisation']['id']['numOrganisation'] == 8

def test_modifier_organisation(organisation_service, organisation_data):
    """Test modifying an existing organisation."""
    # First, create the organisation
    organisation_service.creer_organisation(**organisation_data)
    # Modify the organisation
    result = organisation_service.modifier_organisation(organisation_data['num_adm_formation'], 8, organisation_data['date_debut'], organisation_data['date_fin'], enseignementHybride=True)
    assert result['body']['success'] is True
    assert result['body']['response']['organisation']['enseignementHybride'] is True

def test_supprimer_organisation(organisation_service, organisation_data):
    """Test deleting an existing organisation."""
    # First, create the organisation
    organisation_service.creer_organisation(**organisation_data)
    # Delete the organisation
    result = organisation_service.supprimer_organisation(organisation_data['num_adm_formation'], 8)
    assert result['body']['success'] is True