"""Canonical SOAP response dicts for EPROM regression tests.

These dicts mimic the shape produced by zeep's ``serialize_object(result, dict)``
for each EPROM operation. They are intentionally rich (every field a parser
reads) so that future refactorings cannot silently drop information.

Reference vintage: SOAP responses observed against ws-tq.etnic.be in 2025
(etabId=3052, implId=6050).
"""

from datetime import date

# ---------------------------------------------------------------------------
# Generic envelopes
# ---------------------------------------------------------------------------

EMPTY_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": None,
    },
}

SUCCESS_FALSE_RESPONSE: dict = {
    "body": {
        "success": False,
        "messages": {"error": [{"code": "12345", "description": "Erreur générique"}]},
        "response": None,
    },
}

# ---------------------------------------------------------------------------
# FormationsListe
# ---------------------------------------------------------------------------

CANONICAL_LISTER_FORMATIONS_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "formation": [
                {
                    "numAdmFormation": 328,
                    "libelleFormation": "Formation Test 1",
                    "codeFormation": "F328",
                    "organisation": [
                        {
                            "numOrganisation": 1,
                            "implId": 6050,
                            "dateDebutOrganisation": date(2024, 9, 2),
                            "dateFinOrganisation": date(2025, 6, 27),
                            "statutDocumentOrganisation": {
                                "statut": "APPROUVE",
                                "dateStatut": date(2024, 9, 1),
                            },
                            "statutDocumentPopulationPeriodes": None,
                            "statutDocumentDroitsInscription": None,
                            "statutDocumentAttributions": None,
                        },
                    ],
                },
                {
                    "numAdmFormation": 455,
                    "libelleFormation": "Formation Test 2",
                    "codeFormation": "F455",
                    "organisation": [],
                },
            ],
        },
    },
}

CANONICAL_LISTER_FORMATIONS_ORGANISABLES_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "formation": [
                {
                    "numAdmFormation": 328,
                    "libelleFormation": "Formation Test 1",
                    "codeFormation": "F328",
                },
                {
                    "numAdmFormation": 455,
                    "libelleFormation": "Formation Test 2",
                    "codeFormation": "F455",
                },
            ],
        },
    },
}

EMPTY_FORMATIONS_LISTE_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {"formation": []},
    },
}

# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------

CANONICAL_ORGANISATION_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "organisation": {
                "id": {
                    "anneeScolaire": "2024-2025",
                    "etabId": 3052,
                    "numAdmFormation": 328,
                    "numOrganisation": 1,
                    "implId": 6050,
                },
                "dateDebutOrganisation": date(2024, 9, 2),
                "dateFinOrganisation": date(2025, 6, 27),
                "nombreSemaineFormation": 36,
                "statut": {"statut": "APPROUVE", "dateStatut": date(2024, 9, 1)},
                "organisationPeriodesSupplOuEPT": False,
                "valorisationAcquis": True,
                "enPrison": False,
                "eLearning": False,
                "reorientation7TP": False,
                "activiteFormation": True,
                "conseillerPrevention": False,
                "partiellementDistance": False,
                "enseignementHybride": False,
                "numOrganisation2AnneesScolaires": None,
                "typeInterventionExterieure": None,
                "interventionExterieure50p": None,
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Document 1
# ---------------------------------------------------------------------------


def _canonical_pop_line(approuve: bool = False) -> dict:
    return {
        "coAnnEtude": 1,
        "nbEleveA": 10,
        "nbEleveEhr": 0,
        "nbEleveFse": 0,
        "nbElevePi": 0,
        "nbEleveB": 0,
        "nbEleveTot2a5": 10,
        "nbEleveDem": 1,
        "nbEleveMin": 0,
        "nbEleveExm": 0,
        "nbElevePl": 0,
        "nbEleveTot6et8": 1,
        "nbEleveTotFse": 0,
        "nbEleveTotPi": 0,
        "nbEleveTotHom": 4,
        "nbEleveTotFem": 6,
        "swAppPopD1": approuve,
        "swAppD1": approuve,
        "tsMaj": "2025-01-01T00:00:00",
        "teUserMaj": "TEST",
    }


CANONICAL_DOCUMENT1_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "document1": {
                "id": {
                    "anneeScolaire": "2024-2025",
                    "etabId": 3052,
                    "numAdmFormation": 328,
                    "numOrganisation": 1,
                },
                "populationListe": {
                    "population": [_canonical_pop_line(approuve=False)],
                },
            },
        },
    },
}

