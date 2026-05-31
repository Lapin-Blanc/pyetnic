# Registre des types XSD partagés — Services ETNIC EPROM

> Ce fichier centralise tous les types XSD réutilisés par plusieurs services EPROM.
> Il est enrichi à chaque session d'analyse d'un nouveau service.
> Dernière mise à jour : 2026-04-14 (session 3 — Formation Population v1 + Formation Périodes v1)

---

## 1. Types simples

### AnneeScolaireST
- **Fichier XSD** : `AnneeScolaire_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/AnneeScolaire/v1`
- **Type de base** : `xsd:string`
- **Pattern** : `\d{4}-\d{4}`
- **Exemple** : `"2023-2024"`
- **Utilisé par** : Formations Liste, Formation Organisation, Document 1/2/3, Population, Périodes

### EtabIdST
- **Fichier XSD** : `Etablissement_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/etablissement/v1`
- **Type de base** : `xsd:int`
- **Description** : Identifiant FASE de l'établissement
- **Utilisé par** : tous les services EPROM

### ImplIdST
- **Fichier XSD** : `Etablissement_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/etablissement/v1`
- **Type de base** : `xsd:int`
- **Description** : Identifiant FASE de l'implantation
- **Obligatoire/Facultatif** : toujours facultatif en entrée (si omis, couvre toutes les implantations)
- **Règle métier** : JAMAIS envoyé en Lire/Modifier/Supprimer pour Organisation et Documents (seulement en Créer)
- **Utilisé par** : tous les services EPROM

### CodeUniteST (énumération)
- **Fichier XSD** : `Etablissement_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/etablissement/v1`
- **Type de base** : `xsd:string` (3 chiffres, pattern `[0-9]{3}`)
- **Valeurs pertinentes pour la promotion sociale** :
  - `212` → Promotion Sociale ordinaire secondaire
  - `215` → Promotion Sociale ordinaire supérieur
  - `219` → Promotion Sociale ordinaire secondaire en alternance
  - `222` → Promotion Sociale spécial secondaire
- **Utilisé par** : à confirmer (probablement Organisation)

### UUIDType (requestId)
- **Fichier XSD** : `requestId_v1.xsd`
- **Namespace** : `http://etnic.be/types/technical/requestId/v1`
- **Type de base** : `xsd:string`
- **Pattern** : `[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}`
- **Utilisation** : header SOAP optionnel en requête, obligatoire en réponse (endpoint EPROM)
- **Note** : si non fourni, l'ETNIC en génère un — toujours le joindre aux demandes de support
- **Utilisé par** : tous les services EPROM

---

## 2. Types complexes communs

### AbstractExternalResponseType (bloc retour v1)
- **Fichier XSD** : `Common_v1.xsd` (DEPRECATED, mais toujours utilisé par certains services)
- **Namespace** : `http://etnic.be/types/technical/common/v1`
- **Structure** :
  ```
  AbstractExternalResponseType (abstract)
  ├── success : xsd:boolean [obligatoire]
  │   → true = requête traitée avec succès
  │   → false = erreur (voir messages)
  └── messages : messagesType [0..1]
      ├── error   : MessageType [0..*]
      ├── warning : MessageType [0..*]
      └── info    : MessageType [0..*]
  ```
- **Hérité par** : réponses des services utilisant Common_v1
- **Utilisé par** : Formations Liste v2

### ResponseType (bloc retour v2)
- **Fichier XSD** : `Common_v2.xsd`
- **Namespace** : `http://etnic.be/types/technical/common/v2`
- **Structure** :
  ```
  ResponseType (abstract, extends ResponseAttributesType)
  ├── @requestId    : UUIDType   [attribut, obligatoire]
  ├── @transactionId : Str36Type [attribut, obligatoire]
  ├── success       : xsd:boolean [obligatoire]
  └── messages      : messagesType [0..1]
      ├── error   : MessageType [0..*]
      ├── warning : MessageType [0..*]
      └── info    : MessageType [0..*]
  ```
