# Guide d'utilisation de pyetnic pour les assistants IA

Ce fichier est destiné aux assistants IA (Claude, Copilot, etc.) qui aident un utilisateur à travailler avec pyetnic. Il complète le README avec les informations nécessaires pour éviter les erreurs courantes.

---

## Ce que fait pyetnic

Client Python pour les services web SOAP d'ETNIC (Fédération Wallonie-Bruxelles). Il couvre :
- **`pyetnic.eprom`** : formations, organisations et documents administratifs (EPROM)
- **`pyetnic.seps`** : recherche/enregistrement d'étudiants et d'inscriptions dans le registre national / CFWB (authentification X509)

---

## Prérequis indispensables

1. **Un fichier `.env`** à la racine du projet (généré via `pyetnic init-config`)
2. **Des identifiants ETNIC** (fournis par ETNIC à l'établissement)
3. **Pour SEPS uniquement** : un certificat `.pfx` fourni par ETNIC (IAM-PROD) + `pip install pyetnic[seps]`

---

## Règles critiques à ne jamais enfreindre

### 1. `implId` est interdit dans les requêtes
`OrganisationId` a un champ `implId` qui est **retourné** par le serveur mais **refusé** dans les requêtes de lecture/modification/suppression.

```python
from pyetnic.eprom import OrganisationId

# ✅ Correct
org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1)

# ❌ Incorrect — le serveur rejettera la requête
org_id = OrganisationId(anneeScolaire="2024-2025", etabId=3052, numAdmFormation=455, numOrganisation=1, implId=6050)
```

Seul `creer_organisation(impl_id=...)` accepte ce paramètre.

### 2. Les fonctions retournent `None`, pas d'exception, si le document est inaccessible

```python
from pyetnic.eprom import lire_document_1

doc1 = lire_document_1(org_id)
if doc1 is None:
    # Normal : organisation pas encore approuvée par l'inspection,
    # ou document dans un statut incompatible
    print("Document non accessible")
```

Ne jamais supposer qu'une fonction retourne toujours un objet.

### 3. Types Save ≠ types lecture

Pour modifier un document, utiliser les types `*Save` (depuis `pyetnic.eprom`), pas les types retournés par `lire_*` :

```python
# lire_document_1() retourne FormationDocument1 (type lecture, lecture seule)
# modifier_document_1() attend Doc1PopulationListSave (type Save)
from pyetnic.eprom import Doc1PopulationListSave, Doc1PopulationLineSave
```

### 4. SEPS uniquement en production

Le service SEPS ne fonctionne qu'avec `ENV=prod` dans `.env`. En mode dev, le certificat prod n'est pas enregistré dans l'annuaire TQ et retourne SECU-0104.

---

## Workflow métier ETNIC — ordre obligatoire

```
eprom.creer_organisation()
    → statut "Encodé école" → Doc 1/2/3 retournent None

[L'inspection approuve via son interface]
    → statut "Approuvé" → Doc 1/2 accessibles

eprom.approuver_document_1()
    → Doc 3 accessible
```

Il n'y a **pas** de fonction `approuver_organisation()` — c'est fait manuellement par l'inspection.

---

## Référence rapide des fonctions publiques

```python
import pyetnic
from pyetnic.eprom import OrganisationId

# --- Formations ---
pyetnic.eprom.lister_formations_organisables(annee_scolaire="2024-2025")  # → FormationsListeResult
pyetnic.eprom.lister_formations(annee_scolaire="2024-2025")               # → FormationsListeResult

# --- Organisation ---
pyetnic.eprom.lire_organisation(org_id)                    # → Organisation | None
pyetnic.eprom.creer_organisation(annee_scolaire, etab_id, impl_id, num_adm_formation, date_debut, date_fin, **options)
pyetnic.eprom.modifier_organisation(org)                   # → Organisation | None
pyetnic.eprom.supprimer_organisation(org_id)               # → bool

# --- Document 1 (population) ---
pyetnic.eprom.lire_document_1(org_id)                      # → FormationDocument1 | None
pyetnic.eprom.modifier_document_1(org_id, population_liste=None)
pyetnic.eprom.approuver_document_1(org_id, population_liste=None)

# --- Document 2 (périodes) ---
pyetnic.eprom.lire_document_2(org_id)                      # → FormationDocument2 | None
pyetnic.eprom.modifier_document_2(org_id, activite_enseignement_liste=None, intervention_exterieure_liste=None)

# --- Document 3 (attributions) ---
pyetnic.eprom.lire_document_3(org_id)                      # → FormationDocument3 | None
pyetnic.eprom.modifier_document_3(org_id, activite_liste)

# --- Nomenclatures ---
pyetnic.eprom.TYPES_INTERVENTION_EXTERIEURE                # liste des types valides pour Doc2

# --- SEPS (prod uniquement, pip install pyetnic[seps]) ---
pyetnic.seps.lire_etudiant(cf_num, from_date=None)         # → Etudiant | None
pyetnic.seps.rechercher_etudiants(niss=None, nom=None, prenom=None, date_naissance=None, sexe=None, force_rn_flag=None)  # → List[Etudiant]
pyetnic.seps.enregistrer_etudiant(mode_enregistrement, etudiant_details=None, double_flag=None, create_bis_flag=None)  # → Etudiant | None
pyetnic.seps.modifier_etudiant(cf_num, etudiant_details=None)  # → Etudiant | None

# --- SEPS Inscriptions (prod uniquement) ---
pyetnic.seps.rechercher_inscriptions(annee_scolaire=None, etab_id=None, date_requete=None, cf_num=None, no_administratif=None, no_organisation=None)  # → List[Inscription]
pyetnic.seps.enregistrer_inscription(inscription_input_data=None)  # → Inscription | None
pyetnic.seps.modifier_inscription(inscription_input_data=None)     # → Inscription | None
```

---

## Modèles importants

```python
from pyetnic.eprom import (
    # Communs
    OrganisationId, OrganisationApercu, Organisation, StatutDocument,

    # Document 1
    Doc1PopulationLineSave, Doc1PopulationListSave,

    # Document 2
    Doc2ActiviteEnseignementLineSave, Doc2ActiviteEnseignementListSave,
    Doc2InterventionExtLineSave, Doc2InterventionExtListSave,

    # Document 3
    Doc3ActiviteDetailSave, Doc3ActiviteListeSave,
    Doc3EnseignantDetailSave, Doc3EnseignantListSave,
)

from pyetnic.seps import (
    # Lecture étudiants
    Etudiant, EtudiantDetails, SepsAdresse, SepsNaissance, SepsDeces, SepsLocalite,
    # Envoi étudiants
    EtudiantDetailsSave, SepsAdresseSave, SepsNaissanceSave,
    # Lecture inscriptions
    Inscription, SepsUE, SepsLieuCours, SepsSpecificite,
    SepsDroitInscription, SepsDroitInscriptionSpecifique,
    SepsAdmission, SepsSanction,
    # Envoi inscriptions
    InscriptionInputDataSave, InscriptionInputSave, SepsUESave, SepsSpecificiteSave,
    SepsDroitInscriptionSave, SepsAdmissionSave, SepsSanctionSave,
    # Exceptions
    SepsEtnicError, SepsAuthError, NissMutationError, TropDeResultatsError,
)
```

---

## Erreurs fréquentes et solutions

| Erreur | Cause | Solution |
|---|---|---|
| Fonction retourne `None` | Workflow non respecté (doc inaccessible) | Vérifier le statut via `eprom.lister_formations()` |
| `SoapError` au démarrage | Mauvais credentials ou `.env` manquant | Vérifier `.env` et relancer `pyetnic init-config` |
| `SECU-0104` (SEPS) | Certificat prod utilisé en mode dev | Passer à `ENV=prod` dans `.env` |
| `xmlsec` ImportError | Package optionnel manquant | `pip install pyetnic[seps]` |
| `implId` rejeté | `implId` inclus dans une requête | Construire `OrganisationId` sans `implId` |
| `TropDeResultatsError` | Trop de résultats (nom trop court) | Affiner avec `prenom`, `date_naissance`, `sexe` |
| `NissMutationError` | NISS remplacé | Utiliser `e.nouveau_niss` pour relancer la recherche |
| `SepsEtnicError` | Erreur métier SEPS | Vérifier `e.code` et `e.description` |

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
