# EPROM - Formation Organisation v8.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL et XSD servis par la production (`https://ws.etnic.be/eprom/formation/organisation/v8?wsdl`, identiques à l'archive « 8.0 » du catalogue SOA), embarqués dans `pyetnic/resources/EPROM_Formation_Organisation_8.0/` (relevé du 2026-11-24) + PDF Manuel d'utilisation v8.0.0 rev6.0 (27-04-2026, édité le 21-05-2026, `ETNIC_Services_Web_EPROM_FormationOrganisation_v8.0_Manuel_d_utilisation_rev6.0.pdf`). La v7 (manuel rev5.1, 01-07-2025) n'est plus embarquée depuis 0.3.0.
> Date d'analyse : 2026-04-14 (v7) ; passage à la v8 le 2026-11-24 (#32)

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | Formation Organisation |
| Version service | 8.0.0 (v7 : 7.0.0, le manuel n'annonce pas sa fin) |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security Username Token Profile (ou certificat X.509) |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/organisation/v8` |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/organisation/messages/v8` |
| Types namespace | `http://enseignement.cfwb.be/types/formation/organisation/v8` |
| Binding | `EPROMFormationOrganisationV8Binding` (document/literal) |

### Endpoints

| Env | URL |
|---|---|
| TQ | `https://ws-tq.etnic.be/eprom/formation/organisation/v8` |
| PROD | `https://ws.etnic.be/eprom/formation/organisation/v8` |

> Le manuel v8 (§2.2.1, « Endpoint EPROM ») et le catalogue SOA donnent ces deux adresses, sur la
> passerelle ETNIC ; ce sont celles de pyetnic. Le manuel rev4.1 (mai 2023) annonçait aussi
> `services-web(.tq).etnic.be:11443`, qui ne figure plus au manuel v8. Lecture vérifiée sur TQ et
> en production le 2026-11-24, certificat TLS vérifié dans les deux environnements.

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
> (au lieu de `Common_v1.xsd`). Le `requestId` et le `transactionId` sont des **attributs XML**
> de l'élément réponse.
>
> **Observé sur TQ (2026-11-24, `LireOrganisation` v8, succès et erreur 00009)** : le serveur
> renvoie le `requestId` reçu **deux fois**, dans l'en-tête SOAP `requestId` (comme les services
> Common_v1) et en attribut de la racine de la réponse, avec la même valeur ; il ajoute un
> `transactionId` propre au serveur (ex. `000001a1d5d8e8dc-8984b`). pyetnic lit l'en-tête, puis
> l'attribut en repli.

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
`http://services-web.etnic.be/eprom/formation/organisation/v8/CreerOrganisation`

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
| `BESAeSI` | boolean | non | Flag : formation donnée uniquement pour les BES AeSI, Brevet d'Enseignement Supérieur d'Assistant en Soins Infirmiers (**ajouté v8**, rentrée 2026-2027, erreur 30010 avant) |
| `activiteFormation` | boolean | non | Flag : formation organisée dans le cadre des activités de formation |
| `conseillerPrevention` | boolean | non | Flag : formation organisée dans le cadre de la mission de conseiller en prévention ou de DPO |
| `enseignementHybride` | boolean | non | Flag : formation donnée en enseignement hybride (ajouté depuis rentrée 2022-2023) |
| `numOrganisation2AnneesScolaires` | int | non | Numéro de l'organisation de l'année précédente (formation sur 2 années scolaires consécutives) |
| `typeInterventionExterieure` | string | non | Code type d'intervention extérieure (voir liste des valeurs) |
| `interventionExterieure50p` | boolean | non | Intervention d'un tiers de 50% ou plus |

> **Règle métier** : `implId` est **obligatoire** dans CreerOrganisation (contrairement à Lire/Modifier/Supprimer où il est absent du bloc id de la requête).

> **Sémantique observée en production (11/06/2026, un établissement)** : UE sur 2 années scolaires :
> chaque année porte son propre enregistrement d'organisation, et **les deux portent les dates
> complètes** de l'UE (y compris la portion hors de leur année scolaire). L'enregistrement de la
> **première** année a `numOrganisation2AnneesScolaires = 0` ; celui de la **seconde** année pointe
> vers le `numOrganisation` de la première. Exemple réel : UE 511, org 4 de 2024-2025 et org 2 de
> 2025-2026 portent toutes deux 22/05/2025 → 30/01/2026, la seconde avec
> `numOrganisation2AnneesScolaires = 4`.

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

