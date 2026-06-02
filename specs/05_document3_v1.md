# EPROM — Formation Document 3 (Attributions) v1.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationDocument3Service_external_v1.wsdl` + PDF Manuel d'utilisation rev1.3 (01-05-2023, édité 10-05-2023, 22 pages)
> Date d'analyse : 2026-06-02 (session 4)

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
| Binding générique Ecole (déprécié) | `FormationDocument3Binding` (cité par le PDF, **absent du WSDL externe fourni**) |
| WSDL service | `service_eprom_formation_document3_external_v1` |
| WSDL port | `EPROMFormationDocument3ExternalV1Port` |

> **SOAP 1.1 confirmé deux fois** : (1) le binding du WSDL utilise exclusivement l'espace de noms
> `http://schemas.xmlsoap.org/wsdl/soap/` (SOAP 1.1) — il n'y a **pas** de binding `soap12/` ;
> (2) le PDF (§2.2) indique « Le service EPROM FormationDocument3 est compatible avec le protocole SOAP 1.1 ».
> C'est une différence avec Formation Organisation v7 et les autres services qui acceptent SOAP 1.1 **ou** 1.2.

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL + PDF | `https://ws-tq.etnic.be/eprom/formation/document3/v1` |
| PROD | PDF + prompt | `https://ws.etnic.be/eprom/formation/document3/v1` |

> **Endpoint générique « Ecole »** (déprécié) :
> - TQ : `https://ws-tq.etnic.be/ecole`
> - PROD : `https://ws.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument3V1?mode=sync`, To = `http://services-web.etnic.be/eprom`
> - (dans l'exemple de réponse du PDF, l'`Action` est écrite `eprom:formationDocument3V1?mode=sync` — `f` minuscule ; casse à confirmer côté plateforme)
>
> Le endpoint spécifique EPROM **ne requiert pas** de WS-Addressing. Il a été ajouté en rev 1.3 (2023) ;
> auparavant seul le endpoint générique `/ecole` existait.

---

## Description fonctionnelle

Le service EPROM FormationDocument3 permet à l'école de **gérer la liste des attributions relatives
aux activités d'enseignement** (Doc 3) sauvegardées dans EPROM. Autrement dit : **quel enseignant
enseigne quelle activité (branche), et combien de périodes lui sont attribuées**.

