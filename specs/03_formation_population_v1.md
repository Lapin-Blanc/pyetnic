# EPROM — Formation Population (Document 1) v1.0

> Spécification technique et fonctionnelle complète
> Sources : contrat embarqué dans `pyetnic/resources/EPROM_Formation_Population_1.0/` (WSDL `EpromFormationDocument1Service_external_v1.wsdl` + 10 XSD), identique au WSDL servi par la passerelle et à l'archive du catalogue SOA (relevé du 2026-11-24 ; la passerelle ne sert pas les XSD, importés en relatif) + PDF Manuel d'utilisation rev1.1 (01-05-2023, édité le 10-05-2023, 23 pages, `ETNIC_EpromFormationPopulation_v1.0.0_Manuel_d_utilisation_rev1.1.pdf`) + observations datées en production et sur TQ.
> Le contrat prime sur le manuel pour les types et les cardinalités.
> Date d'analyse : 2026-04-14 ; revue contre le manuel et le contrat le 2026-11-24

---

## Métadonnées

| Propriété | Valeur | Source |
|---|---|---|
| Produit | EPROM | manuel rev 1.1, page de garde |
| Service | Formation Population (Document 1) | manuel rev 1.1, page de garde et §1.1 |
| Version service | 1.0.0 | manuel rev 1.1, page de garde |
| Révision document | 1.1 (01-05-2023) | manuel rev 1.1, historique |
| Domaine | Enseignement - Promotion sociale | manuel rev 1.1, objectifs du document |
| Type d'échange | Synchrone | manuel rev 1.1, §2.1 |
| Format messages | SOAP 1.1 | manuel rev 1.1, §2.2 ; contrat : binding `http://schemas.xmlsoap.org/wsdl/soap/` seul |
| Sécurité | WS-Security : certificat X.509 ou login / mot de passe ; pyetnic envoie un UsernameToken | manuel rev 1.1, §2.1 ; code (`soap_client.py`) |
| Transport | TLS 1.0 ou TLS 1.2 | manuel rev 1.1, §2.1 |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/document1/v1` | contrat : `EpromFormationDocument1Service_external_v1.wsdl` |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/document1/messages/v1` | contrat : `EpromFormationDocument1Messages_external_v1.xsd` |
| Types namespace (doc1) | `http://enseignement.cfwb.be/types/formation/document1/v1` | contrat : `FormationDocument1_v1.xsd` |
| Types namespace (org) | `http://enseignement.cfwb.be/types/organisation/v1` | contrat : `Organisation_v1.xsd` |
| Binding | `EPROMFormationDocument1ExternalV1Binding` (document/literal) | contrat ; manuel rev 1.1, §2.2.1 |
| Binding « Ecole » (déprécié) | `FormationDocument1Binding`, absent du WSDL externe | manuel rev 1.1, §2.2.2 ; contrat |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | contrat (`soap:address` du WSDL) + catalogue SOA | `https://ws-tq.etnic.be/eprom/formation/document1/v1` |
| PROD | catalogue SOA | `https://ws.etnic.be/eprom/formation/document1/v1` |
| TQ | manuel rev 1.1, §2.2.1 | `https://services-web.tq.etnic.be/eprom/formation/document1/v1` |
| PROD | manuel rev 1.1, §2.2.1 | `https://services-web.etnic.be/eprom/formation/document1/v1` |

> pyetnic appelle `ws.etnic.be` / `ws-tq.etnic.be` depuis 0.3.0, certificat TLS vérifié dans les deux
> environnements (lectures vérifiées sur TQ et en production, 2026-11-24). Le manuel ne connaît que
> `services-web(.tq).etnic.be` et demande d'y ajouter le port `11443` pour TLS 1.2 (manuel rev 1.1,
> §2.2) ; pyetnic appelait ces adresses jusqu'à 0.2, sans pouvoir vérifier le certificat de TQ
> (CHANGELOG, section [Unreleased]). Leur disponibilité actuelle n'a pas été revérifiée (inconnu).

