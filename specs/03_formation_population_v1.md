# EPROM — Formation Population (Document 1) v1.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationDocument1Service_external_v1.wsdl` + PDF Manuel d'utilisation rev1.1 (01-05-2023)
> Date d'analyse : 2026-04-14

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | Formation Population (Document 1) |
| Version service | 1.0.0 |
| Révision document | 1.1 |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security Username Token Profile (ou certificat X.509) |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/document1/v1` |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/document1/messages/v1` |
| Types namespace (doc1) | `http://enseignement.cfwb.be/types/formation/document1/v1` |
| Types namespace (org) | `http://enseignement.cfwb.be/types/organisation/v1` |
| Binding | `EPROMFormationDocument1ExternalV1Binding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/eprom/formation/document1/v1` |
| PROD | prompt | `https://ws.etnic.be/eprom/formation/document1/v1` |
| TQ | PDF (TLS 1.2) | `https://services-web.tq.etnic.be:11443/eprom/formation/document1/v1` |
| PROD | PDF (TLS 1.2) | `https://services-web.etnic.be:11443/eprom/formation/document1/v1` |

> **Endpoint générique « Ecole »** (déprécié) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument1V1?mode=sync`, To = `http://services-web.etnic.be/eprom`

---

## Description fonctionnelle

Le service FormationDocument1 permet de gérer les informations relatives à la **population
scolaire au 1/10ème** de la formation (Doc 1) sauvegardées dans EPROM.

⚠️ **Terminologie** : le nom interne « Document 1 » correspond à « Population » (les étudiants
inscrits). Ne pas confondre avec « Document 1D » qui désigne « Droits d'Inscription ».

Il expose **3 opérations** :

1. **LireDocument1** — fournit les informations du document 1
2. **ModifierDocument1** — permet de modifier les données du document 1
3. **ApprouverDocument1** — permet d'approuver les données du document 1

**Règle clé** : une fois approuvé, le document 1 ne peut plus être modifié (erreur 1545).

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> **Pattern identique à Formations Liste v2** : ce service utilise `Common_v1.xsd`
> (et non `Common_v2.xsd` comme Formation Organisation v7).
> Le `requestId` est un **header SOAP séparé** (optionnel en requête, obligatoire en réponse).

### Structure AbstractExternalResponseType

```
AbstractExternalResponseType (abstract)
├── success  : boolean      [obligatoire]
│   → true = requête traitée avec succès
│   → false = erreur (voir messages)
└── messages : messagesType [0..1]
    ├── error   : MessageType [0..*]
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```

---

## Type d'identification — Organisation_v1.xsd (NOUVEAU)

> **Nouveau XSD** non présent dans les sessions 1-2. Partagé entre Document 1 et Document 2.
> Namespace : `http://enseignement.cfwb.be/types/organisation/v1`
>
> **Différence avec OrganisationIdCT** (sessions 1-2, namespace `/organisation/v2` ou `/v7`) :
> pas de champ `implId` en requête (OrganisationReqIdCT), et `implId` optionnel en réponse
> (OrganisationResIdCT).

### OrganisationReqIdCT (identification en requête)

```
OrganisationReqIdCT
├── anneeScolaire   : AnneeScolaireST [obligatoire]
├── etabId          : EtabIdST        [obligatoire]
├── numAdmFormation : int             [obligatoire]
└── numOrganisation : int             [obligatoire]
```

> ⚠️ **Pas de `implId`** en requête — l'organisation est identifiée uniquement par
> anneeScolaire + etabId + numAdmFormation + numOrganisation.

### OrganisationResIdCT (identification en réponse)

```
OrganisationResIdCT
├── anneeScolaire   : AnneeScolaireST [obligatoire]
├── etabId          : EtabIdST        [obligatoire]
├── implId          : ImplIdST        [0..1]
├── numAdmFormation : int             [obligatoire]
└── numOrganisation : int             [obligatoire]
```

