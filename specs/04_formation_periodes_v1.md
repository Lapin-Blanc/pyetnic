# EPROM - Formation Périodes (Document 2) v1.0

> Spécification technique et fonctionnelle complète
> Sources : contrat embarqué dans `pyetnic/resources/EPROM_Formation_Periodes_1.0/` (WSDL `EpromFormationDocument2Service_external_v1.wsdl` + `xsd/`), identique au service en ligne et à l'archive du catalogue SOA (relevé du 2026-11-24) + PDF Manuel d'utilisation v1.0.0 rev1.4 (27-04-2026, pied de page « Édité le 10/06/2025 », `ETNIC_Services_Web_EPROM_FormationPeriodes_v1.0_Manuel_d_utilisation_rev1.4.pdf`). La rev1.2 (30-09-2024, `Etnic_EpromFormationPeriodes_v1.0.0_Manuel_d_utilisation_rev1.2.pdf`) sert de point de comparaison ; la rev1.3 (01-07-2025), que suivait la version précédente de cette spec, n'est pas conservée dans `documentation/`.
> Date d'analyse : 2026-04-14 (rev1.3) ; passage à la rev1.4 le 2026-11-24

---

## Métadonnées

| Propriété | Valeur | Source |
|---|---|---|
| Produit | EPROM | manuel rev 1.4, p.1 |
| Service | Formation Périodes (Document 2) | manuel rev 1.4, p.1 et §1.1 |
| Version service | 1.0.0 | manuel rev 1.4, p.1 |
| Révision document | 1.4 (27-04-2026) | manuel rev 1.4, p.1 |
| Domaine | Enseignement - Promotion sociale | manuel rev 1.4, p.1 (« Objectifs du document ») |
| Type d'échange | Synchrone | manuel rev 1.4, §2.1 |
| Format messages | SOAP 1.1 | manuel rev 1.4, §2.2 ; contrat (binding `soap`) |
| Sécurité | WS-Security Username Token Profile (ou certificat X.509) | manuel rev 1.4, §2.1 |
| WSDL namespace | `http://services-web.etnic.be/eprom/formation/document2/v1` | contrat (WSDL) |
| Messages namespace | `http://services-web.etnic.be/eprom/formation/document2/messages/v1` | contrat (`EpromFormationDocument2Messages_external_v1.xsd`) |
| Types namespace (doc2) | `http://enseignement.cfwb.be/types/formation/document2/v1` | contrat (`FormationDocument2_v1.xsd`) |
| Types namespace (org) | `http://enseignement.cfwb.be/types/organisation/v1` | contrat (`Organisation_v1.xsd`) |
| Binding | `EPROMFormationDocument2ExternalV1Binding` (document/literal) | contrat (WSDL) ; manuel rev 1.4, §2.2.1 |

### Endpoints

| Env | URL | Source |
|---|---|---|
| TQ | `https://ws-tq.etnic.be/eprom/formation/document2/v1` | contrat (`soap:address` du WSDL) ; adresse de pyetnic depuis 0.3.0 |
| PROD | `https://ws.etnic.be/eprom/formation/document2/v1` | adresse de pyetnic depuis 0.3.0 |

