# pyetnic

[![Tests](https://github.com/Lapin-Blanc/pyetnic/actions/workflows/tests.yml/badge.svg)](https://github.com/Lapin-Blanc/pyetnic/actions/workflows/tests.yml)

Bibliothèque Python d'accès aux services web SOAP d'[ETNIC](https://www.etnic.be/) pour l'Enseignement pour adultes, ex-promotion sociale (Fédération Wallonie-Bruxelles).

Les services web EPROM sont le canal que l'Administration met à la disposition des
logiciels de gestion des établissements (ENORA, GIPS, PROSOC...) : pyetnic en est un client
Python, qui s'en tient aux contrats SOAP. Les calculs réglementaires (dotation, encadrement)
relèvent des applications qui l'utilisent.

## Fonctionnalités

| Namespace | Service | Opérations |
|---|---|---|
| `pyetnic.eprom` | **Formations** | Lister les formations organisables (catalogue), lister les formations organisées |
| `pyetnic.eprom` | **Organisation** | Créer, lire, modifier, supprimer une organisation de formation |
| `pyetnic.eprom` | **Document 1** | Lire, modifier, approuver le document de population (inscriptions) |
| `pyetnic.eprom` | **Document 1D** | Lire, modifier, approuver les droits d'inscription (population au 5/10 et montants) |
| `pyetnic.eprom` | **Document 2** | Lire, modifier le document des périodes d'activités d'enseignement |
| `pyetnic.eprom` | **Document 3** | Lire, modifier le document des attributions d'enseignants |
| `pyetnic.seps` | **Recherche étudiants** | Lire un étudiant par numéro CF, rechercher par NISS ou nom *(prod uniquement)* |
| `pyetnic.seps` | **Enregistrement étudiants** | Enregistrer un nouvel étudiant, modifier un étudiant existant *(prod uniquement)* |
| `pyetnic.seps` | **Inscriptions** | Rechercher, enregistrer, modifier des inscriptions d'étudiants *(prod uniquement)* |

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
# Environnement : dev (ws-tq.etnic.be) ou prod (ws.etnic.be)
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

### Configuration programmatique

Pour les applications qui gèrent leurs propres credentials (ex. Django), il est possible de configurer `pyetnic` sans fichier `.env` :

```python
from pyetnic.config import Config

Config.ENV = "prod"
Config.USERNAME = "my_user"
Config.PASSWORD = "my_pass"

# Optionnel : charger explicitement un fichier .env
Config.load_from_dotenv()
```

La configuration est **lazy** : rien n'est résolu à l'import. Les overrides programmatiques ont priorité sur les variables d'environnement.

---

## Namespaces

`pyetnic` expose deux namespaces publics :

- **`pyetnic.eprom`** — services EPROM (Enseignement de Promotion Sociale) : formations, organisations, documents 1/2/3.
  Authentification : WSSE UsernameToken (credentials dev ou prod).

- **`pyetnic.seps`** — services SEPS (registre des étudiants CFWB).
  Authentification : certificat X509 (PFX). Production uniquement.
  Nécessite `pip install pyetnic[seps]`.

Toutes les fonctions, modèles et exceptions publiques s'importent directement depuis ces namespaces :

```python
from pyetnic.eprom import lire_organisation, OrganisationId, EtnicBusinessError
from pyetnic.seps import lire_etudiant, NissMutationError
```

L'ancien namespace plat (`pyetnic.lire_organisation`) n'est plus documenté et ne devrait pas être utilisé dans du nouveau code.

---

## Utilisation

### Formations

```python
import pyetnic

# Formations organisables (catalogue de l'année)
result = pyetnic.eprom.lister_formations_organisables(annee_scolaire="2024-2025")
for formation in result:
    print(formation.numAdmFormation, formation.codeFormation, formation.libelleFormation)

# Formations déjà organisées (avec leurs organisations et statuts de documents)
result = pyetnic.eprom.lister_formations(annee_scolaire="2024-2025")
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
from pyetnic.eprom import OrganisationId, lire_organisation, creer_organisation
from pyetnic.eprom import modifier_organisation, supprimer_organisation

org_id = OrganisationId(
    anneeScolaire="2024-2025",
    etabId=1234,
    numAdmFormation=455,
    numOrganisation=1,
)

# Lire
org = lire_organisation(org_id)

# Créer (numOrganisation attribué par le serveur)
org = creer_organisation(
    annee_scolaire="2025-2026",
    etab_id=1234,
    impl_id=5678,
    num_adm_formation=455,
    date_debut=date(2025, 9, 15),
    date_fin=date(2026, 6, 26),
)

# Modifier : partir de l'organisation relue. Le serveur remplace l'organisation
# entière et remet à faux un indicateur omis (champ laissé à None).
org.dateFinOrganisation = date(2026, 6, 20)
org = modifier_organisation(org)

# Organisation v8 : BESAeSI (BES d'assistant en soins infirmiers), à partir de 2026-2027
org = creer_organisation(
    annee_scolaire="2026-2027", etab_id=1234, impl_id=5678, num_adm_formation=455,
    date_debut=date(2026, 9, 14), date_fin=date(2027, 6, 25), BESAeSI=True,
)

# Supprimer
ok = supprimer_organisation(org_id)
```

### Document 1 — Population

```python
from pyetnic.eprom import lire_document_1, modifier_document_1, approuver_document_1
from pyetnic.eprom import Doc1PopulationListSave, Doc1PopulationLineSave

doc1 = lire_document_1(org_id)
# EtnicDocumentNotAccessibleError (20101) tant que le Doc A n'est pas approuvé

# Modifier
liste_save = Doc1PopulationListSave(population=[
    Doc1PopulationLineSave(coAnnEtude=1, nbEleveA=12, nbEleveTotHom=5, nbEleveTotFem=7),
])
doc1 = modifier_document_1(org_id, population_liste=liste_save)

# Valider la population (case « Validé ») : le serveur compare la population envoyée
# à celle qu'il a enregistrée et refuse sans elle (erreur 20104). La population est donc
# obligatoire : relire, puis renvoyer.
doc1 = lire_document_1(org_id)
doc1 = approuver_document_1(org_id, Doc1PopulationListSave.from_document(doc1))
```

### Document 1D - Droits d'inscription

Par année d'études : la population au 5/10 (`nbEleves5ieme`), puis le montant des droits
(`mtDroitsInscription`). La population s'encode jusqu'à son approbation par l'école, le montant
seulement après (erreur 20112 avant) ; l'approbation de l'administration fige tout.

```python
from pyetnic.eprom import lire_document_1d, modifier_document_1d, approuver_document_1d
from pyetnic.eprom import (
    Doc1DDroitInscriptionListSave, Doc1DDroitInscriptionLineSave, Doc1DDroitInscriptionListAppr,
)

doc1d = lire_document_1d(org_id)   # refusé (20101) tant que le Doc A n'est pas approuvé

# 1. La population au 5/10
modifier_document_1d(org_id, Doc1DDroitInscriptionListSave([
    Doc1DDroitInscriptionLineSave(coAnnEtude="1", nbEleves5ieme=14),
]))

# 2. L'approuver : renvoyer la population telle que relue (erreur 20104 sinon)
approuver_document_1d(org_id, Doc1DDroitInscriptionListAppr.from_document(lire_document_1d(org_id)))

# 3. Le montant des droits
modifier_document_1d(org_id, Doc1DDroitInscriptionListSave([
    Doc1DDroitInscriptionLineSave(coAnnEtude="1", mtDroitsInscription=12.5),
]))
```

### Document 2 — Périodes d'activités

```python
from pyetnic.eprom import lire_document_2, modifier_document_2
from pyetnic.eprom import Doc2ActiviteEnseignementListSave, Doc2ActiviteEnseignementLineSave

doc2 = lire_document_2(org_id)

liste_save = Doc2ActiviteEnseignementListSave(activiteEnseignement=[
    Doc2ActiviteEnseignementLineSave(coNumBranche=1, nbEleveC1=15, nbPeriodePrevueAn1=32.0),
])
doc2 = modifier_document_2(org_id, activite_enseignement_liste=liste_save)
```

### Document 3 — Attributions d'enseignants

```python
from pyetnic.eprom import (
    lire_document_3, modifier_document_3,
    Doc3ActiviteListeSave, Doc3ActiviteDetailSave,
    Doc3EnseignantListSave, Doc3EnseignantDetailSave,
)

doc3 = lire_document_3(org_id)
# EtnicDocumentNotAccessibleError (20102) tant que le Doc A et le Doc 2 ne sont pas approuvés

# La liste envoyée REMPLACE celle de la branche : envoyer toutes ses lignes.
# coNumAttribution est facultatif et ne cible rien : le serveur numérote les lignes.
liste_save = Doc3ActiviteListeSave(activite=[
    Doc3ActiviteDetailSave(
        coNumBranche=1,
        noAnneeEtude="1",
        enseignantListe=Doc3EnseignantListSave(enseignant=[
            Doc3EnseignantDetailSave(
                noMatEns="10101012345",
                teStatut="T",
                nbPeriodesAttribuees=52.0,
            )
        ]),
    ),
])
doc3 = modifier_document_3(org_id, liste_save)

# Ajouter une attribution sans effacer les autres : ajouter_attributions_document_3 relit le
# document, renvoie les lignes existantes de chaque branche touchée (avec leur numéro) et y
# ajoute les nouvelles. Les branches absentes de la liste ne sont pas envoyées.
from pyetnic.eprom import ajouter_attributions_document_3
doc3 = ajouter_attributions_document_3(org_id, liste_save)
```

### SEPS — Recherche et enregistrement d'étudiants

> **Prérequis :** `pip install pyetnic[seps]` + certificat `.pfx` fourni par ETNIC (IAM-PROD).
> Ces services fonctionnent **uniquement en production** (`ws.etnic.be`).

```python
from pyetnic.seps import (
    rechercher_etudiants, lire_etudiant,
    enregistrer_etudiant, modifier_etudiant,
    EtudiantDetailsSave, SepsNaissanceSave, SepsAdresseSave,
    NissMutationError,
)

# Recherche par nom
etudiants = rechercher_etudiants(nom="DUPONT", prenom="Jean")
for e in etudiants:
    details = e.rnDetails or e.cfwbDetails
    if details:
        print(e.cfNum, details.nom, details.prenom, details.naissance.date if details.naissance else "")

# Recherche par NISS (avec gestion de mutation)
try:
    etudiants = rechercher_etudiants(niss="850101-123-45")
except NissMutationError as e:
    etudiants = rechercher_etudiants(niss=e.nouveau_niss)

# Lecture par numéro CF (format : [0-9]{1,10}-[0-9]{2})
etudiant = lire_etudiant("12345678-01")
if etudiant:
    rn = etudiant.rnDetails
    print(rn.nom, rn.prenom, rn.niss)

# Enregistrement d'un étudiant (mode DETAILS = recherche par identité)
details = EtudiantDetailsSave(
    nom="DUPONT",
    prenom="Jean",
    sexe="M",
    naissance=SepsNaissanceSave(date="1985-01-15", codePays="00150"),
)
resultat = enregistrer_etudiant("DETAILS", etudiant_details=details)
print(resultat.etudiant.cfNum, resultat.code)  # 201 : créé (resultat.cree) ; 200 : fusionné (resultat.fusionne)

# Modification d'un étudiant existant : le serveur EFFACE tout champ facultatif absent.
# mettre_a_jour_etudiant relit la fiche (version établissement), n'y change que ce qui
# est donné, et renvoie la fiche complète.
from pyetnic.seps import mettre_a_jour_etudiant
resultat = mettre_a_jour_etudiant("12345678-01", EtudiantDetailsSave(
    adresse=SepsAdresseSave(rue="Rue de la Paix", codePostal="1000", codePays="00150"),
))
# modifier_etudiant envoie la fiche telle quelle : à réserver à une fiche complète,
# par exemple EtudiantDetailsSave.from_details(lire_etudiant(cf).cfwbDetails).
```

### SEPS — Inscriptions

```python
from pyetnic.seps import (
    rechercher_inscriptions, enregistrer_inscription, modifier_inscription,
    InscriptionInputDataSave, InscriptionInputSave, SepsUESave,
)

# Recherche des inscriptions d'un étudiant
inscriptions = rechercher_inscriptions(cf_num="12345678-01", annee_scolaire=2024)
for i in inscriptions:
    print(i.cfNum, i.anneeScolaire, i.statut, i.ue.noAdministratif if i.ue else "")

# Enregistrement d'une nouvelle inscription
data = InscriptionInputDataSave(
    cfNum="12345678-01",
    idEtab=1234,
    idImplantation=5678,
    codePostalLieuCours="4000",
    inscription=InscriptionInputSave(
        dateInscription="2024-09-15",
        statut="DE",  # CodeStatut : DE (définitive) ou AN (annulée)
        ue=SepsUESave(noAdministratif=455, noOrganisation=1),
    ),
)
resultat = enregistrer_inscription(inscription_input_data=data)
print(resultat.inscription.ue.label, resultat.code, resultat.plus_de_4_ue)

# Modification d'une inscription existante : le serveur EFFACE tout champ facultatif
# absent (vérifié en production). mettre_a_jour_inscription relit l'inscription, n'y
# change que ce qui est donné, et la renvoie complète.
from pyetnic.seps import mettre_a_jour_inscription, SepsSpecificiteSave, SepsDroitInscription
resultat = mettre_a_jour_inscription(
    "12345678-01", 2024, 1234, 455, 1,
    specificite=SepsSpecificiteSave(
        droitInscription=SepsDroitInscription(indicateurDroitInscription="O", montant="125"),
    ),
)
# regulier3 et ajournement1Session ne se relisent pas : les redonner s'ils sont posés.
```

### SEPS - Notifications

```python
from pyetnic.seps import lire_notifications, lire_etudiant, CodeNotification

# Changements de signalétique des étudiants de l'établissement depuis une date
for n in lire_notifications(1234, "2026-10-01"):
    print(n.date, n.cfNum, CodeNotification(n.code).name)  # puis relire : lire_etudiant(n.cfNum)
```

---

## Workflow métier

Les documents suivent un workflow séquentiel imposé par ETNIC :

```
Doc A : créer l'organisation      →  statut "Encodé école"
        ↓  l'administration approuve  →  "Approuvé"
Doc 1 : encoder la population, puis la valider (approuver_document_1)
Doc 1D : population au 5/10, l'approuver (approuver_document_1d), puis les montants
        ↓
Doc 2 : n'existe qu'une fois la population validée ; l'école l'encode
        ↓  l'administration approuve Doc 1 et Doc 2 ensemble
Doc A ET Doc 2 approuvés  →  Doc 3 accessible (l'école encode, rien à approuver)
```

**Règles de blocage :**
- Doc 1 et Doc 1D : inaccessibles tant que l'organisation (Doc A) n'est pas approuvée (erreur 20101)
- Doc 3 : nécessite que le Doc A (l'organisation) **et** le Doc 2 soient approuvés (erreur ETNIC 20102)
- L'approbation de l'organisation est effectuée par l'inspection, pas par l'école

---

## Modèles de données

### Identifiant d'organisation

```python
from pyetnic.eprom import OrganisationId

org_id = OrganisationId(
    anneeScolaire="2024-2025",  # ex. "2024-2025"
    etabId=1234,                # identifiant établissement
    numAdmFormation=455,        # numéro administratif de la formation
    numOrganisation=1,          # numéro d'organisation (attribué par le serveur à la création)
    # implId : présent dans les réponses serveur, NE PAS inclure dans les requêtes
)
```

> **Important** : `implId` est retourné par le serveur mais **ne doit pas** être envoyé dans les requêtes Lire/Modifier/Supprimer. Seul `creer_organisation` accepte `impl_id`.

### Vue d'une organisation

`OrganisationApercu` (retourné par `lister_formations`) contient les statuts des 4 documents :

| Champ | Description |
|---|---|
| `statutDocumentOrganisation` | Statut de l'organisation elle-même |
| `statutDocumentPopulationPeriodes` | Statut commun du Document 1 et du Document 2 |
| `statutDocumentDroitsInscription` | Statut du Document droits d'inscription |
| `statutDocumentAttributions` | Statut du Document 3 |

`Organisation` (retourné par `lire_organisation`) hérite de `OrganisationApercu` et ajoute les champs métier complets. Note : les champs `statutDocument*` sont toujours `None` dans `Organisation` — ils ne sont disponibles que via `lister_formations`.

---

## Gestion des erreurs

Depuis 0.3.0, un refus du serveur **lève une exception typée**, pour EPROM comme pour SEPS :

```python
from pyetnic import EtnicBusinessError, EtnicDocumentNotAccessibleError
from pyetnic.eprom import lire_document_3

try:
    doc3 = lire_document_3(org_id)
except EtnicDocumentNotAccessibleError as e:
    print(f"Doc 3 pas encore accessible : {e}")
except EtnicBusinessError as e:
    print(f"Erreur ETNIC {e.code} : {e.description}")
```

**Migration depuis 0.2 et avant** : le code qui testait `None` (ou `success` de
`lister_formations*`) peut, le temps de migrer, retrouver l'ancien comportement dans un bloc
`permissive_errors()` (ou avec `Config.RAISE_ON_ERROR = False`). Ce mode émet un
`DeprecationWarning` et disparaîtra en 1.0 :

```python
from pyetnic import permissive_errors

with permissive_errors():
    doc3 = lire_document_3(org_id)   # None en cas de refus, comme avant 0.3.0
```

`strict_errors()` reste disponible (c'est le défaut) et rétablit les exceptions à l'intérieur
d'un bloc permissif. Le mode est stocké dans un `ContextVar` : chaque thread et chaque tâche
asyncio voit le sien.

**Hiérarchie des exceptions :**

```
EtnicError
├── EtnicTransportError          # erreurs réseau/SOAP (alias historique : SoapError)
└── EtnicBusinessError           # refus serveur (success=False)
    ├── EtnicDocumentNotAccessibleError  # 20101, 20102, 20103, 20112 : document pas encore accessible
    ├── EtnicNotFoundError               # code 00009
    ├── EtnicValidationError             # entrée invalide
    ├── EtnicAlreadyApprovedError        # 1530, 1545 (Doc 1, Doc 1D)
    ├── EtnicConcurrencyError            # 00011, 20104 : relire, puis recommencer
    └── SepsEtnicError                   # tout refus SEPS
        ├── SepsAuthError                # 30550
        ├── TropDeResultatsError         # 30501, 30503
        ├── NissMutationError            # 30401 (.ancien_niss, .nouveau_niss)
        ├── SepsValidationError          # BAD_REQUEST (est aussi un EtnicValidationError)
        ├── SepsNotFoundError            # NOT_FOUND (est aussi un EtnicNotFoundError)
        │   ├── SepsUeInconnueError      # 30100, 30101
        │   └── SepsEtudiantInconnuError # 30011, 30120
        ├── SepsConflictError
        │   ├── SepsInscriptionExisteError  # 30200
        │   ├── SepsEtudiantExisteError     # 30201 (.cf_num)
        │   └── SepsDoublonsError           # 30202 à 30204 (.cf_nums, .niss)
        └── SepsAucuneModificationError  # 30443
```

**Codes d'erreur ETNIC courants :**

| Code | Description |
|---|---|
| 00009 | Aucun enregistrement trouvé |
| 20102 | Le Doc A (l'organisation) et le Doc 2 doivent être approuvés pour accéder au Doc 3 |
| 20104 | Validation du Doc 1 refusée : renvoyer la population telle qu'elle vient d'être lue |
| SECU-0102 / SECU-0104 | Certificat X509 de production refusé sur TQ (SEPS en dev) |

---

## Dépannage

| Symptôme | Cause probable | Que faire |
|---|---|---|
| `EtnicDocumentNotAccessibleError` à la lecture | Document pas encore accessible : Doc A, Doc 1 ou Doc 2 non approuvé (20101, 20103, 20102) | Lire les statuts via `eprom.lister_formations()` |
| Les `statutDocument*` d'une organisation valent `None` | `lire_organisation()` ne les reçoit pas du serveur | Les lire via `eprom.lister_formations()` |
| `SoapError` au démarrage | Identifiants erronés ou `.env` absent | Vérifier le `.env`, au besoin `pyetnic init-config` |
| `SECU-0104` (SEPS) | Appel SEPS en `ENV=dev` | SEPS n'existe qu'en production : `ENV=prod` |
| `ImportError` sur `xmlsec` | Extra SEPS non installé | `pip install "pyetnic[seps]"` |
| `TropDeResultatsError` | Critères de recherche trop larges | Ajouter `prenom`, `date_naissance`, `sexe` |
| `NissMutationError` | Le NISS a été remplacé | Relancer avec `e.nouveau_niss` |
| `SepsUeInconnueError` (30101) | SEPS ne connaît pas encore l'organisation : elle lui parvient avec un délai après sa déclaration dans EPROM | Réessayer plus tard |
| `SepsEtudiantExisteError` | L'étudiant est déjà dans SEPS | Utiliser `e.cf_num` |
| `SepsDoublonsError` | Plusieurs fiches pour la même identité | Examiner `e.cf_nums` (ou `e.niss`) |
| `SepsEtnicError` | Erreur métier SEPS | Lire `e.code` et `e.description` |

---

## Structure du projet

```
pyetnic/
├── __init__.py                  # Point d'entrée : from . import eprom, seps
├── eprom/
│   └── __init__.py              # Namespace public EPROM (fonctions + modèles)
├── seps/
│   └── __init__.py              # Namespace public SEPS (fonctions + modèles)
├── cli.py                       # CLI : commande init-config
├── config.py                    # Configuration (.env, endpoints SOAP)
├── soap_client.py               # SoapClientManager (zeep + WSSE/X509)
├── services/                    # Implémentation interne
│   ├── models.py                # Tous les dataclasses
│   ├── formations_liste.py
│   ├── organisation.py
│   ├── document1.py
│   ├── document1d.py
│   ├── document2.py
│   ├── document3.py
│   ├── seps.py
│   ├── seps_errors.py
│   ├── enregistrer_etudiant.py
│   ├── inscriptions.py
│   └── notifications.py
└── resources/
    ├── EPROM_Formations_Liste_2.0/
    ├── EPROM_Formation_Organisation_8.0/
    ├── EPROM_Formation_Population_1.0/
    ├── EPROM_Formation_Droits_Inscription_1.0/
    ├── EPROM_Formation_Periodes_1.0/
    ├── EPROM_Document_3_1.0/
    ├── SEPS_Recherche_Etudiants_2.1/
    ├── SEPS_Enregistrer_Etudiant_2.1/
    ├── SEPS_Enregistrer_Inscription_2.1/
    ├── SEPS_Recherche_Inscriptions_2.1/
    └── SEPS_Notifications_1.0.8/
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
- `dev` → `ws-tq.etnic.be` (TQ, environnement de test d'ETNIC)
- `prod` → `ws.etnic.be` (production)

Le certificat TLS est vérifié dans les deux environnements.

---

## Dépendances

| Package | Usage |
|---|---|
| [zeep](https://docs.python-zeep.org/) | Client SOAP |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Chargement `.env` |
| [requests](https://pypi.org/project/requests/) | Transport HTTP |
| [cryptography](https://pypi.org/project/cryptography/) *(extra seps)* | Extraction PFX en mémoire |
| [openpyxl](https://pypi.org/project/openpyxl/) *(extra excel)* | Export Excel des exemples |
| [xmlsec](https://pypi.org/project/xmlsec/) *(extra seps)* | Signature XML X509 |

## Licence

MIT — voir [LICENSE](LICENSE)
