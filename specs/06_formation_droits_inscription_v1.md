# EPROM — Formation Droits d'Inscription (Document 1D) v1.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationDocument1DService_external_v1.wsdl` + PDF Manuel d'utilisation rev1.1 (01-05-2023, édité 10-05-2023, 23 pages)
> Date d'analyse : 2026-06-02 (session 5)

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | FormationDocument1D (Droits d'Inscription) |
| Version service | 1.0.0 |
| Révision document | 1.1 (01-05-2023) |
| Version XSD `FormationDocument1D_v1.xsd` | 1.0 |
| Version XSD `Organisation_v1.xsd` | 2.0 (identique sessions 3/4) |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | **SOAP 1.1 uniquement** |
| Sécurité | WS-Security : certificat X.509 **ou** login / mot de passe |
| Transport | TLS 1.0 ou TLS 1.2 |
| WSDL namespace (`tns`) | `http://services-web.etnic.be/eprom/formation/document1D/v1` |
| Messages namespace (`eprom`) | `http://services-web.etnic.be/eprom/formation/document1D/messages/v1` |
| Types namespace (`doc1D`) | `http://enseignement.cfwb.be/types/formation/document1D/v1` |
| Types namespace (`org`) | `http://enseignement.cfwb.be/types/organisation/v1` |
| Binding spécifique EPROM | `EPROMFormationDocument1DExternalV1Binding` (document/literal) |
| Binding générique Ecole (déprécié) | `FormationDocument1DBinding` (cité par le PDF §2.2.2, **absent du WSDL externe fourni**) |
| WSDL service | `service_eprom_formation_document1D_external_v1` |
| WSDL port | `EPROMFormationDocument1DExternalV1Port` |

> **« Document 1D » = nom interne du service Droits d'Inscription.** Le WSDL, les XSD et le manuel
> utilisent systématiquement le radical `Document1D` / `Doc 1D`. Le « D » signifie vraisemblablement
> « Droits » : c'est le pendant « droits d'inscription » de la famille Document 1 (Population). Le service
> gère **deux choses liées** : la *population scolaire au 5/10ᵉ de la formation* (`nbEleves5ieme`) **et**
> les *montants des droits d'inscription* (`mtDroitsInscription`).

> **SOAP 1.1 confirmé deux fois** : (1) le binding du WSDL utilise exclusivement l'espace de noms
> `http://schemas.xmlsoap.org/wsdl/soap/` (SOAP 1.1) — il n'y a **pas** de binding `soap12/` ;
> (2) le PDF (§2.2) indique « Le service EPROM FormationDocument1D est compatible avec le protocole SOAP 1.1 ».
> Même situation que le Document 3 ; différence avec Formation Organisation v7 (SOAP 1.1 **ou** 1.2).

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL + PDF | `https://ws-tq.etnic.be/eprom/formation/document1D/v1` |
| PROD | PDF | `https://ws.etnic.be/eprom/formation/document1D/v1` |

> Le WSDL externe ne déclare que l'adresse TQ (`<soap:address location="https://ws-tq.etnic.be/eprom/formation/document1D/v1"/>`) ;
> l'URL PROD provient du PDF (§2.2.1).
>
> **Endpoint générique « Ecole »** (déprécié) :
> - TQ : `https://ws-tq.etnic.be/ecole`
> - PROD : `https://ws.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument1DV1?mode=sync`, To = `http://services-web.etnic.be/eprom`
> - (dans les exemples de réponse du PDF, l'`Action` est écrite `eprom:formationDocument1DV1?mode=sync` —
>   `f` minuscule ; même incohérence de casse qu'au Document 3, à confirmer côté plateforme)
>
> Le endpoint spécifique EPROM **ne requiert pas** de WS-Addressing. Il a été ajouté en rev 1.1 (2023) en
> même temps que TLS 1.2 ; auparavant seul le endpoint générique `/ecole` existait.

---

## Description fonctionnelle

Le service EPROM FormationDocument1D permet à l'école de **gérer les informations relatives à la
population scolaire au 5/10ᵉ de la formation et aux montants des droits d'inscription** (Doc 1D)
sauvegardés dans EPROM.

Deux notions distinctes mais liées sont portées par le même document, **par année d'études** :

1. **`nbEleves5ieme`** — le **nombre d'élèves comptabilisés au 5/10ᵉ** (mi-parcours) de la formation.
   C'est le comptage de référence qui sert de base au calcul de financement / des droits.
2. **`mtDroitsInscription`** — le **montant des droits d'inscription** correspondant.

Il expose **3 opérations** (comme le Document 1 / Population — avec une opération d'approbation) :

1. **LireDocument1D** — fournit les informations du document 1D.
2. **ModifierDocument1D** — modifie les données du document 1D (population au 5/10ᵉ et/ou montants).
3. **ApprouverDocument1D** — approuve (côté école/PO) la population au 5/10ᵉ du document 1D.

> **Différence avec Doc 2 et Doc 3** : ces derniers n'ont que Lire + Modifier. Doc 1D **et** Doc 1
> (Population) possèdent en plus une opération `Approuver`.

### Modèle de données (hiérarchie)

```
Document 1D (1 organisation de formation)
└── droitInscriptionListe
    └── droitInscription (0..N lignes, une par année d'études)
        ├── coAnnEtude                       (code année d'études — clé de ligne)
        ├── nbEleves5ieme                    (population au 5/10ᵉ)
        ├── mtDroitsInscription              (montant des droits)
        ├── mtDroitsInscriptionOccupationnel (⚠️ « n'est plus utilisé »)
        ├── swAppPopD1D                      (approuvé école/PO)
        ├── swAppD1D                         (approuvé administration)
        ├── tsMaj                            (timestamp dernière MAJ)
        └── teUserMaj                        (userid dernière MAJ)
```

> **Deux switches d'approbation** dans la ligne de réponse — structure **parallèle au Document 1**
> (`swAppPopD1` + `swAppD1`), avec le suffixe « D » :
> - `swAppPopD1D` : population au 5/10ᵉ approuvée par l'**école / le PO**.
> - `swAppD1D` : document approuvé par l'**administration**.

> **`mtDroitsInscriptionOccupationnel`** : présent en réponse (obligatoire au XSD) mais **« n'est plus
> utilisé »** (PDF §3.1.3.4). Absent des lignes de requête (Modifier / Approuver). Le client peut le lire
> mais ne doit pas s'en servir ; en pratique il vaut `0.0` dans les exemples.

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> Pattern **Common_v1** (ancien), identique à Population (Doc 1), Périodes (Doc 2), Attributions (Doc 3)
> et Formations Liste v2. Le `Messages` XSD importe bien `common:AbstractExternalResponseType`.

```
AbstractExternalResponseType (abstract)
├── success  : boolean       [obligatoire]
└── messages : messagesType  [0..1]
    ├── error   : MessageType [0..*]   (code [≤10c] + description + zone)
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```

Le `requestId` (UUID) est porté par un **header SOAP** : optionnel en requête, obligatoire en réponse
(endpoint EPROM). S'il n'est pas fourni, l'ETNIC en génère un.

> Le type de réponse `Document1DReponseCT` est **partagé par les 3 opérations** (Lire, Modifier,
> Approuver) : il étend `AbstractExternalResponseType` et ajoute `response` (`Document1DReponseMetierCT`,
> `[0..1]`). Toutes les opérations renvoient donc le document 1D complet après traitement.

---

## Opération 1 : LireDocument1D

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1D/v1/LireDocument1D`

### Requête

**Élément** : `LireDocument1D` → **Type** : `LireDocument1DRequeteCT` extends `FormationDocument1DLireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex : `"2016-2017"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

> `OrganisationReqIdCT` ne contient **pas** d'`implId` (identique aux Documents 1, 2 et 3). Voir `00_REGISTRE.md`.

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse).

### Réponse

**Élément** : `LireDocument1DReponse` → **Type XSD** : `Document1DReponseCT` extends `AbstractExternalResponseType`

> Le PDF nomme ce type `LireDocument1DReponseCT`, mais le XSD `Messages` utilise un **type unique partagé
> `Document1DReponseCT`** pour les réponses des trois opérations.

```
Document1DReponseCT
├── success    : boolean                 [obligatoire] (hérité)
├── messages   : messagesType            [0..1]        (hérité)
└── response   : Document1DReponseMetierCT [0..1]
    └── document1D : FormationDocument1DCT  [obligatoire]
```

### FormationDocument1DCT (structure du document 1D)

```
FormationDocument1DCT
├── id                   : OrganisationResIdCT       [obligatoire]   (avec implId [0..1])
└── droitInscriptionListe : Doc1DDroitInscriptionLstCT [obligatoire au XSD / « facultatif » au PDF ⚠️]
    └── droitInscription : Doc1DDroitInscriptionLineCT [0..*]
```

> ⚠️ **Divergence de cardinalité (`droitInscriptionListe`)** : au XSD, `droitInscriptionListe` est un
> élément **obligatoire** de `FormationDocument1DCT` (pas de `minOccurs="0"`), alors que le PDF (§3.1.3.4)
> l'annote « facultatif ». La liste *interne* `droitInscription` est bien `[0..*]`. Interprétation sûre :
> l'élément conteneur est toujours présent, éventuellement vide.

### Doc1DDroitInscriptionLineCT (ligne par année d'études — réponse, 8 champs)

| Champ | Type (XSD) | Card. (XSD) | PDF (texte) | Description |
|---|---|---|---|---|
| `coAnnEtude` | **string** | obligatoire | « int » ⚠️ | Code de l'année d'études (clé de ligne) |
| `nbEleves5ieme` | int | obligatoire | int | Nombre d'élèves au 5/10ᵉ |
| `mtDroitsInscription` | float | obligatoire | float | Montant des droits d'inscription |
| `mtDroitsInscriptionOccupationnel` | float | obligatoire | float | Montant occupationnel — **« n'est plus utilisé »** |
| `swAppPopD1D` | boolean | obligatoire | boolean | Approuvé (école / PO) |
| `swAppD1D` | boolean | obligatoire | boolean | Approuvé par l'administration |
| `tsMaj` | **string** | obligatoire | « boolean » ⚠️ | Date/heure de dernière modification |
| `teUserMaj` | **string** | obligatoire | « boolean » ⚠️ | Userid de dernière modification |

> ⚠️ **Coquilles de typage dans le texte du PDF** (résolues par le diagramme UML + le XSD, qui concordent) :
> - `coAnnEtude` : le texte dit « int », mais le **diagramme UML (p.9) et le XSD disent `string`** → c'est
>   un `string`. Les exemples (`<coAnnEtude>1</…>`) sont compatibles avec les deux, mais le contrat est `string`.
> - `tsMaj` et `teUserMaj` : le texte les annote « boolean », mais le **diagramme UML et le XSD disent
>   `string`** (et les exemples montrent un timestamp `2017-03-07 16:18:19.406491` et un userid). → ce sont des `string`.

> **Booléens sérialisés `0`/`1`** : dans les exemples de réponse, `swAppPopD1D`/`swAppD1D` valent `1` ou `0`
> (et non `true`/`false`). zeep mappe `xs:boolean` et accepte `0`/`1` → pas de souci, mais à garder en tête.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1D/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1D/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:LireDocument1D>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>5</v12:numOrganisation>
      </v11:id>
    </v1:LireDocument1D>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (corps métier, 1 ligne)

```xml
<LireDocument1DReponse xmlns="http://services-web.etnic.be/eprom/formation/document1D/messages/v1">
  <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
  <response>
    <p590:document1D xmlns:p590="http://enseignement.cfwb.be/types/formation/document1D/v1">
      <p590:id>
        <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2016-2017</p752:anneeScolaire>
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">41</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">66</p752:implId>
        <p752:numAdmFormation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">44</p752:numAdmFormation>
        <p752:numOrganisation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">5</p752:numOrganisation>
      </p590:id>
      <p590:droitInscriptionListe>
        <p590:droitInscription>
          <p590:coAnnEtude>1</p590:coAnnEtude>
          <p590:nbEleves5ieme>0</p590:nbEleves5ieme>
          <p590:mtDroitsInscription>444719.0</p590:mtDroitsInscription>
          <p590:mtDroitsInscriptionOccupationnel>0.0</p590:mtDroitsInscriptionOccupationnel>
          <p590:swAppPopD1D>1</p590:swAppPopD1D>
          <p590:swAppD1D>1</p590:swAppD1D>
          <p590:tsMaj>2017-03-07 16:18:19.406491</p590:tsMaj>
          <p590:teUserMaj/>
        </p590:droitInscription>
      </p590:droitInscriptionListe>
    </p590:document1D>
  </response>
</LireDocument1DReponse>
```

> Ici les deux switches valent `1` (document entièrement approuvé). `teUserMaj` est vide. `mtDroitsInscription`
> vaut `444719.0` (valeur d'exemple). Le `success` est, comme pour les autres services, dans le namespace
> `ResponseStatus/v3` même si l'élément racine est dans le namespace `messages/v1`.

---

## Opération 2 : ModifierDocument1D

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1D/v1/ModifierDocument1D`

### Description fonctionnelle (règle métier essentielle)

> **Fenêtres de modification (PDF §3.1.4.1)** — règle centrale du service :
> « Le nombre d'élèves n'est modifiable **que jusqu'à l'approbation** de la population au 5ᵉ/10ᵉ par
> l'école et/ou le PO ; et les droits d'inscription ne sont modifiables **qu'après l'approbation** de la
> population au 5ᵉ/10ᵉ par l'école et/ou le PO. »

Autrement dit, le cycle de vie d'une ligne est en **deux phases**, pivotant sur `swAppPopD1D` :

| Phase | `swAppPopD1D` | `nbEleves5ieme` | `mtDroitsInscription` |
|---|---|---|---|
| Avant approbation population | `0` | **modifiable** | **figé** (erreur `1546` si tenté) |
| Après approbation population | `1` | **figé** | **modifiable** |
| Après approbation administration (`swAppD1D=1`) | `1` | figé | figé (erreur `1530` si tenté) |

### Requête

**Élément** : `ModifierDocument1D` → **Type** : `ModifierDocument1DRequeteCT` extends `FormationDocument1DModifReqCT`

```
FormationDocument1DModifReqCT
├── id                    : OrganisationReqIdCT          [obligatoire]
└── droitInscriptionListe : Doc1DDroitInscriptionSaveLstCT [obligatoire au XSD / « facultatif » au PDF ⚠️]
    └── droitInscription  : Doc1DDroitInscriptionSaveLineCT [0..*]
```

### Doc1DDroitInscriptionSaveLineCT (ligne — requête Modifier, 3 champs)

| Champ | Type (XSD) | Card. (XSD) | PDF | Description |
|---|---|---|---|---|
| `coAnnEtude` | **string** | obligatoire | « int », obligatoire | Code de l'année d'études (cible la ligne à modifier) |
| `nbEleves5ieme` | int | [0..1] | facultatif | Nombre d'élèves au 5/10ᵉ (avant approbation population) |
| `mtDroitsInscription` | float | [0..1] | facultatif | Montant des droits (après approbation population) |

> Le diagramme UML (p.13) confirme `coAnnEtude:string` (sans annotation = obligatoire), `nbEleves5ieme [0..1] int`,
> `mtDroitsInscription [0..1] float`. **Aucune divergence de cardinalité** ici (texte ↔ XSD ↔ UML concordent),
> seule subsiste la coquille `int` vs `string` sur `coAnnEtude`.

> **On ne renvoie que ce qu'on modifie** : la ligne Save ne porte ni `mtDroitsInscriptionOccupationnel`, ni
> les switches, ni `tsMaj`/`teUserMaj` (champs en lecture seule / gérés serveur). Pour cibler une ligne, on
> envoie son `coAnnEtude` puis le(s) champ(s) à mettre à jour.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1D/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1D/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ModifierDocument1D>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>4</v12:numOrganisation>
      </v11:id>
      <v11:droitInscriptionListe>
        <v11:droitInscription>
          <v11:coAnnEtude>1</v11:coAnnEtude>
          <v11:mtDroitsInscription>20</v11:mtDroitsInscription>
        </v11:droitInscription>
      </v11:droitInscriptionListe>
    </v1:ModifierDocument1D>
  </soapenv:Body>
</soapenv:Envelope>
```

> Cet exemple ne modifie **que** `mtDroitsInscription` (la population n'est pas renvoyée). C'est cohérent
> avec la phase « après approbation population » : on ajuste le montant. La réponse (page 17) renvoie alors
> `mtDroitsInscription=20.0`, `swAppPopD1D=1`, `swAppD1D=0`.

### Réponse

**Type** : `Document1DReponseCT` (identique à LireDocument1D — type partagé). Renvoie le document 1D complet
après modification.

---

## Opération 3 : ApprouverDocument1D

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1D/v1/ApprouverDocument1D`

### Description fonctionnelle

> « Cette fonctionnalité permet d'approuver un document 1D. Quand un document 1D est approuvé, **il n'est
> plus possible de modifier la population au 5ᵉ/10ᵉ** » (PDF §3.1.5.1). C'est l'approbation **école/PO** de
> la population, qui positionne `swAppPopD1D=1` et fait basculer la ligne en phase 2 (montants modifiables).

L'utilisateur renvoie, par année d'études, le `nbEleves5ieme` **afin de vérifier que les données n'ont pas
été modifiées entre la dernière consultation et l'approbation** (contrôle de concurrence optimiste → erreur
`00011` si écart).

### Requête

**Élément** : `ApprouverDocument1D` → **Type** : `ApprouverDocument1DRequeteCT` extends `FormationDocument1DApprReqCT`

```
FormationDocument1DApprReqCT
├── id                    : OrganisationReqIdCT          [obligatoire]
└── droitInscriptionListe : Doc1DDroitInscriptionApprLstCT [obligatoire au XSD / « facultatif » au PDF ⚠️]
    └── droitInscription  : Doc1DDroitInscriptionApprLineCT [0..*]
```

### Doc1DDroitInscriptionApprLineCT (ligne — requête Approuver, 2 champs)

| Champ | Type (XSD) | Card. (XSD) | PDF (texte) | Description |
|---|---|---|---|---|
| `coAnnEtude` | **string** | obligatoire | « int », obligatoire | Code de l'année d'études |
| `nbEleves5ieme` | int | **obligatoire** | « facultatif » ⚠️ | Nombre d'élèves au 5/10ᵉ (vérification anti-concurrence) |

> ⚠️ **Divergence de cardinalité (`nbEleves5ieme` en Approuver)** : le texte du PDF dit « facultatif », mais
> le **XSD ET le diagramme UML (p.18) le rendent obligatoire** (aucun `[0..1]`). Comme la valeur sert à
> détecter une modification concurrente, l'interprétation **XSD (obligatoire) est la plus sûre** : toujours
> fournir le `nbEleves5ieme` lu lors du dernier `LireDocument1D`.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document1D/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document1D/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ApprouverDocument1D>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>8</v12:numOrganisation>
      </v11:id>
      <v11:droitInscriptionListe>
        <v11:droitInscription>
          <v11:coAnnEtude>1</v11:coAnnEtude>
          <v11:nbEleves5ieme>4</v11:nbEleves5ieme>
        </v11:droitInscription>
      </v11:droitInscriptionListe>
    </v1:ApprouverDocument1D>
  </soapenv:Body>
</soapenv:Envelope>
```

> Dans l'exemple de réponse (page 22), après approbation : `swAppPopD1D=1`, `swAppD1D=0` (l'approbation
> école/PO est posée, l'approbation administration reste à faire), `nbEleves5ieme=4` confirmé.

### Réponse

**Type** : `Document1DReponseCT` (identique aux autres opérations — type partagé).

---

## Codes d'erreur

Table complète (PDF §4, page 23) :

| Success | Code | Description (libellé exact PDF) | Type |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | — |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | commun |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | commun (concurrence) |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | commun (sécurité) |
| `false` | `00999` | Erreur sql : | commun (technique) |
| `false` | `1114` | Matricule école inexistant | validation entrée |
| `false` | `1113` | Année Scolaire invalide | validation entrée |
| `false` | `2106` | Année d'étude invalide. | validation entrée |
| `false` | `1545` | Document déjà approuvé ! | workflow approbation |
| `false` | `1546` | Document non encore approuvé ! | workflow approbation |
| `false` | `1530` | Mise à jour impossible; ce document est déjà approuvé par l'administration ! | workflow approbation |
| `false` | `99999` | (Autres Erreurs) | fourre-tout |

### Mapping erreurs ↔ workflow (interprétation)

Le PDF ne précise pas l'opération déclenchant chaque code ; mapping le plus cohérent avec la règle métier :

- `1546` « Document non encore approuvé ! » → `ModifierDocument1D` tentant d'écrire `mtDroitsInscription`
  **alors que `swAppPopD1D=0`** (la population n'a pas encore été approuvée par l'école/PO).
- `1545` « Document déjà approuvé ! » → `ApprouverDocument1D` sur un document déjà approuvé (école/PO), ou
  `ModifierDocument1D` tentant de modifier `nbEleves5ieme` après l'approbation population.
- `1530` « … déjà approuvé par l'administration ! » → toute `ModifierDocument1D` après `swAppD1D=1`
  (verrou final administration).
- `00011` → écart entre le `nbEleves5ieme` envoyé en approbation et la valeur serveur (concurrence).

### ⚠️ Réutilisation de codes entre services (attention typage d'exceptions)

Les codes numériques **ne sont pas universels** : un même code a un libellé différent selon le service.

| Code | Doc 1D (ce service) | Doc 1 / Doc 2 (sessions 3) |
|---|---|---|
| `1545` | **Document déjà approuvé !** | Doc 1 approuvé / max 5 interventions extérieures |
| `1114` | **Matricule école inexistant** | Numéro d'établissement incorrect |
| `2106` | **Année d'étude invalide** | Code Année d'études de la population scolaire incorrect |
| `1530` | … déjà approuvé par l'administration | … déjà approuvé par l'administration *(idem)* |

> **Implication pyetnic** : les exceptions typées doivent être **indexées par (service, code)** et non par
> code seul. `1545` et `1114` n'ont pas le même sens ici qu'au Document 1/2.

### Codes partagés / spécifiques
- **Communs à tous les services EPROM** : `00009`, `00025`, `00999`, `99999`.
- **Communs Documents** : `00011`, `1113`, `1114`, `2106`.
- **Spécifiques workflow Doc 1D** : `1545`, `1546`, `1530`.

---

## Règles métier & workflow

### Cycle de vie d'un document 1D (intra-document)

```
   (encodage)                 ApprouverDocument1D            (approbation admin,
   nbEleves5ieme              (école / PO)                    hors de ce service)
   modifiable        ──────────────────────────►  swAppPopD1D=1  ──────────────►  swAppD1D=1
   swAppPopD1D=0                                   nbEleves5ieme FIGÉ              tout FIGÉ
   mtDroits FIGÉ                                   mtDroits modifiable            (erreur 1530)
   (erreur 1546)
```

- **Phase 1** : l'école encode/corrige `nbEleves5ieme` (population au 5/10ᵉ). Les montants sont refusés (`1546`).
- **Bascule** : `ApprouverDocument1D` (école/PO) → `swAppPopD1D=1`. La population est figée.
- **Phase 2** : l'école saisit `mtDroitsInscription`. La population n'est plus modifiable.
- **Verrou** : l'administration approuve (`swAppD1D=1`, **non exposé par ce service** — géré côté admin
  comme pour Doc 1/Doc 2). Toute modification ultérieure est refusée (`1530`).

### Place dans le workflow inter-documents (point d'attention)

`statutDocumentDroitsInscription` (vu dans `OrganisationApercuCT` de **Formations Liste v2**) correspond
**exactement à ce service Doc 1D**. La vue résumée d'une organisation expose **quatre** statuts :

| Statut (Formations Liste) | Document(s) interne(s) | Switch(es) d'approbation |
|---|---|---|
| `statutDocumentOrganisation` | Organisation (Form. Organisation v7) | statut `StatutCT` |
| `statutDocumentPopulationPeriodes` | Document 1 (Population) **+** Document 2 (Périodes) | `swAppPopD1`/`swAppD1` + `swAppD2` |
| `statutDocumentDroitsInscription` | **Document 1D (Droits d'Inscription)** ← *ce service* | `swAppPopD1D` + `swAppD1D` |
| `statutDocumentAttributions` | Document 3 (Attributions) | *(aucun switch propre)* |

> **Observation clé** : le Doc 1D possède **son propre statut**, distinct de `PopulationPeriodes`. Les
> valeurs de `StatutCT.statut` (« Encodé école », « Encodé PO », « Approuvé ») projettent l'état des deux
> switches `swAppPopD1D`/`swAppD1D` dans la vue Formations Liste.

> **« Doc A » (erreur `20102` du Doc 3)** : ce manuel **ne mentionne pas « Doc A »** (aucune occurrence).
> L'hypothèse de la session 4 (« Doc A » = Document 1 / Population) reste donc la plus probable et **n'est
> pas remise en cause** par le Doc 1D. La nomenclature interne complète des documents EPROM promotion
> sociale est désormais : **Doc 1** (Population), **Doc 1D** (Droits d'Inscription), **Doc 2** (Périodes),
> **Doc 3** (Attributions), **Doc 8bis** (référencé par le Doc 3). Le mapping littéral de la lettre « A »
> reste à confirmer côté ETNIC.

> **Dépendance amont éventuelle du Doc 1D** : le manuel ne déclare **aucune** erreur de type `20102`
> (« document X doit être approuvé pour accéder »). Le Doc 1D semble donc **gérable indépendamment** des
> autres documents — sa logique d'approbation est purement interne (population → montants). À confirmer en
> session 6 (le `nbEleves5ieme` « au 5/10ᵉ » suppose toutefois qu'une organisation existe et est en cours).

### Notion « population au 5/10ᵉ »

`nbEleves5ieme` = population scolaire comptabilisée **au 5/10ᵉ (mi-parcours) de la formation**. C'est la
photographie de référence qui conditionne les droits d'inscription (financement). À ne pas confondre avec la
« population scolaire » du **Document 1** (Population), qui décrit la ventilation des élèves par année
d'étude en début/cours d'organisation. Doc 1 et Doc 1D portent donc des comptages à des moments différents.

---

## Vérification croisée UML / XSD / PDF

> Méthode (identique session 4) : couche texte native exploitable (`pdftotext -layout`, ~2750 c/page) ;
> rendu image (`pdftoppm`) des pages à boîtes UML repliées : 5, 8, 9, 13, 14, 18. **OCR non nécessaire.**
> Les boîtes UML donnent les **types et cardinalités** ; le **texte** donne les libellés ; le **XSD reste
> la référence contractuelle**.

### Page 9 (réponse — `Doc1DDroitInscriptionLineCT`)
- ✅ Boîte UML : 8 champs avec types `coAnnEtude:string`, `nbEleves5ieme:int`, `mtDroitsInscription:float`,
  `mtDroitsInscriptionOccupationnel:float`, `swAppPopD1D:boolean`, `swAppD1D:boolean`, `tsMaj:string`,
  `teUserMaj:string` — **strictement conforme au XSD**.
- ⚠️ Le **texte** sous le diagramme annote `coAnnEtude` « int » et `tsMaj`/`teUserMaj` « boolean » :
  **coquilles** contredites par l'UML + le XSD (`string`).

### Page 8 (`FormationDocument1DCT`, `OrganisationResIdCT`)
- ✅ `id` + `droitInscriptionListe`. `OrganisationResIdCT` à 5 champs (avec `implId`).
- ⚠️ `implId` : texte « obligatoire » vs XSD `minOccurs="0"` — **même divergence que sessions 3/4** ;
  l'`implId` est toujours présent en pratique (valeur `66` dans les exemples).

### Page 13 (requête Modifier — `Doc1DDroitInscriptionSaveLineCT`)
- ✅ Boîte UML : `coAnnEtude:string` (obligatoire), `nbEleves5ieme [0..1] int`, `mtDroitsInscription [0..1] float`
  — conforme XSD, **pas de divergence de cardinalité**.

### Page 18 (requête Approuver — `Doc1DDroitInscriptionApprLineCT`)
- ✅ Boîte UML : `coAnnEtude:string`, `nbEleves5ieme:int` — **les deux sans `[0..1]` = obligatoires**.
- ⚠️ Le **texte** dit `nbEleves5ieme` « facultatif » → contredit par l'UML + le XSD (obligatoire).

### Récapitulatif des divergences PDF (texte) ↔ XSD/UML

| # | Élément | PDF (texte) | XSD + UML | Reco. client |
|---|---|---|---|---|
| 1 | `coAnnEtude` (toutes lignes) | int | **string** | traiter en `string` |
| 2 | `tsMaj` (réponse) | boolean | **string** | traiter en `string` (timestamp) |
| 3 | `teUserMaj` (réponse) | boolean | **string** | traiter en `string` |
| 4 | `nbEleves5ieme` (Approuver) | facultatif | **obligatoire** | toujours fournir |
| 5 | `droitInscriptionListe` (conteneur) | facultatif | **obligatoire** | toujours présent (peut être vide) |
| 6 | `OrganisationResIdCT.implId` | obligatoire | `minOccurs="0"` | optionnel (XSD), présent en pratique |

> À l'inverse du Document 3, **aucune divergence de *type numérique*** (pas de champ `int` recevant « 24.0 ») :
> ici `nbEleves5ieme` est un vrai `int` (exemples `0`, `4`) et les montants sont des `float` déclarés (`20.0`,
> `444719.0`). Pas de risque de `ValueError` zeep sur ce service.

---

## XSD utilisés

| Fichier XSD | Rôle | Identique session 4 (Doc 3) ? |
|---|---|---|
| `FormationDocument1D_v1.xsd` | **spécifique** (types doc1D, v1.0) | nouveau |
| `EpromFormationDocument1DMessages_external_v1.xsd` | **spécifique** (messages, éléments racine) | nouveau |
| `Organisation_v1.xsd` | partagé (OrganisationReqIdCT / ResIdCT, v2.0) | ✅ byte-for-byte identique |
| `Common_v1.xsd` | partagé (AbstractExternalResponseType) | ✅ byte-for-byte identique |
| `AnneeScolaire_v1.xsd` | partagé | ✅ byte-for-byte identique |
| `Etablissement_v1.xsd` | partagé (EtabIdST, ImplIdST) | ✅ byte-for-byte identique |
| `ResponseStatus_v3.xsd` | partagé (MessageType) | ✅ byte-for-byte identique |
| `requestId_v1.xsd` | partagé (header UUID) | ✅ byte-for-byte identique |
| `Addressing_v2.xsd` | partagé (déprécié, endpoint Ecole) | ✅ byte-for-byte identique |
| `Authorisation_v2.xsd` | partagé (déprécié) | ✅ byte-for-byte identique |

> Vérification par `diff` des 8 XSD partagés entre `contrat_formation_droits_inscription_v1/xsd/` et
> `contrat_document3_v1/xsd/` → **aucune différence**. `Organisation_v1.xsd` est également identique à la
> session 3 (Périodes). Le référentiel technique partagé est donc stable sur les 5 services analysés.

---

## Mapping pyetnic

### Classe proposée : `FormationDocument1DService` (alias métier : Droits d'Inscription)

```python
class FormationDocument1DService:
    """Service EPROM Formation Document 1D (Droits d'Inscription) v1.0 — SOAP 1.1 uniquement.

    Gère, par année d'études : la population scolaire au 5/10e de la formation (nbEleves5ieme)
    et les montants des droits d'inscription (mtDroitsInscription).
    """

    WSDL = "EpromFormationDocument1DService_external_v1.wsdl"
    ENDPOINT_TQ = "https://ws-tq.etnic.be/eprom/formation/document1D/v1"
    ENDPOINT_PROD = "https://ws.etnic.be/eprom/formation/document1D/v1"

    def lire(self, annee_scolaire: str, etab_id: int,
             num_adm_formation: int, num_organisation: int) -> Document1DResponse:
        """LireDocument1D — lecture des droits d'inscription / population au 5/10e."""

    def modifier(self, annee_scolaire: str, etab_id: int,
                 num_adm_formation: int, num_organisation: int,
                 lignes: list[DroitInscriptionSave]) -> Document1DResponse:
        """ModifierDocument1D — MAJ population (avant appro.) et/ou montants (après appro.)."""

    def approuver(self, annee_scolaire: str, etab_id: int,
                  num_adm_formation: int, num_organisation: int,
                  lignes: list[DroitInscriptionAppr]) -> Document1DResponse:
        """ApprouverDocument1D — approbation ecole/PO de la population au 5/10e.

        nbEleves5ieme doit etre fourni (controle de concurrence cote serveur -> 00011).
        """
```

### Dataclasses proposées

```python
@dataclass
class DroitInscriptionSave:
    """Ligne de droit d'inscription (type Save / requete Modifier)."""
    co_ann_etude: str                       # obligatoire (XSD: string, pas int)
    nb_eleves_5ieme: int | None = None       # modifiable AVANT approbation population
    mt_droits_inscription: float | None = None  # modifiable APRES approbation population


@dataclass
class DroitInscriptionAppr:
    """Ligne a approuver (type Appr / requete Approuver)."""
    co_ann_etude: str                       # obligatoire
    nb_eleves_5ieme: int                    # obligatoire (XSD+UML), verif anti-concurrence


@dataclass
class DroitInscriptionResponse:
    """Ligne de droit d'inscription (reponse, 8 champs)."""
    co_ann_etude: str | None
    nb_eleves_5ieme: int | None
    mt_droits_inscription: float | None
    mt_droits_inscription_occupationnel: float | None  # "n'est plus utilise"
    sw_app_pop_d1d: bool | None             # approuve ecole/PO
    sw_app_d1d: bool | None                 # approuve administration
    ts_maj: str | None                      # timestamp (string, pas bool)
    te_user_maj: str | None                 # userid (string, pas bool)
```

### Recommandations d'implémentation
1. **Forcer SOAP 1.1** dans le transport zeep (ce service ne supporte pas SOAP 1.2, comme le Doc 3).
2. **`coAnnEtude` = `str`** dans toute l'API publique (le contrat XSD est `string` malgré le « int » du PDF).
3. **Refléter la règle des deux phases** côté client : exposer des helpers ou une validation préalable —
   refuser `mt_droits_inscription` si `sw_app_pop_d1d` est faux (sinon `1546`) ; refuser `nb_eleves_5ieme`
   après approbation population. Cela évite des allers-retours serveur inutiles.
4. **`approuver()` exige `nb_eleves_5ieme`** : le récupérer du dernier `lire()` et le repasser tel quel
   (sinon risque de `00011` si la valeur serveur a changé).
5. **Exceptions typées indexées par (service, code)** : `1545`/`1114`/`2106` ont un sens différent ici
   qu'au Doc 1/Doc 2. Ne pas mutualiser un registre de codes global naïf.
6. **`mt_droits_inscription_occupationnel`** : exposer en lecture seule, marquer *deprecated* (« n'est plus
   utilisé »).
7. **Mock server stateful (session 6)** : modéliser les deux switches `swAppPopD1D`/`swAppD1D` et les trois
   transitions (encodage → appro. pop. → appro. admin) pour tester `1546`, `1545`, `1530` et `00011`.

---

## Synthèse de la session 5

- **« Document 1D » = service Droits d'Inscription** (radical interne `Document1D`/`Doc 1D`). Gère, par
  année d'études, la **population au 5/10ᵉ** (`nbEleves5ieme`) **et** les **montants des droits**
  (`mtDroitsInscription`).
- **3 opérations** : LireDocument1D, ModifierDocument1D, **ApprouverDocument1D** — comme le Document 1
  (Population), contrairement à Doc 2 / Doc 3 (Lire+Modifier seulement).
- **SOAP 1.1 uniquement** (binding WSDL `soap/` + PDF §2.2) — comme le Doc 3.
- **Pattern Common_v1** (ancien), bloc retour `AbstractExternalResponseType` ; type de réponse
  `Document1DReponseCT` **partagé par les 3 opérations**.
- **Deux switches d'approbation** `swAppPopD1D` (école/PO) + `swAppD1D` (administration) — parallèle exact
  au Doc 1 (`swAppPopD1`/`swAppD1`).
- **Règle métier des deux phases** : `nbEleves5ieme` modifiable *jusqu'à* l'approbation population ;
  `mtDroitsInscription` modifiable *après* (erreurs `1546`/`1545`/`1530`).
- **`statutDocumentDroitsInscription`** (Formations Liste) = statut **de ce Doc 1D**, distinct de
  `statutDocumentPopulationPeriodes` (Doc 1 + Doc 2). Quatre statuts au total dans `OrganisationApercuCT`.
- **« Doc A » non mentionné** ici → hypothèse session 4 (Doc A = Population) inchangée. Pas d'erreur `20102`
  (pas de dépendance inter-documents bloquante déclarée pour le Doc 1D).
- **Coquilles de typage du PDF résolues par l'UML + le XSD** : `coAnnEtude` = `string` (pas int),
  `tsMaj`/`teUserMaj` = `string` (pas boolean), `nbEleves5ieme` (Approuver) = obligatoire (pas facultatif).
- **Pas de divergence de type numérique** (contrairement au Doc 3 et ses « 24.0 » sur des `int`).
- **8 XSD partagés byte-for-byte identiques** à la session 4 (diff). Référentiel technique stable.