> pyetnic appelle ces deux adresses de la passerelle ETNIC, certificat TLS vérifié dans les deux
> environnements : lecture vérifiée sur TQ et en production le 2026-11-24, pour tous les services
> EPROM (pyetnic 0.3.0).
>
> Le manuel donne d'autres adresses (rev 1.4, §2.2 et §2.2.1, p.4) : endpoint spécifique « EPROM »
> `https://services-web.tq.etnic.be/eprom/formation/document2/v1` (TQ) et
> `https://services-web.etnic.be/eprom/formation/document2/v1` (PROD), avec le port `11443` à
> ajouter pour TLS 1.2. pyetnic les appelait avant 0.3.0, port `11443` compris (CHANGELOG, #32).

> **Endpoint générique « Ecole »** (déprécié selon le manuel rev 1.4, §2.2.2, p.4 ; pyetnic ne l'utilise pas) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:FormationDocument2V1?mode=sync`, To = `http://services-web.etnic.be/eprom` (manuel rev 1.4, §3.1.2.2, p.6)
> - Binding annoncé : `FormationDocument2Binding` (manuel rev 1.4, §2.2.2), absent du WSDL embarqué, qui ne déclare que `EPROMFormationDocument2ExternalV1Binding` (contrat)

---

## Description fonctionnelle

Le service FormationDocument2 permet de gérer les informations relatives aux **périodes
de la formation organisée** (Doc 2) sauvegardées dans EPROM (manuel rev 1.4, §1.1 et §3.1.1).

Il expose **2 opérations** (contrat : WSDL ; manuel rev 1.4, §1.1), sans opération d'approbation,
contrairement au Document 1 :

1. **LireDocument2** - fournit les informations du document 2
2. **ModifierDocument2** - permet de modifier les données du document 2

> **Note sur le titre du PDF** : le titre mentionne "Formation Périodes" mais le nom interne
> est "Document 2" (manuel rev 1.4, §1.1 : « Doc 2 », opérations `LireDocument2` /
> `ModifierDocument2`). Le service gère deux grandes sections de données (contrat :
> `FormationDocument2CT`) :
> - Les **activités d'enseignement** (branches/cours avec périodes prévues et réelles)
> - Les **interventions extérieures** (conventions, fonds, projets) avec leurs propres périodes

> **Révisions du manuel** (historique, manuel rev 1.4, p.1) :
> - 1.0 (28-02-2017) : version initiale.
> - 1.1 (01-05-2023) : endpoint spécifique EPROM + TLS 1.2.
> - 1.2 (30-09-2024) : mise à jour des listes de valeurs. `R` et `S` (`coCatCol`) et onze codes
>   `coObjFse` y sont déjà barrés (manuel rev 1.2, p.20-21).
> - 1.3 (01-07-2025) : mise à jour des listes de valeurs pour le type d'intervention extérieure.
>   Fichier non conservé ; d'après la version précédente de cette spec, construite sur lui, il
>   ajoutait `coCatCol = "J"` (Réorientation 7TQ/7P) avec `coObjFse = "OA"` (à confirmer).
> - 1.4 (27-04-2026) : mise à jour des listes de valeurs pour le type d'intervention extérieure.
>
> **De la rev 1.2 à la rev 1.4** (comparaison des deux fichiers) :
> - `coCatCol` : ajout de `G` « BES » et de `J` « Réorientation 7TQ/7P », surlignés en jaune
>   (rev 1.4, §3.1.4.2, p.17) ; liste datée du 27-04-2026 au lieu du 30-09-2024.
> - `coObjFse` : ajout de `AI` « AeSI » (relation `G`) et de `OA` « Organisation des
>   Alternatives » (relation `J`), surlignés (p.18) ; mêmes codes barrés qu'à la rev 1.2.
> - Nouvelle règle : le type `J` impose le sous-type `OA`, le type `G` impose le sous-type `AI`
>   (rev 1.4, §1.2.2 p.3 et note p.17).
> - Nouvelle erreur `20041` (rev 1.4, §4, p.25).
> - Exemples : les en-têtes WS-Security / WS-Addressing des exemples de réponse disparaissent ;
>   l'exemple `LireDocument2` porte sur 2021-2022 (formation 186) au lieu de 2016-2017
>   (formation 44). 25 pages au lieu de 30.
> - Inchangés : le texte décrivant les types et cardinalités, les listes `coCategorie` et
>   `coCodePar` (toujours datées du 30-09-2024), les endpoints, le reste du tableau des erreurs.

---

## Bloc Retour - AbstractExternalResponseType (Common_v1.xsd)

> Même pattern que Formation Population (Document 1) et Formations Liste v2 (contrat :
> `Common_v1.xsd`, `success` obligatoire, `messages` 0..1 ; manuel rev 1.4, §2.4, p.5).
> Voir la documentation dans `03_formation_population_v1.md` ou `00_REGISTRE.md`.
> Le manuel renvoie à une « section 5 » pour les codes (§2.4) : ils sont en section 4.

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

(contrat : `EpromFormationDocument2Messages_external_v1.xsd`, `FormationDocument2_v1.xsd`,
`Organisation_v1.xsd`, `AnneeScolaireST` = motif `\d{4}-\d{4}` dans `AnneeScolaire_v1.xsd` ;
libellés : manuel rev 1.4, §3.1.3.2, p.7)

**Header SOAP** : `requestId` (UUID, optionnel en requête, obligatoire en réponse ; contrat : WSDL,
`wsdl:required` à `false` en entrée et `true` en sortie ; format UUID : manuel rev 1.4, §2.3, p.5).

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

(contrat : `Document2ReponseCT` dans `EpromFormationDocument2Messages_external_v1.xsd`,
`FormationDocument2CT` dans `FormationDocument2_v1.xsd` ; manuel rev 1.4, §3.1.3.4, p.8-11)

> **Écarts du manuel** (rev 1.4, §3.1.3.4) : le texte type `tsMaj` et `teUserMaj` en `boolean`
> (p.8), le contrat et le diagramme de la même page en `string` ; le texte dit `implId`
> « obligatoire » (p.9), le contrat et le diagramme (p.8) le donnent `[0..1]`. Le manuel nomme la
> réponse `LireDocument2ReponseCT` (p.8) et `ModifierDocument2ReponseCT` (p.20) : le contrat ne
> déclare que `Document2ReponseCT`, pour les deux opérations. Le contrat fait foi.

> **Différence avec Document 1** : un seul switch d'approbation (`swAppD2`) au lieu de deux
> (`swAppPopD1` + `swAppD1`) (contrat : `FormationDocument2_v1.xsd`, `FormationDocument1_v1.xsd`).
> `swAppD2` indique si le document est approuvé par l'administration (manuel rev 1.4, §3.1.3.4,
> p.8). Pas d'opération ApprouverDocument2 dans ce service (contrat : WSDL).
>
> L'administration bascule `swAppD1` et `swAppD2` ensemble, sans changer le `tsMaj` des deux
> documents (observé une fois, 2026-09-19).

> **Totaux** : les `nbTot*` comptent aussi les lignes administratives 91 à 99, pas seulement les
> branches de cours (observé une fois en production, sur une organisation, date non consignée).
> Le manuel les décrit seulement comme « périodes prévues / réelles totales » (rev 1.4, §3.1.3.4,
> p.9).

> **Avant la validation de la population**, `LireDocument2` est refusé en `20103` (testé sur TQ,
> 2026-11-10), qui lève `EtnicDocumentNotAccessibleError` depuis pyetnic 0.3.0. **À la
> validation**, le Doc 2 apparaît en squelette : toutes les branches du
> dossier avec leur volume (`nbPeriodeBranche`), les lignes 91 à 99 (`SEtu`, `ExPT`, `PeSu`,
> `PSup`, `CEtu`), tous les chiffres à 0 (observé en production le 2026-09-18, testé sur TQ le
> 2026-11-10). `nbEleveC1` y est aussi à 0 : l'effectif du Doc 1 n'est pas reporté (10 élèves au
> Doc 1, 0 au Doc 2 ; testé sur TQ, 2026-11-10).

### Doc2ActiviteEnseignementLineCT (ligne d'activité d'enseignement - réponse)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.3.4, p.9-10.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumBranche` | int | oui | Numéro de l'activité d'enseignement |
| `coCategorie` | string | oui | Code de la catégorie (voir table ci-dessous) |
| `teNomBranche` | string | oui | Nom de la branche |
| `coAnnEtude` | string | oui | Code de l'année d'étude |
| `nbEleveC1` | int | oui | Nombre d'élèves |
| `nbPeriodeBranche` | float | oui | Périodes prévues pour cette branche (volume complet : pour une UE sur deux années scolaires, différent de An1 + An2 ; observé en production, 2026-06-10, spec 20 §1.4) |
| `nbPeriodePrevueAn1` | float | oui | Périodes prévues la 1ʳᵉ année civile de l'année scolaire (septembre-décembre) |
| `nbPeriodePrevueAn2` | float | oui | Périodes prévues la 2ᵉ année civile de l'année scolaire (janvier-août) |
| `nbPeriodeReelleAn1` | float | oui | Périodes réelles la 1ʳᵉ année civile (septembre-décembre) |
| `nbPeriodeReelleAn2` | float | oui | Périodes réelles la 2ᵉ année civile (janvier-août) |
| `coAdmReg` | int | oui | Numéro administratif Rgp (regroupement activités) |
| `coOrgReg` | int | oui | Numéro d'organisation Rgp |
| `coBraReg` | int | oui | Numéro d'activité d'enseignement Rgp |
| `coEtuReg` | string | oui | Année d'études Rgp |

> **An1 / An2 = les deux années civiles** de l'année scolaire, pour les activités comme pour les
> interventions extérieures : l'écran nomme les colonnes par l'année civile (« Prévue (16) 2024 »,
> « Réel (19) 2025 » pour 2024-2025 ; observé en production, 2026-06-10, spec 20 §1.4). Les bornes
> en mois (septembre-décembre, janvier-août) sont déduites de ce découpage, non vérifiées. Le manuel
> dit seulement « la première année » / « la deuxième année » (rev 1.4, §3.1.3.4, p.10-11).

### Table des catégories (`coCategorie`)

Valeurs possibles à la date du 30-09-2024 (manuel rev 1.4, §3.1.3.4, p.9-10, liste identique à la
rev 1.2 ; hors contrat : `coCategorie` est un `xs:string`) :

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

### Doc2InterventionExtLineCT (ligne d'intervention extérieure - réponse)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.3.4, p.11. Valeurs de `coCatCol` et `coObjFse` : voir les tables de `ModifierDocument2`.

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

### Doc2PeriodeExtLineCT (période d'intervention extérieure - réponse)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.3.4, p.11 ; années civiles : voir la note An1 / An2 ci-dessus.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coCodePar` | string | oui | Code du type de périodes en intervention extérieure |
| `teLibPeriode` | string | oui | Label du type de périodes |
| `nbPerAn1` | float | oui | Nombre de périodes pour la 1ʳᵉ année civile (septembre-décembre) |
| `nbPerAn2` | float | oui | Nombre de périodes pour la 2ᵉ année civile (janvier-août) |

### Table des types de périodes d'intervention (`coCodePar`)

Valeurs possibles à la date du 30-09-2024 (manuel rev 1.4, §3.1.3.4, p.11 ; hors contrat :
`coCodePar` est un `xs:string`). L'écran EPROM affiche les mêmes trois lignes (observé en
production, 2026-06-10, spec 20 §1.4).

