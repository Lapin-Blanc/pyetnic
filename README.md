# pyetnic

Bibliothèque Python d'accès aux services web SOAP d'[ETNIC](https://www.etnic.be/) pour l'enseignement de promotion sociale (Wallonie-Bruxelles).

## Fonctionnalités

| Service | Opérations |
|---|---|
| **Formations** | Lister les formations organisables (catalogue), lister les formations organisées |
| **Organisation** | Créer, lire, modifier, supprimer une organisation de formation |
| **Document 1** | Lire, modifier, approuver le document de population (inscriptions) |
| **Document 2** | Lire, modifier le document des périodes d'activités d'enseignement |
| **Document 3** | Lire, modifier le document des attributions d'enseignants |
| **SEPS** | Lire un étudiant par numéro CF, rechercher des étudiants par NISS ou nom *(prod uniquement)* |

## Installation

```bash
pip install pyetnic
```

Pour utiliser les services SEPS (signature X509) :

```bash
pip install pyetnic[seps]
```

## Configuration

Générer un fichier `.env` de départ :

```bash
pyetnic init-config
```

Remplir les valeurs dans `.env` :

```ini
# Environnement : dev (services-web.tq.etnic.be) ou prod (services-web.etnic.be)
ENV=dev

# Identifiants pour le développement
DEV_USERNAME=
DEV_PASSWORD=

# Identifiants pour la production
PROD_USERNAME=
PROD_PASSWORD=

# Paramètres par défaut
DEFAULT_ETABID=       # identifiant établissement (int)
DEFAULT_IMPLID=       # identifiant implantation (int)
DEFAULT_SCHOOLYEAR=2024-2025

# Certificat X509 pour les services SEPS (chemin relatif au répertoire courant)
# Fourni par ETNIC (IAM-PROD). Uniquement nécessaire pour les services SEPS.
SEPS_PFX_PATH=
SEPS_PFX_PASSWORD=
```

Les identifiants EPROM sont fournis par ETNIC pour accéder aux services web de votre établissement.
Le certificat SEPS (fichier `.pfx`) est fourni séparément par ETNIC via IAM-PROD.

---

## Utilisation

### Formations

```python
import pyetnic
from pyetnic.services.models import OrganisationId

# Formations organisables (catalogue de l'année)
result = pyetnic.lister_formations_organisables(annee_scolaire="2024-2025")
for formation in result:
    print(formation.numAdmFormation, formation.codeFormation, formation.libelleFormation)

# Formations déjà organisées (avec leurs organisations et statuts de documents)
result = pyetnic.lister_formations(annee_scolaire="2024-2025")
for formation in result:
    for org in formation.organisations:
        print(
            f"F{org.id.numAdmFormation}/org{org.id.numOrganisation}",
            org.dateDebutOrganisation, "→", org.dateFinOrganisation,
            org.statutDocumentOrganisation.statut if org.statutDocumentOrganisation else "—",
        )
```

### Organisation

```python
from datetime import date
import pyetnic
from pyetnic.services.models import OrganisationId

org_id = OrganisationId(
    anneeScolaire="2024-2025",
    etabId=3052,
    numAdmFormation=455,
    numOrganisation=1,
)

# Lire
org = pyetnic.lire_organisation(org_id)

# Créer (numOrganisation attribué par le serveur)
org = pyetnic.creer_organisation(
    annee_scolaire="2025-2026",
    etab_id=3052,
    impl_id=6050,
    num_adm_formation=455,
    date_debut=date(2025, 9, 15),
    date_fin=date(2026, 6, 26),
)

# Modifier
org.dateFinOrganisation = date(2026, 6, 20)
org = pyetnic.modifier_organisation(org)

# Supprimer
ok = pyetnic.supprimer_organisation(org_id)
```

### Document 1 — Population

```python
from pyetnic.services.models import Doc1PopulationListSave, Doc1PopulationLineSave

doc1 = pyetnic.lire_document_1(org_id)
# doc1 est None si le document n'est pas accessible (statut org insuffisant)

# Modifier
liste_save = Doc1PopulationListSave(population=[
    Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12, nbEleveTotHom=5, nbEleveTotFem=7),
])
doc1 = pyetnic.modifier_document_1(org_id, population_liste=liste_save)

# Approuver
doc1 = pyetnic.approuver_document_1(org_id)
```

### Document 2 — Périodes d'activités

```python
from pyetnic.services.models import Doc2ActiviteEnseignementListSave, Doc2ActiviteEnseignementLineSave

doc2 = pyetnic.lire_document_2(org_id)

liste_save = Doc2ActiviteEnseignementListSave(activiteEnseignement=[
    Doc2ActiviteEnseignementLineSave(coNumBranche=1, nbEleveC1=15, nbPeriodePrevueAn1=32.0),
])
doc2 = pyetnic.modifier_document_2(org_id, activite_enseignement_liste=liste_save)
```

### Document 3 — Attributions d'enseignants

```python
from pyetnic.services.models import (
    Doc3ActiviteListeSave, Doc3ActiviteDetailSave,
    Doc3EnseignantListSave, Doc3EnseignantDetailSave,
)

doc3 = pyetnic.lire_document_3(org_id)
# doc3 est None si Doc 1 et Doc 2 ne sont pas encore approuvés

liste_save = Doc3ActiviteListeSave(activite=[
    Doc3ActiviteDetailSave(
        coNumBranche=1,
        noAnneeEtude="1",
        enseignantListe=Doc3EnseignantListSave(enseignant=[
            Doc3EnseignantDetailSave(
                coNumAttribution=1,
                noMatEns="28901061314",
                teStatut="T",
                nbPeriodesAttribuees=52.0,
            )
        ]),
    ),
])
doc3 = pyetnic.modifier_document_3(org_id, liste_save)
```

### SEPS — Recherche d'étudiants

> **Prérequis :** `pip install pyetnic[seps]` + certificat `.pfx` fourni par ETNIC (IAM-PROD).
> Ce service fonctionne **uniquement en production** (`ws.etnic.be`).

```python
import pyetnic

# Recherche par nom
etudiants = pyetnic.rechercher_etudiants(nom="DUPONT", prenom="Jean")
for e in etudiants:
    details = e.rnDetails or e.cfwbDetails
    if details:
        print(e.cfNum, details.nom, details.prenom, details.naissance.date if details.naissance else "")

# Recherche par NISS
etudiants = pyetnic.rechercher_etudiants(niss="850101-123-45")

# Lecture par numéro CF (format : [0-9]{1,10}-[0-9]{2})
etudiant = pyetnic.lire_etudiant("12345678-01")
if etudiant:
    rn = etudiant.rnDetails
    print(rn.nom, rn.prenom, rn.niss)
    print(rn.adresse.rue, rn.adresse.codePostal)
```

---

## Workflow métier

Les documents suivent un workflow séquentiel imposé par ETNIC :

```
Créer organisation  →  statut "Encodé école"
        ↓
Inspection approuve →  statut "Approuvé"
        ↓
Doc 1 accessible (lecture/modification/approbation)
        ↓
Doc 2 accessible (lecture/modification)
        ↓
Doc 1 ET Doc 2 approuvés  →  Doc 3 accessible
```

**Règles de blocage :**
- Doc 1 : inaccessible si l'organisation est "Encodé école"
- Doc 3 : nécessite que Doc 1 **et** Doc 2 soient approuvés (erreur ETNIC 20102)
- L'approbation de l'organisation est effectuée par l'inspection, pas par l'école

---

## Modèles de données

### Identifiant d'organisation

```python
@dataclass
class OrganisationId:
    anneeScolaire: str      # ex. "2024-2025"
    etabId: int             # identifiant établissement
    numAdmFormation: int    # numéro administratif de la formation
    numOrganisation: int    # numéro d'organisation (attribué par le serveur à la création)
    implId: Optional[int]   # identifiant implantation (présent dans les réponses serveur)
```

> **Important** : `implId` est retourné par le serveur dans ses réponses mais **ne doit pas** être envoyé dans les requêtes Lire/Modifier/Supprimer. Seul `creer_organisation` accepte `impl_id`.

### Vue d'une organisation

`OrganisationApercu` (retourné par `lister_formations`) contient les statuts des 4 documents :

| Champ | Description |
|---|---|
| `statutDocumentOrganisation` | Statut de l'organisation elle-même |
| `statutDocumentPopulationPeriodes` | Statut du Document 1 |
| `statutDocumentDroitsInscription` | Statut du Document droits d'inscription |
| `statutDocumentAttributions` | Statut du Document 3 |

`Organisation` (retourné par `lire_organisation`) hérite de `OrganisationApercu` et ajoute les champs métier complets. Note : les champs `statutDocument*` sont toujours `None` dans `Organisation` — ils ne sont disponibles que via `lister_formations`.

---

## Gestion des erreurs

Toutes les fonctions de service retournent `None` (plutôt qu'une exception) si :
- Le serveur répond avec `success: False` (accès refusé, document non existant, workflow non respecté, etc.)
- Le document n'est pas accessible selon le workflow métier

Les erreurs réseau et SOAP sont encapsulées dans `SoapError` et propagées.

**Codes d'erreur ETNIC courants :**

| Code | Description |
|---|---|
| 00009 | Aucun enregistrement trouvé |
| 20102 | Doc 1 et Doc 2 doivent être approuvés pour accéder au Doc 3 |
| SECU-0104 | Certificat X509 non enregistré dans l'annuaire (SEPS en dev) |

---

## Structure du projet

```
pyetnic/
├── __init__.py                  # Point d'entrée public
├── cli.py                       # CLI : commande init-config
├── config.py                    # Configuration (.env, endpoints SOAP)
├── soap_client.py               # SoapClientManager (zeep + WSSE/X509)
├── services/
│   ├── __init__.py              # Instanciation des services, exports
│   ├── models.py                # Tous les dataclasses (EPROM + SEPS)
│   ├── formations_liste.py      # FormationsListeService
│   ├── organisation.py          # OrganisationService
│   ├── document1.py             # Document1Service
│   ├── document2.py             # Document2Service
│   ├── document3.py             # Document3Service
│   └── seps.py                  # RechercheEtudiantsService (SEPS)
└── resources/
    ├── EPROM_Formations_Liste_2.0/
    ├── EPROM_Formation_Organisation_7.0/
    ├── EPROM_Formation_Population_1.0/
    ├── EPROM_Formation_Périodes_1.0/
    ├── EPROM_Document_3_1.0/
    └── SEPS_Recherche_Étudiants_2.1/
```

---

## Tests

```bash
# Tous les tests (mock + intégration)
pytest tests/

# Mock uniquement (sans credentials)
pytest tests/ -k "mock"
```

Les tests d'intégration nécessitent un `.env` valide. Ils skipent automatiquement si les credentials sont absents ou si le document n'est pas accessible dans l'environnement courant.

**Environnements ETNIC :**
- `dev` → `services-web.tq.etnic.be` / `ws-tq.etnic.be` (test, SSL non vérifié)
- `prod` → `services-web.etnic.be` / `ws.etnic.be` (production, SSL vérifié)

---

## Dépendances

| Package | Usage |
|---|---|
| [zeep](https://docs.python-zeep.org/) | Client SOAP |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Chargement `.env` |
| [requests](https://pypi.org/project/requests/) | Transport HTTP |
| [cryptography](https://pypi.org/project/cryptography/) | Extraction PFX en mémoire (SEPS) |
| [openpyxl](https://pypi.org/project/openpyxl/) | Export Excel |
| [xmlsec](https://pypi.org/project/xmlsec/) *(extra seps)* | Signature XML X509 |

## Licence

MIT — voir [LICENSE](LICENSE)
