# EPROM — Formation Organisation v7.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationOrganisationService_v7.wsdl` + PDF Manuel d'utilisation rev5.1 (01-07-2025)
> Date d'analyse : 2026-04-14

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | Formation Organisation |
| Version service | 7.0.0 |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security Username Token Profile (ou certificat X.509) |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/organisation/v7` |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/organisation/messages/v7` |
| Types namespace | `http://enseignement.cfwb.be/types/formation/organisation/v7` |
| Binding | `EPROMFormationOrganisationV7Binding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/eprom/formation/organisation/v7` |
| PROD | page web | `https://ws.etnic.be/eprom/formation/organisation/v7` |
| TQ | PDF (TLS 1.2) | `https://services-web.tq.etnic.be:11443/eprom/formation/organisation/v7` |
| PROD | PDF (TLS 1.2) | `https://services-web.etnic.be:11443/eprom/formation/organisation/v7` |

> **Note** : même divergence que pour Formations Liste entre WSDL (`ws-tq.etnic.be`) et PDF (`services-web.tq.etnic.be:11443`).
> Le PDF rev4.1 a ajouté le port 11443 pour TLS 1.2 (mai 2023).

---

## Description fonctionnelle

Le service FormationOrganisation met à disposition toutes les fonctionnalités de gestion
des organisations de formation (Doc A) aux utilisateurs gérant les formations de leur établissement.

Il expose **4 opérations** CRUD :

1. **CreerOrganisation** — crée une nouvelle organisation de formation
2. **LireOrganisation** — fournit les informations de la formation et de son organisation
3. **ModifierOrganisation** — modifie les informations de la formation et de son organisation
4. **SupprimerOrganisation** — supprime l'organisation de la formation

**Règle clé** : l'opération Créer renvoie en retour le même ID fourni en entrée **complété du numéro
d'organisation généré par le système**. C'est cet ID complété qu'il faut utiliser pour toute
lecture, modification ou suppression ultérieure.

---

## Bloc Retour — ResponseType (Common_v2.xsd)

> **Évolution par rapport à Formations Liste v2** : ce service utilise `Common_v2.xsd`
> (au lieu de `Common_v1.xsd`). Le `requestId` et le `transactionId` sont désormais
> des **attributs XML** de l'élément réponse, et non plus un header SOAP séparé.

### Structure ResponseType

```
ResponseType (abstract, extends ResponseAttributesType)
├── @requestId    : UUIDType   [attribut, obligatoire]
│   → Code identifiant de la requête
├── @transactionId : Str36Type [attribut, obligatoire]
│   → Code unique identifiant de la transaction
├── success       : boolean    [obligatoire]
│   → true = requête traitée avec succès
│   → false = erreur (voir messages)
└── messages      : messagesType [0..1]
    ├── error   : MessageType [0..*]
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```

### Types auxiliaires

| Type | Base | Description |
|---|---|---|
| `ResponseAttributesType` | — | Porte les attributs `requestId` (UUIDType) et `transactionId` (Str36Type) |
| `Str36Type` | `xsd:string` (maxLength 36) | Identifiant de transaction |
| `UUIDType` | `xsd:string` (pattern UUID) | Identifiant de requête |

> **Note** : le `requestId` est optionnel en entrée (header SOAP), mais **obligatoire en sortie**
> (attribut de la réponse). Si non fourni en entrée, l'ETNIC en génère un.
> Le `transactionId` est toujours généré par l'ETNIC.

---

## Opération 1 : CreerOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v7/CreerOrganisation`

### Requête