| Code | Libellé |
|---|---|
| `CG` | Cas généraux |
| `CP` | Cas particuliers |
| `SU` | Suppléments |

### Exemple de requête XML

Manuel rev 1.4, §3.1.3.3, p.7 ; `etabId` remplacé par 1234.

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
        <v12:etabId>1234</v12:etabId>
        <v12:numAdmFormation>186</v12:numAdmFormation>
        <v12:numOrganisation>1</v12:numOrganisation>
      </v11:id>
    </v1:LireDocument2>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (simplifié)

Manuel rev 1.4, §3.1.3.5, p.12-15, réduit à la première ligne ; `etabId` et `implId` remplacés par
1234 et 5678. Les totaux (10, 10, 20, 20) sont ceux de l'exemple complet, qui compte une seconde
branche.

```xml
<LireDocument2Reponse xmlns="http://services-web.etnic.be/eprom/formation/document2/messages/v1">
  <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
  <response>
    <p575:document2 xmlns:p575="http://enseignement.cfwb.be/types/formation/document2/v1">
      <p575:id>
        <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2021-2022</p752:anneeScolaire>
        <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">1234</p752:etabId>
        <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">5678</p752:implId>
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

(contrat : `FormationDocument2_v1.xsd` ; manuel rev 1.4, §3.1.4.2, p.16)

### Doc2ActiviteEnseignementLineSaveCT (activité d'enseignement - requête)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.4.2, p.16.

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
> `teNomBranche`, `coAnnEtude`, `nbPeriodeBranche`, que ce service ne peut donc pas modifier
> (contrat : `Doc2ActiviteEnseignementLineSaveCT`).

### Doc2InterventionExtLineSaveCT (intervention extérieure - requête)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.4.2, p.17-19.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coNumIex` | int | non | Numéro d'intervention (absent de l'exemple de requête du manuel, dont la réponse rend `coNumIex` 1 : rev 1.4, §3.1.4.3 et §3.1.4.5) |
| `coCatCol` | string | oui | Code du type d'intervention extérieure |
| `coObjFse` | string | non | Code du sous-type d'intervention |
| `coRefPro` | string | non | Code Projet global / Référence |
| `coCriCee` | string | non | Numéro agrément |
| `periodeListe` | Doc2PeriodeExtLstSaveCT | non | Liste de périodes |