> **Observé en production** :
> - Les champs facultatifs omis reviennent avec les valeurs par défaut du serveur : booléens à
>   `False`, `numOrganisation2AnneesScolaires` à `0`, `typeInterventionExterieure` à `None`
>   (observé une fois, 2026-06-11).
> - Une création refusée est atomique : rien ne reste en base (observé une fois, 2026-06-11).
> - `CreerOrganisation` ne vérifie pas que la formation est encore organisable quand son dossier a
>   été remplacé par un nouveau : l'enregistrement est accepté, le refus ne vient qu'à
>   l'approbation (observé une fois, octobre 2026).

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v8="http://services-web.etnic.be/eprom/formation/organisation/messages/v8">
  <soapenv:Header/>
  <soapenv:Body>
    <v8:CreerOrganisation>
      <v8:id>
        <v8:anneeScolaire>2024-2025</v8:anneeScolaire>
        <v8:etabId>41</v8:etabId>
        <v8:implId>66</v8:implId>
        <v8:numAdmFormation>186</v8:numAdmFormation>
      </v8:id>
      <v8:dateDebutOrganisation>2024-09-01</v8:dateDebutOrganisation>
      <v8:dateFinOrganisation>2024-10-30</v8:dateFinOrganisation>
      <!--Optional:-->
      <v8:enseignementHybride>true</v8:enseignementHybride>
    </v8:CreerOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (succès, simplifié)

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:msg="http://services-web.etnic.be/eprom/formation/organisation/messages/v8"
                  xmlns:orgv8="http://enseignement.cfwb.be/types/formation/organisation/v8"
                  xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3">
  <soapenv:Body>
    <CreerOrganisationReponse requestId="a6424b1b-a08e-4b89-91e6-0ca4107ef25b"
                             transactionId="000001955cf2dcb4-22c41b6"
                             xmlns="http://services-web.etnic.be/eprom/formation/organisation/messages/v8">
      <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
      <response>
        <organisation>
          <orgv8:id>
            <orgv8:anneeScolaire>2024-2025</orgv8:anneeScolaire>
            <orgv8:etabId>41</orgv8:etabId>
            <orgv8:implId>66</orgv8:implId>
            <orgv8:numAdmFormation>186</orgv8:numAdmFormation>
            <orgv8:numOrganisation>1</orgv8:numOrganisation>
          </orgv8:id>
          <orgv8:dateDebutOrganisation>2024-09-01</orgv8:dateDebutOrganisation>
          <orgv8:dateFinOrganisation>2024-10-30</orgv8:dateFinOrganisation>
          <orgv8:nombreSemaineFormation>9</orgv8:nombreSemaineFormation>
          <orgv8:organisationPeriodesSupplOuEPT>false</orgv8:organisationPeriodesSupplOuEPT>
          <orgv8:valorisationAcquis>false</orgv8:valorisationAcquis>
          <orgv8:enPrison>false</orgv8:enPrison>
          <orgv8:reorientation7TP>false</orgv8:reorientation7TP>
          <orgv8:activiteFormation>false</orgv8:activiteFormation>
          <orgv8:conseillerPrevention>false</orgv8:conseillerPrevention>
          <orgv8:enseignementHybride>true</orgv8:enseignementHybride>
          <orgv8:statut>
            <orgv8:statut>Encodé école</orgv8:statut>
            <orgv8:dateStatut>2025-04-29</orgv8:dateStatut>
          </orgv8:statut>
        </organisation>
      </response>
    </CreerOrganisationReponse>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 2 : LireOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v8/LireOrganisation`

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
                  xmlns:v8="http://services-web.etnic.be/eprom/formation/organisation/messages/v8">
  <soapenv:Header/>
  <soapenv:Body>
    <v8:LireOrganisation>
      <v8:id>
        <v8:anneeScolaire>2024-2025</v8:anneeScolaire>
        <v8:etabId>41</v8:etabId>
        <v8:numAdmFormation>186</v8:numAdmFormation>
        <v8:numOrganisation>1</v8:numOrganisation>
      </v8:id>
    </v8:LireOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 3 : ModifierOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v8/ModifierOrganisation`

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
| `BESAeSI` | boolean | non | Flag BES AeSI (**ajouté v8**, rentrée 2026-2027) |
| `activiteFormation` | boolean | non | Flag activité de formation |
| `conseillerPrevention` | boolean | non | Flag conseiller prévention / DPO |
| `enseignementHybride` | boolean | non | Flag enseignement hybride |
| `numOrganisation2AnneesScolaires` | int | non | Numéro organisation année précédente |
| `typeInterventionExterieure` | string | non | Code type intervention extérieure |
| `interventionExterieure50p` | boolean | non | Intervention ≥ 50% |