> **Endpoint générique « Ecole »** (déprécié ; manuel rev 1.1, §2.2.2 et §3.1.2.2) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument1V1?mode=sync`, To = `http://services-web.etnic.be/eprom` ;
>   les réponses d'exemple du manuel portent `eprom:formationDocument1V1?mode=sync`, initiale en
>   minuscule (§3.1.3.5, §3.1.4.5, §3.1.5.5)

---

## Description fonctionnelle

Le service FormationDocument1 permet de gérer les informations relatives à la **population
scolaire au 1/10ème** de la formation (Doc 1) sauvegardées dans EPROM (manuel rev 1.1, §1.1).

⚠️ **Terminologie** : le nom interne « Document 1 » désigne la population (manuel rev 1.1, §1.1).
Ne pas confondre avec le « Doc 1D », les droits d'inscription (manuel Formations Liste rev 2.0,
§3.1.4.2 ; spec 06).

Il expose **3 opérations** (manuel rev 1.1, §1.1 ; contrat) :

1. **LireDocument1** - fournit les informations du document 1
2. **ModifierDocument1** - permet de modifier les données du document 1
3. **ApprouverDocument1** - permet d'approuver les données du document 1

**Règle clé** : une fois approuvé, le document 1 ne peut plus être modifié (manuel rev 1.1,
§3.1.5.1), erreur `1545` (manuel rev 1.1, §4). Quelle approbation déclenche `1545`, celle de l'école
(`swAppPopD1`) ou celle de l'administration (`swAppD1`, qui a son code `1530`), n'a pas été testé sur
le Doc 1 (à confirmer) ; au Doc 1D, c'est celle de l'école (testé sur TQ, 2026-11-24, spec 06).

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> **Pattern identique à Formations Liste v2** : ce service utilise `Common_v1.xsd`, et non
> `Common_v2.xsd` comme Formation Organisation v8 (contrat : `EpromFormationDocument1Messages_external_v1.xsd`).
> Le `requestId` est un **header SOAP séparé**, optionnel en requête et obligatoire en réponse
> (contrat : `wsdl:required` du WSDL ; manuel rev 1.1, §2.3).

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

(contrat : `Common_v1.xsd`, `ResponseStatus_v3.xsd` ; manuel rev 1.1, §2.4)

---

## Type d'identification - Organisation_v1.xsd

> XSD partagé par les Documents 1, 2, 3 et 1D (contrat : même contenu dans les quatre contrats
> embarqués). Décrit dans `00_REGISTRE.md`.
> Namespace : `http://enseignement.cfwb.be/types/organisation/v1`
>
> **Différence avec `OrganisationIdCT`** (namespace `.../formation/organisation/v2` dans Formations
> Liste, `.../v8` dans Organisation) : pas de champ `implId` en requête (`OrganisationReqIdCT`), et
> `implId` optionnel en réponse (`OrganisationResIdCT`) (contrat).

### OrganisationReqIdCT (identification en requête)

```
OrganisationReqIdCT
├── anneeScolaire   : AnneeScolaireST [obligatoire]
├── etabId          : EtabIdST        [obligatoire]
├── numAdmFormation : int             [obligatoire]
└── numOrganisation : int             [obligatoire]
```

> ⚠️ **Pas de `implId`** en requête : l'organisation est identifiée uniquement par
> anneeScolaire + etabId + numAdmFormation + numOrganisation (contrat ; manuel rev 1.1, §3.1.3.2).

### OrganisationResIdCT (identification en réponse)

```
OrganisationResIdCT
├── anneeScolaire   : AnneeScolaireST [obligatoire]
├── etabId          : EtabIdST        [obligatoire]
├── implId          : ImplIdST        [0..1]
├── numAdmFormation : int             [obligatoire]
└── numOrganisation : int             [obligatoire]
```