### Doc2PeriodeExtLineSaveCT (période - requête)

Types et cardinalités : contrat (`FormationDocument2_v1.xsd`) ; libellés : manuel rev 1.4,
§3.1.4.2, p.19.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `coCodePar` | string | oui | Code du type de périodes (`CG`, `CP`, `SU`) |
| `nbPerAn1` | float | non | Nombre de périodes année 1 |
| `nbPerAn2` | float | non | Nombre de périodes année 2 |

> **Différence requête vs réponse** : le type Save n'a pas `teLibPeriode` (contrat).
> L'exemple du manuel envoie `CP` et `CG` seulement et reçoit les trois lignes `CG`, `CP`, `SU`,
> `SU` à 0 (rev 1.4, §3.1.4.3 et §3.1.4.5).

### Table des types d'intervention extérieure (`coCatCol`)

Valeurs possibles à la date du 27-04-2026 (manuel rev 1.4, §3.1.4.2, p.17, « validé hors contrat
xml » : `coCatCol` est un `xs:string` au contrat). Mêmes codes que `typeInterventionExterieure`
de l'Organisation v8 (spec 02). `R` et `S` sont barrés dans le manuel depuis la rev 1.2 au moins
(rev 1.2, p.20) ; `G` et `J` sont surlignés comme nouveaux à la rev 1.4.

