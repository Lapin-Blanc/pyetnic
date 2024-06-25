# test_formation_document1.py

import pytest
from pprint import pprint
from pyetnic.services import lire_document_1, modifier_document_1

def test_lire_document_1():
    doc = lire_document_1(328, 1)
    assert 'body' in doc
    assert doc['body']['success'] == True
    assert 'response' in doc['body']
    assert 'document1' in doc['body']['response']
    
    document1 = doc['body']['response']['document1']
    assert document1['id']['numAdmFormation'] == 328
    assert document1['id']['numOrganisation'] == 1

def test_modifier_document_1():
    populations_liste = [
        {
            'coAnnEtude': 1,
            'nbEleveA': 9,
            'nbEleveEhr': 0,
            'nbEleveB': 0,
            'nbEleveDem': 1,
            'nbEleveMin': 0,
            'nbEleveExm': 0,
            'nbElevePl': 2,
            'nbEleveTotHom': 2,
            'nbEleveTotFem': 7
        }
    ]
    
    
    doc_modifie = modifier_document_1(328, 1, 
                                      populations_liste=populations_liste)
    
    pprint(doc_modifie)
    assert doc_modifie['body']['success'] == True
    assert 'document1' in doc_modifie['body']['response']
    
    document1 = doc_modifie['body']['response']['document1']
    
    # Vérification des droits d'inscription
    droit_inscription_modifie = document1['droitInscriptionListe']['droitInscription'][0]
    assert droit_inscription_modifie['coTypeDroitInscription'] == "DI"
    assert droit_inscription_modifie['mnMontant'] == 50.00
    assert droit_inscription_modifie['nbEleve'] == 10
    
