# SEPS — Enregistrer Inscription (à une UE) v1 (release 2.1.9)

> Spécification technique et fonctionnelle complète
> Sources : WSDL `SEPSEnregistrerInscriptionService_external_v1.wsdl` + `inscription_v1.xsd` + PDF « Services Web SEPS » v2.1.9, §3.1.9-3.1.11 et §3.6
> Date d'analyse : 2026-06-09 (session 7)
> **Préambule famille SEPS, X.509, SOAP Fault, bloc retour** : voir **spec 09**.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Enregistrer Inscription à une Unité d'Enseignement (UE) |
| Version contrat / release | external **v1** / **2.1.9** |
| Sécurité | WS-Security **X.509** · SOAP 1.1 · synchrone |
| WSDL namespace | `http://ws.etnic.be/seps/enregistrerInscription/v1` |
| Messages namespace | `http://ws.etnic.be/seps/enregistrerInscription/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/inscription/v1` |
| Binding | `SEPSEnregistrerInscriptionV1ExternalBinding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/seps/enregistrerInscription/v1` |
| TQ / PROD | PDF §2.2 | `https://services-web(.tq).etnic.be/seps/enregistrerInscription/v1` |

### Contrôle d'accès (manuel §3.6)
- Profil **support** : non limité.
- Profil **établissement** : sauvegarde uniquement dans le périmètre du/des profil(s).
- Profil **PO** : sauvegarde uniquement dans les établissements du PO.

---

## Description fonctionnelle

Gestion de l'**inscription d'un étudiant à une UE**. Deux opérations partageant la **même structure de requête** (`InscriptionInputDataType`) et de réponse (`InscriptionType`) :

1. **enregistrerInscription** — création d'une nouvelle inscription.
2. **modifierInscription** — modification d'une inscription existante.