**Type** : `CreerOrganisationRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex: `"2024-2025"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/implId` | ImplIdST (int) | **oui** | Identifiant FASE de l'implantation (**obligatoire en Créer**) |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `dateDebutOrganisation` | date | oui | Date de début de l'organisation |
| `dateFinOrganisation` | date | oui | Date de fin de l'organisation |
| `organisationPeriodesSupplOuEPT` | boolean | non | Flag : périodes supplémentaires ou expertise pédagogique/technique |
| `valorisationAcquis` | boolean | non | Flag : formation pour la valorisation des acquis |
| `enPrison` | boolean | non | Flag : formation donnée en prison |
| `reorientation7TP` | boolean | non | Flag : formation donnée uniquement pour les 7TQ, 7P (ajouté v7, rentrée 2025-2026) |
| `activiteFormation` | boolean | non | Flag : formation organisée dans le cadre des activités de formation |
| `conseillerPrevention` | boolean | non | Flag : formation organisée dans le cadre de la mission de conseiller en prévention ou de DPO |
| `enseignementHybride` | boolean | non | Flag : formation donnée en enseignement hybride (ajouté depuis rentrée 2022-2023) |
| `numOrganisation2AnneesScolaires` | int | non | Numéro de l'organisation de l'année précédente (formation sur 2 années scolaires consécutives) |
| `typeInterventionExterieure` | string | non | Code type d'intervention extérieure (voir liste des valeurs) |
| `interventionExterieure50p` | boolean | non | Intervention d'un tiers de 50% ou plus |

> **Règle métier** : `implId` est **obligatoire** dans CreerOrganisation (contrairement à Lire/Modifier/Supprimer où il est absent du bloc id de la requête).

### Réponse

**Type** : `CreerOrganisationReponseCT` extends `ResponseType`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `@requestId` | UUIDType | oui | Attribut — identifiant de requête |
| `@transactionId` | Str36Type | oui | Attribut — identifiant de transaction |
| `success` | boolean | oui | `true` si la requête a abouti |
| `messages` | messagesType | non | Bloc erreurs/warnings/infos |
| `response` | responseType | non | Présent uniquement si `success=true` |
| `response/organisation` | FormationOrganisationCT | oui | Détail complet de l'organisation créée |

> **Comportement** : la réponse renvoie l'organisation créée avec le `numOrganisation` généré
> par le système (incrémenté automatiquement). Ce numéro est nécessaire pour les opérations
> Lire, Modifier, Supprimer.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v7="http://services-web.etnic.be/eprom/formation/organisation/messages/v7">
  <soapenv:Header/>
  <soapenv:Body>
    <v7:CreerOrganisation>
      <v7:id>
        <v7:anneeScolaire>2024-2025</v7:anneeScolaire>
        <v7:etabId>41</v7:etabId>
        <v7:implId>66</v7:implId>
        <v7:numAdmFormation>186</v7:numAdmFormation>
      </v7:id>
      <v7:dateDebutOrganisation>2024-09-01</v7:dateDebutOrganisation>
      <v7:dateFinOrganisation>2024-10-30</v7:dateFinOrganisation>
      <!--Optional:-->
      <v7:enseignementHybride>true</v7:enseignementHybride>
    </v7:CreerOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (succès, simplifié)

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:msg="http://services-web.etnic.be/eprom/formation/organisation/messages/v7"
                  xmlns:orgv7="http://enseignement.cfwb.be/types/formation/organisation/v7"
                  xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3">
  <soapenv:Body>
    <CreerOrganisationReponse requestId="a6424b1b-a08e-4b89-91e6-0ca4107ef25b"
                             transactionId="000001955cf2dcb4-22c41b6"
                             xmlns="http://services-web.etnic.be/eprom/formation/organisation/messages/v7">
      <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
      <response>
        <organisation>
          <orgv7:id>
            <orgv7:anneeScolaire>2024-2025</orgv7:anneeScolaire>
            <orgv7:etabId>41</orgv7:etabId>
            <orgv7:implId>66</orgv7:implId>
            <orgv7:numAdmFormation>186</orgv7:numAdmFormation>
            <orgv7:numOrganisation>1</orgv7:numOrganisation>
          </orgv7:id>
          <orgv7:dateDebutOrganisation>2024-09-01</orgv7:dateDebutOrganisation>
          <orgv7:dateFinOrganisation>2024-10-30</orgv7:dateFinOrganisation>
          <orgv7:nombreSemaineFormation>9</orgv7:nombreSemaineFormation>
          <orgv7:organisationPeriodesSupplOuEPT>false</orgv7:organisationPeriodesSupplOuEPT>
          <orgv7:valorisationAcquis>false</orgv7:valorisationAcquis>
          <orgv7:enPrison>false</orgv7:enPrison>
          <orgv7:reorientation7TP>false</orgv7:reorientation7TP>
          <orgv7:activiteFormation>false</orgv7:activiteFormation>
          <orgv7:conseillerPrevention>false</orgv7:conseillerPrevention>
          <orgv7:enseignementHybride>true</orgv7:enseignementHybride>
          <orgv7:statut>
            <orgv7:statut>Encodé école</orgv7:statut>
            <orgv7:dateStatut>2025-04-29</orgv7:dateStatut>
          </orgv7:statut>
        </organisation>
      </response>
    </CreerOrganisationReponse>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 2 : LireOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v7/LireOrganisation`