- **Types auxiliaires** :
  - `ResponseAttributesType` : porte les attributs `requestId` et `transactionId`
  - `Str36Type` : `xsd:string` (maxLength 36), identifiant de transaction
- **Différence avec v1** : `requestId` et `transactionId` sont des **attributs XML** de la réponse
  (et non plus un header SOAP séparé). Ajout de `transactionId`.
- **Utilisé par** : Formation Organisation v7

### MessageType
- **Fichier XSD** : `ResponseStatus_v3.xsd`
- **Namespace** : `http://etnic.be/types/technical/ResponseStatus/v3`
- **Structure** :
  ```
  MessageType
  ├── code        : xsd:string [obligatoire, max 10 car.]
  ├── description : xsd:string [0..1]
  └── zone        : xsd:string [0..1]
  ```
- **Utilisé par** : tous les services (via AbstractExternalResponseType)

### StatutCT
- **Fichier XSD** : `FormationOrganisation_v2.xsd` (Formations Liste) / `FormationOrganisation_v7.xsd` (Formation Organisation)
- **Namespace** : `http://enseignement.cfwb.be/types/formation/organisation/v2` (ou `/v7`)
- **Structure** :
  ```
  StatutCT
  ├── statut     : xsd:string [obligatoire]
  └── dateStatut : xsd:date   [obligatoire]
  ```
- **Valeurs possibles de `statut`** (source : PDF manuel) :
  - `"Encodé école"` — encodé par l'école, pas encore validé
  - `"Encodé PO"` — encodé par le pouvoir organisateur
  - `"Approuvé"` — approuvé/validé
- **Utilisé par** : Formations Liste (OrganisationApercuCT), Formation Organisation v7
- **Note** : structure identique entre v2 et v7, seul le namespace change

### OrganisationApercuCT
- **Fichier XSD** : `FormationOrganisation_v2.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/formation/organisation/v2`
- **Structure** :
  ```
  OrganisationApercuCT
  ├── implId                              : ImplIdST [0..1]
  ├── numOrganisation                     : xsd:int  [obligatoire]
  ├── dateDebutOrganisation               : xsd:date [obligatoire]
  ├── dateFinOrganisation                 : xsd:date [obligatoire]
  ├── statutDocumentOrganisation          : StatutCT [0..1]
  ├── statutDocumentPopulationPeriodes    : StatutCT [0..1]
  ├── statutDocumentDroitsInscription     : StatutCT [0..1]
  └── statutDocumentAttributions          : StatutCT [0..1]
  ```
- **Rôle** : vue résumée d'une organisation, retournée dans les listes
- **Utilisé par** : Formations Liste (réponse ListerFormations)

### OrganisationReqIdCT (NOUVEAU — session 3)
- **Fichier XSD** : `Organisation_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/organisation/v1`
- **Structure** :
  ```
  OrganisationReqIdCT
  ├── anneeScolaire   : AnneeScolaireST [obligatoire]
  ├── etabId          : EtabIdST        [obligatoire]
  ├── numAdmFormation : int             [obligatoire]
  └── numOrganisation : int             [obligatoire]
  ```
- **Différence avec OrganisationIdCT** (namespace `/v2` ou `/v7`) : pas de `implId`
- **Utilisé par** : Document 1 (Population), Document 2 (Périodes)

### OrganisationResIdCT (NOUVEAU — session 3)
- **Fichier XSD** : `Organisation_v1.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/organisation/v1`
- **Structure** :
  ```
  OrganisationResIdCT
  ├── anneeScolaire   : AnneeScolaireST [obligatoire]
  ├── etabId          : EtabIdST        [obligatoire]
  ├── implId          : ImplIdST        [0..1]
  ├── numAdmFormation : int             [obligatoire]
  └── numOrganisation : int             [obligatoire]
  ```
- **⚠️ Divergence** : le PDF Document 1 (page 9) dit `implId` « obligatoire », mais le XSD déclare `minOccurs="0"`
- **Utilisé par** : Document 1 (Population), Document 2 (Périodes) — en réponse uniquement