> ⚠️ **Divergence manuel/contrat** : le texte du manuel (§3.1.3.4, page 8, et `ImplIdST` page 9)
> donne `implId` « obligatoire » dans `OrganisationResIdCT` ; le contrat (`Organisation_v1.xsd`) et
> le diagramme du manuel (page 8) le déclarent `[0..1]`. Les exemples de réponse du manuel le portent
> (§3.1.3.5, §3.1.4.5, §3.1.5.5). pyetnic ne le lit pas (voir Mapping) ; sa présence dans les
> réponses réelles n'a pas été relevée (inconnu).

---

## Opération 1 : LireDocument1

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1/v1/LireDocument1` (contrat : WSDL)

### Requête

**Élément** : `LireDocument1` → **Type** : `LireDocument1RequeteCT` extends `FormationDocument1LireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex: `"2016-2017"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

(contrat : `FormationDocument1_v1.xsd`, `Organisation_v1.xsd` ; manuel rev 1.1, §3.1.3.2)

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse ; contrat).

### Réponse

**Élément** : `LireDocument1Reponse` → **Type** : `Document1ReponseCT` extends `AbstractExternalResponseType`

```
Document1ReponseCT
├── success         : boolean                   [obligatoire] (hérité)
├── messages        : messagesType              [0..1]        (hérité)
└── response        : Document1ReponseMetierCT  [0..1]
    └── document1   : FormationDocument1CT      [obligatoire]
        ├── id              : OrganisationResIdCT              [obligatoire]
        └── populationListe : PopDocument1AnneeEtudeLstCT      [obligatoire]
            └── population  : PopDocument1AnneeEtudeLineCT     [1..*]
```

> Arbre du contrat (`EpromFormationDocument1Messages_external_v1.xsd`, `FormationDocument1_v1.xsd`).
> Le texte du manuel (§3.1.3.4) dit `populationListe` « facultatif » et `population` « 0 à N » ; le
> contrat et les diagrammes du manuel (pages 8 et 9) exigent la liste et au moins une ligne.

> **Doc 1 jamais encodé** : `LireDocument1` rend déjà une ligne de population à zéro
> (`coAnnEtude` 1, `swAppPopD1` et `swAppD1` faux) ; sa présence ne dit pas que le Doc 1 a été
> encodé (observé en production le 2026-09-16, confirmé sur TQ le 2026-11-10). Avant
> l'approbation du Doc A, la lecture est refusée en `20101` (testé sur TQ, 2026-11-10).

### PopDocument1AnneeEtudeLineCT (ligne de population - réponse)

(contrat : `FormationDocument1_v1.xsd` pour les types et cardinalités ; manuel rev 1.1, §3.1.3.4,
pour les descriptions)

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
| `tsMaj` | string | oui | Date de la dernière modification (format de l'exemple du manuel, §3.1.3.5 : `2017-03-06 12:21:06.562526`) |
| `teUserMaj` | string | oui | Dernier utilisateur à avoir modifié le document |

> **`tsMaj` et `teUserMaj`** : le texte du manuel les type `boolean` (§3.1.3.4, page 10) ; le contrat
> et le diagramme du manuel (page 9) les déclarent `string`.

> **Note** : 4 champs marqués « n'est plus utilisé » (`nbEleveFse`, `nbElevePi`, `nbEleveTotFse`,
> `nbEleveTotPi` ; manuel rev 1.1, §3.1.3.4) restent obligatoires dans la réponse et ne figurent
> **pas** dans le type Save (contrat). L'exemple de lecture du manuel les porte non nuls, celui de la
> modification suivante à 0 (§3.1.3.5, §3.1.4.5) ; leurs valeurs en production n'ont pas été
> relevées (inconnu).

> **Formules de contrôle** (déduites des libellés des erreurs, manuel rev 1.1, §4, et des
> descriptions des totaux, §3.1.3.4 ; les exemples du manuel les vérifient : 22 et 26 au §3.1.3.5,
> 20 et 24 au §3.1.4.5) :
> - `nbEleveTot2a5` = `nbEleveA` + `nbEleveEhr` + `nbEleveFse` + `nbElevePi` + `nbEleveB`
> - `nbEleveTot6et8` = `nbEleveTot2a5` + `nbElevePl`
> - `nbEleveTotHom` + `nbEleveTotFem` = `nbEleveTot6et8` (erreur 4011)
> - `nbEleveDem` ≤ `nbEleveTot2a5` (erreur 4004)
> - `nbEleveExm` ≤ `nbEleveTot2a5` (erreurs 4005, 4012)
> - `nbEleveMin` ≤ `nbEleveTot2a5` (erreur 4008)
> - `nbEleveTotHom` ≤ `nbEleveTot6et8` (erreur 4009)
> - `nbEleveTotFem` ≤ `nbEleveTot6et8` (erreur 4010)
>
> `Dem`, `Min` et `Exm` sont des sous-comptes des élèves **comptés une fois** (`nbEleveTot2a5`),
> pas de `nbElevePl` : les libellés des erreurs 4004, 4005, 4008 et 4012 disent « comptés 1 fois »,
> l'exemple de réponse du manuel porte `nbEleveDem` 10 pour `nbElevePl` 4, et en production ces
> colonnes ne sont jamais remplies sur une ligne entièrement en `Pl` (0 sur 50) et le sont toujours
> sur une ligne entièrement en `A` (17 sur 17) (observé en production, date non relevée). La borne
> du serveur elle-même n'a pas été testée au-delà de ces données.

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

### Exemple de réponse XML (corps de la réponse, manuel rev 1.1, §3.1.3.5)

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

> **Booléens** : l'exemple sérialise `swAppPopD1` et `swAppD1` en `1`/`0`, formes lexicales
> valides de `xs:boolean` (XML Schema) au même titre que `true`/`false` ; zeep les rend en `bool`.
> L'exemple a été capturé sur l'endpoint « Ecole » (en-têtes WS-Addressing du manuel).

---

## Opération 2 : ModifierDocument1

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document1/v1/ModifierDocument1` (contrat : WSDL)

