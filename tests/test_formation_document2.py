import pytest
from pyetnic.services import lire_document_2, modifier_document_2

def test_lire_document_2():
    doc = lire_document_2(328, 1)
    assert doc['body']['success'] == True
    assert doc['body']['response']['document2']['id']['numAdmFormation'] == 328
    assert doc['body']['response']['document2']['id']['numOrganisation'] == 1

def test_modifier_document_2():
    activites = [
        {
            "coNumBranche": 1,
            "nbEleveC1": 12,
            "nbPeriodePrevueAn1": 20.0,
            "nbPeriodePrevueAn2": 0.0,
        }
    ]
    
    doc_modifie = modifier_document_2(328, 1, activite_enseignement_liste=activites)
    assert doc_modifie['body']['success'] == True
    assert 'document2' in doc_modifie['body']['response']
    
    document2 = doc_modifie['body']['response']['document2']
    activite_modifiee = document2['activiteEnseignementDetail']['activiteEnseignementListe']['activiteEnseignement'][0]
    assert activite_modifiee['nbEleveC1'] == 12
    assert activite_modifiee['nbPeriodePrevueAn1'] == 20.0