# Guide d'utilisation de pyetnic pour les assistants IA

Ce fichier est destiné aux assistants IA (Claude, Copilot, etc.) qui aident un utilisateur à travailler avec pyetnic. Il complète le README avec les informations nécessaires pour éviter les erreurs courantes.

---

## Ce que fait pyetnic

Client Python pour les services web SOAP d'ETNIC (Fédération Wallonie-Bruxelles). Il couvre :
- **Services EPROM** : gestion des formations, organisations et documents administratifs de l'enseignement de promotion sociale
- **Service SEPS** : recherche d'étudiants dans le registre national / CFWB (authentification X509)

---

## Prérequis indispensables

1. **Un fichier `.env`** à la racine du projet (généré via `pyetnic init-config`)
2. **Des identifiants ETNIC** (fournis par ETNIC à l'établissement)
3. **Pour SEPS uniquement** : un certificat `.pfx` fourni par ETNIC (IAM-PROD) + `pip install pyetnic[seps]`

---

## Règles critiques à ne jamais enfreindre

### 1. `implId` est interdit dans les requêtes
`OrganisationId` a un champ `implId` qui est **retourné** par le serveur mais **refusé** dans les requêtes de lecture/modification/suppression. Ne jamais le passer à `lire_organisation`, `modifier_organisation`, `supprimer_organisation`, ni aux fonctions de documents.

```python
# ✅ Correct
org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1)

# ❌ Incorrect — le serveur rejettera la requête
org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1, implId=6050)
```

Seul `creer_organisation(impl_id=...)` accepte ce paramètre.

### 2. Les fonctions retournent `None`, pas d'exception, si le document est inaccessible

```python
doc1 = pyetnic.lire_document_1(org_id)
if doc1 is None:
    # Normal : organisation pas encore approuvée par l'inspection,
    # ou document dans un statut incompatible
    print("Document non accessible")
```

Ne jamais supposer qu'une fonction retourne toujours un objet.

### 3. Types Save ≠ types lecture

Pour modifier un document, utiliser les types `*Save`, pas les types retournés par `lire_*` :

```python
# lire_document_1() retourne FormationDocument1 (type lecture, lecture seule)
# modifier_document_1() attend Doc1PopulationListSave (type Save)
from pyetnic.services.models import Doc1PopulationListSave, Doc1PopulationLineSave
```

### 4. SEPS uniquement en production

Le service SEPS ne fonctionne qu'avec `ENV=prod` dans `.env`. En mode dev, le certificat prod n'est pas enregistré dans l'annuaire TQ et retourne SECU-0104.

---

## Workflow métier ETNIC — ordre obligatoire

```
creer_organisation()
    → statut "Encodé école" → Doc 1/2/3 retournent None

[L'inspection approuve via son interface]
    → statut "Approuvé" → Doc 1/2 accessibles

approuver_document_1()
    → Doc 3 accessible
```

Il n'y a **pas** de fonction `approuver_organisation()` — c'est fait manuellement par l'inspection.

---

## Référence rapide des fonctions publiques

```python
import pyetnic
from pyetnic.services.models import OrganisationId

# --- Formations ---
pyetnic.lister_formations_organisables(annee_scolaire="2024-2025")  # → FormationsListeResult
pyetnic.lister_formations(annee_scolaire="2024-2025")               # → FormationsListeResult

# --- Organisation ---
pyetnic.lire_organisation(org_id)                   # → Organisation | None
pyetnic.creer_organisation(annee_scolaire, etab_id, impl_id, num_adm_formation, date_debut, date_fin, **options)  # → Organisation | None
pyetnic.modifier_organisation(org)                  # → Organisation | None
pyetnic.supprimer_organisation(org_id)              # → bool

# --- Document 1 (population) ---
pyetnic.lire_document_1(org_id)                     # → FormationDocument1 | None
pyetnic.modifier_document_1(org_id, population_liste=None)  # → FormationDocument1 | None
pyetnic.approuver_document_1(org_id, population_liste=None) # → FormationDocument1 | None

# --- Document 2 (périodes) ---
pyetnic.lire_document_2(org_id)                     # → FormationDocument2 | None
pyetnic.modifier_document_2(org_id, activite_enseignement_liste=None, intervention_exterieure_liste=None)

# --- Document 3 (attributions) ---
pyetnic.lire_document_3(org_id)                     # → FormationDocument3 | None
pyetnic.modifier_document_3(org_id, activite_liste) # → FormationDocument3 | None

# --- SEPS (prod uniquement, pip install pyetnic[seps]) ---
pyetnic.lire_etudiant(cf_num, from_date=None)       # → Etudiant | None
pyetnic.rechercher_etudiants(niss=None, nom=None, prenom=None, date_naissance=None, sexe=None, force_rn_flag=None)  # → List[Etudiant]

# --- Nomenclatures ---
pyetnic.TYPES_INTERVENTION_EXTERIEURE               # liste des types valides pour Doc2
```

---

## Modèles importants

```python
from pyetnic.services.models import (
    # Communs
    OrganisationId, OrganisationApercu, Organisation, StatutDocument,

    # Document 1
    Doc1PopulationLineSave, Doc1PopulationListSave,

    # Document 2
    Doc2ActiviteEnseignementLineSave, Doc2ActiviteEnseignementListSave,
    Doc2InterventionExterieureLineSave, Doc2InterventionExterieureListSave,

    # Document 3
    Doc3ActiviteDetailSave, Doc3ActiviteListeSave,
    Doc3EnseignantDetailSave, Doc3EnseignantListSave,

    # SEPS
    Etudiant, EtudiantDetails, SepsAdresse, SepsNaissance, SepsDeces, SepsLocalite,
)
```

---

## Erreurs fréquentes et solutions

| Erreur | Cause | Solution |
|---|---|---|
| Fonction retourne `None` | Workflow non respecté (doc inaccessible) | Vérifier le statut de l'organisation avec `lister_formations()` |
| `SoapError` au démarrage | Mauvais credentials ou `.env` manquant | Vérifier `.env` et relancer `pyetnic init-config` |
| `SECU-0104` (SEPS) | Certificat prod utilisé en mode dev | Passer à `ENV=prod` dans `.env` |
| `xmlsec` ImportError | Package optionnel manquant | `pip install pyetnic[seps]` |
| `implId` rejeté | `implId` inclus dans une requête | Construire `OrganisationId` sans `implId` |

---

## Configuration `.env` minimale

```ini
ENV=prod
PROD_USERNAME=mon_identifiant
PROD_PASSWORD=mon_mot_de_passe
DEFAULT_ETABID=3052
DEFAULT_IMPLID=6050
DEFAULT_SCHOOLYEAR=2024-2025

# Uniquement pour SEPS :
SEPS_PFX_PATH=mon_certificat.pfx
SEPS_PFX_PASSWORD=mot_de_passe_pfx
```