### OrganisationIdCT
- **Fichier XSD** : `FormationOrganisation_v2.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/formation/organisation/v2`
- **Structure** :
  ```
  OrganisationIdCT
  ├── anneeScolaire   : AnneeScolaireST [obligatoire]
  ├── etabId          : EtabIdST        [obligatoire]
  ├── implId          : ImplIdST        [0..1]
  ├── numAdmFormation : xsd:int         [obligatoire]
  └── numOrganisation : xsd:int         [obligatoire]
  ```
- **Utilisé par** : Formation Organisation, Document 1/2/3

### FormationCT
- **Fichier XSD** : `Formation_v2.xsd`
- **Namespace** : `http://enseignement.cfwb.be/types/formation/v2`
- **Structure** :
  ```
  FormationCT
  ├── numAdmFormation : xsd:int                [obligatoire]
  ├── libelleFormation : xsd:string            [obligatoire]
  ├── codeFormation    : xsd:string            [obligatoire]
  └── organisation     : OrganisationApercuCT  [0..*]
  ```
- **Note fonctionnelle** : le champ `organisation` est **ignoré** (non renvoyé)
  dans la réponse de `ListerFormationsOrganisables`, mais **renseigné** dans
  la réponse de `ListerFormations`
- **Utilisé par** : Formations Liste

### FormationOrganisationCT
- **Fichier XSD** : `FormationOrganisation_v7.xsd` (remplace v2)
- **Namespace** : `http://enseignement.cfwb.be/types/formation/organisation/v7`
- **Structure** :
  ```
  FormationOrganisationCT
  ├── id                              : OrganisationIdCT [obligatoire]
  ├── dateDebutOrganisation           : xsd:date         [obligatoire]
  ├── dateFinOrganisation             : xsd:date         [obligatoire]
  ├── nombreSemaineFormation          : xsd:int          [obligatoire] (calculé)
  ├── organisationPeriodesSupplOuEPT  : xsd:boolean      [0..1]
  ├── valorisationAcquis             : xsd:boolean      [0..1]
  ├── eLearning                      : xsd:boolean      [0..1] (supprimé depuis 2022-2023)
  ├── enPrison                       : xsd:boolean      [0..1]
  ├── reorientation7TP               : xsd:boolean      [0..1] (ajouté v7, 2025-2026)
  ├── activiteFormation              : xsd:boolean      [0..1]
  ├── conseillerPrevention           : xsd:boolean      [0..1]
  ├── partiellementDistance          : xsd:boolean      [0..1] (supprimé depuis 2022-2023)
  ├── enseignementHybride            : xsd:boolean      [0..1] (ajouté 2022-2023)
  ├── numOrganisation2AnneesScolaires : xsd:int          [0..1]
  ├── typeInterventionExterieure     : xsd:string       [0..1]
  ├── interventionExterieure50p      : xsd:boolean      [0..1]
  └── statut                         : StatutCT         [0..1]
  ```
- **Utilisé par** : Formation Organisation v7 (réponses Créer, Lire, Modifier)

---

## 3. Namespaces de référence

| Préfixe courant | URI | Description |
|---|---|---|
| `ann` | `http://enseignement.cfwb.be/types/AnneeScolaire/v1` | Année scolaire |
| `etab` | `http://enseignement.cfwb.be/types/etablissement/v1` | Établissement |
| `org` | `http://enseignement.cfwb.be/types/formation/organisation/v2` | Organisation de formation |
| `form` | `http://enseignement.cfwb.be/types/formation/v2` | Formation |
| `common` | `http://etnic.be/types/technical/common/v1` | Types communs (DEPRECATED) |
| `status` | `http://etnic.be/types/technical/ResponseStatus/v3` | Statut de réponse |
| `req` | `http://etnic.be/types/technical/requestId/v1` | Request ID |
| `addr` | `http://etnic.be/types/technical/addressing/v2` | Adressage (DEPRECATED) |
| `auth` | `http://etnic.be/types/technical/authorisation/v2` | Autorisation (DEPRECATED) |
| `orgdoc` | `http://enseignement.cfwb.be/types/organisation/v1` | Organisation (Documents 1/2/3) |
| `doc1` | `http://enseignement.cfwb.be/types/formation/document1/v1` | Formation Document 1 (Population) |
| `doc2` | `http://enseignement.cfwb.be/types/formation/document2/v1` | Formation Document 2 (Périodes) |