| Code | Libellé | Statut |
|---|---|---|
| `A` | Personnel non chargé de cours | actif |
| `B` | Octroi périodes supplémentaires-bonus | actif |
| `C` | Convention | actif |
| `D` | Discriminations positives | actif |
| `E` | EHR | actif |
| `F` | Fonds Européens | actif |
| `G` | BES | **nouveau** (rev 1.4) - requiert `coObjFse = "AI"` |
| `I` | Formation des publics Infra scolarisés | actif |
| `J` | Réorientation 7TQ/7P | **nouveau** (rev 1.3 selon la version précédente de cette spec, surligné à la rev 1.4) - requiert `coObjFse = "OA"` |
| `K` | Octroi périodes cabinet-projets transver | actif |
| `P` | Formations continuées | actif |
| `Q` | Agence Qualité | actif |
| ~~`R`~~ | ~~Récupération périodes complémentaires~~ | **supprimé** (barré) |
| ~~`S`~~ | ~~CISCO système~~ | **supprimé** (barré) |
| `U` | Union Européenne | actif |
| `V` | Validation des compétences | actif |

> **Sous-type imposé** : « sélectionnez obligatoirement le sous-type « OA » avec le type « J » et
> le sous-type « AI » avec le type « G » » (manuel rev 1.4, note p.17 et §1.2.2 p.3). Le refus
> correspondant est sans doute `20041` (« Le sous-type d'intervention "x" est obligatoire avec le
> type d'intervention "x" », §4) : à confirmer sur TQ.

### Table des sous-types d'intervention (`coObjFse`)

Valeurs possibles à la date du 27-04-2026 (manuel rev 1.4, §3.1.4.2, p.17-19, « validé hors
contrat xml » ; codes actifs, avec la relation avec `coCatCol` que donne le manuel) :

| Code | Libellé | coCatCol |
|---|---|---|
| `AF` | AFOSOC(cnv cadre) | C |
| `AP` | APEF-FEBI | I |
| `PP` | APP Wallonie | K |
| `AC` | Actiris (Forem Bxl) | C |
| `AI` | AeSI | **G** (obligatoire pour coCatCol G ; nouveau rev 1.4) |
| `AE` | Aide à la Promotion de l'Emploi | B |
| `AL` | Alphabétisation | B |
| `CG` | CCG | F |
| `CD` | CEFORA(cnv cadre demandeurs emplois) | C |
| `CA` | CEFORA(cnv cadre pour employés) | C |
| `CE` | CEFORA(experts hors convention) | C |
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
| `OA` | Organisation des Alternatives | **J** (obligatoire pour coCatCol J ; surligné rev 1.4) |
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
| `LX` | zone Luxembourg | F |
| `WL` | Zone Wallonie | F |

> **Codes dépréciés (barrés dans le manuel, rev 1.2 p.20-21 et rev 1.4 p.18-19)** :
> `PI` (Convention Passerelle infirmière → I), `EP` (Epreuve de validation → V),
> `FE` (Fonds Européens → I), `FL` (Français langue étrangère → B),
> `1` (Obj 1:Hainaut → F), `2` (Obj.2:Hors Hainaut(Programmat 2007-2013) → F),
> `FR` (Plan de formation réseau → I), `PM` (Projets Ministre → I),
> `RC` (Remédiation Covid 19 → K), `RA` (Renfort administratif → B),
> `CS` (complément CESS → I)
>
> Le code `G` de cette table (« Sacrifices ENCC (antigel) ») est un sous-type du type `A` : à ne
> pas confondre avec le type `G` « BES » de `coCatCol`, dont le sous-type est `AI` (manuel rev 1.4,
> p.17 et p.19).

### Réponse

**Type** : `Document2ReponseCT` (identique à LireDocument2 - même type pour les 2 opérations ;
contrat : `EpromFormationDocument2Messages_external_v1.xsd`).

La réponse contient le document 2 complet après modification (manuel rev 1.4, §3.1.4.4 et
exemple §3.1.4.5, p.20-24).

### Sémantique d'écriture : mise à jour ligne par ligne

`ModifierDocument2` met à jour les lignes envoyées, ligne par ligne ; les lignes absentes de la
requête ne sont pas modifiées (testé sur TQ, 2026-11-10 : deux branches écrites à 10 et 20
périodes réelles An1, puis la première seule renvoyée à 11 ; la seconde est restée à 20). C'est
l'inverse du Document 3, dont `ModifierDocument3` remplace la liste d'enseignants de chaque
branche envoyée (spec 05).

La première écriture du Doc 2 fait passer `statutDocumentPopulationPeriodes` à « Encodé école »,
avec `dateStatut` au jour de l'écriture (spec 01 ; testé sur TQ, 2026-11-10).

Une fois le document approuvé par l'administration (`swAppD2`), la modification est refusée en
`1530` « Mise à jour impossible; ce document est déjà approuvé par l'administration ! » (libellé :
manuel rev 1.4, §4 ; rattachement à `swAppD2` : à confirmer).