CANONICAL_DOCUMENT1_APPROUVE_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "document1": {
                "id": {
                    "anneeScolaire": "2024-2025",
                    "etabId": 3052,
                    "numAdmFormation": 328,
                    "numOrganisation": 1,
                },
                "populationListe": {
                    "population": [_canonical_pop_line(approuve=True)],
                },
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Document 2
# ---------------------------------------------------------------------------

_CANONICAL_DOC2_ACTIVITE = {
    "coNumBranche": 10,
    "coCategorie": "A",
    "teNomBranche": "Mathématiques",
    "coAnnEtude": "1",
    "nbEleveC1": 15,
    "nbPeriodeBranche": 30.0,
    "nbPeriodePrevueAn1": 28.0,
    "nbPeriodePrevueAn2": 0.0,
    "nbPeriodeReelleAn1": 26.0,
    "nbPeriodeReelleAn2": 0.0,
    "coAdmReg": 328,
    "coOrgReg": 1,
    "coBraReg": 10,
    "coEtuReg": "1",
}

_CANONICAL_DOC2_INTERVENTION = {
    "coNumIex": 1,
    "coCatCol": "X",
    "teTypeInterventionExt": "FSE",
    "coObjFse": "OBJ1",
    "teSousTypeInterventionExt": "SOUS1",
    "coRefPro": "REF1",
    "coCriCee": "CEE1",
    "periodeListe": {
        "periode": [
            {
                "coCodePar": "PAR1",
                "teLibPeriode": "Période 1",
                "nbPerAn1": 10.0,
                "nbPerAn2": 0.0,
            },
        ],
    },
}

CANONICAL_DOCUMENT2_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "document2": {
                "id": {
                    "anneeScolaire": "2024-2025",
                    "etabId": 3052,
                    "numAdmFormation": 328,
                    "numOrganisation": 1,
                },
                "activiteEnseignementDetail": {
                    "activiteEnseignementListe": {
                        "activiteEnseignement": [_CANONICAL_DOC2_ACTIVITE],
                    },
                    "nbTotPeriodePrevueAn1": 28.0,
                    "nbTotPeriodePrevueAn2": 0.0,
                    "nbTotPeriodeReelleAn1": 26.0,
                    "nbTotPeriodeReelleAn2": 0.0,
                },
                "interventionExterieureListe": {
                    "interventionExterieure": [_CANONICAL_DOC2_INTERVENTION],
                },
                "swAppD2": True,
                "tsMaj": "2025-01-01T00:00:00",
                "teUserMaj": "TEST",
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Document 3
# ---------------------------------------------------------------------------

_CANONICAL_DOC3_ENSEIGNANT = {
    "coNumAttribution": 1,
    "noMatEns": "123456",
    "teNomEns": "Dupont",
    "tePrenomEns": "Jean",
    "teAbrEns": "DUP",
    "teEnseignant": "Dupont Jean",
    "coDispo": "D",
    "teStatut": "DEF",
    "nbPeriodesAttribuees": 4.0,
    "tsMaj": "2025-01-01T00:00:00",
    "teUserMaj": "TEST",
}

CANONICAL_DOCUMENT3_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {
            "document3": {
                "id": {
                    "anneeScolaire": "2024-2025",
                    "etabId": 3052,
                    "numAdmFormation": 328,
                    "numOrganisation": 1,
                },
                "activiteListe": {
                    "activite": [
                        {
                            "coNumBranche": 10,
                            "coCategorie": "A",
                            "teNomBranche": "Mathématiques",
                            "noAnneeEtude": "1",
                            "nbPeriodesDoc8": 4.0,
                            "nbPeriodesPrevuesDoc2": 4.0,
                            "nbPeriodesReellesDoc2": 4.0,
                            "enseignantListe": {
                                "enseignant": [_CANONICAL_DOC3_ENSEIGNANT],
                            },
                        },
                    ],
                },
            },
        },
    },
}