> **Règle métier** : la structure est identique à CreerOrganisation sauf que
> l'id contient `numOrganisation` (au lieu de `implId`). Les dates restent obligatoires.

> **Un champ facultatif omis est remis à sa valeur par défaut, pas conservé** (testé sur TQ,
> 2026-11-24) : une organisation créée avec `BESAeSI` et `enPrison` à `true`, modifiée par une
> requête qui omet ces deux champs, se relit avec les deux à `false`. Modifier remplace donc
> l'organisation entière : envoyer l'organisation telle que relue, changements appliqués. Le
> même essai montre `BESAeSI` accepté en 2026-2027 et relu tel quel, et une création 2025-2026
> portant `BESAeSI` refusée par l'erreur 30010.

### Réponse

**Type** : `ModifierOrganisationReponseCT` extends `ResponseType`

Structure identique à CreerOrganisationReponseCT : retourne l'organisation modifiée complète.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v8="http://services-web.etnic.be/eprom/formation/organisation/messages/v8">
  <soapenv:Header/>
  <soapenv:Body>
    <v8:ModifierOrganisation>
      <v8:id>
        <v8:anneeScolaire>2024-2025</v8:anneeScolaire>
        <v8:etabId>41</v8:etabId>
        <v8:numAdmFormation>186</v8:numAdmFormation>
        <v8:numOrganisation>1</v8:numOrganisation>
      </v8:id>
      <v8:dateDebutOrganisation>2024-09-01</v8:dateDebutOrganisation>
      <v8:dateFinOrganisation>2024-10-30</v8:dateFinOrganisation>
      <!--Optional:-->
      <v8:conseillerPrevention>true</v8:conseillerPrevention>
    </v8:ModifierOrganisation>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 4 : SupprimerOrganisation

### SOAP Action
`http://services-web.etnic.be/eprom/formation/organisation/v8/SupprimerOrganisation`

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

> **Observé en production** (2026-09-30, six suppressions, année relue après chacune) :
> `SupprimerOrganisation` accepte une organisation « Encodé école » sans document ; il ne laisse ni
> statut ni trace : l'organisation disparaît de `ListerFormations`, et les autres organisations de
> l'année ne bougent pas. Une organisation approuvée ou portant des documents n'a pas été essayée
> (le manuel annonce `30003`).
>
> **Numéro libéré** (testé sur TQ, 2026-11-10) : la création suivante reçoit le plus grand
> `numOrganisation` existant + 1. Un numéro supprimé au milieu de la série n'est donc jamais
> réattribué ; le dernier numéro, une fois supprimé, l'est de nouveau (règle 2).

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v8="http://services-web.etnic.be/eprom/formation/organisation/messages/v8">
  <soapenv:Header/>
  <soapenv:Body>
    <v8:SupprimerOrganisation>
      <v8:id>
        <v8:anneeScolaire>2024-2025</v8:anneeScolaire>
        <v8:etabId>41</v8:etabId>
        <v8:numAdmFormation>186</v8:numAdmFormation>
        <v8:numOrganisation>1</v8:numOrganisation>
      </v8:id>
    </v8:SupprimerOrganisation>
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
| `BESAeSI` | boolean | non | BES AeSI (**ajouté v8**, rentrée 2026-2027) ; lu `false` sur une organisation qui ne le porte pas (TQ, 2026-11-24) |
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

> **Pas de dates de dixièmes** : aucun service ne porte les dates des dixièmes d'une organisation.
> Les seules dates des XSD EPROM sont `dateDebutOrganisation`, `dateFinOrganisation`,
> `dateStatut`, `dateFemeture` (sic) et `tsMaj`, et l'écran n'affiche aucune date de dixième (écran
> relu le 2026-11-05).

---