---

## 4. Codes d'erreur communs (cross-service)

> Enrichi au fil des sessions. Certains codes sont spécifiques à un service.

| Code | Success | Description | Services concernés |
|---|---|---|---|
| *(pas de code)* | `true` | Exécution sans erreur | tous |
| `00009` | `false` | Aucun enregistrement correspondant aux critères | Formations Liste, Organisation, Documents |
| `00025` | `false` | Problème de sécurité — contacter l'administrateur | tous |
| `00999` | `false` | Erreur SQL interne | tous |
| `20005` | `false` | Numéro d'organisation incorrect | Organisation |
| `20006` | `false` | Date début doit être < date fin d'organisation | Organisation |
| `20007` | `false` | Switch périodes supplémentaires incorrect (O/N) | Organisation |
| `20010` | `false` | Date début d'organisation ne peut être inférieure à xx/xx/xxxx | Organisation |
| `20011` | `false` | Date fin d'organisation ne peut être supérieure à xx/xx/xxxx | Organisation |
| `20012` | `false` | Date fin ne peut être supérieure d'1 an à la date de début | Organisation |
| `20013` | `false` | Nombre de semaines doit être entre 1 et 52 | Organisation |
| `20016` | `false` | Type d'intervention n'existe pas | Organisation |
| `20019` | `false` | Switch en-prison incorrect (O/N) | Organisation |
| `20023` | `false` | Switch uniquement VAE incorrect (O/N) | Organisation |
| `20024` | `false` | Switch Activité de formation incorrect (O/N) | Organisation |
| `20025` | `false` | Veuillez sélectionner le type d'intervention extérieure | Organisation |
| `20026` | `false` | Switch conseiller prévention/DPO incorrect (O/N) | Organisation |
| `20027` | `false` | Switch Partiellement à distance incorrect (O/N) | Organisation |
| `20028` | `false` | Numéro d'organisation année précédente incorrect | Organisation |
| `20029` | `false` | Date début ne peut être ≥ date fermeture formation | Organisation |
| `20030` | `false` | Date début ne peut excéder 4 mois max | Organisation |
| `20031` | `false` | Switch Enseignement hybride incorrect (O/N) | Organisation |
| `20034` | `false` | Type d'intervention n'est plus disponible à l'encodage | Organisation |
| `20037` | `false` | Switch réorientation 7TQ 7P incorrect (O/N) | Organisation |
| `20038` | `false` | Switch réorientation 7TQ 7P doit être oui pour cette implantation | Organisation |
| `30001` | `false` | Numéro d'établissement incorrect | Formations Liste, Organisation |
| `30002` | `false` | Numéro d'implantation incorrect | Formations Liste, Organisation (Créer) |
| `30003` | `false` | Statut des documents ne permet pas cette opération | Organisation (Modifier, Supprimer) |
| `30004` | `false` | Type d'intervention extérieure incorrect | Organisation |
| `30005` | `false` | Numéro administratif de la formation incorrect | Organisation |
| `30006` | `false` | Opération impossible (Passage PO non actif) | Organisation |
| `30007` | `false` | Paramètre anneeScolaire incorrect (format xxxx-xxxx) | Formations Liste, Organisation |
| `30008` | `false` | enseignementHybride disponible qu'à partir 2022-2023 | Organisation |
| `30009` | `false` | reorientation7TP disponible qu'à partir 2025-2026 | Organisation |
| `00011` | `false` | Enregistrement modifié par un autre utilisateur | Document 1, Document 2 |
| `1113` | `false` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | Document 1, Document 2 |
| `1114` | `false` | Numéro d'établissement incorrect | Document 1, Document 2 |
| `1530` | `false` | Document déjà approuvé par l'administration | Document 1 (Approuver), Document 2 (Modifier) |
| `1545` | `false` | Doc 1 approuvé / max 5 interventions ext. (Doc 2) | Document 1 (Modifier), Document 2 (Modifier) |
| `2106` | `false` | Code Année d'études de la population scolaire incorrect | Document 1, Document 2 |
| `4004`-`4012` | `false` | Contrôles cohérence population (totaux, ventilations) | Document 1 |
| `1527`-`1528` | `false` | Données regroupement invalides | Document 2 |
| `1598`-`1604` | `false` | Erreurs type/sous-type intervention extérieure | Document 2 |
| `2118` | `false` | Numéro activité d'enseignement incorrect | Document 2 |
| `20015`-`20036` | `false` | Erreurs intervention extérieure (type, sous-type, relation) | Document 2 |
| `30016`-`30017` | `false` | Contraintes métier (date valorisation, part supplémentaire) | Document 2 |

