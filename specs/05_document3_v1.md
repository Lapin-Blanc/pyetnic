# EPROM - Formation Document 3 (Attributions) v1.0

> Spécification technique et fonctionnelle complète
> Sources : contrat embarqué dans `pyetnic/resources/EPROM_Document_3_1.0/` (WSDL `EpromFormationDocument3Service_external_v1.wsdl` + `xsd/`), identique au service en ligne et à l'archive du catalogue SOA (vérifié le 2026-11-24) + PDF Manuel d'utilisation rev1.3, révision courante du catalogue (01-05-2023, édité 10-05-2023, 22 pages, `ETNIC_Services_Web_EPROM_Formation_Document3_1.0.0_Manuel_d_utilisation_rev1.3.pdf`) + observations de production et essais sur TQ, datés dans le texte.
> Le contrat prime sur le manuel pour les types et les cardinalités. Les renvois « manuel » visent la rev 1.3 (§ et pages).
> Les identifiants des exemples XML sont fictifs (établissement 1234, implantation 5678, enseignant inventé).
> Date d'analyse : 2026-06-02 (session 4) ; relu sur le contrat et le manuel le 2026-11-24

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | FormationDocument3 (Attributions) |
| Version service | 1.0.0 |
| Révision document | 1.3 (01-05-2023) |
| Version XSD `FormationDocument3_v1.xsd` | 1.1 |
| Version XSD `Organisation_v1.xsd` | 2.0 |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | **SOAP 1.1 uniquement** |
| Sécurité | WS-Security : certificat X.509 **ou** login / mot de passe |
| Transport | TLS 1.0 ou TLS 1.2 |
| WSDL namespace (`tns`) | `http://services-web.etnic.be/eprom/formation/document3/v1` |
| Messages namespace (`eprom`) | `http://services-web.etnic.be/eprom/formation/document3/messages/v1` |
| Types namespace (`doc3`) | `http://enseignement.cfwb.be/types/formation/document3/v1` |
| Types namespace (`org`) | `http://enseignement.cfwb.be/types/organisation/v1` |
| Binding spécifique EPROM | `EPROMFormationDocument3ExternalV1Binding` (document/literal) |
| Binding générique Ecole (déprécié) | `FormationDocument3Binding` (cité par le manuel §2.2.2, **absent du WSDL embarqué**) |
| WSDL service | `service_eprom_formation_document3_external_v1` |
| WSDL port | `EPROMFormationDocument3ExternalV1Port` |

> Sources du tableau : manuel (page de garde, §2.1, §2.2) pour le produit, les versions, le domaine,
> l'échange, la sécurité et le transport ; contrat pour le reste (`FormationDocument3_v1.xsd`
> `version="1.1"`, `Organisation_v1.xsd` `version="2.0"`, espaces de noms, binding, service et port du WSDL).

> **SOAP 1.1 confirmé deux fois** : (1) le binding du WSDL utilise exclusivement l'espace de noms
> `http://schemas.xmlsoap.org/wsdl/soap/` (SOAP 1.1) : il n'y a **pas** de binding `soap12/` (contrat) ;
> (2) le manuel (§2.2) indique « Le service EPROM FormationDocument3 est compatible avec le protocole SOAP 1.1 ».
> Ce n'est pas une particularité du Doc 3 : les WSDL embarqués des six services EPROM n'ont tous qu'un
> binding SOAP 1.1 (contrats, vérifié le 2026-11-24), et les manuels des Documents 1 et 2, de Formations
> Liste v2 et de Formation Organisation v7 et v8 annoncent SOAP 1.1 (§2.2 de chacun).

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | contrat (`soap:address` du WSDL) + manuel §2.2.1 ; appelé par pyetnic (`ENV=dev`) | `https://ws-tq.etnic.be/eprom/formation/document3/v1` |
| PROD | manuel §2.2.1 ; appelé par pyetnic (`ENV=prod`) | `https://ws.etnic.be/eprom/formation/document3/v1` |

> pyetnic appelle ces deux adresses depuis 0.3.0, certificat TLS vérifié (`pyetnic/config.py`).

