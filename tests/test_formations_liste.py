# test_formations_liste.py

import pytest
from pyetnic.services import lister_formations_organisables, lister_formations

def test_lister_formations_organisables():
    result = lister_formations_organisables()
    assert 'body' in result
    assert result['body']['success'] == True
    assert 'response' in result['body']
    assert 'formation' in result['body']['response']
    assert isinstance(result['body']['response']['formation'], list)
    assert len(result['body']['response']['formation']) > 0
    
    formation = result['body']['response']['formation'][0]
    assert 'numAdmFormation' in formation
    assert 'libelleFormation' in formation
    assert 'codeFormation' in formation

def test_lister_formations():
    result = lister_formations()
    assert 'body' in result
    assert result['body']['success'] == True
    assert 'response' in result['body']
    assert 'formation' in result['body']['response']
    assert isinstance(result['body']['response']['formation'], list)
    assert len(result['body']['response']['formation']) > 0
    
    formation = result['body']['response']['formation'][0]
    assert 'numAdmFormation' in formation
    assert 'libelleFormation' in formation
    assert 'codeFormation' in formation
    assert 'organisation' in formation
    
    if formation['organisation']:
        organisation = formation['organisation'][0]
        assert 'numOrganisation' in organisation
        assert 'dateDebutOrganisation' in organisation
        assert 'dateFinOrganisation' in organisation