> ⚠️ **Divergence PDF/XSD** : le PDF (page 9) indique `implId` comme « obligatoire » dans
> OrganisationResIdCT, mais le XSD déclare `minOccurs="0"`. L'exemple XML de réponse
> (page 12) montre bien `implId` renseigné. **Recommandation** : traiter comme optionnel
> côté parsing (confiance au XSD), mais s'attendre à le recevoir systématiquement.

---

## Opération 1 : LireDocument1

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1/v1/LireDocument1`

### Requête

**Élément** : `LireDocument1` → **Type** : `LireDocument1RequeteCT` extends `FormationDocument1LireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex: `"2016-2017"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse).

### Réponse

**Élément** : `LireDocument1Reponse` → **Type** : `Document1ReponseCT` extends `AbstractExternalResponseType`

```
Document1ReponseCT
├── success         : boolean                   [obligatoire] (hérité)
├── messages        : messagesType              [0..1]        (hérité)
└── response        : Document1ReponseMetierCT  [0..1]
    └── document1   : FormationDocument1CT      [obligatoire]
        ├── id              : OrganisationResIdCT              [obligatoire]
        └── populationListe : PopDocument1AnneeEtudeLstCT      [0..1]
            └── population  : PopDocument1AnneeEtudeLineCT     [1..*]
```

### PopDocument1AnneeEtudeLineCT (ligne de population — réponse)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coAnnEtude` | int | oui | Code de l'année d'étude |
| `nbEleveA` | int | oui | Nombre d'élèves de type A |
| `nbEleveEhr` | int | oui | Nombre d'élèves en horaire réduit |
| `nbEleveFse` | int | oui | Nombre d'élèves FSE (**n'est plus utilisé**) |
| `nbElevePi` | int | oui | Nombre d'élèves en parcours d'insertion (**n'est plus utilisé**) |
| `nbEleveB` | int | oui | Nombre d'élèves de type B |
| `nbEleveTot2a5` | int | oui | Somme des élèves A, Ehr, Fse, Pi et B |
| `nbEleveDem` | int | oui | Nombre d'élèves demandeurs d'emploi |
| `nbEleveMin` | int | oui | Nombre d'élèves minimexés |
| `nbEleveExm` | int | oui | Nombre d'élèves (non minimexés, non chômeur) exemptés |
| `nbElevePl` | int | oui | Nombre d'élèves comptés plusieurs fois |
| `nbEleveTot6et8` | int | oui | Somme des élèves A, Ehr, Fse, Pi, B et comptés plusieurs fois |
| `nbEleveTotFse` | int | oui | Nombre total d'élèves FSE (**n'est plus utilisé**) |
| `nbEleveTotPi` | int | oui | Nombre total d'élèves en parcours d'insertion (**n'est plus utilisé**) |
| `nbEleveTotHom` | int | oui | Nombre d'élèves de sexe masculin |
| `nbEleveTotFem` | int | oui | Nombre d'élèves de sexe féminin |
| `swAppPopD1` | boolean | oui | Document approuvé par l'école ou le PO |
| `swAppD1` | boolean | oui | Document approuvé par l'administration |
| `tsMaj` | string | oui | Date de la dernière modification (format: `2017-03-06 12:21:06.562526`) |
| `teUserMaj` | string | oui | Dernier utilisateur à avoir modifié le document |

> **Note** : 4 champs marqués « n'est plus utilisé » (`nbEleveFse`, `nbElevePi`, `nbEleveTotFse`,
> `nbEleveTotPi`) sont toujours présents dans la réponse (valeurs à 0 ou historiques), mais ne
> doivent plus être renseignés en entrée. Ils ne figurent **pas** dans le type Save (requête).

