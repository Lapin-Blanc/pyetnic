# EPROM — Formation Périodes (Document 2) v1.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationDocument2Service_external_v1.wsdl` + PDF Manuel d'utilisation rev1.3 (01-07-2025)
> Date d'analyse : 2026-04-14

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | Formation Périodes (Document 2) |
| Version service | 1.0.0 |
| Révision document | 1.3 |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security Username Token Profile (ou certificat X.509) |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/document2/v1` |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/document2/messages/v1` |
| Types namespace (doc2) | `http://enseignement.cfwb.be/types/formation/document2/v1` |
| Types namespace (org) | `http://enseignement.cfwb.be/types/organisation/v1` |
| Binding | `EPROMFormationDocument2ExternalV1Binding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/eprom/formation/document2/v1` |
| PROD | prompt | `https://ws.etnic.be/eprom/formation/document2/v1` |
| TQ | PDF (TLS 1.2) | `https://services-web.tq.etnic.be:11443/eprom/formation/document2/v1` |
| PROD | PDF (TLS 1.2) | `https://services-web.etnic.be:11443/eprom/formation/document2/v1` |

> **Endpoint générique « Ecole »** (déprécié) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument2V1?mode=sync`, To = `http://services-web.etnic.be/eprom`

---

## Description fonctionnelle

Le service FormationDocument2 permet de gérer les informations relatives aux **périodes
de la formation organisée** (Doc 2) sauvegardées dans EPROM.

