# pyetnic — Spécifications techniques pour reprise IA

Ce document est destiné à un agent IA reprenant le développement. Il décrit l'architecture, les conventions, l'état actuel et les règles métier critiques.

---

## Présentation du projet

**pyetnic** est un client Python pour les services web SOAP d'ETNIC (organisme informatique de la Fédération Wallonie-Bruxelles). Il cible spécifiquement les services EPROM (Enseignement de Promotion Sociale), qui gèrent les formations, organisations et documents administratifs des établissements scolaires.

- Repo : https://github.com/Lapin-Blanc/pyetnic
- Auteur : Fabien Toune (fabien.toune@eica.be)
- Version : 0.0.9 (alpha)
- Python ≥ 3.8

---

## Architecture

### Vue d'ensemble

```
pyetnic/__init__.py          ← from . import eprom, seps (API publique)
pyetnic/config.py            ← Config (variables .env, endpoints SOAP)
pyetnic/soap_client.py       ← SoapClientManager (zeep + WSSE auth)
pyetnic/cli.py               ← CLI (init-config)
pyetnic/eprom/
    __init__.py              ← namespace public EPROM (re-exports depuis services/)
pyetnic/seps/
    __init__.py              ← namespace public SEPS (re-exports depuis services/)
pyetnic/services/            ← implémentation interne (ne pas importer directement)
    __init__.py              ← instanciation singletons
    models.py                ← tous les dataclasses (source de vérité)
    formations_liste.py      ← FormationsListeService
    organisation.py          ← OrganisationService
    document1.py             ← Document1Service
    document2.py             ← Document2Service
    document3.py             ← Document3Service
    seps.py                  ← RechercheEtudiantsService (SEPS, X509)
    enregistrer_etudiant.py  ← EnregistrerEtudiantService (SEPS, X509)
    inscriptions.py          ← InscriptionsService (SEPS, X509)
    nomenclatures.py         ← TYPES_INTERVENTION_EXTERIEURE
pyetnic/resources/           ← fichiers WSDL et XSD (packagés, un dossier par ZIP)
tests/                       ← tests pytest (mock + intégration)
```

**API publique :**
```python
import pyetnic
pyetnic.eprom.lister_formations(annee_scolaire="2024-2025")
pyetnic.seps.rechercher_etudiants(nom="DUPONT")

from pyetnic.eprom import OrganisationId, lire_organisation
from pyetnic.seps import lire_etudiant
```

**Note :** les tests importent depuis `pyetnic.services.*` (niveau interne) — c'est voulu pour les tests unitaires.

### Couche SOAP (`soap_client.py`)

`SoapClientManager` :
- Un client zeep par service (cache de classe `_client_cache`)
- Authentification WS-Security configurable via `ServiceConfig.auth_type` :
  - `"username_token"` (défaut) : UsernameToken (services EPROM)
  - `"x509_pfx"` : signature X509 BinarySignature (services SEPS)
- SSL désactivé en mode `dev`, activé en `prod` (toujours `True` pour `x509_pfx`)
- `call_service(method_name, **kwargs)` → retourne `serialize_object(result, dict)`
- La réponse sérialisée a toujours la forme :
  ```python
  {
      'header': {'requestId': str},
      'body': {
          'success': bool,
          'messages': {'error': [...], 'warning': [...], 'info': [...]},
          'response': dict | None   # None si success=False ou réponse vide
      }
  }
  ```

#### Authentification X509 (SEPS)

- Classe `_EtnicBinarySignature` (sous-classe de `MemorySignature` zeep) : signe les requêtes, ignore la vérification des réponses (CA ETNIC non distribué)
- Fonction `_build_x509_wsse()` : charge le PFX depuis `Config.SEPS_PFX_PATH`, extrait clé + cert en mémoire via `cryptography`, retourne un plugin `_EtnicBinarySignature`
- **Aucune écriture sur disque** — extraction PEM en mémoire seulement
- **Zéro perte de performances** — extraction faite une seule fois au premier appel, mise en cache dans `_client_cache` avec le client zeep
- Dépendances : `cryptography` (obligatoire) + `xmlsec` (optionnel, extra `pip install pyetnic[seps]`)
- Chemin PFX : relatif au répertoire courant (résolu via `os.path.abspath`)