## Valeurs de typeInterventionExterieure

Liste exhaustive des codes (manuel v8 rev6.0, « validé hors contrat xml » au 27-04-2026 ; la liste du manuel v7 rev5.1 datait du 10-06-2025). R et S sont barrés dans les deux manuels :

| Code | Description | Statut |
|---|---|---|
| `"A"` | Personnel non chargé de cours | actif |
| `"B"` | Octroi périodes supplémentaires-bonus | actif |
| `"C"` | Convention | actif |
| `"D"` | Discriminations positives | actif |
| `"E"` | EHR | actif |
| `"F"` | Fonds Européens | actif |
| `"G"` | BES | actif (**nouveau v8**) |
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
| `false` | `20011` | La date de fin d'organisation ne peut être supérieure au xx/xx/xxxx (`xx/xx/xxxx` = 31 août de l'année de fin de l'année scolaire, testé sur TQ, 2026-11-10 ; exception non éclaircie pour une UE sur deux années, voir règle 5) | Créer, Modifier |
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
| `false` | `20030` | La date de début d'organisation ne peut excéder un délai de 4 mois maximum (compté depuis la date de déclaration ; une date passée est acceptée, voir règle 5) | Créer, Modifier |
| `false` | `20031` | Switch Enseignement hybride incorrect (O/N) | Créer, Modifier |
| `false` | `20034` | Le type d'intervention x n'est plus disponible à l'encodage | Créer, Modifier |
| `false` | `20037` | Switch réorientation 7TQ 7P incorrect (O/N) | Créer, Modifier |
| `false` | `20038` | Le switch réorientation 7TQ 7P doit obligatoirement être à oui pour cette implantation réservée aux réorientations des 7e TQ/P | Créer, Modifier |
| `false` | `20042` | Switch BES AeSI incorrect (O/N) (**nouveau v8**) | Créer, Modifier |

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
| `false` | `30010` | La donnée 'BESAeSI' n'est disponible qu'à partir de la rentrée scolaire 2026-2027 (**nouveau v8**) | Créer, Modifier |

---

## Règles métier (extraites du PDF)

1. **implId obligatoire uniquement en Créer** : les opérations Lire, Modifier et Supprimer
   n'incluent pas `implId` dans leur bloc `id` de requête. Seul Créer le requiert.

2. **numOrganisation généré automatiquement** : lors de la création, le système attribue un
   numéro d'organisation incrémental, **dans l'ordre de déclaration**. Ce numéro est retourné
   dans la réponse et doit être utilisé pour toutes les opérations suivantes. Le numéro attribué
   est le plus grand `numOrganisation` existant + 1 (testé sur TQ, 2026-11-10) : avec 1 et 2
   créés puis 1 supprimé, la création suivante reçoit 3, et le trou n'est jamais comblé ; 3
   supprimé, la création suivante reçoit de nouveau 3 : supprimer le dernier numéro le libère.

3. **nombreSemaineFormation calculé** : ce champ est calculé automatiquement par le système
   à partir des dates de début et fin. Il apparaît uniquement dans les réponses (pas en entrée).
   Ce n'est pas un simple nombre de semaines : la valeur est **plafonnée à 40**, observé trois
   fois : 40 rendu pour le 09/03/2026 → 29/01/2027 (46 semaines) et pour le 08/01/2026 →
   07/01/2027 (52 semaines) en production, et pour le 01/09/2026 → 31/08/2027 (52 semaines
   calendaires), à la création comme à la relecture `LireOrganisation` (testé sur TQ,
   2026-11-10). L'origine du plafond n'est pas connue.

4. **Champs supprimés** : `eLearning` et `partiellementDistance` ont été supprimés depuis la
   rentrée 2022-2023 et remplacés par `enseignementHybride`. Ils restent dans
   FormationOrganisationCT (retour) mais ne sont plus dans les types de requête Créer/Modifier.