Il expose **2 opérations** (pas d'approbation directe, contrairement au Document 1) :

1. **LireDocument2** — fournit les informations du document 2
2. **ModifierDocument2** — permet de modifier les données du document 2

> **Note sur le titre du PDF** : le titre mentionne "Formation Périodes" mais le nom interne
> est "Document 2". Le service gère deux grandes sections de données :
> - Les **activités d'enseignement** (branches/cours avec périodes prévues et réelles)
> - Les **interventions extérieures** (conventions, fonds, projets) avec leurs propres périodes

> **Changements rev 1.3 (01-07-2025)** :
> - Mise à jour des listes de valeurs pour `coCatCol` et `coObjFse` (interventions extérieures)
> - Nouveau code `coCatCol = "J"` (Réorientation 7TQ/7P) → nécessite `coObjFse = "OA"`
> - Codes `coCatCol "R"` et `"S"` supprimés (dépréciés)
> - Nombreux codes `coObjFse` supprimés (dépréciés, barrés dans le PDF)

---

## Bloc Retour — AbstractExternalResponseType (Common_v1.xsd)

> Même pattern que Formation Population (Document 1) et Formations Liste v2.
> Voir la documentation dans `03_formation_population_v1.md` ou `00_REGISTRE.md`.

---

## Opération 1 : LireDocument2

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document2/v1/LireDocument2`

### Requête

**Élément** : `LireDocument2` → **Type** : `LireDocument2RequeteCT` extends `FormationDocument2LireReqCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | OrganisationReqIdCT | oui | Identifiant du document |
| `id/anneeScolaire` | AnneeScolaireST | oui | Année scolaire (ex: `"2021-2022"`) |
| `id/etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `id/numAdmFormation` | int | oui | Numéro administratif de la formation |
| `id/numOrganisation` | int | oui | Numéro de l'organisation |

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse).

### Réponse

**Élément** : `LireDocument2Reponse` → **Type** : `Document2ReponseCT` extends `AbstractExternalResponseType`

```
Document2ReponseCT
├── success         : boolean                   [obligatoire] (hérité)
├── messages        : messagesType              [0..1]        (hérité)
└── response        : Document2ReponseMetierCT  [0..1]
    └── document2   : FormationDocument2CT      [obligatoire]
```

### FormationDocument2CT (structure complète du document 2)

```
FormationDocument2CT
├── id                           : OrganisationResIdCT              [obligatoire]
├── activiteEnseignementDetail   : Doc2ActiviteEnseignementDetailCT [0..1]
│   ├── activiteEnseignementListe : Doc2ActiviteEnseignementLstCT   [0..1]
│   │   └── activiteEnseignement  : Doc2ActiviteEnseignementLineCT  [0..*]
│   ├── nbTotPeriodePrevueAn1    : float                            [obligatoire]
│   ├── nbTotPeriodePrevueAn2    : float                            [obligatoire]
│   ├── nbTotPeriodeReelleAn1    : float                            [obligatoire]
│   └── nbTotPeriodeReelleAn2    : float                            [obligatoire]
├── interventionExterieureListe  : Doc2InterventionExtLstCT         [0..1]
│   └── interventionExterieure   : Doc2InterventionExtLineCT        [0..*]
├── swAppD2                      : boolean                          [obligatoire]
├── tsMaj                        : string                           [obligatoire]
└── teUserMaj                    : string                           [obligatoire]
```

> **Différence avec Document 1** : un seul switch d'approbation (`swAppD2`) au lieu de deux
> (`swAppPopD1` + `swAppD1`). Pas d'opération ApprouverDocument2 dans ce service.

### Doc2ActiviteEnseignementLineCT (ligne d'activité d'enseignement — réponse)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumBranche` | int | oui | Numéro de l'activité d'enseignement |
| `coCategorie` | string | oui | Code de la catégorie (voir table ci-dessous) |
| `teNomBranche` | string | oui | Nom de la branche |
| `coAnnEtude` | string | oui | Code de l'année d'étude |
| `nbEleveC1` | int | oui | Nombre d'élèves |
| `nbPeriodeBranche` | float | oui | Périodes prévues pour cette branche |
| `nbPeriodePrevueAn1` | float | oui | Périodes prévues la 1ère année |
| `nbPeriodePrevueAn2` | float | oui | Périodes prévues la 2ème année |
| `nbPeriodeReelleAn1` | float | oui | Périodes réelles la 1ère année |
| `nbPeriodeReelleAn2` | float | oui | Périodes réelles la 2ème année |
| `coAdmReg` | int | oui | Numéro administratif Rgp (regroupement activités) |
| `coOrgReg` | int | oui | Numéro d'organisation Rgp |
| `coBraReg` | int | oui | Numéro d'activité d'enseignement Rgp |
| `coEtuReg` | string | oui | Année d'études Rgp |

### Table des catégories (`coCategorie`)

Valeurs possibles à la date du 30-09-2024 :

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
| `CTPe` | COURS TECHN.& PRATIQUE PROF. - encadrement |
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

### Doc2InterventionExtLineCT (ligne d'intervention extérieure — réponse)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumIex` | int | oui | Numéro d'intervention |
| `coCatCol` | string | oui | Code du type d'intervention extérieure |
| `teTypeInterventionExt` | string | oui | Label du type d'intervention extérieure |
| `coObjFse` | string | oui | Code du sous-type d'intervention extérieure |
| `teSousTypeInterventionExt` | string | oui | Label du sous-type d'intervention |
| `coRefPro` | string | oui | Code projet global / référence |
| `coCriCee` | string | oui | Numéro agrément |
| `periodeListe` | Doc2PeriodeExtLstCT | 0..1 | Liste de périodes extérieures |

### Doc2PeriodeExtLineCT (période d'intervention extérieure — réponse)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coCodePar` | string | oui | Code du type de périodes en intervention extérieure |
| `teLibPeriode` | string | oui | Label du type de périodes |
| `nbPerAn1` | float | oui | Nombre de périodes pour l'année 1 |
| `nbPerAn2` | float | oui | Nombre de périodes pour l'année 2 |

### Table des types de périodes d'intervention (`coCodePar`)

| Code | Libellé |
|---|---|
| `CG` | Cas généraux |
| `CP` | Cas particuliers |
| `SU` | Suppléments |

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document2/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document2/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:LireDocument2>
      <v11:id>
        <v12:anneeScolaire>2021-2022</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>186</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
    </v1:LireDocument2>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (simplifié)

```xml
<LireDocument2Reponse xmlns="http://services-web.etnic.be/eprom/formation/document2/messages/v1">
  <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
  <response>
    <p575:document2 xmlns:p575="http://enseignement.cfwb.be/types/formation/document2/v1">
      <p575:id>
        <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2021-2022</p752:anneeScolaire>
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">41</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">66</p752:implId>
        <p752:numAdmFormation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">186</p752:numAdmFormation>
        <p752:numOrganisation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">1</p752:numOrganisation>
      </p575:id>
      <p575:activiteEnseignementDetail>
        <p575:activiteEnseignementListe>
          <p575:activiteEnseignement>
            <p575:coNumBranche>1</p575:coNumBranche>
            <p575:coCategorie>PRET</p575:coCategorie>
            <p575:teNomBranche>PRESTATIONS ETUDIANTS (STAGE)</p575:teNomBranche>
            <p575:coAnnEtude>1</p575:coAnnEtude>
            <p575:nbEleveC1>0</p575:nbEleveC1>
            <p575:nbPeriodeBranche>24.0</p575:nbPeriodeBranche>
            <p575:nbPeriodePrevueAn1>0.0</p575:nbPeriodePrevueAn1>
            <p575:nbPeriodePrevueAn2>0.0</p575:nbPeriodePrevueAn2>
            <p575:nbPeriodeReelleAn1>0.0</p575:nbPeriodeReelleAn1>
            <p575:nbPeriodeReelleAn2>0.0</p575:nbPeriodeReelleAn2>
            <p575:coAdmReg>0</p575:coAdmReg>
            <p575:coOrgReg>0</p575:coOrgReg>
            <p575:coBraReg>0</p575:coBraReg>
            <p575:coEtuReg/>
          </p575:activiteEnseignement>
          <!-- ... autres activités ... -->
        </p575:activiteEnseignementListe>
        <p575:nbTotPeriodePrevueAn1>10.0</p575:nbTotPeriodePrevueAn1>
        <p575:nbTotPeriodePrevueAn2>10.0</p575:nbTotPeriodePrevueAn2>
        <p575:nbTotPeriodeReelleAn1>20.0</p575:nbTotPeriodeReelleAn1>
        <p575:nbTotPeriodeReelleAn2>20.0</p575:nbTotPeriodeReelleAn2>
      </p575:activiteEnseignementDetail>
      <p575:swAppD2>1</p575:swAppD2>
      <p575:tsMaj>2021-12-16 14:28:31.471891</p575:tsMaj>
      <p575:teUserMaj>EDU3NG</p575:teUserMaj>
    </p575:document2>
  </response>
</LireDocument2Reponse>
```

---

## Opération 2 : ModifierDocument2

### SOAP Action
`http://services-web.etnic.be/eprom/formation/document2/v1/ModifierDocument2`

### Requête

**Élément** : `ModifierDocument2` → **Type** : `ModifierDocument2RequeteCT` extends `FormationDocument2ModifReqCT`

```
FormationDocument2ModifReqCT
├── id                           : OrganisationReqIdCT                [obligatoire]
├── activiteEnseignementListe    : Doc2ActiviteEnseignementLstSaveCT  [0..1]
│   └── activiteEnseignement     : Doc2ActiviteEnseignementLineSaveCT [0..*]
└── interventionExterieureListe  : Doc2InterventionExtLstSaveCT       [0..1]
    └── interventionExterieure   : Doc2InterventionExtLineSaveCT      [0..*]
```

### Doc2ActiviteEnseignementLineSaveCT (activité d'enseignement — requête)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumBranche` | int | oui | Numéro de l'activité d'enseignement |
| `nbEleveC1` | int | non | Nombre d'élèves |
| `nbPeriodePrevueAn1` | float | non | Périodes prévues année 1 |
| `nbPeriodePrevueAn2` | float | non | Périodes prévues année 2 |
| `nbPeriodeReelleAn1` | float | non | Périodes réelles année 1 |
| `nbPeriodeReelleAn2` | float | non | Périodes réelles année 2 |
| `coAdmReg` | int | non | Numéro administratif Rgp |
| `coOrgReg` | int | non | Numéro d'organisation Rgp |
| `coBraReg` | int | non | Numéro d'activité Rgp |
| `coEtuReg` | string | non | Année d'études Rgp |

> **Différence requête vs réponse** : le type Save n'a pas les champs `coCategorie`,
> `teNomBranche`, `coAnnEtude`, `nbPeriodeBranche` (en lecture seule, calculés/référentiels).

### Doc2InterventionExtLineSaveCT (intervention extérieure — requête)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumIex` | int | non | Numéro d'intervention (facultatif pour création) |
| `coCatCol` | string | oui | Code du type d'intervention extérieure |
| `coObjFse` | string | non | Code du sous-type d'intervention |
| `coRefPro` | string | non | Code Projet global / Référence |
| `coCriCee` | string | non | Numéro agrément |
| `periodeListe` | Doc2PeriodeExtLstSaveCT | non | Liste de périodes |

### Doc2PeriodeExtLineSaveCT (période — requête)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coCodePar` | string | oui | Code du type de périodes (`CG`, `CP`, `SU`) |
| `nbPerAn1` | float | non | Nombre de périodes année 1 |
| `nbPerAn2` | float | non | Nombre de périodes année 2 |

> **Différence requête vs réponse** : le type Save n'a pas `teLibPeriode` (lecture seule).

### Table des types d'intervention extérieure (`coCatCol`)

Valeurs possibles à la date du 01-07-2025 :

| Code | Libellé | Statut |
|---|---|---|
| `A` | Personnel non chargé de cours | actif |
| `B` | Octroi périodes supplémentaires-bonus | actif |
| `C` | Convention | actif |
| `D` | Discriminations positives | actif |
| `E` | EHR | actif |
| `F` | Fonds Européens | actif |
| `I` | Formation des publics Infra scolarisés | actif |
| `J` | Réorientation 7TQ/7P | **nouveau** (v7) — requiert `coObjFse = "OA"` |
| `K` | Octroi périodes cabinet-projets transver | actif |
| `P` | Formations continuées | actif |
| `Q` | Agence Qualité | actif |
| ~~`R`~~ | ~~Récupération périodes complémentaires~~ | **supprimé** |
| ~~`S`~~ | ~~CISCO système~~ | **supprimé** |
| `U` | Union Européenne | actif |
| `V` | Validation des compétences | actif |

### Table des sous-types d'intervention (`coObjFse`)

Valeurs possibles à la date du 01-07-2025 (sélection des actifs, relation avec `coCatCol`) :

| Code | Libellé | coCatCol |
|---|---|---|
| `AF` | AFOSOC (cnv cadre) | C |
| `AP` | APEF-FEBI | I |
| `PP` | APP Wallonie | K |
| `AC` | Actiris (Forem Bxl) | C |
| `AE` | Aide à la Promotion de l'Emploi | B |
| `AL` | Alphabétisation | B |
| `CG` | CCG | F |
| `CD` | CEFORA (cnv cadre demandeurs emplois) | C |
| `CA` | CEFORA (cnv cadre pour employés) | C |
| `CE` | CEFORA (experts hors convention) | C |
| `CF` | Carrefour formation | BC |
| `CL` | Cell-Learning | K |
| `CP` | Citoyenneté prison | I |
| `CO` | Conseiller en prévention | C |
| `BF` | Convention EPS-Bruxelles formation | CI |
| `MI` | Convention EPS-MIRE | I |
| `CQ` | Coordonnateurs qualité | I |
| `CR` | Coref | V |
| `EL` | E-learning CRP | K |
| `SC` | EPS - Secteur construction | CI |
| `CC` | EPS-CEFORA | I |
| `EN` | Ecole numérique | K |
| `FP` | Fonction publique | C |
| `FO` | Forem-Convention cadre | CI |
| `FS` | Forem-Formations spécifiques | C |
| `NT` | Formation NEET'S | I |
| `FC` | Formations continuées | C |
| `NE` | Neet's CPAS-EPS | C |
| `CI` | Neutralité et Citoyenneté | I |
| `OA` | Organisation des Alternatives | **J** (obligatoire pour coCatCol J) |
| `PR` | PRISON REINSERT | K |
| `C` | Partage ENCC (conventionnement) | A |
| `PT` | Projets transversaux (association FSE) | B |
| `IN` | Périodes Projet Inclusif | K |
| `SP` | Périodes Suivi Pédagogique | K |
| `RR` | RRF collaborations | U |
| `RE` | Réfugiés | B |
| `RW` | Région Wallonne | C |
| `G` | Sacrifices ENCC (antigel) | A |
| `SI` | Sensibilisation à l'EPS inclusif | I |
| `TP` | Technopédagogue | K |
| `BW` | Zone Brabant Wallon | F |
| `BX` | Zone Bruxelles | F |
| `LX` | Zone Luxembourg | F |
| `WL` | Zone Wallonie | F |

> **Codes dépréciés (barrés dans le PDF rev1.3)** :
> `PI` (Convention Passerelle infirmière → I), `EP` (Epreuve de validation → V),
> `FE` (Fonds Européens → I), `EL` (Français langue étrangère → B),
> `1` (Obj 1:Hainaut → F), `2` (Obj.2:Hors Hainaut → F),
> `FR` (Plan de formation réseau → I), `PM` (Projets Ministre → I),
> `RC` (Remédiation Covid 19 → K), `RA` (Renfort administratif → B),
> `CS` (complément CESS → I)

### Réponse

**Type** : `Document2ReponseCT` (identique à LireDocument2 — même type pour les 2 opérations).

La réponse contient le document 2 complet après modification.

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formation/document2/messages/v1"
                  xmlns:v11="http://enseignement.cfwb.be/types/formation/document2/v1"
                  xmlns:v12="http://enseignement.cfwb.be/types/organisation/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ModifierDocument2>
      <v11:id>
        <v12:anneeScolaire>2016-2017</v12:anneeScolaire>
        <v12:etabId>41</v12:etabId>
        <v12:numAdmFormation>44</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
      <v11:activiteEnseignementListe>
        <v11:activiteEnseignement>
          <v11:coNumBranche>1</v11:coNumBranche>
          <v11:nbEleveC1>1</v11:nbEleveC1>
          <v11:nbPeriodePrevueAn1>2</v11:nbPeriodePrevueAn1>
          <v11:nbPeriodePrevueAn2>3</v11:nbPeriodePrevueAn2>
          <v11:nbPeriodeReelleAn1>4</v11:nbPeriodeReelleAn1>
          <v11:nbPeriodeReelleAn2>5</v11:nbPeriodeReelleAn2>
        </v11:activiteEnseignement>
      </v11:activiteEnseignementListe>
      <v11:interventionExterieureListe>
        <v11:interventionExterieure>
          <v11:coCatCol>C</v11:coCatCol>
          <v11:coObjFse>AC</v11:coObjFse>
          <v11:coRefPro>4</v11:coRefPro>
          <v11:coCriCee>5</v11:coCriCee>
          <v11:periodeListe>
            <v11:periode>
              <v11:coCodePar>CP</v11:coCodePar>
              <v11:nbPerAn1>2.0</v11:nbPerAn1>
              <v11:nbPerAn2>2.0</v11:nbPerAn2>
            </v11:periode>
            <v11:periode>
              <v11:coCodePar>CG</v11:coCodePar>
              <v11:nbPerAn1>5.0</v11:nbPerAn1>
              <v11:nbPerAn2>5.0</v11:nbPerAn2>
            </v11:periode>
          </v11:periodeListe>
        </v11:interventionExterieure>
      </v11:interventionExterieureListe>
    </v1:ModifierDocument2>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Codes d'erreur spécifiques

| Success | Code | Description | Opérations |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | toutes |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | Lire |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | Modifier |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | toutes |
| `false` | `00999` | Erreur sql | toutes |
| `false` | `1114` | Numéro d'établissement incorrect | toutes |
| `false` | `1113` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | toutes |
| `false` | `1527` | Données regroupement invalides. (Adm + Org.) | Modifier |
| `false` | `1528` | Données regroupement invalides. (Adm + Org.+ Branch. + An.étude) | Modifier |
| `false` | `1530` | Mise à jour impossible; ce document est déjà approuvé par l'administration ! | Modifier |
| `false` | `1545` | Vous ne pouvez pas créer une 5ième intervention extérieure | Modifier |
| `false` | `1598` | Le type d'intervention extérieure est obligatoire | Modifier |
| `false` | `1599` | Le type d'intervention extérieure n'existe pas | Modifier |
| `false` | `1600` | Le sous-type d'intervention extérieure n'existe pas | Modifier |
| `false` | `1604` | La classification des périodes en intervention extérieure est incorrecte | Modifier |
| `false` | `2106` | Le code Année d'études de la population scolaire est incorrect | Modifier |
| `false` | `2118` | Le numéro de l'activité d'enseignement est incorrect | Modifier |
| `false` | `20015` | Le type d'intervention est obligatoire | Modifier |
| `false` | `20016` | Le type d'intervention "x" n'existe pas | Modifier |
| `false` | `20017` | Le sous-type d'intervention "x" n'existe pas | Modifier |
| `false` | `20034` | Le type d'intervention "x" n'est plus disponible à l'encodage | Modifier |
| `false` | `20035` | Le sous-type d'intervention "x" n'est plus disponible à l'encodage | Modifier |
| `false` | `20036` | Le sous-type d'intervention "x" n'est pas en relation avec le type d'intervention "x" | Modifier |
| `false` | `30016` | La date limite du "x" est dépassée pour l'encodage des valorisations en sanction (branches 92 et 94) | Modifier |
| `false` | `30017` | L'activité d'enseignement 98 (part supplémentaire) ne peut pas être encodée | Modifier |
| `false` | `99999` | Autres erreurs | toutes |

> **Codes partagés avec Document 1** : `00009`, `00011`, `00025`, `00999`, `1114`, `1113`,
> `1530`, `2106`, `99999`.
> **Codes spécifiques à Document 2** : `1527`, `1528`, `1545` (ici limité aux interventions),
> `1598`, `1599`, `1600`, `1604`, `2118`, `20015`-`20036`, `30016`, `30017`.

---

## Vérification croisée UML / XSD / PDF

### Diagramme page 7 (requête LireDocument2)
- ✅ `FormationDocument2LireReqCT` → `id : OrganisationReqIdCT` — conforme au XSD

### Diagramme page 8 (réponse LireDocument2 — FormationDocument2CT)
- ✅ Structure d'héritage `AbstractExternalResponseType` → `Document2ReponseCT` — conforme
- ✅ `FormationDocument2CT` : `id`, `activiteEnseignementDetail [0..1]`, `interventionExterieureListe [0..1]`, `swAppD2`, `tsMaj`, `teUserMaj` — conforme au XSD
- ⚠️ Même divergence PDF/XSD que Document 1 pour `implId` dans `OrganisationResIdCT` (PDF dit « obligatoire », XSD dit `minOccurs="0"`)

### Diagramme page 9 (Doc2ActiviteEnseignementDetailCT + Doc2ActiviteEnseignementLineCT)
- ✅ 14 champs dans `Doc2ActiviteEnseignementLineCT` — tous confirmés dans le XSD
- ✅ 4 totaux dans `Doc2ActiviteEnseignementDetailCT` — conformes

### Diagramme page 11 (Doc2InterventionExtLineCT + Doc2PeriodeExtLineCT)
- ✅ 8 champs dans `Doc2InterventionExtLineCT` — conformes au XSD
- ✅ 4 champs dans `Doc2PeriodeExtLineCT` — conformes

### Diagramme page 16 (requête ModifierDocument2)
- ✅ `FormationDocument2ModifReqCT` : `id` + `activiteEnseignementListe [0..1]` + `interventionExterieureListe [0..1]` — conforme
- ✅ `Doc2ActiviteEnseignementLineSaveCT` : 10 champs, 9 facultatifs — conforme
- ✅ `Doc2InterventionExtLineSaveCT` : 6 champs, `coNumIex` et `coCatCol` conformes

### Diagramme page 17 (Doc2InterventionExtLineSaveCT + Doc2PeriodeExtLineSaveCT)
- ✅ `Doc2PeriodeExtLineSaveCT` : `coCodePar` + `nbPerAn1 [0..1]` + `nbPerAn2 [0..1]` — conforme

### Diagramme page 20 (réponse ModifierDocument2)
- ✅ Structure identique à LireDocument2Reponse — conforme

---

## Mapping pyetnic

### Classe proposée : `FormationPeriodesService`

```python
class FormationPeriodesService:
    """Service EPROM Formation Périodes (Document 2) v1.0"""

    WSDL = "EpromFormationDocument2Service_external_v1.wsdl"
    ENDPOINT_TQ = "https://ws-tq.etnic.be/eprom/formation/document2/v1"
    ENDPOINT_PROD = "https://ws.etnic.be/eprom/formation/document2/v1"

    def lire(self, annee_scolaire: str, etab_id: int,
             num_adm_formation: int, num_organisation: int) -> Document2Response:
        """LireDocument2 — lecture du document périodes"""

    def modifier(self, annee_scolaire: str, etab_id: int,
                 num_adm_formation: int, num_organisation: int,
                 activites: list[ActiviteEnseignementSave] | None = None,
                 interventions: list[InterventionExtSave] | None = None) -> Document2Response:
        """ModifierDocument2 — modification des périodes et interventions"""
```

### Dataclasses proposées

```python
@dataclass
class ActiviteEnseignementSave:
    """Activité d'enseignement (type Save)"""
    co_num_branche: int
    nb_eleve_c1: int | None = None
    nb_periode_prevue_an1: float | None = None
    nb_periode_prevue_an2: float | None = None
    nb_periode_reelle_an1: float | None = None
    nb_periode_reelle_an2: float | None = None
    co_adm_reg: int | None = None
    co_org_reg: int | None = None
    co_bra_reg: int | None = None
    co_etu_reg: str | None = None


@dataclass
class PeriodeExtSave:
    """Période d'intervention extérieure (type Save)"""
    co_code_par: str                    # "CG", "CP", "SU"
    nb_per_an1: float | None = None
    nb_per_an2: float | None = None


@dataclass
class InterventionExtSave:
    """Intervention extérieure (type Save)"""
    co_cat_col: str                     # code type intervention
    co_num_iex: int | None = None       # numéro (facultatif pour création)
    co_obj_fse: str | None = None       # sous-type
    co_ref_pro: str | None = None       # projet global
    co_cri_cee: str | None = None       # agrément
    periodes: list[PeriodeExtSave] | None = None


@dataclass
class ActiviteEnseignementResponse:
    """Activité d'enseignement (type réponse, 14 champs)"""
    co_num_branche: int
    co_categorie: str
    te_nom_branche: str
    co_ann_etude: str
    nb_eleve_c1: int
    nb_periode_branche: float
    nb_periode_prevue_an1: float
    nb_periode_prevue_an2: float
    nb_periode_reelle_an1: float
    nb_periode_reelle_an2: float
    co_adm_reg: int
    co_org_reg: int
    co_bra_reg: int
    co_etu_reg: str
```

---

## XSD utilisés

| Fichier XSD | Identique à Document 1 ? |
|---|---|
| `Organisation_v1.xsd` | ✅ identique |
| `Common_v1.xsd` | ✅ identique |
| `AnneeScolaire_v1.xsd` | ✅ identique |
| `Etablissement_v1.xsd` | ✅ identique |
| `ResponseStatus_v3.xsd` | ✅ identique |
| `requestId_v1.xsd` | ✅ identique |
| `Addressing_v2.xsd` | ✅ identique |
| `Authorisation_v2.xsd` | ✅ identique |