### Pattern des services

Chaque service (`Document1Service`, etc.) suit exactement le même pattern :

```python
class DocumentXService:
    def __init__(self):
        self.client_manager = SoapClientManager("DOCUMENTX")

    @staticmethod
    def _organisation_id_dict(org_id: OrganisationId) -> dict:
        # Retourne les 4 champs sans implId (OrganisationReqIdCT)
        ...

    def _parse_documentX_response(self, result, org_id) -> Optional[FormationDocumentX]:
        # Vérifie result['body'].get('response') avant d'accéder aux clés
        # Retourne None si réponse vide ou success=False
        ...

    def lire_document_X(self, org_id: OrganisationId) -> Optional[FormationDocumentX]:
        ...

    def modifier_document_X(self, org_id, ...) -> Optional[FormationDocumentX]:
        ...
```

---

## Règle critique : `implId`

**Ne jamais inclure `implId` dans les requêtes Lire/Modifier/Supprimer/LireDocumentX/ModifierDocumentX.**

- `OrganisationReqIdCT` (requêtes) : 4 champs seulement (`anneeScolaire`, `etabId`, `numAdmFormation`, `numOrganisation`)
- `OrganisationResIdCT` (réponses serveur) : inclut `implId` en plus
- `CreerOrganisation` seul accepte `implId` dans son `id`

Tous les services implémentent `_organisation_id_dict()` pour construire le dict sans `implId`.
**Ne jamais utiliser `dataclasses.asdict(organisation_id)` directement** — cela inclurait `implId=None` et serait rejeté.

---

## Modèles de données (`services/models.py`)

Organisation des sections dans l'ordre :

1. **Types communs** : `StatutDocument`, `OrganisationId`, `OrganisationApercu`, `Organisation`, `Formation`, `FormationsListeResult`
2. **Document 1** : `Doc1PopulationLine`, `Doc1PopulationList`, `Doc1PopulationLineSave`, `Doc1PopulationListSave`, `FormationDocument1`
3. **Document 2** : `Doc2Activite*`, `Doc2PeriodeExt*`, `Doc2InterventionExt*` (read + save), `FormationDocument2`
4. **Document 3** : `Doc3EnseignantDetail`, `Doc3EnseignantList`, `Doc3ActiviteDetail`, `Doc3ActiviteListe` (read), puis `Doc3*Save` (save), `FormationDocument3`
5. **SEPS étudiants** : `SepsLocalite`, `SepsAdresse`, `SepsNaissance`, `SepsDeces`, `EtudiantDetails`, `Etudiant`, `SepsNaissanceSave`, `SepsAdresseSave`, `EtudiantDetailsSave`
6. **SEPS inscriptions (lecture)** : `SepsUE`, `SepsLieuCours`, `SepsDroitInscription`, `SepsExempteDroitInscription`, `SepsDroitInscriptionSpecifique`, `SepsExempteDroitInscriptionSpec`, `SepsAdmission`, `SepsSanction`, `SepsSpecificite`, `Inscription`
7. **SEPS inscriptions (save)** : `SepsUESave`, `SepsDroitInscriptionSave`, `SepsAdmissionSave`, `SepsSanctionSave`, `SepsSpecificiteSave`, `InscriptionInputSave`, `InscriptionInputDataSave`

### Hiérarchie Organisation

```
OrganisationApercu     ← retourné par lister_formations() (OrganisationApercuCT)
    id, dateDebut, dateFin
    statutDocumentOrganisation        (StatutDocument | None)
    statutDocumentPopulationPeriodes  (StatutDocument | None) = Doc 1
    statutDocumentDroitsInscription   (StatutDocument | None)
    statutDocumentAttributions        (StatutDocument | None) = Doc 3

Organisation(OrganisationApercu) ← retourné par lire_organisation() (FormationOrganisationCT)
    + nombreSemaineFormation, organisationPeriodesSupplOuEPT, ...
    (statutDocumentPopulationPeriodes etc. sont toujours None ici — ils ne sont pas dans FormationOrganisationCT)
```