---

## 5. Infrastructure commune

### Endpoints EPROM

| Environnement | URL spécifique EPROM (recommandé) | URL générique Ecole (déprécié) |
|---|---|---|
| TQ (dev) | `https://services-web.tq.etnic.be/eprom/{service}/v{n}` | `https://services-web.tq.etnic.be/ecole` |
| PROD | `https://services-web.etnic.be/eprom/{service}/v{n}` | `https://services-web.etnic.be/ecole` |

- **Port TLS 1.2** : 11443 (en complément du port standard)
- **Protocole** : SOAP 1.1 ou SOAP 1.2, document/literal
- **Authentification** : WS-Security Username Token Profile
- **Endpoint spécifique EPROM** : pas de WS-Addressing requis
- **Endpoint générique Ecole** : WS-Addressing requis (Action + To), déprécié

### WS-Addressing (endpoint générique Ecole uniquement)

| Paramètre | Valeur |
|---|---|
| Action | `eprom.formationsListeV2?mode=sync` |
| To | `http://services-web.etnic.be/eprom` |

---

## 6. Suivi des XSD par service

> Tableau de traçabilité : quel XSD est utilisé par quel service.
> ✓ = confirmé par analyse WSDL, ? = probable, à confirmer

| Fichier XSD | Formations Liste v2 | Organisation v7 | Document 1 | Document 2 | Document 3 | Droits Inscription |
|---|---|---|---|---|---|---|
| AnneeScolaire_v1.xsd | ✓ | ✓ (identique) | ✓ (identique) | ✓ (identique) | ? | ? |
| Etablissement_v1.xsd | ✓ | ✓ (identique) | ✓ (identique) | ✓ (identique) | ? | ? |
| Organisation_v1.xsd | — | — | ✓ (NOUVEAU) | ✓ (identique) | ? | ? |
| Formation_v2.xsd | ✓ | — | — | — | | |
| FormationOrganisation_v2.xsd | ✓ | — (remplacé par v7) | — | — | ? | ? |
| FormationOrganisation_v7.xsd | — | ✓ | — | — | ? | ? |
| FormationDocument1_v1.xsd | — | — | ✓ (spécifique) | — | — | — |
| FormationDocument2_v1.xsd | — | — | — | ✓ (spécifique) | — | — |
| ResponseStatus_v3.xsd | ✓ | ✓ (identique) | ✓ (identique) | ✓ (identique) | ? | ? |
| Common_v1.xsd | ✓ | — (remplacé par v2) | ✓ (identique) | ✓ (identique) | ? | ? |
| Common_v2.xsd | — | ✓ | — | — | ? | ? |
| requestId_v1.xsd | ✓ | ✓ (identique) | ✓ (identique) | ✓ (identique) | ? | ? |
| Addressing_v2.xsd | ✓ | — | ✓ (identique) | ✓ (identique) | ? | ? |
| Authorisation_v2.xsd | ✓ | — | ✓ (identique) | ✓ (identique) | ? | ? |