### Requête

**Type** : `LireOrganisationRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

> **Règle métier** : `implId` est **absent** de la requête Lire (et Modifier/Supprimer).
> Seul Créer requiert `implId`.

### Réponse

**Type** : `LireOrganisationReponseCT` extends `ResponseType`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `@requestId` | UUIDType | oui | Attribut |
| `@transactionId` | Str36Type | oui | Attribut |
| `success` | boolean | oui | |
| `messages` | messagesType | non | |
| `response` | responseType | non | |
| `response/organisation` | FormationOrganisationCT | oui | Détail complet de l'organisation |

> **Note** : la réponse Lire renvoie **tous les champs** de FormationOrganisationCT,
> y compris les champs supprimés comme `eLearning` (supprimé depuis 2022-2023)
> et `partiellementDistance` (supprimé depuis 2022-2023). Ces champs restent dans le
> type de retour pour compatibilité mais ne sont plus éditables.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v7="http://services-web.etnic.be/eprom/formation/organisation/messages/v7">
  <soapenv:Header/>
  <soapenv:Body>
    <v7:LireOrganisation>
      <v7:id>
        <v7:anneeScolaire>2024-2025</v7:anneeScolaire>
        <v7:etabId>41</v7:etabId>
        <v7:numAdmFormation>186</v7:numAdmFormation>
        <v7:numOrganisation>1</v7:numOrganisation>
      </v7:id>
    </v7:LireOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 3 : ModifierOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v7/ModifierOrganisation`

### Requête

**Type** : `ModifierOrganisationRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |
| `dateDebutOrganisation` | date | oui | Date de début |
| `dateFinOrganisation` | date | oui | Date de fin |
| `organisationPeriodesSupplOuEPT` | boolean | non | Flag périodes supplémentaires / EPT |
| `valorisationAcquis` | boolean | non | Flag valorisation des acquis |
| `enPrison` | boolean | non | Flag formation en prison |
| `reorientation7TP` | boolean | non | Flag réorientation 7TQ/7P |
| `activiteFormation` | boolean | non | Flag activité de formation |
| `conseillerPrevention` | boolean | non | Flag conseiller prévention / DPO |
| `enseignementHybride` | boolean | non | Flag enseignement hybride |
| `numOrganisation2AnneesScolaires` | int | non | Numéro organisation année précédente |
| `typeInterventionExterieure` | string | non | Code type intervention extérieure |
| `interventionExterieure50p` | boolean | non | Intervention ≥ 50% |

> **Règle métier** : la structure est identique à CreerOrganisation sauf que
> l'id contient `numOrganisation` (au lieu de `implId`). Les dates restent obligatoires.

### Réponse

**Type** : `ModifierOrganisationReponseCT` extends `ResponseType`

Structure identique à CreerOrganisationReponseCT : retourne l'organisation modifiée complète.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v7="http://services-web.etnic.be/eprom/formation/organisation/messages/v7">
  <soapenv:Header/>
  <soapenv:Body>
    <v7:ModifierOrganisation>
      <v7:id>
        <v7:anneeScolaire>2024-2025</v7:anneeScolaire>
        <v7:etabId>41</v7:etabId>
        <v7:numAdmFormation>186</v7:numAdmFormation>
        <v7:numOrganisation>1</v7:numOrganisation>
      </v7:id>
      <v7:dateDebutOrganisation>2024-09-01</v7:dateDebutOrganisation>
      <v7:dateFinOrganisation>2024-10-30</v7:dateFinOrganisation>
      <!--Optional:-->
      <v7:conseillerPrevention>true</v7:conseillerPrevention>
    </v7:ModifierOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 4 : SupprimerOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v7/SupprimerOrganisation`

### Requête