### Types Save vs types lecture

Pour chaque document, il existe des types "Save" (envoyés au serveur) et des types "lecture" (reçus du serveur). Les types Save ont généralement moins de champs (seuls les champs modifiables). Ne pas mélanger les deux.

### `Doc3ActiviteDetailSave` — champs requis

```python
@dataclass
class Doc3ActiviteDetailSave:
    coNumBranche: int              # requis (XSD sans minOccurs="0")
    noAnneeEtude: str              # requis
    enseignantListe: Doc3EnseignantListSave  # requis
```

---

## Workflow métier ETNIC

```
Créer organisation
    → statut "Encodé école"
    → Doc 1, 2, 3 : inaccessibles

Inspection approuve l'organisation
    → statut "Approuvé"
    → Doc 1 : accessible en lecture et modification
    → Doc 2 : accessible en lecture et modification

École approuve Doc 1 (ApprouverDocument1)
École approuve Doc 2 (pas d'opération côté école — inspection ?)
    → Doc 3 : accessible (erreur 20102 sinon)
```

**Points d'attention :**
- Il n'y a pas d'opération `ApprouverOrganisation` côté école — l'approbation est faite par l'inspection
- `ApprouverDocument1` est disponible dans le WSDL Document1 (v1)
- En test (tq), les organisations créées restent en "Encodé école" jusqu'à action manuelle de l'inspection

---

## Services ETNIC et versions WSDL

| Clé Config | Service ETNIC | Version WSDL | Auth |
|---|---|---|---|
| `LISTE_FORMATIONS` | EPROMFormationsListe | v2 | UsernameToken |
| `ORGANISATION` | EPROMFormationOrganisation | v7 | UsernameToken |
| `DOCUMENT1` | EPROMFormationDocument1 | v1 | UsernameToken |
| `DOCUMENT2` | EPROMFormationDocument2 | v1 | UsernameToken |
| `DOCUMENT3` | EPROMFormationDocument3 | v1 | UsernameToken |
| `SEPS_RECHERCHE_ETUDIANTS` | SEPSRechercheEtudiants | v1 | X509 PFX |
| `SEPS_ENREGISTRER_ETUDIANT` | SEPSEnregistrerEtudiant | v1 | X509 PFX |
| `SEPS_ENREGISTRER_INSCRIPTION` | SEPSEnregistrerInscription | v1 | X509 PFX |
| `SEPS_RECHERCHE_INSCRIPTIONS` | SEPSRechercheInscriptions | v1 | X509 PFX |

**Endpoints :**
- dev ORGANISATION : `https://ws-tq.etnic.be/eprom/formation/organisation/v7`
- prod ORGANISATION : `https://ws.etnic.be/eprom/formation/organisation/v7`
- dev autres EPROM : `https://services-web.tq.etnic.be:11443/eprom/...`
- prod autres EPROM : `https://services-web.etnic.be:11443/eprom/...`
- SEPS dev : `https://ws-tq.etnic.be/seps/...` (cert prod non enregistré en TQ → erreur SECU-0104)
- SEPS prod : `https://ws.etnic.be/seps/...` (GlobalSign, `verify=True`)

---

## Opérations WSDL implémentées

### FormationsListe (v2)
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `ListerFormationsOrganisables` | `lister_formations_organisables()` | ✅ |
| `ListerFormations` | `lister_formations()` | ✅ |

### Organisation (v7)
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `LireOrganisation` | `lire_organisation(org_id)` | ✅ |
| `CreerOrganisation` | `creer_organisation(...)` | ✅ |
| `ModifierOrganisation` | `modifier_organisation(org)` | ✅ |
| `SupprimerOrganisation` | `supprimer_organisation(org_id)` | ✅ |

> Note : il n'y a **pas** d'opération `ApprouverOrganisation` dans ce WSDL.
> Nouveau champ v7 : `reorientation7TP` (bool, optionnel) dans Creer/Modifier/Lire.

