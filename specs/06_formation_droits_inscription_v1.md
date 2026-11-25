# EPROM - Formation Droits d'Inscription (Document 1D) v1.0

> Spécification technique et fonctionnelle complète
> Sources : contrat de l'archive « EPROM_Formation_Droits_Inscription_1.0 » du catalogue SOA (le WSDL servi par la production lui est identique ; la passerelle ne sert pas les XSD, importés en relatif), embarqué dans `pyetnic/resources/EPROM_Formation_Droits_Inscription_1.0/` (relevé du 2026-11-24) + PDF Manuel d'utilisation rev1.1 (01-05-2023, édité 10-05-2023, 23 pages, `ETNIC_Services_Web_EPROM_Formation_Droits_Inscription_1.0.0_Manuel_d_utilisation_rev1.1.pdf`) + essais sur TQ et lectures en production du 2026-11-24 (#33).
> Date d'analyse : 2026-06-02 (session 5) ; implémentation et essais le 2026-11-24

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | FormationDocument1D (Droits d'Inscription) |
| Version service | 1.0.0 |
| Révision document | 1.1 (01-05-2023) |
| Version XSD `FormationDocument1D_v1.xsd` | 1.0 |
| Version XSD `Organisation_v1.xsd` | 2.0 (même contenu qu'aux Documents 1, 2 et 3, aux blancs près ; comparaison du 2026-11-24) |
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

> Sources : contrat (WSDL et XSD embarqués) ; manuel rev 1.1, §1.2 (historique : endpoint EPROM et
> TLS 1.2 ajoutés en rev 1.1), §2.1 (synchrone, WS-Security, TLS 1.0 ou 1.2) et §2.2 (SOAP 1.1).

> **« Document 1D » = nom interne du service Droits d'Inscription.** Le WSDL, les XSD et le manuel
> utilisent systématiquement le radical `Document1D` / `Doc 1D`. Le « D » signifie vraisemblablement
> « Droits » : c'est le pendant « droits d'inscription » de la famille Document 1 (Population). Le service
> gère **deux choses liées** : la *population scolaire au 5/10ᵉ de la formation* (`nbEleves5ieme`) **et**
> les *montants des droits d'inscription* (`mtDroitsInscription`) (manuel rev 1.1, §1.1).

> **SOAP 1.1 confirmé deux fois** : (1) le binding du WSDL utilise exclusivement l'espace de noms
> `http://schemas.xmlsoap.org/wsdl/soap/` (SOAP 1.1) — il n'y a **pas** de binding `soap12/` ;
> (2) le PDF (§2.2) indique « Le service EPROM FormationDocument1D est compatible avec le protocole SOAP 1.1 ».
> Même situation que le Document 3 (manuel rev 1.3, §2.2) et que Formation Organisation v8 (manuel
> rev 6.0, §2.2 ; la v7 rev 5.1 disait déjà SOAP 1.1 seul).

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL + catalogue | `https://ws-tq.etnic.be/eprom/formation/document1D/v1` |
| PROD | catalogue | `https://ws.etnic.be/eprom/formation/document1D/v1` |

> pyetnic appelle ces deux adresses (lectures vérifiées sur TQ et en production, écritures sur TQ,
> 2026-11-24).

> Le WSDL externe ne déclare que l'adresse TQ (`<soap:address location="https://ws-tq.etnic.be/eprom/formation/document1D/v1"/>`).
> Le manuel rev 1.1 (§2.2.1) donne d'autres hôtes, `https://services-web.tq.etnic.be/eprom/formation/document1D/v1`
> (TQ) et `https://services-web.etnic.be/eprom/formation/document1D/v1` (PROD), et le port `11443`
> pour TLS 1.2 (§2.2) ; pyetnic ne les utilise pas.
>
> **Endpoint générique « Ecole »** (déprécié, manuel rev 1.1, §2.2.2 et §3.1.2.2 ; pyetnic ne l'utilise pas) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument1DV1?mode=sync`, To = `http://services-web.etnic.be/eprom`
> - (dans les exemples de réponse du manuel, §3.1.3.5, §3.1.4.5 et §3.1.5.5, l'`Action` est écrite
>   `eprom:formationDocument1DV1?mode=sync`, `f` minuscule ; même incohérence de casse qu'au Document 3,
>   à confirmer côté plateforme)
>
> Le endpoint spécifique EPROM **ne requiert pas** de WS-Addressing (manuel rev 1.1, §2.2.1). Il a été
> ajouté en rev 1.1 (2023) en même temps que TLS 1.2 ; auparavant seul le endpoint générique `/ecole`
> existait (manuel rev 1.1, historique et §1.2.2).

---

## Description fonctionnelle

Le service EPROM FormationDocument1D permet à l'école de **gérer les informations relatives à la
population scolaire au 5/10ᵉ de la formation et aux montants des droits d'inscription** (Doc 1D)
sauvegardés dans EPROM (manuel rev 1.1, §1.1 et §3.1.1).

Deux notions distinctes mais liées sont portées par le même document, **par année d'études** (une
ligne par `coAnnEtude`, contrat) :

1. **`nbEleves5ieme`** : le « nombre d'élèves au 5/10ème » (manuel rev 1.1, §3.1.3.4), « au
   5ème/10ème de fonctionnement » de la formation (§3.1.4.1).
2. **`mtDroitsInscription`** : le « montant des droits d'inscription » (§3.1.3.4).

Il expose **3 opérations** (contrat : WSDL ; manuel rev 1.1, §1.1), comme le Document 1 (Population),
qui a aussi une opération d'approbation :

1. **LireDocument1D** — fournit les informations du document 1D.
2. **ModifierDocument1D** — modifie les données du document 1D (population au 5/10ᵉ et/ou montants).
3. **ApprouverDocument1D** — approuve (côté école/PO) la population au 5/10ᵉ du document 1D.

> **Différence avec Doc 2 et Doc 3** : ces derniers n'ont que Lire + Modifier. Doc 1D **et** Doc 1
> (Population) possèdent en plus une opération `Approuver` (contrats embarqués).

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

> **Deux switches d'approbation** dans la ligne de réponse, structure **parallèle au Document 1**
> (`swAppPopD1` + `swAppD1`), avec le suffixe « D » (contrats embarqués) :
> - `swAppPopD1D` : « Valeur permettant de savoir si le document est approuvé » (manuel rev 1.1,
>   §3.1.3.4) ; c'est l'approbation de la population par l'**école / le PO** : `ApprouverDocument1D`
>   le pose (testé sur TQ, 2026-11-24).
> - `swAppD1D` : document approuvé par l'**administration** (manuel rev 1.1, §3.1.3.4).

> **`mtDroitsInscriptionOccupationnel`** : présent en réponse (obligatoire au XSD) mais **« n'est plus
> utilisé »** (PDF §3.1.3.4). Absent des lignes de requête (Modifier / Approuver). Le client peut le lire
> mais ne doit pas s'en servir ; il vaut `0.0` dans les exemples du manuel et 0 dans toutes les lignes
> lues en production (2026-11-24).

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> Pattern **Common_v1** (ancien), identique à Population (Doc 1), Périodes (Doc 2), Attributions (Doc 3)
> et Formations Liste v2. Le `Messages` XSD importe bien `common:AbstractExternalResponseType`, que la
> copie de `Common_v1.xsd` livrée avec ce contrat annote « DEPRECATED » (contrat ; manuel rev 1.1, §2.4).

```
AbstractExternalResponseType (abstract)
├── success  : boolean       [obligatoire]
└── messages : messagesType  [0..1]
    ├── error   : MessageType [0..*]   (code [≤10c] + description + zone)
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```

Le `requestId` (UUID) est porté par un **header SOAP** : optionnel en requête, obligatoire en réponse
(WSDL : `wsdl:required` à `false` puis `true` ; endpoint EPROM). S'il n'est pas fourni, l'ETNIC en
génère un (manuel rev 1.1, §2.3).

> Le type de réponse `Document1DReponseCT` est **partagé par les 3 opérations** (Lire, Modifier,
> Approuver) : il étend `AbstractExternalResponseType` et ajoute `response` (`Document1DReponseMetierCT`,
> `[0..1]`). Toutes les opérations renvoient donc le document 1D complet après traitement (contrat :
> `EpromFormationDocument1DMessages_external_v1.xsd` ; exemples du manuel, §3.1.3.5, §3.1.4.5, §3.1.5.5).

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
> élément **obligatoire** de `FormationDocument1DCT` (pas de `minOccurs="0"`), comme dans le diagramme
> UML (p.8), alors que le texte du PDF (§3.1.3.4) l'annote « facultatif ». La liste *interne*
> `droitInscription` est bien `[0..*]`. Le contrat fait foi : l'élément conteneur est toujours présent,
> éventuellement vide ; toutes les lectures du 2026-11-24 (TQ et production) l'ont porté, avec une ligne.

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

> **Booléens sérialisés `0`/`1`** : dans les exemples de réponse du manuel (§3.1.3.5, §3.1.4.5, §3.1.5.5),
> `swAppPopD1D`/`swAppD1D` valent `1` ou `0` (et non `true`/`false`). `xs:boolean` admet les deux
> formes et zeep les convertit en `bool`. La forme émise par le serveur n'a pas été relevée ; les
> lectures du 2026-11-24 rendent des `bool` (test d'intégration en lecture).

### Exemple de requête XML (manuel rev 1.1, §3.1.3.3)

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

### Exemple de réponse XML (corps métier, 1 ligne ; manuel rev 1.1, §3.1.3.5, en-têtes WS-Security et WS-Addressing de l'endpoint générique retirés)

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

> **Fenêtres de modification (PDF §3.1.4.1)**, règle centrale du service :
> « Attention, le nombre d'élèves n'est modifiable **que jusqu'à l'approbation** de la population au
> 5ème/10ème de fonctionnement par l'école et/ou le PO et les droits d'inscription ne sont modifiables
> **qu'après l'approbation** de la population au 5ème/10ème de fonctionnement par l'école et/ou le PO ! »

Autrement dit, le cycle de vie d'une ligne est en **deux phases**, pivotant sur `swAppPopD1D` (les deux
premières phases testées sur TQ, 2026-11-24) :

| Phase | `swAppPopD1D` | `nbEleves5ieme` | `mtDroitsInscription` |
|---|---|---|---|
| Avant approbation population | `0` | **modifiable** | **figé** (erreur `20112` sur TQ, `1546` au manuel) |
| Après approbation population | `1` | **figé** (erreur `1545`) | **modifiable** |
| Après approbation administration (`swAppD1D=1`) | `1` (vu une fois à `0` en production) | figé | figé (erreur `1530` d'après son libellé ; non observé) |

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
> les switches, ni `tsMaj`/`teUserMaj` (champs en lecture seule / gérés serveur ; contrat). Pour cibler une
> ligne, on envoie son `coAnnEtude` puis le(s) champ(s) à mettre à jour. Qu'un champ omis garde sa valeur
> (et ne soit pas remis à zéro, comme à `ModifierOrganisation`, spec 02) : (inconnu), non relevé lors
> des essais TQ du 2026-11-24.

### Exemple de requête XML (manuel rev 1.1, §3.1.4.3)

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
> la population, qui positionne `swAppPopD1D=1` et fait basculer la ligne en phase 2 (montants modifiables)
> (testé sur TQ, 2026-11-24).

L'utilisateur renvoie, par année d'études, le `nbEleves5ieme` **afin de vérifier que les données n'ont pas
été modifiées entre la dernière consultation et l'approbation** (manuel rev 1.1, §3.1.5.2 ; contrôle de
concurrence optimiste → erreur `00011` d'après son libellé au manuel ; **`20104`** observé sur TQ le 2026-11-24).

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
> le **XSD ET le diagramme UML (p.18) le rendent obligatoire** (aucun `[0..1]`). Le contrat fait foi :
> toujours fournir le `nbEleves5ieme` lu lors du dernier `LireDocument1D`, que le serveur compare à la
> valeur enregistrée (`20104` sur écart, testé sur TQ, 2026-11-24).

### Exemple de requête XML (manuel rev 1.1, §3.1.5.3)

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

Table du manuel (PDF §4, page 23), complétée des codes observés le 2026-11-24 (`20112`, `20104`,
`20101`). La colonne « Type » est une classification de cette spec, pas du manuel. Observés : `1545` et
`2106` (TQ, 2026-11-24), en plus des trois codes ajoutés ; aucune observation consignée pour les autres.

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
| `false` | `1546` | Document non encore approuvé ! | workflow approbation (jamais vu : TQ répond `20112`) |
| `false` | `20112` | Mise à jour du champ "mtDroitsInscription" impossible. Vous n'avez pas approuvé la population au 5/10. | Modifier (absent du manuel ; testé sur TQ, 2026-11-24) |
| `false` | `20104` | Les valeurs que vous tentez de valider ne sont pas celles enregistrées. Veuillez recharger les données avant la validation | Approuver (absent du manuel ; testé sur TQ, 2026-11-24) |
| `false` | `20101` | Le "Doc A" doit être approuvé pour pouvoir accéder au document suivant | Lire (absent du manuel ; observé en production, 2026-11-24) |
| `false` | `1530` | Mise à jour impossible; ce document est déjà approuvé par l'administration ! | workflow approbation |
| `false` | `99999` | (Autres Erreurs) | fourre-tout |

### Mapping erreurs ↔ workflow (interprétation)

Le PDF ne précise pas l'opération déclenchant chaque code ; mapping déduit en juin 2026 de la règle
métier, confronté à TQ le 2026-11-24 :

- `1546` « Document non encore approuvé ! » → `ModifierDocument1D` tentant d'écrire `mtDroitsInscription`
  **alors que `swAppPopD1D=0`** (la population n'a pas encore été approuvée par l'école/PO). **Démenti** :
  TQ répond `20112`.
- `1545` « Document déjà approuvé ! » → `ApprouverDocument1D` sur un document déjà approuvé (école/PO), ou
  `ModifierDocument1D` tentant de modifier `nbEleves5ieme` après l'approbation population. **Confirmé**
  dans les deux cas.
- `1530` « … déjà approuvé par l'administration ! » → toute `ModifierDocument1D` après `swAppD1D=1`
  (verrou final administration). Non observé.
- `00011` → écart entre le `nbEleves5ieme` envoyé en approbation et la valeur serveur (concurrence).
  **Démenti** : TQ répond `20104`.

> **Démenti par TQ (2026-11-24)** : le montant écrit avant l'approbation est refusé en `20112`, l'écart à
> l'approbation en `20104` ; `1545` se confirme (population après approbation, seconde approbation).

### ⚠️ Réutilisation de codes entre services (attention typage d'exceptions)

Les codes numériques **ne sont pas universels** : un même code a un libellé différent selon le service.

| Code | Doc 1D (ce service) | Doc 1 / Doc 2 (manuels Population rev 1.1 et Périodes rev 1.4, §4) |
|---|---|---|
| `1545` | **Document déjà approuvé !** | Doc 1 approuvé / max 5 interventions extérieures |
| `1114` | **Matricule école inexistant** | Numéro d'établissement incorrect |
| `2106` | **Année d'étude invalide** | Code Année d'études de la population scolaire incorrect |
| `1530` | … déjà approuvé par l'administration | … déjà approuvé par l'administration *(idem)* |

> **Dans pyetnic** : le routage d'un code vers sa classe d'exception tient compte du service quand la
> classe change d'un service à l'autre. C'est le seul cas de `1545` au Document 2 (erreur de validation) ;
> `1114` et `2106` gardent la même classe partout (voir « Mapping pyetnic »).

### Codes partagés / spécifiques (manuels EPROM, §4)
- **Communs aux manuels EPROM** : `00009`, `00025`, `00999` ; `99999` aux manuels des Documents 1, 2,
  3 et 1D seulement (absent de Formations Liste et de Formation Organisation).
- **Communs aux Documents** : `00011`, `1113`, `1114` (Documents 1, 2, 3 et 1D) ; `2106` (Documents 1, 2
  et 1D).
- **Workflow** : `1530` (Documents 1, 2 et 1D), `1545` (Documents 1 et 1D, autre sens au Document 2),
  `1546` (Document 1D seulement) ; hors manuel, `20112` (Document 1D) et `20104`, `20101` (observés ici
  le 2026-11-24).

---

## Règles métier & workflow

### Cycle de vie d'un document 1D (intra-document)

```
   (encodage)                 ApprouverDocument1D            (approbation admin,
   nbEleves5ieme              (école / PO)                    hors de ce service)
   modifiable        ──────────────────────────►  swAppPopD1D=1  ──────────────►  swAppD1D=1
   swAppPopD1D=0                                   nbEleves5ieme FIGÉ              tout FIGÉ
   mtDroits FIGÉ                                   mtDroits modifiable            (erreur 1530)
   (erreur 20112)
```

- **Phase 1** : l'école encode/corrige `nbEleves5ieme` (population au 5/10ᵉ). Les montants sont refusés (`20112` sur TQ, `1546` au manuel).
- **Bascule** : `ApprouverDocument1D` (école/PO) → `swAppPopD1D=1`. La population est figée.
- **Phase 2** : l'école saisit `mtDroitsInscription`. La population n'est plus modifiable.
- **Verrou** : l'administration approuve (`swAppD1D=1`), opération absente de ce service (contrat :
  aucune opération ne pose `swAppD1D`). Toute modification ultérieure serait refusée en `1530` (libellé
  du manuel, non observé). En production, `swAppD1D` a été vu vrai sans `swAppPopD1D` (observé une fois,
  2026-11-24) : l'administration n'attend pas toujours la bascule.

### Place dans le workflow inter-documents (point d'attention)

`statutDocumentDroitsInscription` (vu dans `OrganisationApercuCT` de **Formations Liste v2**) correspond
**exactement à ce service Doc 1D** : l'écriture d'un `nbEleves5ieme` le fait apparaître (testé sur TQ,
2026-11-24). La vue résumée d'une organisation expose **quatre** statuts (contrat :
`FormationOrganisation_v2.xsd` de Formations Liste ; correspondance déduite des noms, des switches des
contrats et, pour le Doc 1D, de l'essai TQ) :

| Statut (Formations Liste) | Document(s) interne(s) | Switch(es) d'approbation |
|---|---|---|
| `statutDocumentOrganisation` | Organisation (Form. Organisation v8) | statut `StatutCT` |
| `statutDocumentPopulationPeriodes` | Document 1 (Population) **+** Document 2 (Périodes) | `swAppPopD1`/`swAppD1` + `swAppD2` |
| `statutDocumentDroitsInscription` | **Document 1D (Droits d'Inscription)** ← *ce service* | `swAppPopD1D` + `swAppD1D` |
| `statutDocumentAttributions` | Document 3 (Attributions) | *(aucun switch propre)* |

> **Observation clé** : le Doc 1D possède **son propre statut**, distinct de `PopulationPeriodes`. Il ne
> recopie pas simplement les deux switches : absent avant toute écriture, « Encodé école » après
> l'écriture d'une population, il **reste « Encodé école »** après l'approbation de l'école
> (`swAppPopD1D` vrai) (testé sur TQ, 2026-11-24) ; « Approuvé » a été lu en production avec les deux indicateurs vrais, et une fois
> avec `swAppD1D` seul (2026-11-24). « Encodé PO » n'a pas été observé.

> **« Doc A » (erreur `20102` du Doc 3)** : ce manuel **ne mentionne pas « Doc A »** (aucune occurrence).
> « Doc A » est **l'organisation elle-même** : le manuel Formation Organisation v8 (rev 6.0, §1.1 et
> §3.1.1) appelle « dossier de formation (Doc A) » ce que gère le service Formation Organisation, et
> l'écran EPROM le confirme (spec 20, §1.1). La nomenclature des documents EPROM est donc : **Doc A** (Organisation),
> **Doc 1** (Population), **Doc 1D** (Droits d'Inscription), **Doc 2** (Périodes), **Doc 3** (Attributions),
> **Doc 8bis** (référencé par le Doc 3, champ `nbPeriodesDoc8`, spec 05).

> **Dépendance amont du Doc 1D** : le manuel ne déclare aucune erreur de type `20102`, mais la production
> refuse la lecture en `20101` tant que le Doc A n'est pas approuvé (17 organisations sur 45 en 2026-2027,
> 2026-11-24). Le Doc 1D dépend donc du Doc A, comme le Doc 1 ; il ne dépend pas du Doc 1 ni du Doc 2.

### Observé sur TQ et en production (2026-11-24)

> **Cycle complet testé sur TQ** (une organisation 2025-2026 dont le Doc 1D n'avait pas de statut) :
>
> | Étape | Réponse du serveur |
> |---|---|
> | Lecture avant toute écriture | une ligne squelette (`coAnnEtude` `1`, tout à 0, deux indicateurs faux) ; pas de `statutDocumentDroitsInscription` |
> | Modifier avec une liste vide | accepté ; `tsMaj` est mis à jour |
> | Modifier `nbEleves5ieme` | accepté ; le statut passe à « Encodé école » |
> | Modifier `mtDroitsInscription` avant l'approbation | refus **`20112`** « Mise à jour du champ "mtDroitsInscription" impossible. Vous n'avez pas approuvé la population au 5/10. » (le manuel annonce `1546`, jamais vu) |
> | Approuver avec un `nbEleves5ieme` différent | refus **`20104`** « Les valeurs que vous tentez de valider ne sont pas celles enregistrées. Veuillez recharger les données avant la validation » (pas `00011`) |
> | Approuver avec la population relue | accepté ; `swAppPopD1D` vrai, `swAppD1D` faux ; le statut reste « Encodé école » |
> | Modifier `nbEleves5ieme` après l'approbation | refus `1545` « Document déjà approuvé ! » |
> | Modifier `mtDroitsInscription` après l'approbation | accepté |
> | Approuver une seconde fois | refus `1545` |
> | Modifier une année d'études inconnue (`9`) | refus `2106` « Année d'étude invalide. » |
>
> **En production (lecture seule)** : 2026-2027, 45 organisations : 28 Doc 1D lisibles (ligne
> squelette, aucun statut), 17 refusés en **`20101`** (« Le "Doc A" doit être approuvé pour pouvoir
> accéder au document suivant »), comme le Doc 1 : le Doc 1D **dépend du Doc A**, contrairement à ce
> que le manuel laissait penser. 2025-2026 : 101 organisations, toutes « Approuvé », les deux
> indicateurs vrais. 2024-2025 : 123 « Approuvé », dont une avec `swAppD1D` vrai et `swAppPopD1D` faux
> (observé une fois) : l'administration peut approuver sans l'approbation de l'école. Toutes ces
> lignes portent une seule année d'études (`1`) et des valeurs à 0 ; aucune n'a été vue avec plusieurs
> années ni avec un montant non nul en production.

### Notion « population au 5/10ᵉ »

`nbEleves5ieme` est le « nombre d'élèves au 5/10ème » de la formation (manuel rev 1.1, §3.1.3.4), un
entier par année d'études. Le **Document 1** (Population) porte ses propres comptages par année d'études
(spec 03) : ce sont deux documents et deux champs distincts. Le manuel ne dit ni à quelle date le
comptage est arrêté ni à quoi il sert ; ces règles ne relèvent pas du contrat SOAP (voir « Scope
Boundary » dans `docs/ARCHITECTURE.md`).

---

## Vérification croisée UML / XSD / PDF

> Méthode (2026-06-02) : couche texte native exploitable (`pdftotext -layout`, ~2750 c/page) ;
> rendu image (`pdftoppm`) des pages à boîtes UML repliées : 5, 8, 9, 13, 14, 18. **OCR non nécessaire.**
> Pages 8, 9, 13 et 18 rendues de nouveau et relues le 2026-11-24.
> Les boîtes UML donnent les **types et cardinalités** ; le **texte** donne les libellés ; le **XSD reste
> la référence contractuelle**.

### Page 9 (réponse — `Doc1DDroitInscriptionLineCT`)
- ✅ Boîte UML : 8 champs avec types `coAnnEtude:string`, `nbEleves5ieme:int`, `mtDroitsInscription:float`,
  `mtDroitsInscriptionOccupationnel:float`, `swAppPopD1D:boolean`, `swAppD1D:boolean`, `tsMaj:string`,
  `teUserMaj:string` — **strictement conforme au XSD**.
- ⚠️ Le **texte** sous le diagramme annote `coAnnEtude` « int » et `tsMaj`/`teUserMaj` « boolean » :
  **coquilles** contredites par l'UML + le XSD (`string`).

### Pages 8 et 9 (`FormationDocument1DCT`, `OrganisationResIdCT`)
- ✅ `id` + `droitInscriptionListe` (UML p.8 : sans `[0..1]`, donc obligatoire, comme au XSD ; le texte
  dit « facultatif »). `OrganisationResIdCT` à 5 champs (avec `implId`).
- ⚠️ `implId` : texte p.9 « obligatoire » vs XSD `minOccurs="0"` et UML p.8 `[0..1]`, même divergence
  qu'aux Documents 1, 2 et 3 (spec 00). Présent dans les trois exemples de réponse du manuel (valeur
  `66`) ; pyetnic ne le lit pas (il reprend l'`OrganisationId` de l'appel).

### Page 13 (requête Modifier — `Doc1DDroitInscriptionSaveLineCT`)
- ✅ Boîte UML : `coAnnEtude:string` (obligatoire), `nbEleves5ieme [0..1] int`, `mtDroitsInscription [0..1] float`
  : conforme XSD, **pas de divergence de cardinalité** sur la ligne. Le texte annote le conteneur
  `droitInscriptionListe` « facultatif » ; UML et XSD le rendent obligatoire.

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
| 6 | `OrganisationResIdCT.implId` | obligatoire | `minOccurs="0"`, UML `[0..1]` | optionnel (XSD), présent dans les exemples du manuel |

> À l'inverse du Document 3, **aucune divergence de *type numérique*** (pas de champ `int` recevant « 24.0 ») :
> ici `nbEleves5ieme` est un vrai `int` (exemples `0`, `4`) et les montants sont des `float` déclarés (`20.0`,
> `444719.0`). Pas de risque de `ValueError` zeep sur ce service : les lectures de TQ et de production du
> 2026-11-24 n'en ont produit aucune.

---

## XSD utilisés

| Fichier XSD | Rôle | Comparé au Document 3 (2026-11-24) |
|---|---|---|
| `FormationDocument1D_v1.xsd` | **spécifique** (types doc1D, v1.0) | propre au Doc 1D |
| `EpromFormationDocument1DMessages_external_v1.xsd` | **spécifique** (messages, éléments racine) | propre au Doc 1D |
| `Organisation_v1.xsd` | partagé (OrganisationReqIdCT / ResIdCT, v2.0) | même contenu, aux blancs près |
| `Common_v1.xsd` | partagé (AbstractExternalResponseType) | mêmes types ; la copie du Doc 1D ajoute des annotations « DEPRECATED » |
| `AnneeScolaire_v1.xsd` | partagé | même contenu, aux blancs près |
| `Etablissement_v1.xsd` | partagé (EtabIdST, ImplIdST) | même contenu, aux blancs près |
| `ResponseStatus_v3.xsd` | partagé (MessageType) | même contenu, aux blancs près |
| `requestId_v1.xsd` | partagé (header UUID) | même contenu, aux blancs près |
| `Addressing_v2.xsd` | partagé (déprécié, endpoint Ecole) | mêmes types ; la copie du Doc 1D ajoute une annotation « DEPRECATED » |
| `Authorisation_v2.xsd` | partagé (déprécié) | mêmes types ; la copie du Doc 1D ajoute une annotation « DEPRECATED » |

> Comparaison, blancs et fins de ligne ignorés, de `pyetnic/resources/EPROM_Formation_Droits_Inscription_1.0/xsd/`
> et `pyetnic/resources/EPROM_Document_3_1.0/xsd/` (2026-11-24) : les copies ne sont pas identiques
> octet pour octet (le contrat du Doc 1D vient de l'archive du catalogue, en fins de ligne CRLF), mais
> les types définis sont les mêmes. `Organisation_v1.xsd` est aussi celui des Documents 1 et 2.

---

## Mapping pyetnic

| Élément du contrat | pyetnic (`pyetnic.eprom`) |
|---|---|
| `LireDocument1D` | `lire_document_1d(organisation_id)` |
| `ModifierDocument1D` | `modifier_document_1d(organisation_id, droit_inscription_liste)` |
| `ApprouverDocument1D` | `approuver_document_1d(organisation_id, droit_inscription_liste)` |
| `FormationDocument1DCT` | `FormationDocument1D` (`id`, `droitInscriptionListe`) |
| `Doc1DDroitInscriptionLstCT` / `LineCT` | `Doc1DDroitInscriptionList` / `Doc1DDroitInscriptionLine` (8 champs) |
| `Doc1DDroitInscriptionSaveLstCT` / `SaveLineCT` | `Doc1DDroitInscriptionListSave` / `Doc1DDroitInscriptionLineSave` (`coAnnEtude` + `nbEleves5ieme` ou `mtDroitsInscription`) |
| `Doc1DDroitInscriptionApprLstCT` / `ApprLineCT` | `Doc1DDroitInscriptionListAppr` / `Doc1DDroitInscriptionLineAppr` ; `Doc1DDroitInscriptionListAppr.from_document(doc)` reprend la population lue |
| `OrganisationReqIdCT` | `OrganisationId`, `implId` jamais envoyé |
| `OrganisationResIdCT` | `FormationDocument1D.id` : l'`id` de la réponse, `implId` compris (observé sur TQ et en production, 2026-11-25), complété par celui de l'appelant pour ce qui y manquerait (#51) |

- **Types** : `coAnnEtude` est un `str` (le contrat), `tsMaj`/`teUserMaj` des `str`.
  `mtDroitsInscriptionOccupationnel` est lu, « n'est plus utilisé ».
- **Liste obligatoire** à Modifier et Approuver : le contrat exige l'élément `droitInscriptionListe`
  (vide accepté à Modifier).
- **Erreurs** (`pyetnic.exceptions`) : `20101` et `20112` (et `1546`, numéro du manuel) ->
  `EtnicDocumentNotAccessibleError` ; `20104` -> `EtnicConcurrencyError` ; `1545` et `1530` ->
  `EtnicAlreadyApprovedError` ; `2106`, `1113`, `1114` -> `EtnicValidationError`. Le routage tient
  compte du service : `1545` est une erreur de validation au Document 2 (« 5ième intervention
  extérieure »), une approbation déjà faite ici.
- **Pas de validation côté client des deux phases** : le serveur décide et son refus arrive typé
  (voir « Scope Boundary » dans `docs/ARCHITECTURE.md`).
- Symboles classés « construction » dans `docs/PUBLIC_API_SURFACE.md`.

---

## Synthèse (session 5 du 2026-06-02, mise à jour le 2026-11-24)

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
  `mtDroitsInscription` modifiable *après* (erreurs `20112`/`1545`/`1530` ; `1546` au manuel).
- **`statutDocumentDroitsInscription`** (Formations Liste) = statut **de ce Doc 1D**, distinct de
  `statutDocumentPopulationPeriodes` (Doc 1 + Doc 2). Quatre statuts au total dans `OrganisationApercuCT`.
- **« Doc A » non mentionné** par ce manuel ; c'est l'organisation (voir spec 02). Le manuel ne déclare
  aucune dépendance inter-documents, mais la production refuse la lecture en `20101` tant que le Doc A
  n'est pas approuvé (2026-11-24).
- **Coquilles de typage du PDF résolues par l'UML + le XSD** : `coAnnEtude` = `string` (pas int),
  `tsMaj`/`teUserMaj` = `string` (pas boolean), `nbEleves5ieme` (Approuver) = obligatoire (pas facultatif).
- **Pas de divergence de type numérique** (contrairement au Doc 3 et ses « 24.0 » sur des `int`).
- **8 XSD partagés** avec le Document 3 : mêmes types, copies non identiques octet pour octet (blancs,
  fins de ligne, annotations « DEPRECATED » dans `Common_v1`, `Addressing_v2` et `Authorisation_v2`),
  comparaison du 2026-11-24.