> **Endpoint générique « Ecole »** (déprécié, manuel §2.2.2 et §3.1.2.2) :
> - TQ : `https://ws-tq.etnic.be/ecole`
> - PROD : `https://ws.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument3V1?mode=sync`, To = `http://services-web.etnic.be/eprom`
> - (dans les exemples de réponse du manuel, §3.1.3.5 et §3.1.4.5, l'`Action` est écrite `eprom:formationDocument3V1?mode=sync`, `f` minuscule ; casse attendue par la plateforme : à confirmer)
>
> Le endpoint spécifique EPROM **ne requiert pas** de WS-Addressing (manuel §2.2.1 et §3.1.2.1). Il a été
> ajouté en rev 1.3 (2023) ; auparavant seul le endpoint générique `/ecole` existait (manuel, historique
> et §1.2).

---

## Description fonctionnelle

Le service EPROM FormationDocument3 permet à l'école de **gérer la liste des attributions relatives
aux activités d'enseignement** (Doc 3) sauvegardées dans EPROM (manuel §1.1). Autrement dit : **quel
enseignant enseigne quelle activité (branche), et combien de périodes lui sont attribuées** (champs de
`Doc3EnseignantDetailCT`, contrat).

Il expose **2 opérations** (pas d'approbation directe, comme le Document 2) (manuel §1.1 ; contrat :
portType du WSDL) :

1. **LireDocument3** — fournit les informations du document 3.
2. **ModifierDocument3** — permet de modifier les données du document 3.

### Modèle de données (hiérarchie)

```
Document 3 (1 organisation de formation)
└── activiteListe
    └── activite (branches/activités d'enseignement : 0..N à la lecture, 1..N à l'écriture)
        ├── (référentiel : coCategorie, teNomBranche, noAnneeEtude)
        ├── (périodes de référence : nbPeriodesDoc8, nbPeriodesPrevuesDoc2, nbPeriodesReellesDoc2)
        └── enseignantListe
            └── enseignant (0..N attributions)
                ├── identité (noMatEns, teNomEns, tePrenomEns, teAbrEns, teEnseignant)
                ├── coDispo (disponibilité), teStatut (statut)
                └── nbPeriodesAttribuees
```

> **Pas de switch d'approbation dans la structure** : contrairement au Document 1 (`swAppPopD1` + `swAppD1`)
> et au Document 2 (`swAppD2`), `FormationDocument3CT` ne contient **aucun champ d'approbation**
> (contrat : `FormationDocument3_v1.xsd`). L'approbation du Doc 3 n'est ni lisible ni modifiable via ce
> service. En revanche, l'accès au Doc 3 est **conditionné** par l'approbation des documents amont (voir
> Règles métier, erreur `20102`).

> **Données de référence en lecture seule** : les périodes `nbPeriodesDoc8` (« doc8bis »),
> `nbPeriodesPrevuesDoc2` et `nbPeriodesReellesDoc2` (« document 2 ») viennent d'autres documents
> (manuel §3.1.3.4) et n'existent pas dans le type de requête `Doc3ActiviteDetailSaveCT` (contrat). Les
> libellés des erreurs `1538` et `1574`-`1576` (manuel §4) en font les plafonds des attributions.

> **Branches rendues** (observé en production, septembre 2026) : le Doc 3 rend toutes les branches
> du Doc 2, y compris celles à 0 période et les lignes 91 à 99. Les lignes 95 (`ExPT`) et 96
> (`SEtu`) acceptent des attributions.

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> Pattern **Common_v1** (ancien), identique à Formation Population (Doc 1), Formation Périodes (Doc 2)
> et Formations Liste v2 : `Common_v1.xsd` et `ResponseStatus_v3.xsd` sont identiques octet pour octet
> dans les quatre dossiers de `pyetnic/resources` (vérifié le 2026-11-24). Le `Messages` XSD importe bien
> `common:AbstractExternalResponseType` (contrat ; manuel §2.4).
> Voir la documentation détaillée dans `03_formation_population_v1.md` ou `00_REGISTRE.md`.

```
AbstractExternalResponseType (abstract)
├── success  : boolean       [obligatoire]
└── messages : messagesType  [0..1]
    ├── error   : MessageType [0..*]   (code [≤10c] + description + zone)
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```

Le `requestId` (UUID) est porté par un **header SOAP** : optionnel en requête, obligatoire en réponse
(contrat : `wsdl:required` du WSDL, `requestId_v1.xsd`), sur le endpoint EPROM seulement. S'il n'est pas
fourni, l'ETNIC en génère un, à joindre à toute demande de support (manuel §2.3).

---

## Opération 1 : LireDocument3

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document3/v1/LireDocument3`

### Requête

**Élément** : `LireDocument3` → **Type** : `LireDocument3RequeteCT` extends `FormationDocument3LireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST (string, motif `\d{4}-\d{4}`) | oui | Année scolaire (ex : `"2016-2017"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

> Contrat (`FormationDocument3_v1.xsd`, `Organisation_v1.xsd`, `AnneeScolaire_v1.xsd`) et manuel §3.1.3.2
> concordent. `OrganisationReqIdCT` ne contient **pas** d'`implId` (identique aux Documents 1 et 2).
> Voir `00_REGISTRE.md`.

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse).

### Réponse

**Élément** : `LireDocument3Reponse` → **Type XSD** : `Document3ReponseCT` extends `AbstractExternalResponseType`

> Le texte du manuel nomme ce type `LireDocument3ReponseCT` (§3.1.3.4) et `ModifierDocument3ReponseCT`
> (§3.1.4.4), mais ses diagrammes (p. 8 et 18) et le contrat (`EpromFormationDocument3Messages_external_v1.xsd`)
> n'ont qu'un **type unique partagé `Document3ReponseCT`**, porté par les éléments `LireDocument3Reponse`
> et `ModifierDocument3Reponse`.

```
Document3ReponseCT
├── success      : boolean                  [obligatoire] (hérité)
├── messages     : messagesType             [0..1]        (hérité)
└── response     : Document3ReponseMetierCT [0..1]
    └── document3 : FormationDocument3CT    [obligatoire]
```

### FormationDocument3CT (structure complète du document 3)

```
FormationDocument3CT
├── id           : OrganisationResIdCT  [obligatoire]   (avec implId [0..1])
└── activiteListe : Doc3ActiviteListeCT [0..1]
    └── activite : Doc3ActiviteDetailCT [0..*]
```

> **Doc 3 jamais encodé** (observé en production, 2025-2026) : un Doc 3 accessible mais jamais
> écrit se lit comme un squelette : une ligne par branche, `coNumAttribution` 1, matricule et
> statut vides, 0 période attribuée. `statutDocumentAttributions` (spec 01) reste absent jusqu'à
> la première écriture, puis passe à « Encodé école ». L'existence du document ne dit donc pas
> qu'il a été encodé.
>
> Sur TQ, en 2025-2026, tous les Doc 3 lisibles étaient de tels squelettes, alors que ceux de
> 2024-2025 portaient des attributions (observé sur TQ, 2026-11-24).

### Doc3ActiviteDetailCT (activité d'enseignement — réponse)

| Champ | Type (XSD) | Card. (XSD) | PDF | Description |
|---|---|---|---|---|
| `coNumBranche` | int | [0..1] | facultatif | Numéro de l'activité d'enseignement |
| `coCategorie` | string | [0..1] | facultatif | Code catégorie (table ci-dessous, identique Doc 2) |
| `teNomBranche` | string | [0..1] | facultatif | Nom de l'activité d'enseignement |
| `noAnneeEtude` | string | [0..1] | facultatif | Numéro de l'année d'étude |
| `nbPeriodesDoc8` | **int** | [0..1] | int, facultatif | Nombre de périodes au Doc 8bis |
| `nbPeriodesPrevuesDoc2` | **int** | [0..1] | texte : **float, obligatoire** ⚠️ (diagramme p. 9 : int [0..1]) | Périodes prévues au Document 2 |
| `nbPeriodesReellesDoc2` | **int** | [0..1] | texte : **float, obligatoire** ⚠️ (diagramme p. 9 : int [0..1]) | Périodes réelles au Document 2 |
| `enseignantListe` | Doc3EnseignantLstCT | [0..1] | 0 à 1 | Liste des attributions des enseignants |

> Colonnes « XSD » : contrat (`FormationDocument3_v1.xsd`) ; colonne « PDF » : manuel §3.1.3.4, p. 9-10.

> ⚠️ **Divergence de type / cardinalité (périodes Doc 2)** : le contrat déclare `nbPeriodesDoc8`,
> `nbPeriodesPrevuesDoc2` et `nbPeriodesReellesDoc2` en `xs:int` `minOccurs="0"`, comme le diagramme du
> manuel (p. 9) ; le texte du manuel (§3.1.3.4, p. 10) décrit les deux derniers en **`float` obligatoire**,
> et son exemple de réponse (§3.1.3.5, p. 13-14) **sérialise les trois compteurs avec décimales**
> (`<nbPeriodesDoc8>24.0</…>`, `<nbPeriodesPrevuesDoc2>24.0</…>`, `<nbPeriodesReellesDoc2>24.0</…>`).
> Le contrat prime : ce sont des entiers.
>
> **Le flux réel respecte `xs:int`** : un relevé en lecture seule de 123 organisations (765 attributions)
> n'a trouvé **aucune décimale** sur ces trois champs, alors que `nbPeriodesAttribuees` (`xs:float`)
> arrive sous la forme `20.0` (relevé sur TQ, année 2024-2025, rapport du 2026-06-11). Le « 24.0 » ne
> vient que de l'exemple du manuel. Si une décimale arrivait malgré tout, zeep (4.3.2) ne lèverait pas
> d'erreur : il journalise l'échec de conversion et rend `None` pour le champ (vérifié hors ligne sur
> le contrat embarqué, 2026-11-24). pyetnic lève alors `EtnicResponseError` (#52), qui nomme le champ
> et sa valeur brute (`values`) et garde le reste de la réponse (`response`).
>
> Exemple (observé une fois, année scolaire 2024-2025, environnement non consigné) : une branche
> dont les lignes sans `coDispo` totalisaient 4,5 périodes, pour un `nbPeriodesReellesDoc2` de 4, a
> été acceptée. Aucune règle n'en est tirée.

### Doc3EnseignantDetailCT (attribution d'enseignant — réponse, 11 champs)

| Champ | Type (XSD) | Card. | Description |
|---|---|---|---|
| `coNumAttribution` | int | [0..1] | Numéro de l'attribution d'enseignant |
| `noMatEns` | string | [0..1] | Matricule de l'enseignant : le matricule enseignant FWB (celui du listing de paie), distinct du NISS (observé en production sur 679 lignes appariées) |
| `teNomEns` | string | [0..1] | Nom de l'enseignant ; pas toujours complet : un nom composé a été vu tronqué à son premier élément (observé une fois, 2026-09) |
| `tePrenomEns` | string | [0..1] | Prénom de l'enseignant |
| `teAbrEns` | string | [0..1] | Code abréviation de l'enseignant |
| `teEnseignant` | string | [0..1] | Concaténation nom + prénom + matricule |
| `coDispo` | string | [0..1] | Code disponibilité (table §ModifierDocument3) |
| `teStatut` | string | [0..1] | Code statut (table §ModifierDocument3) |
| `nbPeriodesAttribuees` | float | [0..1] | Nombre de périodes attribuées à l'enseignant |
| `tsMaj` | string | [0..1] | Timestamp de la dernière mise à jour du document 3 ; forme `AAAA-MM-JJ hh:mm:ss.ffffff` (exemple du manuel §3.1.3.5 ; relevé sur TQ, rapport du 2026-06-11) |
| `teUserMaj` | string | [0..1] | Userid de la personne ayant effectué la dernière MAJ |

> Les 11 champs du contrat (`FormationDocument3_v1.xsd`) correspondent **exactement** au texte (p. 10)
> et au diagramme (p. 9) du manuel. `tsMaj`/`teUserMaj` ont été ajoutés en rev 1.1 (2018) et
> `nbPeriodesAttribuees` est passé en `float` en rev 1.2 (2019) (manuel, historique des révisions, p. 1).

### Table des catégories (`coCategorie`)

Valeurs possibles à la date du 01-05-2023 (manuel §3.1.3.4, p. 9-10 ; le contrat laisse un `xs:string`
libre), 30 codes. Mêmes 30 codes que la table `coCategorie` du Document 2 (spec 04, manuel du
30-09-2024), à un libellé près : `CTPe` y finit en « encadrement », ici en « encadremt ».

| Code | Libellé |
|---|---|
| `SEtu` | ADMISSION, SUIVI PEDAGOGIQUE, SANCTION |
| `Auto` | AUTONOMIE |
| `CP` | Cas particuliers |
| `CEtu` | CONSEIL DES ETUDES |
| `CG` | COURS GENERAUX |
| `CGen` | COURS GENERAUX - encadrement |
| `CGms` | COURS GENERAUX-methodologie speciale |
| `CGrn` | COURS GENERAUX-remise à niveau |
| `CPPM` | COURS PSYCHO-PEDAGOGIE ET METHODOLOGIE |
| `CS` | COURS SPECIAUX |
| `CSda` | COURS SPECIAUX-dactylo |
| `CSen` | COURS SPECIAUX-encadrement |
| `CTPe` | COURS TECHN.& PRATIQUE PROF. - encadremt |
| `CTPP` | COURS TECHNIQUES ET PRATIQUE PROFESSION. |
| `CTin` | COURS TECHNIQUES industriels |
| `CTni` | COURS TECHNIQUES non industriels |
| `CTen` | COURS TECHNIQUES-encadrement |
| `CTli` | COURS TECHNIQUES-labo industriels |
| `CTln` | COURS TECHNIQUES-labo non industriels |
| `CTms` | COURS TECHNIQUES-methodologie speciale |
| `CTst` | COURS TECHNIQUES-stages |
| `ExPT` | EXPERTISE PEDAGOGIQUE ET TECHNIQUE |
| `PSup` | PART SUPPLEMENTAIRE |
| `PeSu` | PERIODES SUPPLEMENTAIRES |
| `PPni` | PRATIQUE PROFESSION. non industrielle |
| `PPen` | PRATIQUE PROFESSION.-encadrement |
| `PPnu` | PRATIQUE PROFESSION.-nursing |
| `PPst` | PRATIQUE PROFESSION.-stages |
| `PPin` | PRATIQUE PROFESSIONNELLE industrielle |
| `PRET` | PRESTATIONS ETUDIANT |

### Exemple de requête XML

D'après le manuel (§3.1.3.3), espaces de noms corrigés selon le contrat : l'exemple du manuel écrit
`.../formation/Document3/messages/v1` et `.../types/formation/Document3/v1` avec une majuscule, que le
contrat n'a pas.

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document3/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document3/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:LireDocument3>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>1234</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
    </v1:LireDocument3>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (simplifié, 1 activité / 1 enseignant)

```xml
<LireDocument3Reponse xmlns="http://services-web.etnic.be/eprom/formation/document3/messages/v1">
  <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
  <response>
    <p784:document3 xmlns:p784="http://enseignement.cfwb.be/types/formation/document3/v1">
      <p784:id>
        <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2016-2017</p752:anneeScolaire>
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">1234</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">5678</p752:implId>
        <p752:numAdmFormation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">348</p752:numAdmFormation>
        <p752:numOrganisation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">1</p752:numOrganisation>
      </p784:id>
      <p784:activiteListe>
        <p784:activite>
          <p784:coNumBranche>1</p784:coNumBranche>
          <p784:coCategorie>PPni</p784:coCategorie>
          <p784:teNomBranche>DECOUVERTE DE LA FORMATION ET DE LA PROFESSION</p784:teNomBranche>
          <p784:noAnneeEtude>1</p784:noAnneeEtude>
          <p784:nbPeriodesDoc8>24.0</p784:nbPeriodesDoc8>
          <p784:nbPeriodesPrevuesDoc2>24.0</p784:nbPeriodesPrevuesDoc2>
          <p784:nbPeriodesReellesDoc2>24.0</p784:nbPeriodesReellesDoc2>
          <p784:enseignantListe>
            <p784:enseignant>
              <p784:coNumAttribution>1</p784:coNumAttribution>
              <p784:noMatEns>10101012345</p784:noMatEns>
              <p784:teNomEns>DUPONT</p784:teNomEns>
              <p784:tePrenomEns>MARIE</p784:tePrenomEns>
              <p784:teAbrEns>DUMA</p784:teAbrEns>
              <p784:teEnseignant>DUPONT MARIE 10101012345</p784:teEnseignant>
              <p784:coDispo/>
              <p784:teStatut>D</p784:teStatut>
              <p784:nbPeriodesAttribuees>0.0</p784:nbPeriodesAttribuees>
              <p784:tsMaj>2017-06-06 16:51:42.142658</p784:tsMaj>
              <p784:teUserMaj>ec001234</p784:teUserMaj>
            </p784:enseignant>
          </p784:enseignantListe>
        </p784:activite>
        <!-- ... autres activités ... -->
      </p784:activiteListe>
    </p784:document3>
  </response>
</LireDocument3Reponse>
```

> D'après l'exemple du manuel (§3.1.3.5, p. 11-14 : trois activités, ici réduit à une, identités
> remplacées). `coDispo` y est **vide** (`<coDispo/>`) : l'enseignant est en disponibilité « normale »
> (pas de code particulier). Le `teStatut` `"D"` = Définitif (table `teStatut`, manuel p. 17). Les réponses
> relevées sur TQ ont la même forme, `<coDispo/>` compris (rapport du 2026-06-11).

---

## Opération 2 : ModifierDocument3

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document3/v1/ModifierDocument3`

### Requête

**Élément** : `ModifierDocument3` → **Type** : `ModifierDocument3RequeteCT` extends `FormationDocument3ModifReqCT`

```
FormationDocument3ModifReqCT
├── id            : OrganisationReqIdCT      [obligatoire]
└── activiteListe : Doc3ActiviteListeSaveCT  [obligatoire]
    └── activite  : Doc3ActiviteDetailSaveCT [1..*]
```

> **Différence avec le Document 2** : ici `activiteListe` est **obligatoire** (pas `[0..1]`) et contient
> **au moins une** `activite` (`maxOccurs="unbounded"`, `minOccurs` implicite = 1 → `[1..*]`). Contrat
> (`FormationDocument3_v1.xsd`, à comparer à `FormationDocument2_v1.xsd`) et manuel (§3.1.4.2, p. 15 :
> « obligatoire », « 1 à N ») concordent.

### Doc3ActiviteDetailSaveCT (activité - requête)

| Champ | Type (XSD) | Card. (XSD) | PDF | Description |
|---|---|---|---|---|
| `coNumBranche` | int | **obligatoire** | texte : facultatif ⚠️ (diagramme : obligatoire) | Numéro de l'activité d'enseignement |
| `noAnneeEtude` | string | **obligatoire** | texte : facultatif ⚠️ (diagramme : obligatoire) | Numéro de l'année d'étude |
| `enseignantListe` | Doc3EnseignantLstSaveCT | **obligatoire** | texte : 0 à 1 ⚠️ (diagramme : obligatoire) | Liste des attributions des enseignants |

> ⚠️ **Divergence de cardinalité (requête Modifier)** : le texte du manuel (§3.1.4.2, p. 15) annote
> `coNumBranche`, `noAnneeEtude` (facultatif) et `enseignantListe` (« 0 à 1 ») comme optionnels, alors que
> le **contrat les rend obligatoires** (aucun `minOccurs="0"`), comme le diagramme de la même page. Le
> contrat prime ; zeep refuse d'ailleurs avant l'envoi une requête où il en manque un (vérifié hors ligne
> pour `noAnneeEtude`, 2026-11-24 ; voir « Mapping pyetnic »). Le couple `coNumBranche` + `noAnneeEtude` désigne l'activité à modifier ; la réponse du
> serveur à un couple absent du document n'est pas consignée (inconnu).

`Doc3EnseignantLstSaveCT` → `enseignant : Doc3EnseignantDetailSaveCT` : contrat et diagramme (p. 15)
`[1..*]` ⚠️, texte du manuel « 0 à N ». Une branche envoyée porte donc au moins une ligne ; la façon de
vider entièrement une branche n'est pas documentée (inconnu).

### Doc3EnseignantDetailSaveCT (attribution - requête)

| Champ | Type (XSD) | Card. (XSD) | Présent PDF ? | Description |
|---|---|---|---|---|
| `coNumAttribution` | int | [0..1] | **non dans le texte** ⚠️ (oui au diagramme p. 15) | Numéro de l'attribution (facultatif, ne cible rien : voir ci-dessous) |
| `noMatEns` | string | [0..1] | oui | Matricule enseignant FWB (celui du listing de paie), distinct du NISS |
| `coDispo` | string | [0..1] | oui | Code disponibilité (table ci-dessous) |
| `teStatut` | string | [0..1] | oui | Code statut (table ci-dessous) |
| `nbPeriodesAttribuees` | float | [0..1] | oui | Nombre de périodes attribuées |

> ⚠️ **Élément absent du texte du manuel** : `coNumAttribution` (premier élément de
> `Doc3EnseignantDetailSaveCT` dans le contrat) figure au diagramme du manuel (p. 15, `[0..1] int`) mais
> **pas dans la description du texte** (§3.1.4.2), qui ne liste que 4 champs. Il **ne cible aucune
> attribution** : `ModifierDocument3` remplace la liste entière de chaque branche envoyée (voir
> « Sémantique d'écriture »). Des lignes envoyées sans `coNumAttribution` sont acceptées et
> numérotées par le serveur (observé en production, plusieurs
> dizaines d'écritures, 2026-09). Une première ligne envoyée avec le numéro du squelette a gardé le
> n° 1 (observé une fois, 2026-09). Exposé dans le client comme paramètre optionnel.
>
> **Observé en production** : le numéro est un **compteur attribué par le serveur**, pas une position.
> Les numéros libérés ne sont pas repris (une branche réécrite peut porter les n° 1 et 5) : un trou
> dans la numérotation ne signale pas une ligne manquante.
>
> **Testé sur TQ (2026-11-24)** : une branche à une attribution (n° 1) réécrite avec cette ligne,
> renvoyée avec son `coNumAttribution`, suivie d'une nouvelle ligne sans numéro, se relit avec les n° 1
> (inchangée) et 2 ; réécrite ensuite avec la seule ligne d'origine et son numéro, elle se relit à
> l'identique, n° 1 compris. Renvoyer `coNumAttribution` conserve donc le numéro d'une ligne gardée.
> C'est ce que fait `ajouter_attributions_document_3` (lire, garder les lignes de la branche avec leur
> numéro, ajouter les nouvelles, réécrire les seules branches touchées).

> **Comparaison réponse vs requête** (contrat) : le type Save n'a pas les champs en lecture seule de la
> réponse (`teNomEns`, `tePrenomEns`, `teAbrEns`, `teEnseignant`, `tsMaj`, `teUserMaj`, ni les périodes
> Doc2/Doc8 / `coCategorie` / `teNomBranche`). On envoie : numéro d'attribution (facultatif), matricule,
> dispo, statut, périodes attribuées.

### Table des codes de disponibilité (`coDispo`)

Valeurs possibles à la date du 01-05-2023, « validé hors contrat xml » (manuel §3.1.4.2, p. 15-17) : le
contrat laisse un `xs:string` libre, le serveur contrôle la valeur (erreur `20109`, manuel §4).
La 1ʳᵉ colonne est le code tel qu'il circule, **sur deux chiffres** : en production, `05`, `15` et
`28` ont été relus, `05` et `15` écrits puis relus (2026-09-22/23) ; un relevé TQ de 765 attributions
(année 2024-2025, rapport du 2026-06-11) n'a rencontré que ces trois codes (`15` : 104 lignes, `05` : 5,
`28` : 1) ; la liste déroulante de l'écran écrit `02` à `09` (spec 20, §2.2). Le manuel, lui, écrit
`2`, `3`, `4`, `5`, `7` et `9` sans zéro dans sa colonne « Code » (p. 15-16), ses libellés commençant
par `02` à `09` : `5` sans zéro n'a jamais été essayé. Le libellé reprend généralement le code en préfixe.

| Code | Libellé |
|---|---|
| `BE` | BE Bénévolat |
| `02` | 02 Dispo retrait emploi interet service |
| `03` | 03 Dispo mesure disciplinaire |
| `04` | 04 Dispo mission spéciale:gvt,orga inter |
| `05` | 05 Dispo pour maladie (même traitement) |
| `07` | 07 Dispo convenances personnelles |
| `09` | 09 Absence longue durée rais.familiales |
| `11` | 11 Dispo mission spéciale:gvt,orga inter |
| `12` | 12 Congé pr mission:cabinet du Roi |
| `13` | 13 Congé pr mission:groupe politique |
| `14` | 14 Accompagnement FSE ou EHR |
| `15` | 15 Périodes prises en charge Convention |
| `20` | 20 Congé inter.carrière (rempl chômeur) |
| `23` | 23 Accident de travail |
| `24` | 24 Maladie professionnelle |
| `25` | 25 Dispo pour maladie (autre traitement) |
| `27` | 27 Congé maladie ou infirmité rémunéré |
| `28` | 28 Congé maternité rémunéré par la CF |
| `29` | 29 Congé allaitement ou parental |
| `30` | 30 Congé inter.carrière (pas rempl chôm) |
| `31` | 31 Congé de prophylaxie |
| `32` | 33 Désignation provisoire dans une fonct *(sic : libellé préfixé « 33 » dans le manuel, p. 16)* |
| `33` | 33 Désignation en qualité de juré dans |
| `35` | 35 Congé pr mission:SHAPE |
| `36` | 36 Dispo mission spéciale:école europé. |
| `37` | 37 Congé pr mission:organ.jeunesse |
| `38` | 38 Congé pr mission:cabinets,jurys CF |
| `39` | 39 Congé pr mission:associations parents |
| `44` | 44 Congé pr mission:organisations PO |
| `45` | 45 Détachement "De Laet" CF |
| `46` | 46 Congé pour suivre des cours |
| `47` | 47 Prest.réduites + 50ans & 2 enf<14 ans |
| `48` | 48 Déta. fct sel/promo (titu malade) |
| `50` | 50 Congé pr mission:enseign/guidance PMS |
| `52` | 52 Dés.prov:même niveau&rés-titu malade |
| `53` | 53 Dés.prov:autre niveau&rés-titu malade |
| `54` | 54 Suspension disciplinaire |
| `55` | 55 Suspension préventive |
| `58` | 58 Congé politique |
| `60` | 60 Congé accueil pr adoption ou tutelle |
| `61` | 61 Congé pr mission:cabinet non CF |
| `62` | 62 Congé pr mission:programme spécifique |
| `63` | 63 Congé pr mission:orga éduc permanente |
| `64` | 64 Prest.réduites maladie ou infirmité |
| `65` | 65 Congé pr mission non repris nb global |
| `67` | 67 Congé pr mission non repris nb global |
| `69` | 69 Congé syndical permanent |
| `70` | 70 Prest.réduites rais.sociales/famil. |
| `71` | 71 Prest.réduites raisons personnelles |
| `74` | 74 Prest.réduites membres du personnel |
| `76` | 76 Congé de maladie payé par la mutuelle |
| `78` | 78 Congé de maternité payé par la mutuel |
| `79` | 79 Congé raisons familiales |
| `80` | 80 Détachement EHR/CEFA |
| `81` | 81 Déta. fct sel/promo (titu non malade) |
| `94` | 94 Dés.prov:même niv&rés-titu non malade |
| `95` | 95 Dés.prov:autre niv&rés-titu n malade |
| `97` | 97 Absence non règlement. justifiée |
| `98` | 98 Dispo mission spéciale(pas nb glob) |
| `99` | 99 Dispo mission spéciale(pas nb glob) |

> La table du manuel compte 60 codes. La liste déroulante de l'écran du Doc 3 en compte 58
> distincts : `32` et `45` n'y figurent pas, et `33` y apparaît deux fois (spec 20, §2.2). Écart
> non expliqué.

> Un `coDispo` **vide** (chaîne vide) correspond à un enseignant sans disponibilité particulière
> (situation « normale », voir l'exemple de réponse, manuel §3.1.3.5 et §3.1.4.3). C'est le cas le plus
> courant : 655 des 765 lignes du relevé TQ (rapport du 2026-06-11). Un élément `coDispo` **omis** est
> accepté et se relit vide, c'est-à-dire sans code (observé en production, 2026-09).

### Table des codes de statut (`teStatut`)

Valeurs possibles à la date du 01-05-2023, « validé hors contrat xml » (manuel §3.1.4.2, p. 17) : le
contrat laisse un `xs:string` libre, le serveur contrôle la valeur (erreur `20110`, manuel §4). Libellés
du manuel à l'orthographe près (il écrit « Definitif » et « EXpertise pégagogique et technique ») ;
l'écran du Doc 3 donne les libellés ci-dessous (spec 20, §2.1).

| Code | Libellé |
|---|---|
| `C` | ACS |
| `P` | ACS Discriminations Positives |
| `A` | Définitif Accessoire |
| `D` | Définitif |
| `E` | Expert |
| `X` | Expertise pédagogique et technique |
| `T` | Temporaire |

> **Observé en production** : `T`, `D` et `E` sont confirmés comme Temporaire, Définitif et Expert
> (mesuré le 2026-09-19 sur 679 lignes de trois années). `A`, `C`, `P` et `X` non observés : `X`
> sur 0 des 679 lignes, et aucun des quatre parmi les 765 attributions du relevé sur TQ (année
> 2024-2025, rapport du 2026-06-11), où `T`, `E` et `D` comptent 231, 53 et 40 lignes et 441 lignes
> ont un `teStatut` vide. C'est une observation, pas une règle. Le statut appartient à la ligne, pas à la personne : une même
> personne a été vue en `T`, `D` et `E` sur trois organisations de la même UE, la même année.

### Réponse

**Type** : `Document3ReponseCT`, élément `ModifierDocument3Reponse` (contrat : le même type que pour
LireDocument3). La réponse porte le document 3 (`document3`, « détail du document 3 », manuel §3.1.4.4).
Qu'elle reflète toutes les branches après l'écriture n'est pas consigné : relire le document entier
(voir « Sémantique d'écriture »). L'exemple de réponse du manuel (§3.1.4.5) est un `LireDocument3Reponse`
recopié de §3.1.3.5.

### Exemple de requête XML

D'après le manuel (§3.1.4.3), identités remplacées.

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document3/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document3/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ModifierDocument3>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>1234</v12:etabId>
        <v12:numAdmFormation>348</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
      <v11:activiteListe>
        <v11:activite>
          <v11:coNumBranche>1</v11:coNumBranche>
          <v11:noAnneeEtude>1</v11:noAnneeEtude>
          <v11:enseignantListe>
            <v11:enseignant>
              <v11:noMatEns>10101012345</v11:noMatEns>
              <v11:coDispo></v11:coDispo>
              <v11:teStatut>D</v11:teStatut>
              <v11:nbPeriodesAttribuees>24.0</v11:nbPeriodesAttribuees>
            </v11:enseignant>
          </v11:enseignantListe>
        </v11:activite>
      </v11:activiteListe>
    </v1:ModifierDocument3>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Codes d'erreur

Table du manuel (§4, p. 22 ; 15 codes), dans l'ordre des codes. Les observations sont celles consignées
dans cette spec ; la classe levée par pyetnic est dans « Mapping pyetnic ».

| Success | Code | Description (libellé exact PDF) | Type |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | — |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | commun |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | commun (concurrence) |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | commun (sécurité) |
| `false` | `00999` | Erreur sql : | commun (technique) |
| `false` | `1113` | Année scolaire invalide | validation entrée |
| `false` | `1114` | Numéro d'établissement incorrect | validation entrée |
| `false` | `1538` | Périodes Doc3 $1 > périodes Doc2 + IE par branche $2 | cohérence métier (non observé en production) |
| `false` | `1574` | Total attributions $1 > total périodes organisées dans formation $2 | cohérence métier (observé en production, 2026-09-22) |
| `false` | `1575` | Périodes CG attribuées $1 > réel CG + IE CG $2 | cohérence métier (non observé en production) |
| `false` | `1576` | Périodes CP attribuées $1 > réel CP + IE CP $2 | cohérence métier (non observé en production) |
| `false` | `20102` | Les "Doc A" et "Doc 2" doivent être approuvés pour pouvoir accéder au "Doc 3" | **workflow inter-documents** |
| `false` | `20108` | Le numéro de matricule d'enseignement n°$1 est incorrect | validation attribution (observé en production, 2026-09-21) |
| `false` | `20109` | Le code dispo d'enseignement n°$1 est incorrect | validation attribution |
| `false` | `20110` | Le statut d'enseignement $1 est incorrect | validation attribution |
| `false` | `99999` | (Autres Erreurs) | fourre-tout |

> Les `$1`, `$2` sont des **paramètres substitués** par le serveur (valeurs/zones concernées) : le
> message `1574` reçu en production portait des nombres à la place (« 72,00 », voir plus bas). Le manuel
> renvoie à une « section 5 » pour ces codes (§2.4) ; la table est en §4.

### Codes partagés / spécifiques
D'après la table des codes de `00_REGISTRE.md` (§4) :
- **Communs à tous les services EPROM** : `00009`, `00025`, `00999`, `99999`.
- **Communs Documents 1/2/3** : `00011`, `1113`, `1114`.
- **Spécifiques Document 3** : `1538`, `1574`, `1575`, `1576`, `20102`, `20108`, `20109`, `20110`.

---

## Règles métier & workflow inter-documents

### ⭐ Workflow inter-documents

**Erreur `20102` : « Les "Doc A" et "Doc 2" doivent être approuvés pour pouvoir accéder au "Doc 3" »**
(manuel §4).

D'après ce libellé, **le Document 3 (Attributions) n'est accessible (lecture/modification) que si les
documents amont sont approuvés.** Le refus `20102` lui-même n'est pas consigné dans les observations de
production ou de TQ de cette spec (à confirmer).

- `« Doc 2 »` = **Document 2 (Périodes)**, approuvé via le switch `swAppD2` : le service Document 2 n'a
  pas d'opération d'approbation, l'administration bascule le switch (spec 04 ; observé une fois en
  production, 2026-09-19).
- `« Doc A »` = **l'organisation elle-même** (service Formation Organisation, v8 aujourd'hui), et non le
  Document 1 : le manuel Formation Organisation v8 (rev 6.0, §1.1 et §3.1.1) appelle « dossier de
  formation (Doc A) » ce que gère ce service, et l'écran EPROM, dont le tableau « Documents annuels »
  liste `Doc A`, `Doc 1 et 2`, `Doc 1D`, `Doc 3` (spec 20, §1.1), le distingue du Doc 1. Le Document 1
  attend lui aussi le Doc A (`20101`, testé sur TQ, 2026-11-10 ; spec 03).

Chaîne de dépendance :

```
Organisation = Doc A (Formation Organisation v8)  ──approuvée par l'administration──┐
Document 2 (Périodes)                             ──approuvé (swAppD2)──────────────┤
                                                                                    ▼
                                                  Document 3 (Attributions)  ← accessible seulement ici
```

Le Document 1 (Population) et le Doc 1D (droits d'inscription) ne figurent pas dans le libellé de
`20102` : ils ne conditionnent pas l'accès au Doc 3 par cette erreur. En pratique `LireDocument2` est
refusé (`20103`) tant que la population du Doc 1 n'est pas validée (testé sur TQ, 2026-11-10 ; spec 04),
et l'administration a approuvé Doc 1 et Doc 2 ensemble (`swAppD1` et `swAppD2` basculés en même temps,
observé une fois en production, 2026-09-19 ; specs 03 et 04).

### Contrôles de cohérence sur les périodes attribuées

D'après les libellés du manuel (§4), les attributions ne peuvent dépasser les périodes organisées
(issues du Doc 2, IE comprises) :

- `1574` - la **somme des périodes attribuées sur les lignes sans `coDispo`** ne peut excéder le
  **total des périodes organisées** dans la formation. Une ligne portant un `coDispo` n'entre pas
  dans ce total (observé en production, 2026-09) : 116 périodes envoyées pour un Doc 2 de 96, dont
  20 sur une ligne codée, ont été acceptées et relues ; les Doc 3 de 2024-2025 tombent sur leur
  Doc 2 à la période près une fois les lignes codées retirées ; l'écran EPROM affiche « Périodes
  déjà attribuées 40,00 » pour six lignes totalisant 72.
- `1538` - par branche, les **périodes Doc 3** ne peuvent excéder **périodes Doc 2 + IE** (intervention
  extérieure) de la branche (non observé en production).
- `1575` - les périodes **CG** attribuées ≤ réel CG + IE CG (non observé en production).
- `1576` - les périodes **CP** attribuées ≤ réel CP + IE CP (non observé en production).

> Le manuel du Doc 3 ne définit pas `CG` et `CP`. Ce sont à la fois des codes de `coCategorie` (`CG`
> COURS GENERAUX, `CP` Cas particuliers, table ci-dessus) et des types de périodes d'intervention
> extérieure du Document 2 (`coCodePar` : `CG` Cas généraux, `CP` Cas particuliers, `SU` Suppléments ;
> spec 04) ; lequel des deux le serveur compte est inconnu. D'après ces libellés, les périodes
> d'intervention extérieure (IE) du Doc 2 augmentent le plafond attribuable.

**Le plafond se lit sur le réel** (observé en production) : sur une organisation dont le Doc 2 porte
20 périodes prévues et 60 réelles, 60 périodes attribuées passent sans `1574`. Dès que le réel est
rempli, c'est lui qu'il faut comparer, pas le prévu.

Le `$1` du message `1574` n'est pas toujours la somme envoyée : il a annoncé « 72,00 » pour 80
périodes envoyées sans `coDispo` (observé une fois, 2026-09-22, inexpliqué).

### ⚠️ Sémantique d'écriture : `ModifierDocument3` remplace la liste de chaque branche envoyée

**Pour chaque branche présente dans la requête, la liste d'enseignants envoyée remplace celle du
serveur ; elle ne la complète pas.** Envoyer la seule attribution à ajouter **efface les autres
attributions de la branche**. Observé en production : l'envoi de la ligne d'un remplaçant a effacé
celle du titulaire sur la même branche.

- Toujours envoyer la **liste complète** de chaque branche touchée (ce qui rend une réécriture
  idempotente : une branche renvoyée à l'identique garde son contenu et sa numérotation, seul
  `tsMaj` bouge ; observé le 2026-09-23 sur trois UE).
- Les branches absentes de la requête ne sont pas touchées (observé en production, 2026-09).
- Une branche peut porter plusieurs lignes au même `noMatEns` (`teStatut` différents, `coDispo`
  différents, voire triplets identiques) : le serveur les garde séparées, sans les fusionner ni les
  refuser. Une relecture ne peut donc pas apparier sur le seul matricule (observé en production,
  2026-09-22/23).
- Après écriture, **relire le document entier**, pas seulement les lignes envoyées : une relecture
  limitée à ce qu'on a envoyé ne voit pas ce qu'on a effacé.

### Validations d'attribution
- `20108` - matricule enseignant inexistant/incorrect. Renvoyé aussi pour un matricule bien formé
  quand l'enseignant n'est pas (encore) au référentiel enseignants d'EPROM ; transmettre son
  document de paie ne l'y inscrit pas, et le même payload passe une fois le référentiel à jour
  (observé en production : refusé le 2026-09-21, accepté le 2026-09-22). Ce référentiel est
  alimenté hors de ces services. Une écriture refusée en `20108` ne laisse rien : l'organisation
  reste vierge et le même payload peut être rejoué (observé deux fois sur des documents vierges,
  2026-09-21/22 ; non vérifié pour `1574` ni sur un document déjà rempli).
- `20109` - `coDispo` hors liste autorisée (libellé du manuel §4 ; aucune observation consignée).
- `20110` - `teStatut` hors liste autorisée (libellé du manuel §4 ; aucune observation consignée).
- `00011` - « Enregistrement modifié par un autre utilisateur ! » (manuel §4). La requête Modifier ne
  porte ni `tsMaj` ni numéro de version (contrat) : ce qui déclenche ce code au Doc 3 est inconnu
  (aucune observation consignée).

### Points spécifiques demandés (cohérence cross-services)
- **`coCategorie`** : mêmes 30 codes que la table du Document 2 (manuels ; un libellé diffère, voir la
  table) → un seul référentiel partagé. ✓
- **`coCatCol`** (types d'intervention extérieure) : **sans objet pour le Document 3**. Le contrat du
  Doc 3 n'a aucun champ d'intervention extérieure (`FormationDocument3_v1.xsd`) ; il n'en voit que
  l'effet agrégé (IE incluse dans les plafonds de périodes, d'après les libellés `1538`/`1575`/`1576`).
- **`typeInterventionExterieure "J"`** (Réorientation 7TQ/7P) : **sans objet ici**, propre à
  Formation Organisation et aux interventions extérieures du Document 2 (absent du contrat du Doc 3).

---

## Vérification croisée UML / XSD / PDF

> Les « diagrammes » du PDF sont des **boîtes de classes UML repliées** (marqueur `+` d'expansion) : elles
> montrent les références de types et les cardinalités, le détail des champs étant donné dans le **texte**
> sous chaque diagramme. Le contrat **XSD reste la référence** ; pages rendues en image et inspectées : 8, 9, 10, 14, 15, 22
> (2026-06-02), puis 8, 9, 10, 15, 16, 17, 18, 22 (2026-11-24). Quand le texte et le diagramme divergent,
> le diagramme suit le contrat.

### Page 7 (exemple de requête LireDocument3, §3.1.3.3)
- ⚠️ Espaces de noms écrits `.../formation/Document3/...` (majuscule), contrairement au contrat et à
  l'exemple ModifierDocument3 (§3.1.4.3), en minuscules.

### Page 8 (réponse LireDocument3 - chaîne `Document3ReponseCT` → `FormationDocument3CT`)
- ✅ `Document3ReponseCT` (success + response) → `Document3ReponseMetierCT` (document3) → `FormationDocument3CT`
  (id + activiteListe `[0..1]`) : diagramme conforme au XSD ; le texte nomme le type `LireDocument3ReponseCT`.
- ⚠️ **`implId`** dans `OrganisationResIdCT` : le **diagramme affiche `[0..1]`** (conforme XSD `minOccurs="0"`),
  mais le **texte dit « obligatoire »** (§3.1.3.4, p.8 + définition `ImplIdST` p.9). **Même divergence
  qu'en session 3** (Documents 1 et 2). Le XSD/diagramme (optionnel) prime ; l'`implId` figure dans
  l'exemple du manuel et dans les réponses relevées sur TQ (rapport du 2026-06-11).

### Page 9 (`OrganisationResIdCT`, `Doc3ActiviteListeCT`, `Doc3ActiviteDetailCT`)
- ✅ `Doc3ActiviteListeCT.activite` = `[0..N]` : conforme XSD `maxOccurs="unbounded" minOccurs="0"`.
- ✅ 8 champs de `Doc3ActiviteDetailCT` présents ; table `coCategorie` (30 codes) conforme au Doc 2.
- ⚠️ `nbPeriodesPrevuesDoc2` / `nbPeriodesReellesDoc2` : texte (p. 10) « float, obligatoire » vs XSD
  « int, `[0..1]` », que le diagramme (p. 9) suit (voir divergence de type ci-dessus).

### Page 10 (`Doc3EnseignantLstCT`, `Doc3EnseignantDetailCT`)
- ✅ `Doc3EnseignantDetailCT` : **11 champs** du texte = 11 éléments du XSD (tous `[0..1]`). Aucune divergence.

### Pages 14-15 (requête ModifierDocument3)
- ✅ `FormationDocument3ModifReqCT` : `id` + `activiteListe` (obligatoire) ; `OrganisationReqIdCT` **sans
  `implId`** (4 champs) ; `Doc3ActiviteListeSaveCT.activite` = **`[1..*]`** (visible dans le diagramme). — conforme XSD.
- ⚠️ `Doc3ActiviteDetailSaveCT` : texte « facultatif » pour `coNumBranche`/`noAnneeEtude` et « 0 à 1 »
  pour `enseignantListe`, alors que le **XSD les rend obligatoires**, comme le diagramme (p. 15).
- ⚠️ `Doc3EnseignantDetailSaveCT` : le **XSD contient `coNumAttribution` (1ᵉʳ champ, `[0..1]`)**, comme le
  diagramme (p. 15), mais il est **absent de la liste du texte** (qui ne décrit que `noMatEns`, `coDispo`,
  `teStatut`, `nbPeriodesAttribuees`). Tables `coDispo` (60 codes, p. 15-17, colonne « Code » sans zéro
  pour `2` à `9`) et `teStatut` (7 codes, p. 17) données dans le texte uniquement.

### Page 18 (réponse ModifierDocument3, §3.1.4.4 et §3.1.4.5)
- ✅ Diagramme : `ModifierDocument3Reponse` → `Document3ReponseCT`, conforme au XSD ; le texte nomme le type
  `ModifierDocument3ReponseCT`.
- ⚠️ L'exemple de réponse (p. 18-22) est un `LireDocument3Reponse`, recopié de §3.1.3.5.

### Page 22 (table des erreurs)
- ✅ 15 codes d'erreur + ligne succès. Libellé `20102` confirmé **littéralement « Doc A » / « Doc 2 »**
  (couche texte native, pas une erreur d'OCR).

### Récapitulatif des divergences PDF ↔ XSD

Colonne « PDF » : le texte du manuel, avec le diagramme entre parenthèses quand il diffère du texte.
Colonne « pyetnic » : ce que fait le code (voir « Mapping pyetnic »).

| # | Élément | PDF | XSD | pyetnic |
|---|---|---|---|---|
| 1 | `OrganisationResIdCT.implId` | obligatoire (diagramme : `[0..1]`) | `minOccurs="0"` | non repris de la réponse : `FormationDocument3.id` est l'`OrganisationId` de l'appelant |
| 2 | `nbPeriodesPrevuesDoc2` | float, obligatoire (diagramme : int `[0..1]`) | `int`, `[0..1]` | `Optional[int]` ; le flux relevé ne porte pas de décimale (voir plus haut) |
| 3 | `nbPeriodesReellesDoc2` | float, obligatoire (diagramme : int `[0..1]`) | `int`, `[0..1]` | idem |
| 4 | `nbPeriodesDoc8` | int, facultatif ; « 24.0 » dans l'exemple | `int`, `[0..1]` | `Optional[int]` |
| 5 | `Doc3ActiviteDetailSaveCT.coNumBranche` | facultatif (diagramme : obligatoire) | obligatoire | champ obligatoire de `Doc3ActiviteDetailSave` |
| 6 | `Doc3ActiviteDetailSaveCT.noAnneeEtude` | facultatif (diagramme : obligatoire) | obligatoire | idem |
| 7 | `Doc3ActiviteDetailSaveCT.enseignantListe` | 0 à 1 (diagramme : obligatoire) | obligatoire | idem |
| 8 | `Doc3EnseignantLstSaveCT.enseignant` | 0 à N (diagramme : `[1..*]`) | `[1..*]` | liste vide refusée par zeep avant l'envoi |
| 9 | `Doc3EnseignantDetailSaveCT.coNumAttribution` | absent du texte (diagramme : `[0..1]`) | présent `[0..1]` | `Optional[int]` de `Doc3EnseignantDetailSave` |
| 10 | Type des réponses | `LireDocument3ReponseCT`, `ModifierDocument3ReponseCT` (diagrammes : `Document3ReponseCT`) | `Document3ReponseCT` partagé | sans effet (zeep lit le contrat) |
| 11 | Espaces de noms de l'exemple Lire (§3.1.3.3) | `.../Document3/...` | `.../document3/...` | ceux du contrat |

---

## Mapping pyetnic

État du code au 2026-11-24 : `pyetnic/services/document3.py`, `pyetnic/services/models.py`,
`pyetnic/exceptions.py`, symboles exportés par `pyetnic.eprom`.

| Élément du contrat | pyetnic (`pyetnic.eprom`) |
|---|---|
| `LireDocument3` | `lire_document_3(organisation_id)` -> `FormationDocument3` |
| `ModifierDocument3` | `modifier_document_3(organisation_id, activite_liste)` -> `FormationDocument3` : l'écriture brute, qui remplace la liste de chaque branche envoyée |
| *(pas d'opération)* | `ajouter_attributions_document_3(organisation_id, activite_liste)` -> `FormationDocument3` : lit le document, puis écrit chaque branche donnée avec ses lignes actuelles suivies des nouvelles |
| `OrganisationReqIdCT` | `OrganisationId` ; `implId` jamais envoyé |
| `FormationDocument3CT` | `FormationDocument3` (`id`, `activiteListe`) |
| `Doc3ActiviteListeCT` / `Doc3ActiviteDetailCT` | `Doc3ActiviteListe` / `Doc3ActiviteDetail` (8 champs) |
| `Doc3EnseignantLstCT` / `Doc3EnseignantDetailCT` | `Doc3EnseignantList` / `Doc3EnseignantDetail` (11 champs) |
| `Doc3ActiviteListeSaveCT` / `Doc3ActiviteDetailSaveCT` | `Doc3ActiviteListeSave` / `Doc3ActiviteDetailSave` (`coNumBranche`, `noAnneeEtude`, `enseignantListe`, tous trois sans valeur par défaut) |
| `Doc3EnseignantLstSaveCT` / `Doc3EnseignantDetailSaveCT` | `Doc3EnseignantListSave` / `Doc3EnseignantDetailSave` (5 champs facultatifs, `coNumAttribution` compris) |

- **Noms et types** : les dataclasses reprennent les noms du contrat. `coNumBranche` et
  `coNumAttribution` sont des `int` ; `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2` et
  `nbPeriodesReellesDoc2` des `Optional[int]`, comme le contrat (audit D7) ; `nbPeriodesAttribuees` un
  `Optional[float]` ; `noAnneeEtude`, `coCategorie`, `coDispo`, `teStatut`, `tsMaj` et `teUserMaj` des
  `str`. `coDispo` et `teStatut` ne sont pas des énumérations : leurs tables sont « hors contrat » et
  le serveur les contrôle (`20109`, `20110`).
- **Transport** : zeep suit le binding du WSDL embarqué (SOAP 1.1 seul), sur le endpoint spécifique
  EPROM, sans WS-Addressing, avec un `UsernameToken` WS-Security (login / mot de passe de la
  configuration). Chaque appel envoie un `requestId` UUID neuf dans l'en-tête, repris par les exceptions
  (`request_id`).
- **Identifiant** : la réponse porte un `OrganisationResIdCT` avec `implId` ; `FormationDocument3.id`
  est l'`OrganisationId` passé par l'appelant, l'`implId` de la réponse n'est pas repris.
- **Éléments vides** : zeep lit un élément vide (`<coDispo/>`, le `noMatEns` ou le `teStatut` d'un
  squelette) comme `None`, pas comme une chaîne vide. À l'écriture, un champ `None` n'est pas envoyé
  (`to_soap_dict`) : un `coDispo` omis se relit vide (voir la table `coDispo`) ; `coDispo=""` envoie un
  élément vide, comme l'exemple du manuel. Une décimale sur un champ `xs:int` lève
  `EtnicResponseError` au lieu d'être lue `None` (voir la divergence de type). Vérifié hors ligne sur
  le contrat embarqué avec zeep 4.3.2, 2026-11-24.
- **Forme de la requête** : zeep valide la requête contre le contrat avant l'envoi. Une liste
  d'activités ou d'enseignants vide, ou un `noAnneeEtude` manquant, lève
  `zeep.exceptions.ValidationError` sans appel au serveur (vérifié hors ligne, 2026-11-24) ; cette
  exception n'est pas une `EtnicError`.
- **`ajouter_attributions_document_3`** : une lecture, puis une écriture des seules branches données.
  Chaque branche est retrouvée par le couple (`coNumBranche`, `noAnneeEtude`) ; une branche absente du
  document lu lève `ValueError` avant toute écriture. Les lignes actuelles sont renvoyées avec leur
  `coNumAttribution`, `noMatEns`, `coDispo`, `teStatut` et `nbPeriodesAttribuees`, puis les nouvelles
  lignes ; une ligne actuelle sans matricule (celle d'un squelette) n'est pas renvoyée. Le
  comportement serveur sur lequel repose ce choix est le test TQ du 2026-11-24 (voir
  `coNumAttribution`). Rend la réponse de l'écriture ; dans le mode permissif déprécié, une lecture
  refusée rend `None` sans rien écrire.
- **Erreurs** (`pyetnic.exceptions`) : depuis 0.3.0, tout refus (`success=false`) lève par défaut une
  sous-classe d'`EtnicBusinessError` portant `code`, `description` (le libellé reçu, paramètres `$1`/`$2`
  substitués compris) et `request_id` ; `permissive_errors()` rend l'ancien `None`, déprécié.
  Routage des codes du Doc 3 :

  | Classe levée | Codes |
  |---|---|
  | `EtnicDocumentNotAccessibleError` | `20102` |
  | `EtnicNotFoundError` | `00009` |
  | `EtnicConcurrencyError` | `00011` |
  | `EtnicValidationError` | `1113`, `1114`, `1538`, `1574`, `1575`, `1576`, `20108`, `20109`, `20110` |
  | `EtnicBusinessError` (classe de base) | `00025`, `00999`, `99999` |

  Une erreur de transport (SOAP Fault, HTTP, réseau) lève `EtnicTransportError` (alias `SoapError`) ;
  une réponse dont une valeur viole son type, `EtnicResponseError`.
- **Pas de validation côté client** des plafonds (`1538`, `1574`-`1576`), des tables `coDispo` /
  `teStatut` ni des prérequis du workflow (`20102`) : le serveur décide et son refus arrive typé (voir
  « Scope Boundary » dans `docs/ARCHITECTURE.md`). Les statuts des documents se lisent par
  `lister_formations` (`statutDocumentAttributions`, spec 01).
- Classement (`docs/PUBLIC_API_SURFACE.md`) : `lire_document_3`, `modifier_document_3` et les modèles
  `Doc3*` sont stables ; `ajouter_attributions_document_3` est « construction ».

---

## XSD utilisés

| Fichier XSD | Rôle | Identique au Document 2 (session 3) ? |
|---|---|---|
| `FormationDocument3_v1.xsd` | **spécifique** (types doc3, v1.1) | nouveau (équivalent structurel à FormationDocument2) |
| `EpromFormationDocument3Messages_external_v1.xsd` | **spécifique** (messages, éléments racine) | nouveau |
| `Organisation_v1.xsd` | partagé (OrganisationReqIdCT / ResIdCT, v2.0) | ✅ byte-for-byte identique |
| `Common_v1.xsd` | partagé (AbstractExternalResponseType) | ✅ byte-for-byte identique |
| `AnneeScolaire_v1.xsd` | partagé | ✅ byte-for-byte identique |
| `Etablissement_v1.xsd` | partagé (EtabIdST, ImplIdST) | ✅ byte-for-byte identique |
| `ResponseStatus_v3.xsd` | partagé (MessageType) | ✅ byte-for-byte identique |
| `requestId_v1.xsd` | partagé (header UUID) | ✅ byte-for-byte identique |
| `Addressing_v2.xsd` | partagé (déprécié, endpoint Ecole) | ✅ byte-for-byte identique |
| `Authorisation_v2.xsd` | partagé (déprécié) | ✅ byte-for-byte identique |

> Vérification réalisée par `cmp` des 8 XSD partagés entre `pyetnic/resources/EPROM_Document_3_1.0/xsd/`
> et `pyetnic/resources/EPROM_Formation_Periodes_1.0/xsd/` → **aucune différence** (2026-11-24) ; même
> résultat avec `EPROM_Formation_Population_1.0/xsd/` (Document 1).

---

## Synthèse de la session 4

- **2 opérations** : LireDocument3, ModifierDocument3 (**pas d'Approuver**, comme Doc 2).
- **SOAP 1.1 uniquement** (binding WSDL + PDF), comme les autres services EPROM.
- **Pattern Common_v1** (ancien), bloc retour `AbstractExternalResponseType`.
- **Modèle hiérarchique** : activité (branche) → enseignants attribués + périodes.
- **Workflow** (libellé de l'erreur `20102`, manuel §4) : Doc 3 inaccessible tant que « Doc A »
  (l'organisation) **et** Doc 2 (Périodes) ne sont pas approuvés.
- **`coCategorie`** partagé avec le Doc 2 (référentiel commun). Pas de `coCatCol` / intervention
  extérieure propre au Doc 3.
- **2 nouvelles tables de valeurs** : `coDispo` (60 codes de disponibilité) et `teStatut` (7 codes),
  toutes deux « validées hors contrat XML ».
- **11 divergences PDF ↔ XSD** recensées (dont `implId`, types des périodes Doc2, `coNumAttribution`) ;
  elles opposent le texte ou les exemples du manuel au contrat, que ses diagrammes suivent.
- **Relecture du 2026-11-24** : contrat et manuel rev 1.3 confirmés (contrat identique au service en
  ligne et au catalogue), observations datées et sourcées, « Mapping pyetnic » aligné sur le code.
- **8 XSD partagés identiques** à la session 3 (diff byte-for-byte).