### Document1 (v1)
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `LireDocument1` | `lire_document_1(org_id)` | ✅ |
| `ModifierDocument1` | `modifier_document_1(org_id, population_liste?)` | ✅ |
| `ApprouverDocument1` | `approuver_document_1(org_id, population_liste?)` | ✅ |

### Document2 (v1)
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `LireDocument2` | `lire_document_2(org_id)` | ✅ |
| `ModifierDocument2` | `modifier_document_2(org_id, activite_enseignement_liste?, intervention_exterieure_liste?)` | ✅ |

### Document3 (v1)
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `LireDocument3` | `lire_document_3(org_id)` | ✅ |
| `ModifierDocument3` | `modifier_document_3(org_id, activite_liste)` | ✅ |

### SEPS RechercheEtudiants (v1) — authentification X509
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `lireEtudiant` | `lire_etudiant(cf_num, from_date?)` | ✅ |
| `rechercherEtudiants` | `rechercher_etudiants(niss? \| nom, prenom?, date_naissance?, sexe?, force_rn_flag?)` | ✅ |

> Mutation NISS (code 30401) → `NissMutationError(ancien_niss, nouveau_niss)` levée depuis `rechercher_etudiants`.

### SEPS EnregistrerEtudiant (v1) — authentification X509
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `enregistrerEtudiant` | `enregistrer_etudiant(mode_enregistrement, etudiant_details?, double_flag?, create_bis_flag?)` | ✅ |
| `modifierEtudiant` | `modifier_etudiant(cf_num, etudiant_details?)` | ✅ |

