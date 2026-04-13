"""Canonical SOAP response dicts for SEPS regression tests."""

CANONICAL_ETUDIANT_DICT: dict = {
    "cfNum": "1234567-89",
    "rnDetails": {
        "niss": "85010112345",
        "nom": "Dupont",
        "prenom": "Jean",
        "autrePrenom": ["Marc"],
        "sexe": "M",
        "naissance": {
            "date": "1985-01-01",
            "codePays": "BE",
            "localite": {"code": "1000", "description": "Bruxelles"},
        },
        "deces": None,
        "adresse": {
            "rue": "Rue de la Loi",
            "codePostal": "1040",
            "codePays": "BE",
            "numero": "16",
            "boite": None,
            "extension": None,
            "localite": {"code": "1040", "description": "Etterbeek"},
            "localiteExtension": None,
        },
        "codeNationalite": "BE",
    },
    "cfwbDetails": None,
}

CANONICAL_LIRE_ETUDIANT_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {"etudiant": CANONICAL_ETUDIANT_DICT},
    },
}

LIRE_ETUDIANT_NONE_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": None,
    },
}

CANONICAL_RECHERCHER_ETUDIANTS_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": {"etudiant": [CANONICAL_ETUDIANT_DICT]},
    },
}

CANONICAL_RECHERCHER_ETUDIANTS_SINGLE_RESPONSE: dict = {
    # zeep can return a single dict instead of a list when there's one match
    "body": {
        "success": True,
        "response": {"etudiant": CANONICAL_ETUDIANT_DICT},
    },
}

EMPTY_RECHERCHER_ETUDIANTS_RESPONSE: dict = {
    "body": {
        "success": True,
        "response": None,
    },
}

NISS_MUTATION_ERROR_RESPONSE: dict = {
    "body": {
        "success": False,
        "messages": {
            "error": [
                {
                    "code": "30401",
                    "description": "Le NISS fourni a été remplacé par 99887766554",
                },
            ],
        },
    },
}

TROP_DE_RESULTATS_ERROR_RESPONSE: dict = {
    "body": {
        "success": False,
        "messages": {
            "error": [
                {"code": "30501", "description": "Trop de résultats"},
            ],
        },
    },
}

SEPS_AUTH_ERROR_RESPONSE: dict = {
    "body": {
        "success": False,
        "messages": {
            "error": [
                {"code": "30550", "description": "Certificat invalide"},
            ],
        },
    },
}

GENERIC_SEPS_ERROR_RESPONSE: dict = {
    "body": {
        "success": False,
        "messages": {
            "error": [
                {"code": "30999", "description": "Erreur SEPS générique"},
            ],
        },
    },
}
