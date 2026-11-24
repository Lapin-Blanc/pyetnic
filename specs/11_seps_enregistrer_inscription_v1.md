# SEPS - Enregistrer Inscription (à une UE) v1

> Spécification technique et fonctionnelle complète
> Sources :
> - **Manuel** : « Services Web SEPS - Enregistrer Inscriptions » **2.4** (version de service 2.4.0, rev 16.0, 18/06/2026, `ETNIC_Services_Web_SIEL_SEPS_EnregistrerInscriptions_v2.4_Manuel_d_utilisation_rev16.0.pdf`), §2, §3.1 (types), §3.3 (service). Remplace le manuel général 2.1.9 (18/01/2023, §3.1.9 à §3.1.11 et §3.6) comme référence.
> - **Contrat** : WSDL + XSD servis par la production (`https://ws.etnic.be/seps/enregistrerInscription/v1?wsdl`), embarqués dans `pyetnic/resources/SEPS_Enregistrer_Inscription_2.1/` (relevé du 2026-11-24).
> - **Observations de production** (datées dans le texte).
>
> Première analyse : 2026-06-09 (session 7). Refonte : 2026-11-24 (#24).
> **Préambule famille SEPS** (X.509, endpoints, SOAP Fault, bloc retour) : voir **spec 09**.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Enregistrer Inscription à une Unité d'Enseignement (UE) |
| Version contrat / manuel | external **v1** / manuel **2.4** (service 2.4.0) |
| Sécurité | WS-Security X.509 · SOAP 1.1 · synchrone · TLS 1.2 et 1.3 (manuel 2.4, §2.1) |
| WSDL namespace | `http://ws.etnic.be/seps/enregistrerInscription/v1` |
| Messages namespace | `http://ws.etnic.be/seps/enregistrerInscription/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/inscription/v1` |
| Binding | `SEPSEnregistrerInscriptionV1ExternalBinding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | manuel 2.4, §2.2 | `https://ws-tq.etnic.be/seps/enregistrerInscription/v1` |
| PROD | manuel 2.4, §2.2 | `https://ws.etnic.be/seps/enregistrerInscription/v1` |
| PROD | contrat de production (`soap:address`) | `https://ws.etnic.be:443/seps/enregistrerInscription/v1` |

### Contrôle d'accès (manuel 2.4, §3.3)
- Profil **support** : non limité.
- Profil(s) **établissement** : sauvegarde uniquement dans le périmètre du ou des profils.
- Profil **PO** : sauvegarde uniquement dans les établissements du PO.

Hors périmètre : `30013` « You don't have the right to register in this establishment ».

---

## Description fonctionnelle

Gestion de l'**inscription d'un étudiant à une UE**. Deux opérations partageant la **même structure de requête** (`InscriptionInputDataType`) et de réponse (`InscriptionType`) :

1. **enregistrerInscription** : création d'une nouvelle inscription.
2. **modifierInscription** : modification d'une inscription existante.

L'étudiant est identifié par son **`cfNum`** (services Étudiant, specs 09-10). L'UE est identifiée par `noAdministratif` + `noOrganisation` : numéro administratif de la formation et numéro d'organisation EPROM (spec 02).

---

## Versions du contrat

Le schéma `inscription_v1.xsd` existe en trois états (relevé du 2026-11-24) :

| Élément | Catalogue SOA « 2.1 » | Production `rechercheInscriptions` et TQ (les deux services) | Production `enregistrerInscription` |
|---|---|---|---|
| `InscriptionType.audit` | - | ✓ | ✓ |
| `InscriptionInputType.fse` | - | ✓ | ✓ |
| `DroitInscription(Specifique)Type.montant` | - | ✓ | ✓ |
| `SanctionType` : `pourcentageAttribue`, `codeSectionFlag`, `codeSection`, `point` ; `codeSanction` facultatif | - | ✓ | ✓ |
| `CodeAdmissionType` `AUCUN` ; `C50` dans `MotifExemptionSpecType` et `ValorisationAcquisType` | - | ✓ | ✓ |
| `SpecificiteDataType.regulier3` | - | - | ✓ |
| `SanctionType.ajournement1Session` | - | - | ✓ |
| `SpecificiteDataInputType` (type jamais référencé) | défini | supprimé | supprimé |

`regulier3` et `ajournement1Session` arrivent avec le manuel 2.4 rev 16.0 (« Ajout de regulier3 et ajournement1Session », service 2.4.0). Le reste figure déjà dans l'historique des révisions antérieures du manuel. Une requête construite avec le contrat du catalogue reste valide contre celui de production.

---

## Type de requête - `InscriptionInputDataType` (`inscription_v1.xsd`)

L'élément racine de requête est **`inscriptionInputData`** (`minOccurs=0` au contrat, requis en pratique).

```
InscriptionInputDataType
├── cfNum               : cfNumType            [obligatoire]   identifie l'étudiant
├── idEtab              : xs:integer           [obligatoire]   id FASE établissement
├── idImplantation      : xs:integer           [obligatoire]   id FASE implantation
├── codePostalLieuCours : CodePostalLieuType   [obligatoire]   string(≤7) ; erreur 30012 si inconnu
└── inscription         : InscriptionInputType [obligatoire]
```

### InscriptionInputType (manuel 2.4, §3.1.2)
```
InscriptionInputType
├── dateInscription : DateType            [obligatoire]   string(≤10), format AAAA-MM-JJ
├── statut          : CodeStatutType      [obligatoire]   DE / AN
├── anneeScolaire   : xs:integer          [0..1 contrat]  « obligatoire » (manuel : 30101 si absent) ; millésime, ex. 2026
├── ue              : UEInputType         [0..1 contrat]  « obligatoire » (manuel : 30100 si absent)
├── specificite     : SpecificiteDataType [0..1 contrat]  « obligatoire » (manuel : 30025 si absent)
└── fse             : xs:boolean          [0..1]          défaut true (contrat de production, manuel 2.4)
```
- `anneeScolaire`, `ue` et `specificite` sont facultatifs au contrat mais **obligatoires** selon le manuel : les fournir toujours.
- **`fse`** (manuel 2.4, §3.1.2) : facultatif, **`true` par défaut**. À `true`, les champs FSE de `specificite` sont obligatoires **si l'UE est FSE** ; à `false`, ils ne le sont pas. Ils ne le sont pas non plus si l'inscription n'est pas régulière au 1/10.

### UEInputType
```
UEInputType
├── noAdministratif : ShortType [obligatoire]   (xs:integer ≤ 32767), n° administratif de l'UE
└── noOrganisation  : ShortType [obligatoire]   n° d'organisation de l'UE
```

### SpecificiteDataType (entrée et sortie, manuel 2.4 §3.1.2.2 et §3.1.3.3)
```
SpecificiteDataType   (tous les champs [0..1], dans cet ordre au contrat)
├── regulier1                  : IndicateurType     régulier au 1er dixième
├── regulier3                  : IndicateurType     régulier au 3e dixième (contrat enregistrerInscription seulement)
├── regulier5                  : IndicateurType     régulier au 5e dixième
├── droitInscription           : DroitInscriptionType
├── droitInscriptionSpecifique : DroitInscriptionSpecifiqueType
├── dureeInoccupation          : DureeInoccupationType   UE FSE seulement, alors obligatoire
├── situationMenage            : SituationMenageType     UE FSE seulement, alors obligatoire
├── enfantACharge              : IndicateurType          UE FSE seulement, alors obligatoire
├── difficulteHandicap         : IndicateurXType         UE FSE seulement, alors obligatoire
├── difficulteAutre            : IndicateurXType         UE FSE seulement, alors obligatoire
├── admission                  : AdmissionType           obligatoire (30025 si absent)
└── sanction                   : SanctionType            facultatif
```

**Règles des indicateurs de régularité** (manuel 2.4, §3.1.2.2) :
- `regulier1` : défaut **`N`** s'il est absent ; mais défaut **`O`** si l'inscription est enregistrée **après** la validation au 1/10. **Verrouillé** une fois l'UE validée au 1/10 (`30079`).
- `regulier5` : défaut `N` ; **verrouillé** une fois l'UE validée au 5/10 (`30080`).
- `regulier3` : « indique si l'étudiant est régulier au 3e dixième ». Le manuel ne lui donne ni défaut ni verrou propre (la phrase « la valeur par défaut est N » suit `regulier5` dans ce manuel, `regulier3` dans le manuel Recherche Inscriptions 2.4). Aucun code d'erreur ne lui est associé. Non observé en production.

---

## Sous-types et énumérations (manuel 2.4, §3.1.4)

### Indicateurs
- **IndicateurType** : `O` (oui) / `N` (non).
- **IndicateurXType** : `O` / `N` / `X` (« n'accepte pas de préciser »). `difficulteHandicap` et `difficulteAutre` sont de ce type.

### CodeStatutType - statut de l'inscription
| Code | Signification |
|---|---|
| `DE` | Inscription **définitive** |
| `AN` | Inscription **annulée** |

### DroitInscriptionType - droit d'inscription (DI)
```
DroitInscriptionType
├── indicateurDroitInscription : IndicateurType [obligatoire]   O = le droit doit être perçu
├── montant                    : xs:string      [0..1]          contrat de production ; « champ texte facultatif si indicateurDroitInscription est O »
└── exempte : ExempteDroitInscriptionType [0..1]
    ├── indicateurExempteDroitInscription : IndicateurType [obligatoire]   exclusif de indicateurDroitInscription (30033)
    └── motifExemption : MotifExemptionType [obligatoire]   interprété seulement si indicateurExempte = O
```
**MotifExemptionType** :
| Code | Motif |
|---|---|
| `C01` | Mineur soumis à l'obligation scolaire |
| `C02` | Chômeur complet indemnisé |
| `C03` | Étudiant avec handicap reconnu |
| `C04` | Bénéficiaire du revenu d'intégration |
| `C05` | Membre du personnel enseignant en formation continuée ou recyclage |
| `C06` | Obligation d'une autorité publique |
| `C07` | Autre |

### DroitInscriptionSpecifiqueType - droit d'inscription spécifique (DIS)
Manuel 2.4, §3.1.4.5 : « uniquement si l'étudiant est de nationalité hors CEE (sinon code d'erreur 30023) ».
```
DroitInscriptionSpecifiqueType
├── indicateurDroitInscriptionSpecifique : IndicateurType [obligatoire]   O = le droit doit être perçu
├── montant                              : xs:string      [0..1]          contrat de production ; facultatif si l'indicateur est O
└── exempte : ExempteDroitInscriptionSpecType [0..1]
    ├── indicateurExempteDroitInscriptionSpec : IndicateurType [obligatoire]   exclusif (30033 / 30034)
    └── motifExemptionSpec : MotifExemptionSpecType [obligatoire]
```
**MotifExemptionSpecType** :
| Code | Motif | Code | Motif |
|---|---|---|---|
| `C01` | Soumis à l'obligation scolaire | `C08` | Pris en charge par le CPAS |
| `C02` | Ressortissant d'un État membre de l'UE | `C09` | Admis à séjourner plus de 3 mois (loi du 15/12/1980) |
| `C03` | Parents/tuteur belges | `C10` | Demande de régularisation (loi du 15/12/1980) |
| `C04` | Parents/tuteur (non belges) résidant en Belgique | `C11` | Placé par le juge de la jeunesse |
| `C05` | Marié/cohabitant avec conjoint résidant en Belgique | `C12` | Sous tutelle officieuse (Code civil) |
| `C06` | Résidant en Belgique avec activité professionnelle ou revenu de remplacement | `C13` | Visé par l'art. 42bis du décret du 30/06/1998 |
| `C07` | Réfugié ou candidat réfugié reconnu (loi du 15/12/1980) | **`C50`** | **Séjour limité aux études** (contrat de production, manuel 2.4) |

> **Observé en production (2026, fréquence non relevée)** : un `droitInscriptionSpecifique` à indicateur **`O`** a été accepté pour des étudiants **ressortissants de l'UE**. Le contrôle `30023` n'est donc pas appliqué comme le manuel le décrit, et l'indicateur `O` ne garantit pas que l'étudiant relève du DIS.

### DureeInoccupationType (FSE)
| Code | Durée |
|---|---|
| `C00` | < 6 mois |
| `C06` | > 6 et < 12 mois |
| `C12` | > 12 et < 24 mois |
| `C24` | > 24 mois |

### SituationMenageType (FSE)
| Code | Signification |
|---|---|
| `ISOL` | Isolé |
| `SSEM` | Ménage sans emploi |
| `A1EM` | Ménage dont au moins une personne occupe un emploi |
| `X` | N'accepte pas de préciser |

### AdmissionType (manuel 2.4, §3.1.4.8)
```
AdmissionType
├── codeAdmission      : CodeAdmissionType      [obligatoire]
├── typeEnseignement   : TypeEnseignementType   [0..1]  obligatoire si codeAdmission = TITREBEL
├── titreDelivre       : TitreDelivreType       [0..1]  obligatoire si TITREBEL, dépend de typeEnseignement
├── equivalence        : EquivalenceType        [0..1]  obligatoire si codeAdmission = TITREETR
└── valorisationAcquis : ValorisationAcquisType [0..1]  obligatoire si codeAdmission = AUTRE
```
**CodeAdmissionType** : `REUSSITE` (certificat de réussite d'UE), `TITREBEL` (titre d'études en Belgique), `TITREETR` (titre d'études hors Belgique), `AUTRE`, **`AUCUN`** (« aucun titre requis », contrat de production, manuel 2.4).
> Le libellé de `30025` cite toujours « REUSSITE, TITREBEL, TITREETR, AUTRE », sans `AUCUN`. Le manuel ne dit pas quels champs additionnels `AUCUN` admet ; `ValorisationAcquis C40` porte le même libellé. Non observé en production.

**TypeEnseignementType** : `PRI` (primaire), `SIPE`/`SSPE` (secondaire inférieur/supérieur de plein exercice), `SIPS`/`SSPS` (secondaire inférieur/supérieur de promotion sociale), `SCPE`/`SLPE` (supérieur court/long de plein exercice), `SCPS`/`SLPS` (supérieur court/long de promotion sociale).

**TitreDelivreType** (23 valeurs, applicabilité selon `typeEnseignement`, manuel 2.4 §3.1.4.8) : `CEB`, `CE1D`, `CESI`, `CE2D`, `CQ4`, `CESSG`, `CESST`, `CESSQ`, `CESSP`, `CESSA`, `CE6P`, `CQ6`, `CQ7`, `DAES`, `BES`, `BACH`, `MAST`, `CESS`, `CQINF`, `CQSUP`, `BACHSPE`, `MASTSPE`, `DOC`.

**EquivalenceType** (si TITREETR) : `C01` (secondaire inférieur), `C02` (secondaire supérieur), `C03` (supérieur), `C04` (CEB).

**ValorisationAcquisType** (si AUTRE) : `C01`-`C04` (admission ou dispense V1 à V4, formelle), `C10` (VANFI, test/épreuve), `C20` (VANFI, dossier), `C30` (autres), `C40` (aucun titre requis), **`C50`** (« inconnu », **uniquement pour les années scolaires antérieures à 2023** ; contrat de production, manuel 2.4).

### SanctionType (manuel 2.4, §3.1.4.9)
```
SanctionType   (tous les champs [0..1] au contrat de production)
├── codeSanction               : CodeSanctionType               facultatif (obligatoire au catalogue 2.1 et au manuel 2.1.9)
├── valorisationAcquisSanction : ValorisationAcquisSanctionType obligatoire si codeSanction = RE
├── motifAbandon               : MotifAbandonType               obligatoire si codeSanction = AB
├── statutFinFormation         : StatutFinFormationType         UE FSE seulement
├── pourcentageAttribue        : xs:string                      seulement si codeSanction = RE (ajout du 23/09/2024)
├── codeSectionFlag            : xs:boolean                     défaut false ; à true, codeSection doit être rempli
├── codeSection                : CodeSectionType                string de 11 caractères exactement
├── point                      : xs:string                      facultatif
└── ajournement1Session        : IndicateurType                 contrat enregistrerInscription seulement (manuel rev 16.0)
```
- `codeSectionFlag`, `codeSection` et `point` « ne sont pris en compte que pour les **épreuves intégrées** », facultatifs sinon.
- `ajournement1Session` : le manuel n'en donne que le type. Sens supposé (ajournement en première session), non documenté, non observé.
- Le manuel 2.4 corrige la documentation antérieure : le champ de valorisation de la sanction est `valorisationAcquisSanction`, non `valorisationAcquis`.

**CodeSanctionType** : `RE` (réussite) / `AB` (abandon) / `EH` (échec).
**ValorisationAcquisSanctionType** (si RE) : `C00` (réussite), `C01`-`C04` (valorisation des acquis formels V1 à V4), `C05` (VANFI test ou épreuves).
**MotifAbandonType** (si AB) : `TPS` (manque de temps), `PRO` (raisons professionnelles), `FAM` (raisons familiales), `SAN` (santé), `ATT` (formation ne correspondant pas aux attentes), `MEM` (mise à l'emploi), `FMJ` (force majeure), `NUM` (fracture numérique), `AUT` (autres), `INC` (inconnu).
**StatutFinFormationType** (FSE) : le manuel 2.4 écrit désormais `C01`-`C06`, comme le contrat (le manuel 2.1.9 écrivait `01`-`06`) :
| Code | Signification |
|---|---|
| `C01` | Mise à l'emploi après la formation |
| `C02` | Poursuite d'une formation dans le cadre du PI |
| `C03` | Poursuite d'une formation hors du cadre du PI |
| `C04` | Aide à la recherche d'emploi après la formation |
| `C05` | Réorientation vers un autre type d'action |
| `C06` | Fin de formation sans suite connue |

### Types de base
- **CodePostalLieuType** : `string` (maxLength 7).
- **DateType** : `string` (maxLength 10), pas `xs:date`. Format attendu `AAAA-MM-JJ`.
- **TextType** : `string` (maxLength 250).
- **ShortType** : `xs:integer`, maxInclusive 32767.
- **CodeSectionType** : `string`, exactement 11 caractères.
- **CodeNiveauType** (sortie UE) : `SI` (secondaire inférieur) / `SS` (secondaire supérieur) / `SC` (supérieur court) / `SL` (supérieur long).

---

## Opérations enregistrerInscription / modifierInscription

### Requête
`enregistrerInscription` / `modifierInscription` -> `{Enregistrer|Modifier}InscriptionRequeteType` -> `inscriptionInputData : InscriptionInputDataType [0..1]`.

`modifierInscription` (manuel 2.4, §3.3.2.1) : un champ obligatoire reste obligatoire ; un champ facultatif **absent est effacé** après la sauvegarde. Il faut renvoyer l'inscription complète, telle que lue, avec les changements.

### Réponse
`{enregistrer|modifier}InscriptionReponse` -> extends `AbstractExternalResponseType` -> `response/inscription : InscriptionType [0..1]` (type complet de **sortie**, avec `audit` au contrat de production : spec 12).

### Codes de retour (manuel 2.4, §3.3.1.3.2, partagés enregistrer/modifier)

| Code | Description (manuel) | Règle métier | Error label |
|---|---|---|---|
| `201` | Ok création | | SUCCESS |
| `200` | Ok modification | | SUCCESS |
| `30051` | Ok création mais inscrit dans **plus de 4 UE** | oui | SUCCESS |
| `30010` | Please enter a valid inscriptionInput | | BAD_REQUEST |
| `30011` | No student found for this CF | | BAD_REQUEST |
| `30012` | The postCode is unknown | | BAD_REQUEST |
| `30013` | You don't have the right to register in this establishment | | BAD_REQUEST |
| `30014` | The inscription date is a mandatory field | | BAD_REQUEST |
| `30015` | The status code is a mandatory field | | BAD_REQUEST |
| `30016` | You can not modify a canceled inscription | oui | BAD_REQUEST |
| `30017` | You can not create a new inscription with status 'canceled' | | BAD_REQUEST |
| `30018` | Missing mandatory field for admission | oui | BAD_REQUEST |
| `30019` | Missing mandatory field for sanction | oui | BAD_REQUEST |
| `30020` | Missing mandatory field | oui | BAD_REQUEST |
| `30021` | Missing mandatory field for FSE | oui | BAD_REQUEST |
| `30022` | Field not authorized for non FSE | oui | BAD_REQUEST |
| `30023` | Specific right not authorized for UE student | oui | BAD_REQUEST |
| `30024` | The student should have at least 15 years at the beginning of the UE | oui | BAD_REQUEST |
| `30025` | Please fill in one valid admission criteria : REUSSITE, TITREBEL, TITREETR, AUTRE | oui | BAD_REQUEST |
| `30026` | No additional fields are valid for the admission type REUSSITE | oui | BAD_REQUEST |
| `30027` | Only teachingType and the issuedTitle are valid for the admission type TITREBEL | oui | BAD_REQUEST |
| `30028` | Only Equivalence is valid for the admission type TITREETR | oui | BAD_REQUEST |
| `30029` | Only ExperienceEnhancing is valid for the admission type AUTRE | oui | BAD_REQUEST |
| `30030` | Please fill in one valid sanction code : RE, EH, AB | oui | BAD_REQUEST |
| `30031` | Only ExperienceEnhancing is valid for the sanction type RE | oui | BAD_REQUEST |
| `30032` | Only AbandonmentReason is valid for the sanction type AB | oui | BAD_REQUEST |
| `30033` / `30034` | Incompatible fields : can not be at the same time exempted and not exempted (rightIndicator = O) | oui | BAD_REQUEST |
| `30035` | Incompatible fields : the teachingType and the issuedTitle don't match | oui | BAD_REQUEST |
| `30041` | Validation cfNum | | BAD_REQUEST |
| `30070` | You can not cancel the inscription | oui (« flag 1/10ième ») | BAD_REQUEST |
| `30079` | You can not modify regulier1 for this ue | oui | BAD_REQUEST |
| `30080` | You can not modify regulier5 for this ue | oui | BAD_REQUEST |
| `30100` | UE data missing or incomplete - No result found | | NOT_FOUND |
| `30101` | The information doesn't match with an existing UE | | NOT_FOUND |
| `30102` | No inscription found for those criteria | | NOT_FOUND |
| `30200` | An inscription already exists for that UE | | CONFLICT |
| `30443` | Aucune modification à appliquer | | BAD_REQUEST |

> Le tableau est identique à celui du manuel 2.1.9 (§3.6.1.3.2). Aucun code n'est associé à `regulier3`, `fse`, `montant`, `AUCUN`, `C50` ni aux champs ajoutés à la sanction.
> **Niveau du message** : le manuel montre `30200` en `error` et `30101` en **`warning`**, tous deux avec `success=false` (§3.3.1.4.2) ; `30443` en `error` pour `modifierInscription` (§3.3.2.4.2). L'exemple de création réussie (§3.3.1.4.1) ne porte **aucun** message : `success=true` seul.

### Exemple de requête (enregistrerInscription, identifiants fictifs)
```xml
<v11:enregistrerInscription xmlns:v11="http://ws.etnic.be/seps/enregistrerInscription/messages/v1"
                            xmlns:v12="http://enseignement.cfwb.be/types/seps/inscription/v1">
  <v11:inscriptionInputData>
    <v12:cfNum>1234567-89</v12:cfNum>
    <v12:idEtab>1234</v12:idEtab>
    <v12:idImplantation>5678</v12:idImplantation>
    <v12:codePostalLieuCours>1000</v12:codePostalLieuCours>
    <v12:inscription>
      <v12:dateInscription>2026-09-15</v12:dateInscription>
      <v12:statut>DE</v12:statut>
      <v12:anneeScolaire>2026</v12:anneeScolaire>
      <v12:ue><v12:noAdministratif>421</v12:noAdministratif><v12:noOrganisation>1</v12:noOrganisation></v12:ue>
      <v12:specificite>
        <v12:regulier1>O</v12:regulier1><v12:regulier5>O</v12:regulier5>
        <v12:droitInscription>
          <v12:indicateurDroitInscription>N</v12:indicateurDroitInscription>
          <v12:exempte>
            <v12:indicateurExempteDroitInscription>O</v12:indicateurExempteDroitInscription>
            <v12:motifExemption>C03</v12:motifExemption>
          </v12:exempte>
        </v12:droitInscription>
        <v12:dureeInoccupation>C12</v12:dureeInoccupation>
        <v12:situationMenage>ISOL</v12:situationMenage>
        <v12:enfantACharge>O</v12:enfantACharge>
        <v12:difficulteHandicap>O</v12:difficulteHandicap>
        <v12:difficulteAutre>O</v12:difficulteAutre>
        <v12:admission><v12:codeAdmission>REUSSITE</v12:codeAdmission></v12:admission>
      </v12:specificite>
    </v12:inscription>
  </v11:inscriptionInputData>
</v11:enregistrerInscription>
```

---

## Règles métier (manuel 2.4)

- **UE FSE** (`ue.fse = O` en sortie) : `dureeInoccupation`, `situationMenage`, `enfantACharge`, `difficulteHandicap`, `difficulteAutre` deviennent **obligatoires** (`30021`) et `statutFinFormation` s'applique à la sanction ; ces champs sont **interdits** pour une UE non FSE (`30022`). Le flag d'entrée `fse=false`, ou une inscription non régulière au 1/10, lève l'obligation.
- **Admission** : un seul jeu de champs additionnels selon `codeAdmission` (REUSSITE : aucun ; TITREBEL : `typeEnseignement` + `titreDelivre` ; TITREETR : `equivalence` ; AUTRE : `valorisationAcquis`). Erreurs `30018`, `30025` à `30029`, `30035`.
- **Sanction** : RE -> `valorisationAcquisSanction` (et éventuellement `pourcentageAttribue`) ; AB -> `motifAbandon`. Erreurs `30019`, `30030` à `30032`.
- **Droits d'inscription** : `indicateurDroitInscription` et `exempte/indicateurExempte…` sont **exclusifs** (`30033` / `30034`). DIS réservé aux nationalités hors CEE selon le manuel (`30023`), contrôle non appliqué en production (voir plus haut).
- **Âge** : l'étudiant doit avoir **au moins 15 ans au début de l'UE** (`30024`).
- **Cycle de vie** : pas de création avec le statut `AN` (`30017`) ; pas de modification d'une inscription `AN` (`30016`) ; l'annulation (passage à `AN`) est refusée par `30070`, que le manuel rattache au « flag 1/10ième » : refus une fois l'UE validée au 1/10.
- **Verrous** : `regulier1` et `regulier5` figés après la validation de l'UE au 1/10 et au 5/10 (`30079`, `30080`).
- **`30051`** « Ok création mais inscrit dans plus de 4 UEs » est un **succès** (label SUCCESS) : l'inscription est créée.
- **Unicité** : une seule inscription par étudiant et par UE (`30200`).

## Comportements observés en production

- **SEPS apprend les organisations EPROM avec un délai.** Le 2026-11-10, un `enregistrerInscription` envoyé **18 minutes** après la déclaration de l'organisation dans EPROM a reçu `success=false` avec **pour seul message le warning `30101`** « The information doesn't match with an existing UE ». Un warning seul est donc un refus (rien n'a été créé). Délai de propagation exact : inconnu.
- **En sens inverse**, des organisations **supprimées d'EPROM vers midi le 2026-09-30** acceptaient encore des inscriptions **l'après-midi même**.
- **Le Doc A n'a pas besoin d'être approuvé.** Des inscriptions ont été acceptées sur des organisations dont le Doc A n'était pas encore approuvé : `audit.dateCreation` du 2026-09-30 côté SEPS pour des organisations approuvées le 2026-10-23 (confirmé par `rechercherInscriptions`, `dateRequete` 2026-09-29 : aucune inscription ; 2026-09-30 : toutes ; spec 12).
- **La suppression d'une organisation purge ses inscriptions SEPS** : elles n'apparaissent plus à aucune `dateRequete` (vérifié le 2026-11-24 ; spec 12).
- **DIS** : indicateur `O` accepté pour des ressortissants de l'UE (2026, voir `DroitInscriptionSpecifiqueType`).

---

## Vérification croisée manuel / contrat

| Élément | Contrat de production | Manuel 2.4 | Statut |
|---|---|---|---|
| `InscriptionInputDataType` (5 champs) | ✓ | ✓ | conforme |
| `InscriptionInputType.anneeScolaire/ue/specificite` | minOccurs=0 | « obligatoire » | requis (30101 / 30100 / 30025) |
| `InscriptionInputType.fse` | boolean [0..1] | défaut true | conforme |
| `SpecificiteDataType.regulier3` | ✓ (enregistrer seulement) | ✓ | absent de `rechercheInscriptions` et de TQ |
| `SanctionType.ajournement1Session` | ✓ (enregistrer seulement) | type seul | sens non documenté |
| `SanctionType.codeSanction` | facultatif | facultatif | conforme (changement depuis 2.1.9) |
| `InscriptionType.audit` | ✓ | absent | contrat seulement (spec 12) |
| `StatutFinFormationType` | `C01`-`C06` | `C01`-`C06` | conforme (2.1.9 écrivait `01`-`06`) |
| `DateType` = string(≤10) | ✓ | « date » | string, pas xs:date |

---

## Mapping pyetnic

Fonctions publiques de `pyetnic.seps` (construction, `docs/PUBLIC_API_SURFACE.md`) :

```python
def enregistrer_inscription(inscription_input_data: InscriptionInputDataSave | None = None) -> InscriptionResult: ...
def modifier_inscription(inscription_input_data: InscriptionInputDataSave | None = None) -> InscriptionResult: ...
```

Types d'envoi (dataclasses, noms des champs = noms XSD) :

| Classe | Champs |
|---|---|
| `InscriptionInputDataSave` | `cfNum`, `idEtab`, `idImplantation`, `codePostalLieuCours`, `inscription` (tous requis) |
| `InscriptionInputSave` | `dateInscription`, `statut` (requis), `anneeScolaire`, `ue`, `specificite`, `fse` |
| `SepsUESave` | `noAdministratif`, `noOrganisation` |
| `SepsSpecificiteSave` | `regulier1`, `regulier3`, `regulier5`, `droitInscription`, `droitInscriptionSpecifique`, `dureeInoccupation`, `situationMenage`, `enfantACharge`, `difficulteHandicap`, `difficulteAutre`, `admission`, `sanction` |
| `SepsDroitInscription` / `SepsDroitInscriptionSpecifique` | indicateur, `montant`, `exempte` |
| `SepsAdmission` | `codeAdmission`, `typeEnseignement`, `titreDelivre`, `equivalence`, `valorisationAcquis` |
| `SepsSanction` | `codeSanction`, `valorisationAcquisSanction`, `motifAbandon`, `statutFinFormation`, `pourcentageAttribue`, `codeSectionFlag`, `codeSection`, `point`, `ajournement1Session` |

- Énumérations (`(str, Enum)`, comparables à leur valeur brute) : `CodeStatut`, `Indicateur`, `IndicateurX`, `MotifExemption`, `MotifExemptionSpec` (avec `C50`), `DureeInoccupation`, `SituationMenage`, `CodeAdmission` (avec `AUCUN`), `TypeEnseignement`, `TitreDelivre`, `Equivalence`, `ValorisationAcquis` (avec `C50`), `CodeSanction`, `ValorisationAcquisSanction`, `MotifAbandon`, `StatutFinFormation`, `CodeNiveau`.
- `regulier3` et `ajournement1Session` n'existent qu'au contrat d'`enregistrerInscription` : les envoyer est valide ; leur effet n'est pas observé.
- pyetnic ne contrôle pas les règles métier (FSE, admission, sanction, exclusivité DI) avant l'envoi : le serveur tranche.
- **Résultat** (toujours un succès) : `InscriptionResult` avec `inscription` (telle que renvoyée), `code` (`201`, `200`, sinon le premier code non bloquant ; `None` quand le serveur n'envoie aucun message, comme dans l'exemple de création du manuel), `messages`, et `plus_de_4_ue` (le serveur a renvoyé `30051`).
- **Refus** : tout `success=false`, que le code arrive en `error` ou en `warning`, lève une sous-classe de `SepsEtnicError` : `SepsUeInconnueError` pour `30100` / `30101` (cas du délai EPROM -> SEPS), `SepsEtudiantInconnuError` pour `30011`, `SepsNotFoundError` pour `30102`, `SepsInscriptionExisteError` pour `30200`, `SepsAucuneModificationError` pour `30443`, `SepsValidationError` pour les autres codes BAD_REQUEST du tableau (`30010`, `30012` à `30035`, `30041`, `30070`, `30079`, `30080`), `SepsAuthError` pour `30550`.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSEnregistrerInscriptionMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `inscription_v1.xsd` | `InscriptionInputDataType`, `InscriptionType`, sous-types et énumérations | version la plus riche : diffère de celle de la spec 12 par `regulier3` et `ajournement1Session` |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
