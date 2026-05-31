"""Regression tests for single-element SOAP responses (Q8 fix).

zeep returns a single dict instead of a list when there's exactly one
XML element with maxOccurs="unbounded". These tests verify that the
parsers handle this correctly after the _as_list() migration.

Every test here would have FAILED before the migration: the old code
iterated the single dict's keys instead of its one element.
"""

from datetime import date

from pyetnic.eprom import (
    OrganisationId,
    FormationDocument1,
    FormationDocument2,
    FormationDocument3,
    lire_document_1,
    lire_document_2,
    lire_document_3,
    lister_formations,
)


def _org_id() -> OrganisationId:
    return OrganisationId(
        anneeScolaire="2024-2025",
        etabId=3052,
        numAdmFormation=455,
        numOrganisation=1,
    )


def test_document1_single_population_line(mock_soap_call):
    """A document with exactly one population line should parse correctly."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document1': {
                    'populationListe': {
                        # zeep returns a DICT, not a list, for a single element
                        'population': {
                            'coAnnEtude': 1,
                            'nbEleveA': 12,
                            'nbEleveEhr': 0, 'nbEleveFse': 0, 'nbElevePi': 0,
                            'nbEleveB': 0, 'nbEleveTot2a5': 12, 'nbEleveDem': 0,
                            'nbEleveMin': 0, 'nbEleveExm': 0, 'nbElevePl': 0,
                            'nbEleveTot6et8': 0, 'nbEleveTotFse': 0, 'nbEleveTotPi': 0,
                            'nbEleveTotHom': 5, 'nbEleveTotFem': 7,
                            'swAppPopD1': False, 'swAppD1': False,
                        }
                    }
                }
            }
        }
    }
    result = lire_document_1(_org_id())
    assert isinstance(result, FormationDocument1)
    assert len(result.populationListe.population) == 1
    assert result.populationListe.population[0].coAnnEtude == 1
    assert result.populationListe.population[0].nbEleveA == 12


def test_document2_single_activite_single_intervention_single_periode(mock_soap_call):
    """One activité, one intervention extérieure, one période — all as dicts.

    Exercises the three migrated sites in document2 at once: the
    activiteEnseignement, interventionExterieure and (nested) periode
    collections are each returned by zeep as a single dict.
    """
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document2': {
                    'activiteEnseignementDetail': {
                        'activiteEnseignementListe': {
                            # Single activité as dict (not list)
                            'activiteEnseignement': {
                                'coNumBranche': 10,
                                'coCategorie': 'A',
                                'teNomBranche': 'Mathématiques',
                                'coAnnEtude': '1',
                                'nbEleveC1': 15,
                                'nbPeriodeBranche': 30.0,
                                'nbPeriodePrevueAn1': 28.0,
                                'nbPeriodePrevueAn2': 0.0,
                                'nbPeriodeReelleAn1': 26.0,
                                'nbPeriodeReelleAn2': 0.0,
                                'coAdmReg': 328,
                                'coOrgReg': 1,
                                'coBraReg': 10,
                                'coEtuReg': '1',
                            }
                        },
                        'nbTotPeriodePrevueAn1': 28.0,
                        'nbTotPeriodePrevueAn2': 0.0,
                        'nbTotPeriodeReelleAn1': 26.0,
                        'nbTotPeriodeReelleAn2': 0.0,
                    },
                    'interventionExterieureListe': {
                        # Single intervention as dict
                        'interventionExterieure': {
                            'coNumIex': 1,
                            'coCatCol': 'X',
                            'teTypeInterventionExt': 'FSE',
                            'coObjFse': 'OBJ1',
                            'teSousTypeInterventionExt': 'SOUS1',
                            'coRefPro': 'REF1',
                            'coCriCee': 'CEE1',
                            'periodeListe': {
                                # Single période as dict
                                'periode': {
                                    'coCodePar': 'PAR1',
                                    'teLibPeriode': 'Période 1',
                                    'nbPerAn1': 10.0,
                                    'nbPerAn2': 0.0,
                                }
                            },
                        }
                    },
                    'swAppD2': True,
                }
            }
        }
    }
    result = lire_document_2(_org_id())
    assert isinstance(result, FormationDocument2)

    ae = result.activiteEnseignementDetail
    assert len(ae.activiteEnseignementListe.activiteEnseignement) == 1
    assert ae.activiteEnseignementListe.activiteEnseignement[0].coNumBranche == 10

    ie_list = result.interventionExterieureListe
    assert len(ie_list.interventionExterieure) == 1
    intervention = ie_list.interventionExterieure[0]
    assert intervention.coNumIex == 1
    assert len(intervention.periodeListe.periode) == 1
    assert intervention.periodeListe.periode[0].coCodePar == 'PAR1'


def test_document3_single_activite_single_enseignant(mock_soap_call):
    """A document with one activité containing one enseignant."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                'document3': {
                    'activiteListe': {
                        # Single activité as dict (not list)
                        'activite': {
                            'coNumBranche': 1,
                            'coCategorie': 'A',
                            'teNomBranche': 'Mathématiques',
                            'noAnneeEtude': '1',
                            'nbPeriodesDoc8': 40.0,
                            'nbPeriodesPrevuesDoc2': 40.0,
                            'nbPeriodesReellesDoc2': 38.0,
                            'enseignantListe': {
                                # Single enseignant as dict
                                'enseignant': {
                                    'coNumAttribution': 1,
                                    'noMatEns': '12345678901',
                                    'teNomEns': 'DUPONT',
                                    'tePrenomEns': 'Jean',
                                    'nbPeriodesAttribuees': 40.0,
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    result = lire_document_3(_org_id())
    assert isinstance(result, FormationDocument3)
    assert len(result.activiteListe.activite) == 1
    activite = result.activiteListe.activite[0]
    assert activite.coNumBranche == 1
    assert len(activite.enseignantListe.enseignant) == 1
    assert activite.enseignantListe.enseignant[0].teNomEns == 'DUPONT'


def test_lister_formations_single_formation_single_org(mock_soap_call):
    """A response with one formation containing one organisation."""
    mock_soap_call.return_value = {
        'body': {
            'success': True,
            'response': {
                # Single formation as dict
                'formation': {
                    'numAdmFormation': 455,
                    'libelleFormation': 'Informatique',
                    'codeFormation': 'INF',
                    # Single organisation as dict
                    'organisation': {
                        'numOrganisation': 1,
                        'implId': 6050,
                        'dateDebutOrganisation': date(2024, 9, 2),
                        'dateFinOrganisation': date(2025, 6, 27),
                        'statutDocumentOrganisation': None,
                        'statutDocumentPopulationPeriodes': None,
                        'statutDocumentDroitsInscription': None,
                        'statutDocumentAttributions': None,
                    }
                }
            }
        }
    }
    result = lister_formations(annee_scolaire="2024-2025")
    assert result.success
    assert len(result.formations) == 1
    assert result.formations[0].numAdmFormation == 455
    assert len(result.formations[0].organisations) == 1
    assert result.formations[0].organisations[0].id.numOrganisation == 1