**Interventions extérieures** : sémantique d'écriture non établie (inconnu, non testé). Seul
l'exemple du manuel suggère qu'une intervention envoyée sans `coNumIex` est créée (§3.1.4.3 et
§3.1.4.5) ; le sort d'une intervention absente de la requête est inconnu. Le libellé de `1545`,
« Vous ne pouvez pas créer une 5ième intervention extérieure » (manuel rev 1.4, §4), laisse lire
un maximum de quatre interventions par document (non testé).

### Exemple de requête XML

Manuel rev 1.4, §3.1.4.3, p.19-20 ; `etabId` remplacé par 1234.

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
        <v12:etabId>1234</v12:etabId>
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

Codes et libellés : manuel rev 1.4, §4, p.25, sauf `20103`, absent du manuel (libellé renvoyé par
le serveur, testé sur TQ, 2026-11-10). La colonne « Opérations » est une déduction de cette spec :
le manuel ne rattache pas les codes aux opérations (à confirmer, sauf mention d'un test). Exceptions
pyetnic : voir « Mapping pyetnic ».

| Success | Code | Description | Opérations |
|---|---|---|---|
| `true` | *(pas de code)* | Exécution de la requête sans erreur | toutes |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | Lire |
| `false` | `00011` | Enregistrement modifié par un autre utilisateur ! | Modifier |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | toutes |
| `false` | `00999` | Erreur sql | toutes |
| `false` | `1114` | Numéro d'établissement incorrect | toutes |
| `false` | `1113` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | toutes |
| `false` | `20103` | Le "Doc 1" doit être approuvé pour pouvoir accéder au document suivant | Lire, avant la validation de la population ; la validation par l'école (`swAppPopD1`) suffit, `swAppD1` peut rester faux (testé sur TQ, 2026-11-10) ; absent du manuel |
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
| `false` | `20041` | Le sous-type d'intervention "x" est obligatoire avec le type d'intervention "x" | Modifier (**nouveau** rev 1.4, absent de la rev 1.2) |
| `false` | `30016` | La date limite du "x" est dépassée pour l'encodage des valorisations en sanction (branches 92 et 94) | Modifier |
| `false` | `30017` | L'activité d'enseignement 98 (part supplémentaire) ne peut pas être encodée | Modifier |
| `false` | `99999` | Autres erreurs | toutes |

> **Codes partagés avec Document 1** : `00009`, `00011`, `00025`, `00999`, `1114`, `1113`,
> `1530`, `2106`, `99999` (comparaison avec la spec 03).
> **Codes spécifiques à Document 2** : `1527`, `1528`, `1545` (ici limité aux interventions ;
> au Document 1, « Doc 1 approuvé »), `1598`, `1599`, `1600`, `1604`, `2118`, `20015`-`20036`,
> `20041`, `20103`, `30016`, `30017`.

---

## Vérification croisée UML / XSD / PDF

Pages du manuel rev 1.4 (les numéros que citait la version précédente, construite sur la rev 1.3,
y désignent les mêmes diagrammes), confrontées au contrat embarqué le 2026-11-24.

### Diagramme page 7 (requête LireDocument2)
- ✅ `FormationDocument2LireReqCT` → `id : OrganisationReqIdCT` — conforme au XSD

### Diagramme page 8 (réponse LireDocument2 — FormationDocument2CT)
- ✅ Structure d'héritage `AbstractExternalResponseType` → `Document2ReponseCT` — conforme
- ✅ `FormationDocument2CT` : `id`, `activiteEnseignementDetail [0..1]`, `interventionExterieureListe [0..1]`, `swAppD2`, `tsMaj`, `teUserMaj` — conforme au XSD
- ⚠️ Le texte de la page 8 type `tsMaj` et `teUserMaj` en `boolean` ; le diagramme et le XSD disent `string`
- ⚠️ Même divergence PDF/XSD que Document 1 pour `implId` dans `OrganisationResIdCT` : le texte (p.9) dit « obligatoire », le diagramme (p.8) `[0..1]` et le XSD `minOccurs="0"`
- ⚠️ Le texte nomme la réponse `LireDocument2ReponseCT` ; le XSD ne déclare que `Document2ReponseCT`

### Diagramme page 9 (Doc2ActiviteEnseignementDetailCT + Doc2ActiviteEnseignementLineCT)
- ✅ 14 champs dans `Doc2ActiviteEnseignementLineCT` — tous confirmés dans le XSD
- ✅ 4 totaux dans `Doc2ActiviteEnseignementDetailCT` — conformes

### Diagramme page 11 (Doc2InterventionExtLineCT + Doc2PeriodeExtLineCT)
- ✅ 8 champs dans `Doc2InterventionExtLineCT` — conformes au XSD
- ✅ 4 champs dans `Doc2PeriodeExtLineCT` — conformes

### Diagramme page 16 (requête ModifierDocument2)
- ✅ `FormationDocument2ModifReqCT` : `id` + `activiteEnseignementListe [0..1]` + `interventionExterieureListe [0..1]` - conforme
- ✅ `Doc2ActiviteEnseignementLineSaveCT` : 10 champs, 9 facultatifs - conforme

### Diagramme page 17 (Doc2InterventionExtLineSaveCT + Doc2PeriodeExtLineSaveCT)
- ✅ `Doc2InterventionExtLineSaveCT` : 6 champs, seul `coCatCol` obligatoire - conforme
- ✅ `Doc2PeriodeExtLineSaveCT` : `coCodePar` + `nbPerAn1 [0..1]` + `nbPerAn2 [0..1]` - conforme

### Diagramme page 20 (réponse ModifierDocument2)
- ✅ Structure identique à LireDocument2Reponse - conforme
- ⚠️ Le diagramme et le texte nomment `ModifierDocument2ReponseCT` et un `responseType` ; le XSD
  utilise `Document2ReponseCT` et `Document2ReponseMetierCT`, comme pour `LireDocument2`

### Endpoint générique (§2.2.2)
- ⚠️ Le binding `FormationDocument2Binding` annoncé par le manuel n'existe pas dans le WSDL
  embarqué, qui ne déclare que `EPROMFormationDocument2ExternalV1Binding`

---

## Mapping pyetnic

Fonctions de `pyetnic.eprom`, implémentées dans `pyetnic/services/document2.py` (service
`DOCUMENT2` de `Config.SERVICES`, WSDL embarqué, binding `EPROMFormationDocument2ExternalV1Binding`,
authentification `UsernameToken`).

| Élément du contrat | pyetnic | Notes |
|---|---|---|
| `LireDocument2` | `lire_document_2(organisation_id: OrganisationId) -> Optional[FormationDocument2]` | `None` seulement en mode permissif (déprécié) |
| `ModifierDocument2` | `modifier_document_2(organisation_id: OrganisationId, activite_enseignement_liste: Optional[Doc2ActiviteEnseignementListSave] = None, intervention_exterieure_liste: Optional[Doc2InterventionExtListSave] = None) -> Optional[FormationDocument2]` | n'envoie que les listes fournies et, dans chaque ligne, les champs non `None` (`to_soap_dict`) ; rend le document de la réponse |
| `OrganisationReqIdCT` | `OrganisationId` | `implId` n'est jamais envoyé (`organisation_request_id`) |
| `FormationDocument2CT` | `FormationDocument2` | `id` est l'`id` de la réponse, `implId` compris (observé sur TQ et en production, 2026-11-25), complété par celui de l'appelant pour ce qui y manquerait (#51) |
| `Doc2ActiviteEnseignementDetailCT` | `Doc2ActiviteEnseignementDetail` | |
| `Doc2ActiviteEnseignementLstCT` / `Doc2ActiviteEnseignementLineCT` | `Doc2ActiviteEnseignementList` / `Doc2ActiviteEnseignementLine` | 14 champs, dans l'ordre du XSD |
| `Doc2InterventionExtLstCT` / `Doc2InterventionExtLineCT` | `Doc2InterventionExtList` / `Doc2InterventionExtLine` | `periodeListe` à `None` si la réponse n'en porte pas |
| `Doc2PeriodeExtLstCT` / `Doc2PeriodeExtLineCT` | `Doc2PeriodeExtList` / `Doc2PeriodeExtLine` | |
| `Doc2ActiviteEnseignementLstSaveCT` / `Doc2ActiviteEnseignementLineSaveCT` | `Doc2ActiviteEnseignementListSave` / `Doc2ActiviteEnseignementLineSave` | `coNumBranche` requis, le reste `Optional` |
| `Doc2InterventionExtLstSaveCT` / `Doc2InterventionExtLineSaveCT` | `Doc2InterventionExtListSave` / `Doc2InterventionExtLineSave` | `coCatCol` requis et placé en premier, le reste `Optional` |
| `Doc2PeriodeExtLstSaveCT` / `Doc2PeriodeExtLineSaveCT` | `Doc2PeriodeExtListSave` / `Doc2PeriodeExtLineSave` | `coCodePar` requis |
| `coCatCol` | `str` | les 14 codes actifs de la rev 1.4 sont ceux de l'enum `TypeInterventionExterieure`, documentée pour `Organisation.typeInterventionExterieure` |
| `coObjFse`, `coCodePar`, `coCategorie` | `str` | pas d'enum |

**Erreurs** : depuis pyetnic 0.3.0, un refus (`success=false`) lève l'exception typée de son code ;
le mode permissif (`permissive_errors()` ou `Config.RAISE_ON_ERROR = False`, qui rend `None`) est
déprécié et disparaît en 1.0. Une erreur de transport lève `EtnicTransportError` (alias
`SoapError`). Routage pour ce service, `map_etnic_error_code_to_class(code, service="DOCUMENT2")`
(`pyetnic/exceptions.py`) :

| Codes | Exception |
|---|---|
| `00009` | `EtnicNotFoundError` |
| `00011` | `EtnicConcurrencyError` |
| `20103` | `EtnicDocumentNotAccessibleError` |
| `1530` | `EtnicAlreadyApprovedError` |
| `1545` | `EtnicValidationError` : sens propre au Document 2 (« 5ième intervention extérieure »), fixé par `_SERVICE_CODE_TO_CLASS` ; `EtnicAlreadyApprovedError` aux Documents 1 et 1D |
| `1113`, `1114`, `1527`, `1528`, `1598`, `1599`, `1600`, `1604`, `2106`, `2118`, `20015` à `20036`, `20041`, `30016`, `30017` | `EtnicValidationError` |
| `00025`, `00999`, `99999` | `EtnicBusinessError` (classe de base) |

---

## XSD utilisés

Les huit schémas communs sont identiques, octet pour octet, à ceux du Document 1
(`pyetnic/resources/EPROM_Formation_Population_1.0/xsd/`, comparaison du 2026-11-24). Les deux
schémas propres au service sont `FormationDocument2_v1.xsd` (types) et
`EpromFormationDocument2Messages_external_v1.xsd` (messages).

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