5. **Contraintes temporelles sur les dates** :
   - Date début < date fin (code 20006)
   - Date début ≥ une date plancher (code 20010) : plancher non identifié. Le serveur a accepté
     une date de début antérieure à l'année scolaire de l'enregistrement quand
     `numOrganisation2AnneesScolaires` est renseigné (observé en production, 2026-06-11 et
     2026-09-13 ; voir la note sous Opération 1) ; jamais testé sans ce lien.
   - Date fin ≤ date plafond de l'année scolaire (code 20011) : le plafond est le 31 août de
     l'année de fin de l'année scolaire (testé sur TQ, 2026-11-10 : un enregistrement 2026-2027
     finissant le 15/11/2027 est refusé, « ne peut être supérieure au 31/08/2027 »). Contre-exemple
     en production : l'enregistrement 2024-2025 d'une UE sur deux années scolaires finit le
     30/01/2026 (note sous Opération 1) ; comment ce cas passe `20011` n'est pas éclairci.
   - Écart max 1 an entre début et fin (code 20012)
   - Date début < date fermeture de la formation (code 20029)
   - Date début ne peut excéder un délai de 4 mois max (code 20030), compté depuis la **date de
     déclaration** : début à déclaration + 3 mois 4 jours accepté, + 4 mois 22 jours refusé, début
     passé (3 mois avant) accepté (observé en production, 2026-06-11, trois points ; borne exacte
     déduite, non mesurée). Début passé de nouveau accepté : 01/09/2026 déclaré le 10/11/2026
     (testé sur TQ, 2026-11-10).

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
| `EpromFormationOrganisationMessages_v8.xsd` | Messages requête/réponse (4 opérations) | non (spécifique) |
| `FormationOrganisation_v8.xsd` | FormationOrganisationCT, OrganisationIdCT, OrganisationApercuCT, StatutCT | oui (Formations Liste utilise v2) |
| `AnneeScolaire_v1.xsd` | AnneeScolaireST | oui (tous services) — identique |
| `Etablissement_v1.xsd` | EtabIdST, ImplIdST, CodeUniteST | oui (tous services) — identique |
| `ResponseStatus_v3.xsd` | success, messages, MessageType | oui (tous services) — identique |
| `Common_v2.xsd` | ResponseType, ResponseAttributesType, Str36Type | **nouveau** (remplace Common_v1.xsd) |
| `requestId_v1.xsd` | UUIDType | oui (tous services) — identique |

> **Évolution XSD** : ce service utilise `Common_v2.xsd` au lieu de `Common_v1.xsd`.
> Le type de base des réponses est `ResponseType` (avec attributs requestId + transactionId)
> au lieu de `AbstractExternalResponseType` (avec header SOAP).
> De même, `FormationOrganisation_v8.xsd` remplace `FormationOrganisation_v2.xsd` avec
> les nouveaux champs booléens (reorientation7TP, BESAeSI, activiteFormation, conseillerPrevention,
> partiellementDistance, enseignementHybride, numOrganisation2AnneesScolaires).
>
> **v7 -> v8** : seul ajout au contrat, `BESAeSI` (facultatif) dans `FormationOrganisationCT` et dans
> les requêtes Créer et Modifier, entre `reorientation7TP` et `activiteFormation` ; mêmes opérations,
> liaison renommée `EPROMFormationOrganisationV8Binding`. Le manuel ajoute aussi le code « G » et
> les erreurs 20042 et 30010 (comparaison du contrat et du manuel, 2026-11-24).

---

## Mapping vers pyetnic existant

| Élément spec | Code pyetnic actuel | Notes refonte |
|---|---|---|
| `CreerOrganisation` | `pyetnic.eprom.creer_organisation()` | paramètre `BESAeSI` (v8) |
| `LireOrganisation` | `pyetnic.eprom.lire_organisation()` | |
| `ModifierOrganisation` | `pyetnic.eprom.modifier_organisation()` | envoie les champs non `None` de l'`Organisation` |
| `SupprimerOrganisation` | `pyetnic.eprom.supprimer_organisation()` | |
| `FormationOrganisationCT` | dataclass `Organisation` | tous les champs, `BESAeSI` compris (en dernier) |
| `OrganisationIdCT` | dataclass `OrganisationId` | |
| `StatutCT` | dataclass `StatutDocument` | partagé avec Formations Liste |
| `typeInterventionExterieure` | enum `TypeInterventionExterieure` | 14 codes, `G` compris ; pas de R ni de S |
| Codes d'erreur | exceptions typées (`pyetnic.exceptions`) | 20042 et 30010 -> `EtnicValidationError` |
| ResponseType (v2) | `extract_error_info` | `requestId` lu dans l'en-tête, l'attribut en repli ; `transactionId` non exposé |