**Type** : `SupprimerOrganisationRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

### Réponse

**Type** : `SupprimerOrganisationReponseCT` extends `ResponseType`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `@requestId` | UUIDType | oui | Attribut |
| `@transactionId` | Str36Type | oui | Attribut |
| `success` | boolean | oui | |
| `messages` | messagesType | non | |

> **Note** : la réponse Supprimer ne contient **pas de bloc `response`** — uniquement
> le bloc retour (success + messages). C'est la seule opération sans données de retour.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v7="http://services-web.etnic.be/eprom/formation/organisation/messages/v7">
  <soapenv:Header/>
  <soapenv:Body>
    <v7:SupprimerOrganisation>
      <v7:id>
        <v7:anneeScolaire>2024-2025</v7:anneeScolaire>
        <v7:etabId>41</v7:etabId>
        <v7:numAdmFormation>186</v7:numAdmFormation>
        <v7:numOrganisation>1</v7:numOrganisation>
      </v7:id>
    </v7:SupprimerOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## FormationOrganisationCT (type de retour détaillé)

Structure complète du type retourné dans les réponses Créer, Lire et Modifier :

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationIdCT | oui | Identifiant complet de l'organisation |
| `dateDebutOrganisation` | date | oui | Date de début |
| `dateFinOrganisation` | date | oui | Date de fin |
| `nombreSemaineFormation` | int | oui | Nombre de semaines de formation (calculé par le système) |
| `organisationPeriodesSupplOuEPT` | boolean | non | Périodes supplémentaires / EPT |
| `valorisationAcquis` | boolean | non | Valorisation des acquis |
| `eLearning` | boolean | non | Formation en e-Learning (**supprimé depuis rentrée 2022-2023**, présent en lecture seule) |
| `enPrison` | boolean | non | Formation en prison |
| `reorientation7TP` | boolean | non | Réorientation 7TQ/7P (**ajouté rentrée 2025-2026**) |
| `activiteFormation` | boolean | non | Activité de formation |
| `conseillerPrevention` | boolean | non | Conseiller prévention / DPO |
| `partiellementDistance` | boolean | non | Partiellement à distance (**supprimé depuis rentrée 2022-2023**, présent en lecture seule) |
| `enseignementHybride` | boolean | non | Enseignement hybride (**ajouté rentrée 2022-2023**) |
| `numOrganisation2AnneesScolaires` | int | non | Numéro organisation année précédente (2 années scolaires) |
| `typeInterventionExterieure` | string | non | Code type intervention extérieure |
| `interventionExterieure50p` | boolean | non | Intervention ≥ 50% |
| `statut` | StatutCT | non | Statut de l'organisation de formation |

> **Champs supprimés vs ajoutés** : `eLearning` et `partiellementDistance` ont été remplacés par
> `enseignementHybride` à la rentrée 2022-2023. Les anciens champs restent dans le type de retour
> pour compatibilité descendante mais ne sont plus éditables via Créer/Modifier.

---

## Valeurs de typeInterventionExterieure

Liste exhaustive des codes (validée au 10-06-2025, hors contrat XSD) :

| Code | Description | Statut |
|---|---|---|
| `"A"` | Personnel non chargé de cours | actif |
| `"B"` | Octroi périodes supplémentaires-bonus | actif |
| `"C"` | Convention | actif |
| `"D"` | Discriminations positives | actif |
| `"E"` | EHR | actif |
| `"F"` | Fonds Européens | actif |
| `"I"` | Formation des publics Infra scolarisés | actif |
| `"J"` | Réorientation 7TQ/7P | actif (**nouveau v7**) |
| `"K"` | Octroi périodes cabinet-projets transvers | actif |
| `"P"` | Formations continuées | actif |
| `"Q"` | Agence Qualité | actif |
| ~~`"R"`~~ | ~~Récupération périodes complémentaires~~ | **supprimé** |
| ~~`"S"`~~ | ~~CISCO Système~~ | **supprimé** |
| `"U"` | Union Européenne | actif |
| `"V"` | Validation des compétences | actif |

---

## Valeurs de StatutCT.statut

| Valeur | Description |
|---|---|
| `"Encodé école"` | Encodé par l'école, pas encore validé |
| `"Encodé PO"` | Encodé par le pouvoir organisateur |
| `"Approuvé"` | Approuvé/validé |

---

## Codes d'erreur spécifiques

### Codes communs (cross-service)

| Success | Code | Description |
|---|---|---|
| `true` | *(aucun)* | Exécution sans erreur |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. |
| `false` | `00999` | Erreur sql : |

### Codes spécifiques Formation Organisation (20xxx)

| Success | Code | Description | Opérations |
|---|---|---|---|
| `false` | `20005` | Numéro d'organisation incorrect | Lire, Modifier, Supprimer |
| `false` | `20006` | La date de début d'organisation doit être inférieure à la date de fin d'organisation | Créer, Modifier |
| `false` | `20007` | Switch périodes supplémentaires incorrect (O/N) | Créer, Modifier |
| `false` | `20010` | La date de début d'organisation ne peut être inférieure au xx/xx/xxxx | Créer, Modifier |
| `false` | `20011` | La date de fin d'organisation ne peut être supérieure au xx/xx/xxxx | Créer, Modifier |
| `false` | `20012` | La date de fin d'organisation ne peut être supérieure d'un 1 an à la date de début d'organisation | Créer, Modifier |
| `false` | `20013` | Le nombre de semaine de la formation doit être compris entre 1 et 52 | Créer, Modifier |
| `false` | `20016` | Le type d'intervention x n'existe pas | Créer, Modifier |
| `false` | `20019` | Switch en-prison incorrect (O/N) | Créer, Modifier |
| `false` | `20023` | Switch uniquement VAE incorrect (O/N) | Créer, Modifier |
| `false` | `20024` | Switch Activité de formation incorrect (O/N) | Créer, Modifier |
| `false` | `20025` | Veuillez sélectionner le type d'intervention extérieure | Créer, Modifier |
| `false` | `20026` | Switch Uniquement pour l'organisation de la mission de conseiller en prévention ou de DPO incorrect (O/N) | Créer, Modifier |
| `false` | `20027` | Switch Partiellement à distance incorrect (O/N) | Créer, Modifier |
| `false` | `20028` | Numéro d'organisation année précédente incorrect (UE sur 2 années scolaires) | Créer, Modifier |
| `false` | `20029` | La date de début d'organisation ne peut être supérieure ou égale à la date de fermeture de la formation | Créer, Modifier |
| `false` | `20030` | La date de début d'organisation ne peut excéder un délai de 4 mois maximum | Créer, Modifier |
| `false` | `20031` | Switch Enseignement hybride incorrect (O/N) | Créer, Modifier |
| `false` | `20034` | Le type d'intervention x n'est plus disponible à l'encodage | Créer, Modifier |
| `false` | `20037` | Switch réorientation 7TQ 7P incorrect (O/N) | Créer, Modifier |
| `false` | `20038` | Le switch réorientation 7TQ 7P doit obligatoirement être à oui pour cette implantation réservée aux réorientations des 7e TQ/P | Créer, Modifier |

### Codes spécifiques Formation Organisation (30xxx)

| Success | Code | Description | Opérations |
|---|---|---|---|
| `false` | `30001` | Numéro d'établissement incorrect | toutes |
| `false` | `30002` | Numéro d'implantation incorrect | Créer |
| `false` | `30003` | Le statut des documents ne permet pas cette opération | Modifier, Supprimer |
| `false` | `30004` | Le type d'intervention extérieure est incorrect | Créer, Modifier |
| `false` | `30005` | Le numéro administratif de la formation est incorrect | toutes |
| `false` | `30006` | Vous ne pouvez pas effectuer cette opération (Passage PO non actif) | Créer, Modifier, Supprimer |
| `false` | `30007` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | toutes |
| `false` | `30008` | La donnée 'enseignementHybride' n'est disponible qu'à partir de la rentrée scolaire 2022-2023 | Créer, Modifier |
| `false` | `30009` | La donnée 'reorientation7TP' n'est disponible qu'à partir de la rentrée scolaire 2025-2026 | Créer, Modifier |

---

## Règles métier (extraites du PDF)

1. **implId obligatoire uniquement en Créer** : les opérations Lire, Modifier et Supprimer
   n'incluent pas `implId` dans leur bloc `id` de requête. Seul Créer le requiert.

2. **numOrganisation généré automatiquement** : lors de la création, le système attribue un
   numéro d'organisation incrémental. Ce numéro est retourné dans la réponse et doit être
   utilisé pour toutes les opérations suivantes.

3. **nombreSemaineFormation calculé** : ce champ est calculé automatiquement par le système
   à partir des dates de début et fin. Il apparaît uniquement dans les réponses (pas en entrée).

4. **Champs supprimés** : `eLearning` et `partiellementDistance` ont été supprimés depuis la
   rentrée 2022-2023 et remplacés par `enseignementHybride`. Ils restent dans
   FormationOrganisationCT (retour) mais ne sont plus dans les types de requête Créer/Modifier.

5. **Contraintes temporelles sur les dates** :
   - Date début < date fin (code 20006)
   - Date début ≥ date plancher de l'année scolaire (code 20010)
   - Date fin ≤ date plafond de l'année scolaire (code 20011)
   - Écart max 1 an entre début et fin (code 20012)
   - Date début < date fermeture de la formation (code 20029)
   - Date début ne peut excéder un délai de 4 mois max (code 20030)

6. **Contrainte statut documents** (code 30003) : certaines opérations (Modifier, Supprimer)
   ne sont pas autorisées si le statut des documents associés ne le permet pas
   (par ex. un document "Approuvé" bloque la modification).

7. **Passage PO** (code 30006) : certaines opérations ne sont pas possibles si le passage
   au pouvoir organisateur n'est pas actif.

8. **Contraintes de rentrée scolaire** :
   - `enseignementHybride` : disponible uniquement à partir de la rentrée 2022-2023 (code 30008)
   - `reorientation7TP` : disponible uniquement à partir de la rentrée 2025-2026 (code 30009)

9. **reorientation7TP obligatoire** (code 20038) : pour certaines implantations réservées
   aux réorientations 7TQ/7P, le flag doit obligatoirement être à `true`.

10. **Valeurs de statut** : `"Encodé école"`, `"Encodé PO"`, `"Approuvé"` (identiques à
    Formations Liste).

---

## Différences clés avec le type de requête vs le type de retour

| Champ | En requête (Créer) | En requête (Modifier) | En retour (FormationOrganisationCT) |
|---|---|---|---|
| `id/implId` | **obligatoire** | **absent** | présent (dans OrganisationIdCT) |
| `id/numOrganisation` | **absent** (généré) | **obligatoire** | présent |
| `nombreSemaineFormation` | **absent** (calculé) | **absent** (calculé) | **obligatoire** (calculé) |
| `eLearning` | **absent** (supprimé) | **absent** (supprimé) | présent (lecture seule) |
| `partiellementDistance` | **absent** (supprimé) | **absent** (supprimé) | présent (lecture seule) |
| `statut` | **absent** (géré par le système) | **absent** | présent |

---

## Fichiers XSD du contrat

| Fichier | Rôle | Partagé avec d'autres services |
|---|---|---|
| `EpromFormationOrganisationMessages_v7.xsd` | Messages requête/réponse (4 opérations) | non (spécifique) |
| `FormationOrganisation_v7.xsd` | FormationOrganisationCT, OrganisationIdCT, OrganisationApercuCT, StatutCT | oui (Formations Liste utilise v2) |
| `AnneeScolaire_v1.xsd` | AnneeScolaireST | oui (tous services) — identique |
| `Etablissement_v1.xsd` | EtabIdST, ImplIdST, CodeUniteST | oui (tous services) — identique |
| `ResponseStatus_v3.xsd` | success, messages, MessageType | oui (tous services) — identique |
| `Common_v2.xsd` | ResponseType, ResponseAttributesType, Str36Type | **nouveau** (remplace Common_v1.xsd) |
| `requestId_v1.xsd` | UUIDType | oui (tous services) — identique |

> **Évolution XSD** : ce service utilise `Common_v2.xsd` au lieu de `Common_v1.xsd`.
> Le type de base des réponses est `ResponseType` (avec attributs requestId + transactionId)
> au lieu de `AbstractExternalResponseType` (avec header SOAP).
> De même, `FormationOrganisation_v7.xsd` remplace `FormationOrganisation_v2.xsd` avec
> les nouveaux champs booléens (reorientation7TP, activiteFormation, conseillerPrevention,
> partiellementDistance, enseignementHybride, numOrganisation2AnneesScolaires).

---

## Mapping vers pyetnic existant

| Élément spec | Code pyetnic actuel | Notes refonte |
|---|---|---|
| `CreerOrganisation` | `FormationOrganisationService.creer_organisation()` | OK — adapter au nouveau ResponseType |
| `LireOrganisation` | `FormationOrganisationService.lire_organisation()` | OK |
| `ModifierOrganisation` | `FormationOrganisationService.modifier_organisation()` | OK |
| `SupprimerOrganisation` | `FormationOrganisationService.supprimer_organisation()` | OK |
| `FormationOrganisationCT` | `FormationOrganisation` dataclass | **À refondre** : ajouter nouveaux champs v7 |
| `OrganisationIdCT` | `OrganisationId` dataclass | OK |
| `StatutCT` | `StatutDocument` dataclass | OK (partagé avec Formations Liste) |
| Codes d'erreur | catch-all `except Exception` | **À refondre** : exceptions typées par code |
| ResponseType (v2) | non géré | **Nouveau** : parser attributs requestId + transactionId |