> `mode_enregistrement` : `"NISS"` (par NISS) ou `"DETAILS"` (par données d'identité).
> Types Save : `EtudiantDetailsSave`, `SepsNaissanceSave`, `SepsAdresseSave`.
> Tous les services SEPS fonctionnent **uniquement en production** (`ws.etnic.be`). Erreur SECU-0104 en dev.

### SEPS RechercheInscriptions (v1) — authentification X509
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `rechercherInscriptions` | `rechercher_inscriptions(annee_scolaire?, etab_id?, date_requete?, cf_num?, no_administratif?, no_organisation?)` | ✅ |

### SEPS EnregistrerInscription (v1) — authentification X509
| Opération WSDL | Fonction Python | Statut |
|---|---|---|
| `enregistrerInscription` | `enregistrer_inscription(inscription_input_data?)` | ✅ |
| `modifierInscription` | `modifier_inscription(inscription_input_data?)` | ✅ |

> Types Save : `InscriptionInputDataSave`, `InscriptionInputSave`, `SepsUESave`, `SepsSpecificiteSave`.
> `InscriptionInputDataSave` : champs requis = `cfNum`, `idEtab`, `idImplantation`, `codePostalLieuCours`, `inscription`.
> `InscriptionInputSave` : champs requis = `dateInscription`, `statut`.
> `SpecificiteDataInputType` (Save) n'a pas `regulier1`/`regulier5` — ne pas les inclure.

---

## Conventions de code

### Nommage
- Les noms de classes Python reprennent **exactement** les noms des types XSD (ex. `Doc2ActiviteEnseignementLine` ← `Doc2ActiviteEnseignementLineCT`)
- Les paramètres Python sont en `snake_case` même si les champs SOAP sont en `camelCase`

### Parser de réponse
La garde systématique dans chaque `_parse_*_response` :
```python
if not (
    result
    and 'body' in result
    and result['body'].get('response')   # .get() pour éviter TypeError si response=None
    and 'documentX' in result['body']['response']
):
    return None
```

### Sérialisation pour l'envoi
Utiliser `dataclasses.asdict(objet_save)` pour les types Save.
**Jamais** `asdict(organisation_id)` directement (inclurait `implId`).

### Pattern d'export
- `pyetnic/services/__init__.py` : instancie les services comme singletons et expose leurs méthodes comme fonctions de module
- `pyetnic/__init__.py` : ré-exporte les fonctions utiles pour l'API publique

---

## Stratégie de test

### Structure
- **Tests mock** (sans credentials) : `test_*_mock`, `test_organisation_id_dict`, etc.
- **Tests d'intégration** (avec `.env`) : `test_*_reel`

### Règles
1. Les tests d'intégration commencent par `if not Config.ETAB_ID: pytest.skip(...)`
2. Si un doc est inaccessible (`None`), appeler `pytest.skip()` — ne jamais laisser un `assert is not None` échouer
3. Les tests qui modifient des données utilisent `try/finally` pour garantir la restauration
4. Les tests doc3 utilisent `_find_accessible_doc3()` qui itère sur plusieurs années (`ANNEE_SCOLAIRE`, `2023-2024`, `2024-2025`) car l'accessibilité dépend du workflow métier

### Couverture actuelle
```
tests/test_formations_liste.py        8 tests  (intégration uniquement — à refactoriser)
tests/test_formation_organisation.py  10 tests (7 mock + 3 intégration)
tests/test_formation_document1.py     7 tests  (5 mock + 2 intégration)
tests/test_formation_document2.py     7 tests  (5 mock + 2 intégration)
tests/test_formation_document3.py     7 tests  (5 mock + 2 intégration)
```

---

## Environnement de test

- Serveur : `services-web.tq.etnic.be`
- `etabId=3052`, `implId=6050`
- Année courante (25-26) : 2 organisations créées (F327, F328), statut "Encodé école" → Doc 1/2/3 inaccessibles
- Année 24-25 : 34 organisations "Approuvé" → Doc 1/2 lisibles, Doc 3 inaccessible (Doc 1/2 non approuvés)
- Année 23-24 : 119/158 organisations avec Doc 3 accessible — c'est le millésime de test pour Doc 3

---

## Points d'attention pour les développements futurs

### Vérification XSD avant d'implémenter
Avant d'implémenter ou de modifier un service, toujours vérifier le WSDL/XSD dans `pyetnic/resources/`. Chaque service a son propre dossier (ex. `pyetnic/resources/EPROM_Document_3_1.0/xsd/`). Points à vérifier :
1. Les champs obligatoires (absence de `minOccurs="0"`) → ne pas les mettre `Optional`
2. La distinction `OrganisationReqIdCT` vs `OrganisationResIdCT` (avec/sans `implId`)
3. Les noms exacts des éléments (ex. `activiteListe` vs `activiteList`)

### Fonctionnalités non implémentées
- **Export Excel** (`openpyxl` est en dépendance mais non utilisé) — prévu pour exporter les données de formation
- **Tests mock pour `test_formations_liste.py`** — tous les tests sont actuellement d'intégration
- **Approval Doc 2** — pas d'opération `ApprouverDocument2` trouvée dans le WSDL v1 ; à vérifier si une version ultérieure existe
- **Autres services ETNIC** — ETNIC expose d'autres services EPROM non encore couverts

### Limites connues
- `Organisation.statutDocumentPopulationPeriodes` et champs similaires sont toujours `None` quand l'objet vient de `lire_organisation()` — ils ne sont disponibles que via `lister_formations()`
- Le cache `SoapClientManager._client_cache` est de classe (partagé entre toutes les instances) — convient pour les scripts mono-thread ; à revoir pour usage concurrent
- SSL désactivé en `dev` — ne pas déployer avec `ENV=dev` en production

---

## Procédure de vérification XSD

Pour vérifier la cohérence d'un modèle Python avec le contrat WSDL :

```bash
# Lire le WSDL du service ciblé (chaque service dans son propre dossier)
cat "pyetnic/resources/EPROM_Document_3_1.0/EpromFormationDocument3Service_external_v1.wsdl"

# Lire le XSD correspondant
cat "pyetnic/resources/EPROM_Document_3_1.0/xsd/EpromFormationDocument3_external_v1.xsd"
```

Comparer :
- Champs sans `minOccurs="0"` → required dans le dataclass Python (pas de valeur par défaut)
- Champs avec `minOccurs="0"` → `Optional[T] = None`
- Noms des éléments XSD → noms des attributs Python (camelCase conservé)