> L'étudiant est identifié par son **`cfNum`** (obtenu via les services Étudiant, specs 09-10). L'UE est identifiée par `noAdministratif` + `noOrganisation` (= numéro administratif de formation + numéro d'organisation EPROM, cf. Doc 1/2).

---

## Type de requête — `InscriptionInputDataType` (`inscription_v1.xsd`)

L'élément racine de requête est **`inscriptionInputData`** (`minOccurs=0` au XSD, mais requis).

```
InscriptionInputDataType
├── cfNum               : cfNumType          [obligatoire]   identifie l'étudiant
├── idEtab              : xs:integer         [obligatoire]   id FASE établissement
├── idImplantation      : xs:integer         [obligatoire]   id FASE implantation
├── codePostalLieuCours : CodePostalLieuType [obligatoire]   string(≤7) ; erreur 30012 si inconnu
└── inscription         : InscriptionInputType [obligatoire]
```

### InscriptionInputType
```
InscriptionInputType
├── dateInscription : DateType           [obligatoire]   string(≤10), format AAAA-MM-JJ
├── statut          : CodeStatutType     [obligatoire]   DE / AN
├── anneeScolaire   : xs:integer         [0..1 XSD]  ⚠️ « obligatoire » PDF (erreur 30101 si absent) — millésime, ex. 2018
├── ue              : UEInputType        [0..1 XSD]  ⚠️ « obligatoire » PDF (erreur 30100 si absent)
└── specificite     : SpecificiteDataType[0..1 XSD]  ⚠️ « obligatoire » PDF (erreur 30025 si absent)
```
> ⚠️ **Divergence cardinalités** : `anneeScolaire`, `ue`, `specificite` sont `minOccurs=0` au XSD mais **fonctionnellement obligatoires** (codes 30101/30100/30025). Les fournir systématiquement.
> ⚠️ **Type mort** : le XSD définit aussi `SpecificiteDataInputType` (sans `regulier1`/`regulier5`) — **jamais référencé**. L'entrée utilise bien `SpecificiteDataType` (avec `regulier1`/`regulier5`). Ignorer `SpecificiteDataInputType`.

### UEInputType
```
UEInputType
├── noAdministratif : ShortType [obligatoire]   (xs:integer ≤ 32767) — n° administratif UE
└── noOrganisation  : ShortType [obligatoire]   n° d'organisation UE
```

### SpecificiteDataType (entrée ET sortie)
```
SpecificiteDataType   (tous les champs [0..1])
├── regulier1                 : IndicateurType         régulier au 1er/10ᵉ
├── regulier5                 : IndicateurType         régulier au 5ᵉ/10ᵉ
├── droitInscription          : DroitInscriptionType
├── droitInscriptionSpecifique: DroitInscriptionSpecifiqueType
├── dureeInoccupation         : DureeInoccupationType   ⚠️ si UE FSE → obligatoire
├── situationMenage           : SituationMenageType     ⚠️ si UE FSE → obligatoire
├── enfantACharge             : IndicateurType          ⚠️ si UE FSE
├── difficulteHandicap        : IndicateurXType         ⚠️ si UE FSE → obligatoire
├── difficulteAutre           : IndicateurXType         ⚠️ si UE FSE → obligatoire
├── admission                 : AdmissionType           ⚠️ obligatoire (erreur 30025)
└── sanction                  : SanctionType            facultatif
```

**Règles `regulier1`/`regulier5`** (manuel §3.1.9.2) :
- `regulier1` : ne peut plus être modifié si UE **validée au 1/10ᵉ** (erreur `30079`). Défaut `N` (non régulier) si absent ; mais `O` par défaut si l'inscription est enregistrée **après** la validation.
- `regulier5` : ne peut plus être modifié si UE **validée au 5/10ᵉ** (erreur `30080`). Défaut `N`.

---

## Sous-types & énumérations (manuel §3.1.11)

### Indicateurs
- **IndicateurType** : `O` (oui) / `N` (non).
- **IndicateurXType** : `O` / `N` / `X` (« n'accepte pas de préciser »).

### CodeStatutType — statut de l'inscription
| Code | Signification |
|---|---|
| `DE` | Inscription **définitive** |
| `AN` | Inscription **annulée** |

### DroitInscriptionType — droit d'inscription (DI)
```
DroitInscriptionType
├── indicateurDroitInscription : IndicateurType [obligatoire]   O = le DI doit être perçu
└── exempte : ExempteDroitInscriptionType [0..1]
    ├── indicateurExempteDroitInscription : IndicateurType [obligatoire]  ⚠️ exclusif de indicateurDroitInscription (erreur 30033)
    └── motifExemption : MotifExemptionType [obligatoire]   interprété si indicateurExempte = O
```
**MotifExemptionType** (exemption du DI — cf. circulaire 9593, spec 14) :
| Code | Motif |
|---|---|
| `C01` | Mineur soumis à l'obligation scolaire |
| `C02` | Chômeur complet indemnisé |
| `C03` | Étudiant avec handicap reconnu |
| `C04` | Bénéficiaire du revenu d'intégration (RIS) |
| `C05` | Personnel enseignant en formation continuée / recyclage |
| `C06` | Obligation d'une autorité publique |
| `C07` | Autre |

### DroitInscriptionSpecifiqueType — droit d'inscription spécifique (DIS)
Uniquement si étudiant de **nationalité hors CEE** (sinon erreur `30023`).
```
DroitInscriptionSpecifiqueType
├── indicateurDroitInscriptionSpecifique : IndicateurType [obligatoire]
└── exempte : ExempteDroitInscriptionSpecType [0..1]
    ├── indicateurExempteDroitInscriptionSpec : IndicateurType [obligatoire]  (exclusif, erreur 30033/30034)
    └── motifExemptionSpec : MotifExemptionSpecType [obligatoire]
```
**MotifExemptionSpecType** (DIS, hors CEE) :
| Code | Motif | Code | Motif |
|---|---|---|---|
| `C01` | Soumis à l'obligation scolaire | `C08` | Pris en charge par le CPAS |
| `C02` | Ressortissant d'un État membre UE | `C09` | Admis à séjourner > 3 mois (loi 15/12/1980) |
| `C03` | Parents/tuteur belges | `C10` | Demande de régularisation (loi 15/12/1980) |
| `C04` | Parents/tuteur (non belges) résidant en Belgique | `C11` | Placé par le juge de la jeunesse |
| `C05` | Marié/cohabitant avec conjoint résidant en Belgique | `C12` | Sous tutelle officieuse (Code civil) |
| `C06` | Résidant en Belgique avec activité prof. ou revenu de remplacement | `C13` | Visé par l'art. 42bis du décret du 30/06/1998 |
| `C07` | Réfugié ou candidat réfugié reconnu (loi 15/12/1980) | | |

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

### AdmissionType
```
AdmissionType
├── codeAdmission     : CodeAdmissionType   [obligatoire]
├── typeEnseignement  : TypeEnseignementType[0..1]  obligatoire si codeAdmission = TITREBEL
├── titreDelivre      : TitreDelivreType    [0..1]  obligatoire si TITREBEL, dépend de typeEnseignement
├── equivalence       : EquivalenceType     [0..1]  obligatoire si codeAdmission = TITREETR
└── valorisationAcquis: ValorisationAcquisType [0..1] obligatoire si codeAdmission = AUTRE
```
**CodeAdmissionType** : `REUSSITE` (certificat réussite UE) / `TITREBEL` (titre Belgique) / `TITREETR` (titre hors Belgique) / `AUTRE`.

**TypeEnseignementType** : `PRI` (primaire), `SIPE`/`SSPE` (secondaire inf./sup. plein exercice), `SIPS`/`SSPS` (secondaire inf./sup. promotion sociale), `SCPE`/`SLPE` (supérieur court/long plein exercice), `SCPS`/`SLPS` (supérieur court/long promotion sociale).

**TitreDelivreType** (23 valeurs, applicabilité selon `typeEnseignement`) : `CEB`, `CE1D`, `CESI`, `CE2D`, `CQ4`, `CESSG`, `CESST`, `CESSQ`, `CESSP`, `CESSA`, `CE6P`, `CQ6`, `CQ7`, `DAES`, `BES`, `BACH`, `MAST`, `CESS`, `CQINF`, `CQSUP`, `BACHSPE`, `MASTSPE`, `DOC`.

**EquivalenceType** (si TITREETR) : `C01` (équiv. secondaire inférieur), `C02` (équiv. secondaire supérieur), `C03` (équiv. supérieur), `C04` (équiv. CEB).

**ValorisationAcquisType** (si AUTRE) : `C01`-`C04` (admission/dispense V1-V4 formelle), `C10` (VANFI Test/Épreuve), `C20` (VANFI Dossier), `C30` (Autres), `C40` (Aucun titre requis).

### SanctionType
```
SanctionType
├── codeSanction               : CodeSanctionType            [obligatoire]
├── valorisationAcquisSanction : ValorisationAcquisSanctionType [0..1] obligatoire si codeSanction = RE
├── motifAbandon               : MotifAbandonType            [0..1] obligatoire si codeSanction = AB
└── statutFinFormation         : StatutFinFormationType      [0..1] si FSE → obligatoire
```
**CodeSanctionType** : `RE` (Réussite) / `AB` (Abandon) / `EH` (Échec).
**ValorisationAcquisSanctionType** (si RE) : `C00` (Réussite), `C01`-`C04` (valorisation acquis formels V1-V4), `C05` (VANFI Test/Épreuves).
**MotifAbandonType** (si AB) : `TPS` (manque de temps), `PRO` (raisons prof.), `FAM` (raisons familiales), `SAN` (santé), `ATT` (formation ≠ attentes), `MEM` (mise à l'emploi), `FMJ` (force majeure), `NUM` (fracture numérique), `AUT` (autres), `INC` (inconnu).
**StatutFinFormationType** (si FSE) — ⚠️ **XSD = `C01`-`C06`** ; le **texte PDF écrit `01`-`06`** (sans « C ») → **XSD fait foi** :
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
- **DateType** : `string` (maxLength 10) — pas `xs:date` ! Format attendu `AAAA-MM-JJ`.
- **TextType** : `string` (maxLength 250).
- **ShortType** : `xs:integer`, maxInclusive 32767.
- **CodeNiveauType** (sortie UE) : `SI` (sec. inf.) / `SS` (sec. sup.) / `SC` (sup. court) / `SL` (sup. long).

---

## Opérations enregistrerInscription / modifierInscription

### Requête
`enregistrerInscription` / `modifierInscription` → `{Enregistrer|Modifier}InscriptionRequeteType` → `inscriptionInputData : InscriptionInputDataType [0..1]`.

`modifierInscription` (manuel §3.6.2) : champ obligatoire reste obligatoire ; champ facultatif **absent = effacé** après sauvegarde.

### Réponse
`{enregistrer|modifier}InscriptionReponse` → extends `AbstractExternalResponseType` → `response/inscription : InscriptionType [0..1]` (type complet en **sortie**, voir spec 12 §InscriptionType).

### Codes de retour (manuel §3.6.1.3.2 — partagés enregistrer/modifier)

| Success | Code | Description | Règle métier |
|---|---|---|---|
| true | `201` | Ok création | |
| true | `200` | Ok modification | |
| true | `30051` | Ok création mais inscrit dans **plus de 4 UEs** | ⚠️ avertissement |
| false | `30010` | Please enter a valid inscriptionInput | |
| false | `30011` | No student found for this CF | |
| false | `30012` | The postCode is unknown | |
| false | `30013` | Pas le droit d'inscrire dans cet établissement | accès |
| false | `30014` | dateInscription obligatoire | |
| false | `30015` | statut obligatoire | |
| false | `30016` | Modification d'une inscription **annulée** impossible | oui |
| false | `30017` | Création impossible avec statut 'annulé' | oui |
| false | `30018` | Champ obligatoire manquant pour **admission** | oui |
| false | `30019` | Champ obligatoire manquant pour **sanction** | oui |
| false | `30020` | Champ obligatoire manquant | oui |
| false | `30021` | Champ obligatoire manquant pour **FSE** | oui |
| false | `30022` | Champ non autorisé pour **non-FSE** | oui |
| false | `30023` | Droit spécifique non autorisé (étudiant UE non hors-CEE) | oui |
| false | `30024` | L'étudiant doit avoir **≥ 15 ans** au début de l'UE | oui |
| false | `30025` | Critère d'admission valide requis (REUSSITE/TITREBEL/TITREETR/AUTRE) | oui |
| false | `30026` | Aucun champ additionnel valide pour admission REUSSITE | oui |
| false | `30027` | Seuls typeEnseignement + titreDelivre valides pour TITREBEL | oui |
| false | `30028` | Seul equivalence valide pour TITREETR | oui |
| false | `30029` | Seul valorisationAcquis valide pour AUTRE | oui |
| false | `30030` | Code sanction valide requis (RE/EH/AB) | oui |
| false | `30031` | Seul valorisationAcquis valide pour sanction RE | oui |
| false | `30032` | Seul motifAbandon valide pour sanction AB | oui |
| false | `30033`/`30034` | Champs incompatibles : exempté **et** non exempté (rightIndicator=O) | oui |
| false | `30035` | typeEnseignement et titreDelivre incompatibles | oui |
| false | `30041` | Validation cfNum | |
| false | `30070` | Annulation impossible (flag 1/10ᵉ) | oui |
| false | `30079` | `regulier1` non modifiable pour cette UE | oui |
| false | `30080` | `regulier5` non modifiable pour cette UE | oui |
| false | `30100` | Données UE manquantes/incomplètes — aucun résultat | NOT_FOUND |
| false | `30101` | L'information ne correspond pas à une UE existante | NOT_FOUND |
| false | `30102` | Aucune inscription trouvée pour ces critères | NOT_FOUND |
| false | `30200` | Une inscription existe déjà pour cette UE | CONFLICT |
| false | `30443` | Aucune modification à appliquer | |

> ⚠️ **Codes contextuels** : `30100`/`30101` apparaissent en `error` **ou** `warning` selon les cas (cf. exemples). Se fier au code.

### Exemple de requête (enregistrerInscription)
```xml
<v11:enregistrerInscription xmlns:v11="http://ws.etnic.be/seps/enregistrerInscription/messages/v1"
                            xmlns:v12="http://enseignement.cfwb.be/types/seps/inscription/v1">
  <v11:inscriptionInputData>
    <v12:cfNum>8501777-18</v12:cfNum>
    <v12:idEtab>167</v12:idEtab>
    <v12:idImplantation>516</v12:idImplantation>
    <v12:codePostalLieuCours>1000</v12:codePostalLieuCours>
    <v12:inscription>
      <v12:dateInscription>2020-01-03</v12:dateInscription>
      <v12:statut>DE</v12:statut>
      <v12:anneeScolaire>2018</v12:anneeScolaire>
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

## Règles métier transverses (FSE, admission, sanction, DI)

- **UE FSE** (`ue.fse = O` en sortie) : `dureeInoccupation`, `situationMenage`, `difficulteHandicap`, `difficulteAutre` deviennent **obligatoires** ; `enfantACharge` attendu ; `statutFinFormation` obligatoire dans la sanction. Champs FSE **interdits** pour une UE non-FSE (erreur `30022`).
- **Admission** : exactement 1 jeu de champs additionnels selon `codeAdmission` (REUSSITE → aucun ; TITREBEL → typeEnseignement+titreDelivre ; TITREETR → equivalence ; AUTRE → valorisationAcquis). Erreurs `30026`-`30029`, `30035`.
- **Sanction** : RE → valorisationAcquisSanction ; AB → motifAbandon. Erreurs `30031`/`30032`.
- **Droit d'inscription** : `indicateurDroitInscription` et `exempte/indicateurExempte` sont **mutuellement exclusifs** (erreur `30033`). DIS réservé aux **hors-CEE** (erreur `30023`).
- **Âge** : ≥ 15 ans au début de l'UE (erreur `30024`).
- **Cycle de vie** : pas de création avec statut `AN` (`30017`) ; pas de modif d'une inscription `AN` (`30016`) ; annulation soumise au flag 1/10ᵉ (`30070`).
- **Verrous comptage** : `regulier1`/`regulier5` figés après validation au 1/10ᵉ / 5/10ᵉ (`30079`/`30080`) → lien direct avec le **comptage** de la circulaire 9593 (spec 14) et les colonnes du **Document 1** EPROM (spec 03).

---

## Vérification croisée UML / XSD / PDF

| Élément | XSD | PDF | UML (p.11) | Statut |
|---|---|---|---|---|
| `InscriptionInputDataType` (5 champs) | ✓ | ✓ | ✓ | ✅ |
| `InscriptionInputType.anneeScolaire/ue/specificite` | minOccurs=0 | « obligatoire » | — | ⚠️ requis (30101/30100/30025) |
| `SpecificiteDataType` (avec regulier1/5) | ✓ | ✓ | ✓ | ✅ |
| `SpecificiteDataInputType` | défini | non utilisé | — | ⚠️ type mort |
| Enums (statut, motifs, admission, sanction…) | ✓ | ✓ (libellés) | ✓ | ✅ |
| `StatutFinFormationType` | `C01`-`C06` | `01`-`06` | — | ⚠️ XSD fait foi |
| `DateType` = string(≤10) | ✓ | « date » | — | ✅ (string, pas xs:date) |

---

## Mapping pyetnic

```python
class SepsEnregistrerInscriptionService:
    """SEPS Enregistrer/Modifier Inscription v1 (release 2.1.9) — auth X.509."""
    WSDL = "SEPSEnregistrerInscriptionService_external_v1.wsdl"
    ENDPOINT_TQ   = "https://services-web.tq.etnic.be/seps/enregistrerInscription/v1"
    ENDPOINT_PROD = "https://services-web.etnic.be/seps/enregistrerInscription/v1"

    def enregistrer(self, data: InscriptionInput) -> Inscription: ...
    def modifier(self, data: InscriptionInput) -> Inscription: ...
```
```python
@dataclass
class InscriptionInput:
    cf_num: str
    id_etab: int
    id_implantation: int
    code_postal_lieu_cours: str
    date_inscription: str        # "AAAA-MM-JJ" (string, pas date — DateType maxLen 10)
    statut: str                  # DE / AN
    annee_scolaire: int          # millésime (obligatoire en pratique)
    ue: UEInput                  # noAdministratif + noOrganisation (obligatoire en pratique)
    specificite: Specificite     # (obligatoire en pratique)

# Énumérations à modéliser en Enum/Literal : CodeStatut, MotifExemption, MotifExemptionSpec,
# DureeInoccupation, SituationMenage, CodeAdmission, TypeEnseignement, TitreDelivre, Equivalence,
# ValorisationAcquis, CodeSanction, ValorisationAcquisSanction, MotifAbandon, StatutFinFormation, CodeNiveau.
```
- Centraliser ces énumérations (référentiel partagé spec 12) et **valider côté client** les règles conditionnelles (FSE, admission, sanction, DI/DIS exclusifs) pour éviter les A/R serveur (30018-30035).
- Exceptions par **(service, code)**.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSEnregistrerInscriptionMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `inscription_v1.xsd` | `InscriptionInputDataType`, `InscriptionType`, sous-types & enums | = spec 12 (md5 identique) |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