### Requête

**Élément** : `ModifierDocument1` → **Type** : `ModifierDocument1RequeteCT` extends `FormationDocument1ModifReqCT`

```
ModifierDocument1RequeteCT
├── id              : OrganisationReqIdCT              [obligatoire]
└── populationListe : PopDocument1AnneeEtudeLstSaveCT  [0..1]
    └── population  : PopDocument1AnneeEtudeLineSaveCT  [0..*]
```

(contrat : `FormationDocument1_v1.xsd` ; manuel rev 1.1, §3.1.4.2, dont le texte nomme la liste
`Doc1PopulationScolaireAnneeEtudeLstSaveCT`)

### PopDocument1AnneeEtudeLineSaveCT (ligne de population - requête)

(contrat : `FormationDocument1_v1.xsd` ; manuel rev 1.1, §3.1.4.2)

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

> **Différence requête vs réponse** : le type Save a **10 champs** en moins par rapport au type
> de réponse (10 contre 20, contrat). Les champs absents sont :
> - Les 4 champs obsolètes : `nbEleveFse`, `nbElevePi`, `nbEleveTotFse`, `nbEleveTotPi`
> - Les 2 totaux calculés : `nbEleveTot2a5`, `nbEleveTot6et8`
> - Les 2 switchs d'approbation : `swAppPopD1`, `swAppD1`
> - Les 2 champs audit : `tsMaj`, `teUserMaj`

> **Lignes et champs omis** : ce que le serveur fait d'une ligne absente de la requête ou d'un champ
> facultatif omis (conservé ou remis à 0) n'a pas été testé (inconnu).

### Réponse

**Type** : `Document1ReponseCT` (identique à LireDocument1 : même type pour les 3 opérations ;
contrat). Le texte du manuel (§3.1.4.4) le nomme `ModifierDocument1ReponseCT` et dit `response`
« obligatoire » ; le contrat et le diagramme du manuel (page 15) le déclarent `[0..1]`.

La réponse contient le document 1 complet après modification, incluant les totaux recalculés
(exemple du manuel, §3.1.4.5).

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
`http://services-web.etnic.be/eprom/formation/document1/v1/ApprouverDocument1` (contrat : WSDL)

### Description fonctionnelle