Il expose **2 opérations** (pas d'approbation directe, comme le Document 2) :

1. **LireDocument3** — fournit les informations du document 3.
2. **ModifierDocument3** — permet de modifier les données du document 3.

### Modèle de données (hiérarchie)

```
Document 3 (1 organisation de formation)
└── activiteListe
    └── activite (1..N branches/activités d'enseignement)
        ├── (référentiel : coCategorie, teNomBranche, noAnneeEtude)
        ├── (périodes de référence : nbPeriodesDoc8, nbPeriodesPrevuesDoc2, nbPeriodesReellesDoc2)
        └── enseignantListe
            └── enseignant (0..N attributions)
                ├── identité (noMatEns, teNomEns, tePrenomEns, teAbrEns, teEnseignant)
                ├── coDispo (disponibilité), teStatut (statut)
                └── nbPeriodesAttribuees
```

> **Pas de switch d'approbation dans la structure** : contrairement au Document 1 (`swAppPopD1` + `swAppD1`)
> et au Document 2 (`swAppD2`), `FormationDocument3CT` ne contient **aucun champ d'approbation**.
> L'approbation du Doc 3 n'est ni lisible ni modifiable via ce service. En revanche, l'accès au Doc 3
> est **conditionné** par l'approbation des documents amont (voir Règles métier, erreur `20102`).

> **Données de référence en lecture seule** : les périodes `nbPeriodesDoc8` (Doc 8bis),
> `nbPeriodesPrevuesDoc2` et `nbPeriodesReellesDoc2` (Document 2) sont rapatriées depuis d'autres
> documents et servent de plafond de contrôle pour les attributions (voir erreurs `1538`, `1574`-`1576`).

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> Pattern **Common_v1** (ancien), identique à Formation Population (Doc 1), Formation Périodes (Doc 2)
> et Formations Liste v2. Le `Messages` XSD importe bien `common:AbstractExternalResponseType`.
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
(endpoint EPROM). S'il n'est pas fourni, l'ETNIC en génère un.

---

## Opération 1 : LireDocument3

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document3/v1/LireDocument3`

### Requête

**Élément** : `LireDocument3` → **Type** : `LireDocument3RequeteCT` extends `FormationDocument3LireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex : `"2016-2017"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

> `OrganisationReqIdCT` ne contient **pas** d'`implId` (identique aux Documents 1 et 2). Voir `00_REGISTRE.md`.

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse).

### Réponse

**Élément** : `LireDocument3Reponse` → **Type XSD** : `Document3ReponseCT` extends `AbstractExternalResponseType`

> Le PDF nomme ce type `LireDocument3ReponseCT`, mais le XSD `Messages` utilise un **type unique partagé
> `Document3ReponseCT`** pour les réponses des deux opérations (Lire et Modifier).

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

### Doc3ActiviteDetailCT (activité d'enseignement — réponse)

| Champ | Type (XSD) | Card. (XSD) | PDF | Description |
|---|---|---|---|---|
| `coNumBranche` | int | [0..1] | facultatif | Numéro de l'activité d'enseignement |
| `coCategorie` | string | [0..1] | facultatif | Code catégorie (table ci-dessous, identique Doc 2) |
| `teNomBranche` | string | [0..1] | facultatif | Nom de l'activité d'enseignement |
| `noAnneeEtude` | string | [0..1] | facultatif | Numéro de l'année d'étude |
| `nbPeriodesDoc8` | **int** | [0..1] | int, facultatif | Nombre de périodes au Doc 8bis |
| `nbPeriodesPrevuesDoc2` | **int** | [0..1] | **float, obligatoire** ⚠️ | Périodes prévues au Document 2 |
| `nbPeriodesReellesDoc2` | **int** | [0..1] | **float, obligatoire** ⚠️ | Périodes réelles au Document 2 |
| `enseignantListe` | Doc3EnseignantLstCT | [0..1] | 0 à 1 | Liste des attributions des enseignants |

> ⚠️ **Divergence de type / cardinalité (périodes Doc 2)** : le XSD déclare `nbPeriodesPrevuesDoc2` et
> `nbPeriodesReellesDoc2` en `xs:int` `minOccurs="0"`, alors que le PDF (§3.1.3.4, p.10) les décrit en
> **`float` obligatoire**. De plus, **l'exemple de réponse du PDF sérialise les trois compteurs avec
> décimales** (`<nbPeriodesDoc8>24.0</…>`, `<nbPeriodesPrevuesDoc2>24.0</…>`, `<nbPeriodesReellesDoc2>24.0</…>`),
> ce qui est incohérent avec le type `xs:int` du contrat. **Impact client** : un parseur strict (zeep
> appliquant le XSD) tentera de lire `"24.0"` comme `int` → `ValueError`. Prévoir une tolérance
> (coercition float→int, ou patch du type en `xs:float`/`xs:decimal`) sur ces trois champs. À confirmer
> par un appel réel ; le XSD reste la référence contractuelle mais semble en retard sur la réalité du flux.

### Doc3EnseignantDetailCT (attribution d'enseignant — réponse, 11 champs)

| Champ | Type (XSD) | Card. | Description |
|---|---|---|---|
| `coNumAttribution` | int | [0..1] | Numéro de l'attribution d'enseignant |
| `noMatEns` | string | [0..1] | Matricule de l'enseignant |
| `teNomEns` | string | [0..1] | Nom de l'enseignant |
| `tePrenomEns` | string | [0..1] | Prénom de l'enseignant |
| `teAbrEns` | string | [0..1] | Code abréviation de l'enseignant |
| `teEnseignant` | string | [0..1] | Concaténation nom + prénom + matricule |
| `coDispo` | string | [0..1] | Code disponibilité (table §ModifierDocument3) |
| `teStatut` | string | [0..1] | Code statut (table §ModifierDocument3) |
| `nbPeriodesAttribuees` | float | [0..1] | Nombre de périodes attribuées à l'enseignant |
| `tsMaj` | string | [0..1] | Timestamp de la dernière mise à jour du document 3 |
| `teUserMaj` | string | [0..1] | Userid de la personne ayant effectué la dernière MAJ |

> Les 11 champs du XSD correspondent **exactement** au texte du PDF (p.10). `tsMaj`/`teUserMaj` ont été
> ajoutés en rev 1.1 (2018) et `nbPeriodesAttribuees` est passé en `float` en rev 1.2 (2019) — confirmé
> par l'historique du document.

### Table des catégories (`coCategorie`)

Valeurs possibles à la date du 01-05-2023 (**identique à la table `coCategorie` du Document 2** — 30 codes) :

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
        <v12:etabId>41</v12:etabId>
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
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">41</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">66</p752:implId>
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
              <p784:noMatEns>28208171112</p784:noMatEns>
              <p784:teNomEns>AHALLY</p784:teNomEns>
              <p784:tePrenomEns>ANISSA</p784:tePrenomEns>
              <p784:teAbrEns>ANAH</p784:teAbrEns>
              <p784:teEnseignant>AHALLY ANISSA 28208171112</p784:teEnseignant>
              <p784:coDispo/>
              <p784:teStatut>D</p784:teStatut>
              <p784:nbPeriodesAttribuees>0.0</p784:nbPeriodesAttribuees>
              <p784:tsMaj>2017-06-06 16:51:42.142658</p784:tsMaj>
              <p784:teUserMaj>ec000041</p784:teUserMaj>
            </p784:enseignant>
          </p784:enseignantListe>
        </p784:activite>
        <!-- ... autres activités ... -->
      </p784:activiteListe>
    </p784:document3>
  </response>
</LireDocument3Reponse>
```

> Dans l'exemple du PDF, `coDispo` est **vide** (`<coDispo/>`) : l'enseignant est en disponibilité « normale »
> (pas de code particulier). Le `teStatut` `"D"` = Définitif.

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
> **au moins une** `activite` (`maxOccurs="unbounded"`, `minOccurs` implicite = 1 → `[1..*]`).

### Doc3ActiviteDetailSaveCT (activité — requête)

| Champ | Type (XSD) | Card. (XSD) | PDF | Description |
|---|---|---|---|---|
| `coNumBranche` | int | **obligatoire** | facultatif ⚠️ | Numéro de l'activité d'enseignement |
| `noAnneeEtude` | string | **obligatoire** | facultatif ⚠️ | Numéro de l'année d'étude |
| `enseignantListe` | Doc3EnseignantLstSaveCT | **obligatoire** | 0 à 1 ⚠️ | Liste des attributions des enseignants |

> ⚠️ **Divergence de cardinalité (requête Modifier)** : le PDF (§3.1.4.2, p.15) annote `coNumBranche`,
> `noAnneeEtude` (facultatif) et `enseignantListe` (« 0 à 1 ») comme optionnels, alors que le **XSD les
> rend obligatoires** (aucun `minOccurs="0"`). Comme `coNumBranche` + `noAnneeEtude` identifient l'activité
> à modifier, l'interprétation **XSD (obligatoire) est la plus sûre**. À respecter dans le client.

`Doc3EnseignantLstSaveCT` → `enseignant : Doc3EnseignantDetailSaveCT` — XSD `[1..*]` ⚠️ (PDF « 0 à N »).

### Doc3EnseignantDetailSaveCT (attribution — requête)

| Champ | Type (XSD) | Card. (XSD) | Présent PDF ? | Description |
|---|---|---|---|---|
| `coNumAttribution` | int | [0..1] | **NON** ⚠️ | Numéro de l'attribution (cible une attribution existante) |
| `noMatEns` | string | [0..1] | oui | Matricule de l'enseignant |
| `coDispo` | string | [0..1] | oui | Code disponibilité (table ci-dessous) |
| `teStatut` | string | [0..1] | oui | Code statut (table ci-dessous) |
| `nbPeriodesAttribuees` | float | [0..1] | oui | Nombre de périodes attribuées |

> ⚠️ **Élément présent uniquement dans le XSD** : `coNumAttribution` (premier élément de
> `Doc3EnseignantDetailSaveCT` dans le XSD) est **absent de la description PDF** (§3.1.4.2), qui ne liste
> que 4 champs. Il permet vraisemblablement de **cibler une attribution existante** pour la modifier
> (vs en créer une nouvelle). À exposer dans le client comme paramètre optionnel.

> **Comparaison réponse vs requête** : le type Save n'a pas les champs en lecture seule de la réponse
> (`teNomEns`, `tePrenomEns`, `teAbrEns`, `teEnseignant`, `tsMaj`, `teUserMaj`, ni les périodes Doc2/Doc8 /
> `coCategorie` / `teNomBranche`). On envoie : matricule, dispo, statut, périodes attribuées.

### Table des codes de disponibilité (`coDispo`)

Valeurs possibles à la date du 01-05-2023 (« validé hors contrat XML » — contrôle métier, pas dans le XSD).
La 1ʳᵉ colonne est la **valeur à transmettre** ; le libellé reprend généralement le code en préfixe.

| Code | Libellé |
|---|---|
| `BE` | BE Bénévolat |
| `2` | 02 Dispo retrait emploi interet service |
| `3` | 03 Dispo mesure disciplinaire |
| `4` | 04 Dispo mission spéciale:gvt,orga inter |
| `5` | 05 Dispo pour maladie (même traitement) |
| `7` | 07 Dispo convenances personnelles |
| `9` | 09 Absence longue durée rais.familiales |
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
| `32` | 33 Désignation provisoire dans une fonct *(libellé préfixé « 33 » dans le PDF — incohérence probable)* |
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

> Un `coDispo` **vide** (chaîne vide) correspond à un enseignant sans disponibilité particulière
> (situation « normale », voir l'exemple de réponse).

### Table des codes de statut (`teStatut`)

Valeurs possibles à la date du 01-05-2023 (« validé hors contrat XML ») :

| Code | Libellé |
|---|---|
| `C` | ACS |
| `P` | ACS Discriminations Positives |
| `A` | Définitif Accessoire |
| `D` | Définitif |
| `E` | Expert |
| `X` | Expertise pédagogique et technique |
| `T` | Temporaire |

### Réponse

**Type** : `Document3ReponseCT` (identique à LireDocument3 — type unique partagé). La réponse contient le
document 3 complet après modification.

### Exemple de requête XML

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
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>348</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
      <v11:activiteListe>
        <v11:activite>
          <v11:coNumBranche>1</v11:coNumBranche>
          <v11:noAnneeEtude>1</v11:noAnneeEtude>
          <v11:enseignantListe>
            <v11:enseignant>
              <v11:noMatEns>28208171112</v11:noMatEns>
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

| Success | Code | Description (libellé exact PDF) | Type |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | — |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | commun |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | commun (concurrence) |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | commun (sécurité) |
| `false` | `00999` | Erreur sql : | commun (technique) |
| `false` | `1113` | Année scolaire invalide | validation entrée |
| `false` | `1114` | Numéro d'établissement incorrect | validation entrée |
| `false` | `1538` | Périodes Doc3 $1 > périodes Doc2 + IE par branche $2 | cohérence métier |
| `false` | `1574` | Total attributions $1 > total périodes organisées dans formation $2 | cohérence métier |
| `false` | `1575` | Périodes CG attribuées $1 > réel CG + IE CG $2 | cohérence métier |
| `false` | `1576` | Périodes CP attribuées $1 > réel CP + IE CP $2 | cohérence métier |
| `false` | `20102` | Les « Doc A » et « Doc 2 » doivent être approuvés pour pouvoir accéder au « Doc 3 » | **workflow inter-documents** |
| `false` | `20108` | Le numéro de matricule d'enseignement n°$1 est incorrect | validation attribution |
| `false` | `20109` | Le code dispo d'enseignement n°$1 est incorrect | validation attribution |
| `false` | `20110` | Le statut d'enseignement $1 est incorrect | validation attribution |
| `false` | `99999` | (Autres Erreurs) | fourre-tout |

> Les `$1`, `$2` sont des **paramètres substitués** par le serveur (valeurs/zones concernées).

### Codes partagés / spécifiques
- **Communs à tous les services EPROM** : `00009`, `00025`, `00999`, `99999`.
- **Communs Documents 1/2/3** : `00011`, `1113`, `1114`.
- **Spécifiques Document 3** : `1538`, `1574`, `1575`, `1576`, `20102`, `20108`, `20109`, `20110`.

---

## Règles métier & workflow inter-documents

### ⭐ Workflow inter-documents (réponse à la question ouverte des sessions 1-3)

**Erreur `20102` — « Les "Doc A" et "Doc 2" doivent être approuvés pour pouvoir accéder au "Doc 3" ».**

C'est la confirmation tant cherchée du workflow : **le Document 3 (Attributions) n'est accessible
(lecture/modification) que si les documents amont sont approuvés.**

- `« Doc 2 »` = **Document 2 (Périodes)** — approuvé via le switch `swAppD2` (côté administration).
- `« Doc A »` = très probablement **Document 1 (Population)** — le document portant les switches
  d'approbation `swAppPopD1` (école/PO) + `swAppD1` (administration) documentés en session 3.

> ⚠️ **Point à confirmer** : le libellé est littéralement « **Doc A** » (et non « Doc 1 ») dans le texte
> du PDF (couche texte native, pas OCR — vérifié page 22). L'hypothèse « Doc A = Document 1 (Population) »
> est la plus cohérente avec le reste du dossier, mais le mapping exact de la lettre « A » mériterait une
> validation ETNIC ou un test réel. Aucune autre occurrence de « Doc A » dans le manuel.

Chaîne de dépendance reconstituée (à valider/affiner en session 6) :

```
Organisation (Formation Organisation v7)
        │  (créée, dates, type)
        ▼
Document 1 «Doc A»? (Population)  ──approuvé (swAppPopD1 + swAppD1)──┐
Document 2 (Périodes)            ──approuvé (swAppD2)───────────────┤
                                                                    ▼
                                          Document 3 (Attributions)  ← accessible seulement ici
```

### Contrôles de cohérence sur les périodes attribuées

Les attributions ne peuvent dépasser les périodes réellement organisées (issues du Doc 2, IE comprises) :

- `1574` — la **somme des périodes attribuées** (tous enseignants) ne peut excéder le **total des
  périodes organisées** dans la formation.
- `1538` — par branche, les **périodes Doc 3** ne peuvent excéder **périodes Doc 2 + IE** (intervention
  extérieure) de la branche.
- `1575` — les périodes **CG** (Cours Généraux) attribuées ≤ réel CG + IE CG.
- `1576` — les périodes **CP** (Cas Particuliers) attribuées ≤ réel CP + IE CP.

> `CG`/`CP` renvoient à la classification des périodes (cf. `coCodePar` du Document 2 : `CG`, `CP`, `SU`).
> Le Doc 3 **consomme** donc les périodes définies au Doc 2 ; les périodes d'intervention extérieure (IE)
> du Doc 2 viennent augmenter le plafond attribuable.

### Validations d'attribution
- `20108` — matricule enseignant inexistant/incorrect.
- `20109` — `coDispo` hors liste autorisée.
- `20110` — `teStatut` hors liste autorisée.
- `00011` — édition concurrente (le document a été modifié entre la lecture et l'écriture).

### Points spécifiques demandés (cohérence cross-services)
- **`coCategorie`** : table **identique** à celle du Document 2 (30 codes) → un seul référentiel partagé. ✓
- **`coCatCol`** (types d'intervention extérieure) : **sans objet pour le Document 3**. Ce concept
  n'existe qu'au Document 2 ; le Doc 3 ne manipule pas d'intervention extérieure, il n'en voit que
  l'effet agrégé (IE incluse dans les plafonds de périodes, cf. `1538`/`1575`/`1576`).
- **`typeInterventionExterieure "J"`** (Réorientation 7TQ/7P) : **sans objet ici** — propre à
  Formation Organisation v7 et aux interventions extérieures du Document 2.

---

## Vérification croisée UML / XSD / PDF

> Les « diagrammes » du PDF sont des **boîtes de classes UML repliées** (marqueur `+` d'expansion) : elles
> montrent les références de types et les cardinalités, le détail des champs étant donné dans le **texte**
> sous chaque diagramme. Le contrat **XSD reste la référence** ; pages rendues en image et inspectées : 8, 9, 10, 14, 15, 22.

### Page 8 (réponse LireDocument3 — chaîne `Document3ReponseCT` → `FormationDocument3CT`)
- ✅ `Document3ReponseCT` (success + response) → `Document3ReponseMetierCT` (document3) → `FormationDocument3CT`
  (id + activiteListe `[0..1]`) — conforme XSD.
- ⚠️ **`implId`** dans `OrganisationResIdCT` : le **diagramme affiche `[0..1]`** (conforme XSD `minOccurs="0"`),
  mais le **texte dit « obligatoire »** (§3.1.3.4, p.8 + définition `ImplIdST` p.9). **Même divergence
  qu'en session 3** (Documents 1 et 2). Le XSD/diagramme (optionnel) prime ; en pratique l'`implId` est
  toujours renvoyé dans les exemples réels (valeur `66`).

### Page 9 (`OrganisationResIdCT`, `Doc3ActiviteListeCT`, `Doc3ActiviteDetailCT`)
- ✅ `Doc3ActiviteListeCT.activite` = `[0..N]` — conforme XSD `maxOccurs="unbounded" minOccurs="0"`.
- ✅ 8 champs de `Doc3ActiviteDetailCT` présents ; table `coCategorie` (30 codes) conforme au Doc 2.
- ⚠️ `nbPeriodesPrevuesDoc2` / `nbPeriodesReellesDoc2` : texte « float, obligatoire » vs XSD « int, `[0..1]` »
  (voir divergence de type ci-dessus).

### Page 10 (`Doc3EnseignantLstCT`, `Doc3EnseignantDetailCT`)
- ✅ `Doc3EnseignantDetailCT` : **11 champs** du texte = 11 éléments du XSD (tous `[0..1]`). Aucune divergence.

### Pages 14-15 (requête ModifierDocument3)
- ✅ `FormationDocument3ModifReqCT` : `id` + `activiteListe` (obligatoire) ; `OrganisationReqIdCT` **sans
  `implId`** (4 champs) ; `Doc3ActiviteListeSaveCT.activite` = **`[1..*]`** (visible dans le diagramme). — conforme XSD.
- ⚠️ `Doc3ActiviteDetailSaveCT` : texte « facultatif » pour `coNumBranche`/`noAnneeEtude` et « 0 à 1 »
  pour `enseignantListe`, alors que le **XSD les rend obligatoires**.
- ⚠️ `Doc3EnseignantDetailSaveCT` : le **XSD contient `coNumAttribution` (1ᵉʳ champ, `[0..1]`)**, **absent
  de la liste du texte** (qui ne décrit que `noMatEns`, `coDispo`, `teStatut`, `nbPeriodesAttribuees`).
  Tables `coDispo` (~60 codes) et `teStatut` (7 codes) données dans le texte uniquement.

### Page 22 (table des erreurs)
- ✅ 15 codes d'erreur + ligne succès. Libellé `20102` confirmé **littéralement « Doc A » / « Doc 2 »**
  (couche texte native, pas une erreur d'OCR).

### Récapitulatif des divergences PDF ↔ XSD

| # | Élément | PDF | XSD | Reco. client |
|---|---|---|---|---|
| 1 | `OrganisationResIdCT.implId` | obligatoire | `minOccurs="0"` | optionnel (XSD), mais toujours présent en pratique |
| 2 | `nbPeriodesPrevuesDoc2` | float, obligatoire | `int`, `[0..1]` | tolérer décimales / traiter en float |
| 3 | `nbPeriodesReellesDoc2` | float, obligatoire | `int`, `[0..1]` | idem |
| 4 | `nbPeriodesDoc8` | int, facultatif | `int`, `[0..1]` | exemple sérialise « 24.0 » → tolérer décimales |
| 5 | `Doc3ActiviteDetailSaveCT.coNumBranche` | facultatif | obligatoire | **fournir** (identifie l'activité) |
| 6 | `Doc3ActiviteDetailSaveCT.noAnneeEtude` | facultatif | obligatoire | **fournir** |
| 7 | `Doc3ActiviteDetailSaveCT.enseignantListe` | 0 à 1 | obligatoire | **fournir** |
| 8 | `Doc3EnseignantLstSaveCT.enseignant` | 0 à N | `[1..*]` | ≥ 1 |
| 9 | `Doc3EnseignantDetailSaveCT.coNumAttribution` | absent | présent `[0..1]` | exposer en optionnel |

---

## Mapping pyetnic

### Classe proposée : `FormationDocument3Service` (alias métier : Attributions)

```python
class FormationDocument3Service:
    """Service EPROM Formation Document 3 (Attributions) v1.0 — SOAP 1.1 uniquement."""

    WSDL = "EpromFormationDocument3Service_external_v1.wsdl"
    ENDPOINT_TQ = "https://ws-tq.etnic.be/eprom/formation/document3/v1"
    ENDPOINT_PROD = "https://ws.etnic.be/eprom/formation/document3/v1"

    def lire(self, annee_scolaire: str, etab_id: int,
             num_adm_formation: int, num_organisation: int) -> Document3Response:
        """LireDocument3 — lecture des attributions du document 3."""

    def modifier(self, annee_scolaire: str, etab_id: int,
                 num_adm_formation: int, num_organisation: int,
                 activites: list[ActiviteSave]) -> Document3Response:
        """ModifierDocument3 — modification des attributions (≥ 1 activité)."""
```

### Dataclasses proposées

```python
@dataclass
class EnseignantSave:
    """Attribution d'enseignant (type Save / requête)."""
    no_mat_ens: str | None = None          # matricule
    co_dispo: str | None = None            # code disponibilité (table coDispo)
    te_statut: str | None = None           # code statut (C/P/A/D/E/X/T)
    nb_periodes_attribuees: float | None = None
    co_num_attribution: int | None = None  # présent au XSD, absent du PDF → cible une attribution existante


@dataclass
class ActiviteSave:
    """Activité d'enseignement (type Save / requête)."""
    co_num_branche: int                    # obligatoire (XSD), identifie la branche
    no_annee_etude: str                    # obligatoire (XSD)
    enseignants: list[EnseignantSave]      # ≥ 1 (XSD [1..*])


@dataclass
class EnseignantResponse:
    """Attribution d'enseignant (réponse, 11 champs)."""
    co_num_attribution: int | None
    no_mat_ens: str | None
    te_nom_ens: str | None
    te_prenom_ens: str | None
    te_abr_ens: str | None
    te_enseignant: str | None              # "NOM PRENOM MATRICULE"
    co_dispo: str | None
    te_statut: str | None
    nb_periodes_attribuees: float | None
    ts_maj: str | None
    te_user_maj: str | None


@dataclass
class ActiviteResponse:
    """Activité d'enseignement (réponse, 8 champs)."""
    co_num_branche: int | None
    co_categorie: str | None               # table partagée avec Doc 2
    te_nom_branche: str | None
    no_annee_etude: str | None
    nb_periodes_doc8: int | None           # ⚠️ peut arriver en "24.0"
    nb_periodes_prevues_doc2: float | None # ⚠️ XSD int mais flux float
    nb_periodes_reelles_doc2: float | None # ⚠️ idem
    enseignants: list[EnseignantResponse]
```

### Recommandations d'implémentation
1. **Forcer SOAP 1.1** dans le transport zeep (ce service ne supporte pas SOAP 1.2).
2. **Périodes Doc2/Doc8** : prévoir une coercition tolérante (le flux renvoie `"24.0"` alors que le XSD
   dit `int`). Option : patcher le schéma en `xs:decimal`, ou post-traiter avant validation stricte.
3. **Workflow** : avant tout `ModifierDocument3`, s'assurer (côté appelant ou via Formations Liste /
   statuts) que Population (« Doc A ») et Périodes (Doc 2) sont approuvés, sinon erreur `20102`.
4. **Erreurs `1538`/`1574`/`1575`/`1576`** : exposer les paramètres `$1`/`$2` du message pour aider
   l'utilisateur à corriger (valeur attribuée vs plafond).
5. **`coNumAttribution`** : exposer en optionnel pour permettre la modification ciblée d'une attribution
   existante plutôt que la recréation.
6. Tester le **mock server stateful** sur la contrainte `20102` (Doc 3 inaccessible tant que Doc1+Doc2
   non approuvés) — cas d'intégration prioritaire.

---

## XSD utilisés

| Fichier XSD | Rôle | Identique à la session 3 (Doc 2) ? |
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

> Vérification réalisée par `diff` des 8 XSD partagés entre `contrat_document3_v1/xsd/` et
> `contrat_formation_periodes_v1/xsd/` → **aucune différence**.

---

## Synthèse de la session 4

- **2 opérations** : LireDocument3, ModifierDocument3 (**pas d'Approuver**, comme Doc 2).
- **SOAP 1.1 uniquement** (binding WSDL + PDF) — particularité vs les autres services.
- **Pattern Common_v1** (ancien), bloc retour `AbstractExternalResponseType`.
- **Modèle hiérarchique** : activité (branche) → enseignants attribués + périodes.
- **Workflow confirmé** (erreur `20102`) : Doc 3 inaccessible tant que « Doc A » (Population/Doc 1) **et**
  Doc 2 (Périodes) ne sont pas approuvés.
- **`coCategorie`** partagé avec le Doc 2 (référentiel commun). Pas de `coCatCol` / intervention
  extérieure propre au Doc 3.
- **2 nouvelles tables de valeurs** : `coDispo` (~60 codes de disponibilité) et `teStatut` (7 codes),
  toutes deux « validées hors contrat XML ».
- **9 divergences PDF ↔ XSD** recensées (dont `implId`, types des périodes Doc2, `coNumAttribution`).
- **8 XSD partagés identiques** à la session 3 (diff byte-for-byte).