> **Formules de contrôle** (déduites des codes d'erreur) :
> - `nbEleveTot2a5` = `nbEleveA` + `nbEleveEhr` + `nbEleveFse` + `nbElevePi` + `nbEleveB`
> - `nbEleveTot6et8` = `nbEleveTot2a5` + `nbElevePl`
> - `nbEleveTotHom` + `nbEleveTotFem` = `nbEleveTot6et8` (erreur 4011)
> - `nbEleveDem` ≤ `nbElevePl` (erreur 4004)
> - `nbEleveExm` ≤ `nbElevePl` (erreurs 4005, 4012)
> - `nbEleveMin` ≤ `nbElevePl` (erreur 4008)
> - `nbEleveTotHom` ≤ `nbEleveTot6et8` (erreur 4009)
> - `nbEleveTotFem` ≤ `nbEleveTot6et8` (erreur 4010)

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:LireDocument1>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>10</v12:numOrganisation>
      </v11:id>
    </v1:LireDocument1>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (simplifié, endpoint spécifique EPROM)

```xml
<LireDocument1Reponse xmlns="http://services-web.etnic.be/eprom/formation/document1/messages/v1">
  <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
  <response>
    <p366:document1 xmlns:p366="http://enseignement.cfwb.be/types/formation/document1/v1">
      <p366:id>
        <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2016-2017</p752:anneeScolaire>
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">41</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">66</p752:implId>
        <p752:numAdmFormation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">44</p752:numAdmFormation>
        <p752:numOrganisation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">10</p752:numOrganisation>
      </p366:id>
      <p366:populationListe>
        <p366:population>
          <p366:coAnnEtude>1</p366:coAnnEtude>
          <p366:nbEleveA>9</p366:nbEleveA>
          <p366:nbEleveEhr>1</p366:nbEleveEhr>
          <p366:nbEleveFse>1</p366:nbEleveFse>
          <p366:nbElevePi>1</p366:nbElevePi>
          <p366:nbEleveB>10</p366:nbEleveB>
          <p366:nbEleveTot2a5>22</p366:nbEleveTot2a5>
          <p366:nbEleveDem>10</p366:nbEleveDem>
          <p366:nbEleveMin>1</p366:nbEleveMin>
          <p366:nbEleveExm>1</p366:nbEleveExm>
          <p366:nbElevePl>4</p366:nbElevePl>
          <p366:nbEleveTot6et8>26</p366:nbEleveTot6et8>
          <p366:nbEleveTotFse>10</p366:nbEleveTotFse>
          <p366:nbEleveTotPi>10</p366:nbEleveTotPi>
          <p366:nbEleveTotHom>14</p366:nbEleveTotHom>
          <p366:nbEleveTotFem>12</p366:nbEleveTotFem>
          <p366:swAppPopD1>1</p366:swAppPopD1>
          <p366:swAppD1>0</p366:swAppD1>
          <p366:tsMaj>2017-03-06 12:21:06.562526</p366:tsMaj>
          <p366:teUserMaj>ETNZX</p366:teUserMaj>
        </p366:population>
      </p366:populationListe>
    </p366:document1>
  </response>
</LireDocument1Reponse>
```

> **Observation sur l'exemple** : `swAppPopD1` est sérialisé comme `1`/`0` (et non `true`/`false`)
> bien que le XSD déclare `xs:boolean`. À gérer côté parsing.

---

## Opération 2 : ModifierDocument1

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1/v1/ModifierDocument1`

### Requête

**Élément** : `ModifierDocument1` → **Type** : `ModifierDocument1RequeteCT` extends `FormationDocument1ModifReqCT`

```
ModifierDocument1RequeteCT
├── id              : OrganisationReqIdCT              [obligatoire]
└── populationListe : PopDocument1AnneeEtudeLstSaveCT  [0..1]
    └── population  : PopDocument1AnneeEtudeLineSaveCT  [0..*]
```

### PopDocument1AnneeEtudeLineSaveCT (ligne de population — requête)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coAnnEtude` | int | oui | Code de l'année d'étude |
| `nbEleveA` | int | non | Nombre d'élèves de type A |
| `nbEleveEhr` | int | non | Nombre d'élèves en horaire réduit |
| `nbEleveB` | int | non | Nombre d'élèves de type B |
| `nbEleveDem` | int | non | Nombre d'élèves demandeurs d'emploi |
| `nbEleveMin` | int | non | Nombre d'élèves minimexés |
| `nbEleveExm` | int | non | Nombre d'élèves (non minimexés, non chômeur) exemptés |
| `nbElevePl` | int | non | Nombre d'élèves comptés plusieurs fois |
| `nbEleveTotHom` | int | non | Nombre d'élèves de sexe masculin |
| `nbEleveTotFem` | int | non | Nombre d'élèves de sexe féminin |

> **Différence requête vs réponse** : le type Save a **9 champs** en moins par rapport au type
> de réponse. Les champs absents sont :
> - Les 4 champs obsolètes : `nbEleveFse`, `nbElevePi`, `nbEleveTotFse`, `nbEleveTotPi`
> - Les 2 totaux calculés : `nbEleveTot2a5`, `nbEleveTot6et8`
> - Les 2 switchs d'approbation : `swAppPopD1`, `swAppD1`
> - Les 2 champs audit : `tsMaj`, `teUserMaj`

### Réponse

**Type** : `Document1ReponseCT` (identique à LireDocument1 — même type pour les 3 opérations).

La réponse contient le document 1 complet après modification, incluant les totaux recalculés.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ModifierDocument1>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>10</v12:numOrganisation>
      </v11:id>
      <v11:populationListe>
        <v11:population>
          <v11:coAnnEtude>1</v11:coAnnEtude>
          <v11:nbEleveA>9</v11:nbEleveA>
          <v11:nbEleveEhr>1</v11:nbEleveEhr>
          <v11:nbEleveB>10</v11:nbEleveB>
          <v11:nbEleveDem>10</v11:nbEleveDem>
          <v11:nbEleveMin>1</v11:nbEleveMin>
          <v11:nbEleveExm>1</v11:nbEleveExm>
          <v11:nbElevePl>4</v11:nbElevePl>
          <v11:nbEleveTotHom>14</v11:nbEleveTotHom>
          <v11:nbEleveTotFem>10</v11:nbEleveTotFem>
        </v11:population>
      </v11:populationListe>
    </v1:ModifierDocument1>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Opération 3 : ApprouverDocument1

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1/v1/ApprouverDocument1`

### Description fonctionnelle

Permet d'approuver un document 1. **Quand un document 1 est approuvé, il n'est plus possible
de le modifier** (erreur 1545).

L'utilisateur envoie les données d'identification ainsi que les populations **afin de vérifier
que les données n'ont pas été modifiées entre la dernière consultation et l'approbation**.

### Requête

**Élément** : `ApprouverDocument1` → **Type** : `ApprouverDocument1RequeteCT` extends `FormationDocument1ApprReqCT`

```
ApprouverDocument1RequeteCT
├── id              : OrganisationReqIdCT              [obligatoire]
└── populationListe : PopDocument1AnneeEtudeLstSaveCT  [0..1]
    └── population  : PopDocument1AnneeEtudeLineSaveCT  [0..*]
```

> Structure identique à ModifierDocument1. Les données de population sont envoyées pour
> contrôle d'intégrité (vérification d'absence de modification concurrente).

### Réponse

**Type** : `Document1ReponseCT` (identique à LireDocument1 et ModifierDocument1).

> **Observation (diagramme UML page 19)** : le diagramme nomme le type de réponse
> `ApprouverDocument1ReponseCT` avec un sous-élément `(responseType)` contenant
> `document1 : FormationDocument1CT`. En réalité, le XSD utilise le type partagé
> `Document1ReponseCT` → `Document1ReponseMetierCT` pour les 3 opérations. **Divergence
> de nommage dans le diagramme uniquement**, pas d'impact fonctionnel.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ApprouverDocument1>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>10</v12:numOrganisation>
      </v11:id>
      <v11:populationListe>
        <v11:population>
          <v11:coAnnEtude>1</v11:coAnnEtude>
          <v11:nbEleveA>9</v11:nbEleveA>
          <v11:nbEleveEhr>1</v11:nbEleveEhr>
          <v11:nbEleveB>10</v11:nbEleveB>
          <v11:nbEleveDem>10</v11:nbEleveDem>
          <v11:nbEleveMin>1</v11:nbEleveMin>
          <v11:nbEleveExm>1</v11:nbEleveExm>
          <v11:nbElevePl>4</v11:nbElevePl>
          <v11:nbEleveTotHom>14</v11:nbEleveTotHom>
          <v11:nbEleveTotFem>10</v11:nbEleveTotFem>
        </v11:population>
      </v11:populationListe>
    </v1:ApprouverDocument1>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Codes d'erreur spécifiques

| Success | Code | Description | Opérations |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | toutes |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | Lire |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | Modifier, Approuver |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | toutes |
| `false` | `00999` | Erreur sql | toutes |
| `false` | `1114` | Numéro d'établissement incorrect | toutes |
| `false` | `1113` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | toutes |
| `false` | `2106` | Le code Année d'études de la population scolaire est incorrect | Modifier, Approuver |
| `false` | `4004` | Nombre de demandeurs d'emploi > nb d'élèves comptés 1 fois | Modifier, Approuver |
| `false` | `4005` | Nombre d'exemptés > au nb d'élèves comptés 1 fois | Modifier, Approuver |
| `false` | `4006` | Nombre total FSE travailleurs > nb total d'élèves | Modifier, Approuver |
| `false` | `4007` | Nombre total FSE PI > nb total d'élèves | Modifier, Approuver |
| `false` | `4008` | Nombre de minimexés > au nb d'élèves comptés 1 fois | Modifier, Approuver |
| `false` | `4009` | Nombre total Hommes > nb total d'élèves | Modifier, Approuver |
| `false` | `4010` | Nombre total Femmes > nb total d'élèves | Modifier, Approuver |
| `false` | `4011` | Total Hommes + Femmes <> nombre total d'élèves | Modifier, Approuver |
| `false` | `4012` | Nombre d'exemptés > nb d'élèves comptés 1 fois | Modifier, Approuver |
| `false` | `1545` | Le "Doc 1" est approuvé et ne peut plus être modifié | Modifier |
| `false` | `1530` | Mise à jour impossible; ce document est déjà approuvé par l'administration ! | Approuver |
| `false` | `99999` | Autres erreurs | toutes |

> **Codes partagés avec d'autres services** : `00009`, `00025`, `00999` sont communs à tous
> les services EPROM. Les codes `1114` et `1113` remplacent les `30001` et `30007` des sessions
> précédentes — même sémantique, codes différents.

---

## Vérification croisée UML / XSD / PDF

### Diagramme page 7 (requête LireDocument1)
- ✅ `FormationDocument1LireReqCT` → `id : OrganisationReqIdCT` — conforme au XSD
- ✅ `OrganisationReqIdCT` : 4 champs (anneeScolaire, etabId, numAdmFormation, numOrganisation) — conforme

### Diagramme page 8 (réponse LireDocument1)
- ✅ Structure d'héritage `AbstractExternalResponseType` → `Document1ReponseCT` — conforme
- ✅ `Document1ReponseMetierCT` → `document1 : FormationDocument1CT` — conforme
- ✅ `FormationDocument1CT` : `id` + `populationListe` — conforme
- ✅ `OrganisationResIdCT` : 5 champs dont `implId [0..1]` — conforme au XSD
- ⚠️ PDF texte (page 9) dit `implId` « obligatoire » vs XSD `minOccurs="0"` — **divergence**

### Diagramme page 9 (PopDocument1AnneeEtudeLineCT)
- ✅ 20 champs listés dans le diagramme — tous confirmés dans le XSD
- ✅ Tous les champs sont `xs:int` ou `xs:boolean` ou `xs:string` — conforme

### Diagramme page 13 (requête ModifierDocument1)
- ✅ `FormationDocument1ModifReqCT` : `id` + `populationListe [0..1]` — conforme
- ✅ `PopDocument1AnneeEtudeLineSaveCT` : 9 champs facultatifs + `coAnnEtude` obligatoire — conforme

### Diagramme page 15 (réponse ModifierDocument1)
- ✅ Structure identique à la réponse LireDocument1 — conforme

### Diagramme page 18 (requête ApprouverDocument1)
- ✅ Structure identique à ModifierDocument1 — conforme au XSD (`FormationDocument1ApprReqCT` = même structure)

### Diagramme page 19 (réponse ApprouverDocument1)
- ⚠️ Le diagramme nomme le type `ApprouverDocument1ReponseCT` avec sous-élément `(responseType)`.
  Le XSD utilise `Document1ReponseCT` (type partagé) → `Document1ReponseMetierCT`. **Divergence de nommage uniquement**.

---

## Mapping pyetnic

### Classe proposée : `FormationPopulationService`

```python
class FormationPopulationService:
    """Service EPROM Formation Population (Document 1) v1.0"""

    WSDL = "EpromFormationDocument1Service_external_v1.wsdl"
    ENDPOINT_TQ = "https://ws-tq.etnic.be/eprom/formation/document1/v1"
    ENDPOINT_PROD = "https://ws.etnic.be/eprom/formation/document1/v1"

    def lire(self, annee_scolaire: str, etab_id: int,
             num_adm_formation: int, num_organisation: int) -> Document1Response:
        """LireDocument1 — lecture du document population"""

    def modifier(self, annee_scolaire: str, etab_id: int,
                 num_adm_formation: int, num_organisation: int,
                 populations: list[PopulationLine] | None = None) -> Document1Response:
        """ModifierDocument1 — modification des données population"""

    def approuver(self, annee_scolaire: str, etab_id: int,
                  num_adm_formation: int, num_organisation: int,
                  populations: list[PopulationLine] | None = None) -> Document1Response:
        """ApprouverDocument1 — approbation (irréversible)"""
```

### Dataclass proposée : `PopulationLine`

```python
@dataclass
class PopulationLine:
    """Ligne de population par année d'étude (type Save)"""
    co_ann_etude: int
    nb_eleve_a: int | None = None
    nb_eleve_ehr: int | None = None
    nb_eleve_b: int | None = None
    nb_eleve_dem: int | None = None
    nb_eleve_min: int | None = None
    nb_eleve_exm: int | None = None
    nb_eleve_pl: int | None = None
    nb_eleve_tot_hom: int | None = None
    nb_eleve_tot_fem: int | None = None
```

### Dataclass proposée : `PopulationLineResponse`

```python
@dataclass
class PopulationLineResponse:
    """Ligne de population par année d'étude (type réponse, 20 champs)"""
    co_ann_etude: int
    nb_eleve_a: int
    nb_eleve_ehr: int
    nb_eleve_fse: int          # obsolète
    nb_eleve_pi: int           # obsolète
    nb_eleve_b: int
    nb_eleve_tot_2a5: int      # calculé
    nb_eleve_dem: int
    nb_eleve_min: int
    nb_eleve_exm: int
    nb_eleve_pl: int
    nb_eleve_tot_6et8: int     # calculé
    nb_eleve_tot_fse: int      # obsolète
    nb_eleve_tot_pi: int       # obsolète
    nb_eleve_tot_hom: int
    nb_eleve_tot_fem: int
    sw_app_pop_d1: bool
    sw_app_d1: bool
    ts_maj: str
    te_user_maj: str
```

---

## XSD utilisés

| Fichier XSD | Identique aux sessions 1-2 ? |
|---|---|
| `Organisation_v1.xsd` | **NOUVEAU** — à ajouter au registre |
| `Common_v1.xsd` | ✅ identique (même que Formations Liste v2) |
| `AnneeScolaire_v1.xsd` | ✅ identique |
| `Etablissement_v1.xsd` | ✅ identique |
| `ResponseStatus_v3.xsd` | ✅ identique |
| `requestId_v1.xsd` | ✅ identique |
| `Addressing_v2.xsd` | ✅ identique (endpoint générique Ecole) |
| `Authorisation_v2.xsd` | ✅ identique (endpoint générique Ecole) |