Permet d'approuver un document 1. **Quand un document 1 est approuvé, il n'est plus possible
de le modifier** (erreur 1545) (manuel rev 1.1, §3.1.5.1 et §4).

L'utilisateur envoie les données d'identification ainsi que les populations **afin de vérifier
que les données n'ont pas été modifiées entre la dernière consultation et l'approbation** (manuel
rev 1.1, §3.1.5.2).

> **Observé** : `ApprouverDocument1` coche `swAppPopD1` (la case « Validé » de l'écran) et laisse
> `swAppD1` à faux (observé en production le 2026-09-18, testé sur TQ le 2026-11-10). Cette
> validation par l'école suffit à ouvrir le Document 2, dont la lecture est refusée en `20103`
> avant elle (testé sur TQ, 2026-11-10, spec 04). `swAppD1` est basculé ensuite par
> l'administration, en même temps que `swAppD2` du Document 2, sans changer le `tsMaj` des deux
> documents (observé une fois, 2026-09-19).

### Requête

**Élément** : `ApprouverDocument1` → **Type** : `ApprouverDocument1RequeteCT` extends `FormationDocument1ApprReqCT`

```
ApprouverDocument1RequeteCT
├── id              : OrganisationReqIdCT              [obligatoire]
└── populationListe : PopDocument1AnneeEtudeLstSaveCT  [0..1]
    └── population  : PopDocument1AnneeEtudeLineSaveCT  [0..*]
```

> Structure identique à ModifierDocument1 (contrat : `FormationDocument1ApprReqCT`). Les données de
> population sont envoyées pour contrôle d'intégrité (manuel rev 1.1, §3.1.5.2). Le contrat rend
> `populationListe` facultative, le serveur l'exige : sans elle, ou avec une population différente
> de celle enregistrée, l'approbation est refusée en `20104` (observé en production, 2026-09-18).

### Réponse

**Type** : `Document1ReponseCT` (identique à LireDocument1 et ModifierDocument1 ; contrat).

> **Observation (diagramme UML page 19)** : le diagramme nomme le type de réponse
> `ApprouverDocument1ReponseCT` avec un sous-élément `(responseType)` contenant
> `document1 : FormationDocument1CT`. En réalité, le XSD utilise le type partagé
> `Document1ReponseCT` → `Document1ReponseMetierCT` pour les 3 opérations. **Divergence
> de nommage du diagramme et du texte (§3.1.5.4)**, pas d'impact fonctionnel.

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

| Success | Code | Description (manuel rev 1.1, §4, sauf mention) | Opérations |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | toutes |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | Lire |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | Modifier, Approuver |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | toutes |
| `false` | `00999` | Erreur sql | toutes |
| `false` | `1114` | Numéro d'établissement incorrect | toutes |
| `false` | `1113` | Paramètre annéeScolaire incorrect (xxxx-xxxx) | toutes |
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
| `false` | `20101` | Le "Doc A" doit être approuvé pour pouvoir accéder au document suivant (libellé du serveur, absent du manuel) | Lire, avant l'approbation du Doc A (testé sur TQ, 2026-11-10) |
| `false` | `20104` | Les valeurs que vous tentez de valider ne sont pas celles enregistrées. Veuillez recharger les données avant la validation (libellé du serveur, absent du manuel) | Approuver (observé en production, 2026-09-18 : population absente ou différente de celle enregistrée) |
| `false` | `99999` | (Autres erreurs) | toutes |

> La colonne « Opérations » est déduite des libellés, sauf observation indiquée : le manuel (§4) ne
> rattache aucun code à une opération. Au Doc 1D, `1545` a aussi refusé une seconde approbation
> (testé sur TQ, 2026-11-24, spec 06) ; non testé ici.

> **Codes partagés avec d'autres services** : `00009`, `00025` et `00999` figurent aussi au manuel
> Formations Liste (rev 2.0, §4). `1114` et `1113` portent les libellés de `30001` et `30007` de
> Formations Liste (manuel rev 2.0, §4) et d'Organisation (spec 02) : même sens, autre numéro.

---

## Vérification croisée UML / XSD / PDF

### Diagramme page 7 (requête LireDocument1)
- ✅ `FormationDocument1LireReqCT` → `id : OrganisationReqIdCT` — conforme au XSD
- ✅ `OrganisationReqIdCT` : 4 champs (anneeScolaire, etabId, numAdmFormation, numOrganisation) — conforme

### Diagramme page 8 (réponse LireDocument1)
- ✅ Structure d'héritage `AbstractExternalResponseType` → `Document1ReponseCT` - conforme
- ✅ `Document1ReponseMetierCT` → `document1 : FormationDocument1CT` - conforme
- ✅ `FormationDocument1CT` : `id` + `populationListe`, sans `[0..1]` sur la liste - conforme (obligatoire)
- ✅ `OrganisationResIdCT` : 5 champs dont `implId [0..1]` - conforme au XSD
- ⚠️ Texte (§3.1.3.4) : type nommé `LireDocument1ReponseCT` (contrat : `Document1ReponseCT`) ;
  `populationListe` « facultatif » vs contrat obligatoire ; `implId` « obligatoire » (et `ImplIdST`,
  page 9) vs XSD `minOccurs="0"` - **divergences du texte**

### Diagramme page 9 (PopDocument1AnneeEtudeLstCT / PopDocument1AnneeEtudeLineCT)
- ✅ `population [1..*]` - conforme
- ✅ 20 champs listés dans le diagramme - tous confirmés dans le XSD
- ✅ Tous les champs sont `xs:int` ou `xs:boolean` ou `xs:string`, `tsMaj` et `teUserMaj` en `string` - conforme
- ⚠️ Texte : `population` « 0 à N » (page 9), `tsMaj` et `teUserMaj` « boolean » (page 10) - **divergences du texte**

### Diagramme page 13 (requête ModifierDocument1)
- ✅ `FormationDocument1ModifReqCT` : `id` + `populationListe [0..1]` - conforme
- ✅ `PopDocument1AnneeEtudeLstSaveCT` : `population [0..*]` - conforme
- ✅ `PopDocument1AnneeEtudeLineSaveCT` : 9 champs facultatifs + `coAnnEtude` obligatoire - conforme
- ⚠️ Texte (page 14) : la liste est nommée `Doc1PopulationScolaireAnneeEtudeLstSaveCT` - divergence de nommage

### Diagramme page 15 (réponse ModifierDocument1)
- ✅ Structure identique à la réponse LireDocument1, `response [0..1]` - conforme
- ⚠️ Texte (§3.1.4.4) : `ModifierDocument1ReponseCT`, `response` « obligatoire » - divergence

### Diagramme page 18 (requête ApprouverDocument1)
- ✅ Structure identique à ModifierDocument1 — conforme au XSD (`FormationDocument1ApprReqCT` = même structure)

### Diagramme page 19 (réponse ApprouverDocument1)
- ⚠️ Le diagramme nomme le type `ApprouverDocument1ReponseCT` avec sous-élément `(responseType)`.
  Le XSD utilise `Document1ReponseCT` (type partagé) → `Document1ReponseMetierCT`. **Divergence de nommage uniquement**.

### Exemples (§3.1.3.5, §3.1.4.5, §3.1.5.5)
- ⚠️ Ils ne forment pas une séquence cohérente : la lecture (`tsMaj` 2017-03-06) montre `swAppPopD1`
  à 1, la modification suivante (2017-04-05) est acceptée et rend `swAppPopD1` à 0. Ils ne
  renseignent donc pas sur la règle `1545`.
- ✅ Les totaux rendus vérifient les formules de contrôle ; l'approbation rend `swAppPopD1` à 1 et
  `swAppD1` à 0, comme observé en production.

---

## Mapping pyetnic

| Élément du contrat | pyetnic (`pyetnic.eprom`) |
|---|---|
| `LireDocument1` | `lire_document_1(organisation_id)` -> `FormationDocument1` |
| `ModifierDocument1` | `modifier_document_1(organisation_id, population_liste=None)` -> `FormationDocument1` |
| `ApprouverDocument1` | `approuver_document_1(organisation_id, population_liste)` -> `FormationDocument1` ; `population_liste` obligatoire |
| `FormationDocument1CT` | `FormationDocument1` (`id`, `populationListe`) |
| `PopDocument1AnneeEtudeLstCT` / `LineCT` | `Doc1PopulationList` / `Doc1PopulationLine` (20 champs) |
| `PopDocument1AnneeEtudeLstSaveCT` / `LineSaveCT` | `Doc1PopulationListSave` / `Doc1PopulationLineSave` (`coAnnEtude` + 9 champs facultatifs) ; `Doc1PopulationListSave.from_document(doc)` reprend la population lue |
| `OrganisationReqIdCT` | `OrganisationId`, `implId` jamais envoyé |
| `OrganisationResIdCT` | `FormationDocument1.id` : l'`id` de la réponse, `implId` compris (observé sur TQ et en production, 2026-11-25), complété par celui de l'appelant pour ce qui y manquerait (#51) |

- **Approbation** : `approuver_document_1` exige `population_liste`, que le contrat rend facultative,
  et lève `TypeError` sans elle avant tout appel : le serveur refusait tout appel sans elle en
  `20104` (observé en production, 2026-09-18). La population relue s'envoie telle quelle :
  `approuver_document_1(org_id, Doc1PopulationListSave.from_document(lire_document_1(org_id)))`.
- **Modification** : `modifier_document_1` n'envoie que les champs renseignés (`None` retiré) ; sans
  `population_liste`, la requête ne porte que l'`id`.
- **Erreurs** : depuis 0.3.0, un refus lève la sous-classe d'`EtnicBusinessError` de son code
  (`pyetnic.exceptions`) : `20101` -> `EtnicDocumentNotAccessibleError` ; `20104` et `00011` ->
  `EtnicConcurrencyError` ; `1545` et `1530` -> `EtnicAlreadyApprovedError` ; `1113`, `1114`,
  `2106` et `4004` à `4012` -> `EtnicValidationError` ; `00009` -> `EtnicNotFoundError` ; `00025`,
  `00999` et `99999` -> `EtnicBusinessError`. Le mode permissif (`permissive_errors()` ou
  `Config.RAISE_ON_ERROR = False`), déprécié et retiré en 1.0, rend `None` à la place.
- **Types** : `swAppPopD1` et `swAppD1` sont des `bool` ; `tsMaj` et `teUserMaj` des `str`,
  facultatifs dans le modèle (le contrat les rend obligatoires). `FormationDocument1.populationListe`
  est facultatif dans le modèle (`None` si l'élément manque), obligatoire au contrat.
- Symboles stables (`docs/PUBLIC_API_SURFACE.md`), sauf `Doc1PopulationListSave.from_document`,
  classé « construction ».

---

## XSD utilisés

| Fichier XSD | Partage avec les autres contrats embarqués |
|---|---|
| `EpromFormationDocument1Messages_external_v1.xsd` | propre au service |
| `FormationDocument1_v1.xsd` | propre au service |
| `Organisation_v1.xsd` | identique, octet pour octet, à celui des Documents 2 et 3 ; même contenu au Document 1D ; décrit dans `00_REGISTRE.md` |
| `Common_v1.xsd` | identique, octet pour octet, à celui de Formations Liste v2 et des Documents 2 et 3 |
| `AnneeScolaire_v1.xsd` | idem |
| `Etablissement_v1.xsd` | idem |
| `ResponseStatus_v3.xsd` | idem |
| `requestId_v1.xsd` | idem |
| `Addressing_v2.xsd` | idem ; référencé seulement par les types internes de `Common_v1.xsd` |
| `Authorisation_v2.xsd` | idem ; référencé seulement par `AbstractInternalRequestType` de `Common_v1.xsd` |

(contrat : les 10 XSD de `pyetnic/resources/EPROM_Formation_Population_1.0/xsd/`, comparés aux
autres contrats embarqués)
