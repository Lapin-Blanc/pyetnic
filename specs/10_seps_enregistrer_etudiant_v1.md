# SEPS — Enregistrer (Sauvegarde) Étudiant v1 (release 2.1.9)

> Spécification technique et fonctionnelle complète
> Sources : WSDL `SEPSEnregistrerEtudiantService_external_v1.wsdl` + XSD + PDF « Services Web SEPS » v2.1.9 (18/01/2023), §3.5
> Date d'analyse : 2026-06-09 (session 7)
> **Préambule famille SEPS, sécurité X.509, SOAP Fault, bloc retour, types signalétique** : voir **spec 09** (§ préambule + § « Types communs SEPS ») — non répété ici. Types `EtudiantType` / `EtudiantDetailsType` **identiques** (XSD `etudiant_v1.xsd` / `etudiantDetails_v1.xsd` byte-for-byte).

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Enregistrer / Sauvegarde Étudiant |
| Version contrat / release | external **v1** / **2.1.9** |
| Sécurité | WS-Security **X.509** · SOAP 1.1 · synchrone |
| WSDL namespace | `http://ws.etnic.be/seps/enregistrerEtudiant/v1` |
| Messages namespace | `http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1` |
| Binding | `SEPSEnregistrerEtudiantV1ExternalBinding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/seps/enregistrerEtudiant/v1` |
| TQ | PDF §2.2 | `https://services-web.tq.etnic.be/seps/enregistrerEtudiant/v1` |
| PROD | PDF §2.2 | `https://services-web.etnic.be/seps/enregistrerEtudiant/v1` |

> ⚠️ `requestId` en sortie : `wsdl:required="false"` pour ce service (contrairement aux services de recherche).

---

## Description fonctionnelle

Sauvegarde des étudiants dans la **DB SEPS**. Deux opérations :

1. **enregistrerEtudiant** — création d'un nouvel étudiant (2 modes : **NISS** ou **DETAILS**).
2. **modifierEtudiant** — modification de la **version établissement** (`cfwbDetails`) d'un étudiant existant.

> À la création réussie, **une version RN et une version « établissement »** (champs recopiés de la version RN, ou créés à partir du détail fourni) sont enregistrées avec un **nouveau `cfNum`**.

---

## Opération 1 : enregistrerEtudiant

### Requête — `enregistrerEtudiant` (type `EnregistrerEtudiantRequeteType`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `modeEnregistrement` | ModeEnregistrement | **obligatoire** | Énumération **`NISS`** / **`DETAILS`** |
| `doubleFlag` | boolean | 0..1 | Flag doublon. **Défaut `false`** |
| `createBisFlag` | boolean | 0..1 | Flag création d'un BIS. **Défaut `true`** — *uniquement* en mode DETAILS (depuis v2.0) |
| `etudiantDetails` | EtudiantDetailsType | 0..1 | Signalétique (voir spec 09) |

> ⚠️ Le XSD nomme les flags `doubleFlag` / `createBisFlag` (et non `doublonFlag`). `modeEnregistrement` est **obligatoire** au XSD ; `etudiantDetails` est `minOccurs=0` au XSD mais **requis en pratique** (erreur `30042` « pas de EtudiantDetail fourni » si absent).

**Champs obligatoires de `etudiantDetails` si `niss` non spécifié** (mode DETAILS) :
- `nom` et `sexe` ;
- `naissance.date` et `naissance.codePays` ; **+** `naissance.localite.code` si pays = Belgique, **sinon** `naissance.localite.description` ;
- `adresse` : `rue`, `codePostal`, `codePays` (+ `localite.description` si pays ≠ Belgique) ;
- `codeNationalite`.

### Mode NISS (manuel §3.5.1.1.1)
Entrée = NISS (+ `doubleFlag`). Recherche DB SEPS → si trouvé : erreur **`30201`** (exist : N°CF). Sinon **appel ALIM** (BCSS) par NISS :
- rien trouvé → **`30120`** Not Found ;
- 1 trouvé → création (version RN + version établissement recopiée), retour **`200/201`** ;
- **mutation de NISS** détectée → **`30401`** / 406 Not Acceptable ;
- selon `doubleFlag` : si `false` et doublon(s) détecté(s) (même nom/prénom/sexe/DN) → `30203` (liste des CF) ; si `true`, force la création/fusion.

### Mode DETAILS (manuel §3.5.1.1.2)
Entrée = détail étudiant. Recherche sur nom_rech/DN/sexe en DB SEPS, puis BCED :
- plusieurs en DB SEPS → **`409`/`30203`** (liste des CF) ;
- 1 trouvé → selon `doubleFlag` (tracer le doublon si `true`) ; appel ALIM avec le NISS trouvé ;
- aucun en BCED **et** `createBisFlag=true` → appel **PUBLISHPERSON** (création d'un **BIS** = NISS bis) puis ALIM avec le nouveau NISS ; sinon création d'une version établissement **sans** version RN.
- Résultats : **`201`** (CREATED) + ressource étudiant.

### Réponse — `enregistrerEtudiantReponse` (type `EnregistrerEtudiantReponseType`)
```
response
└── etudiant : EtudiantType   [0..1]
```

### Codes de retour (manuel §3.5.1.3.2)

| Success | Code | Label | Description |
|---|---|---|---|
| true | `201` | CREATED | DETAILS : étudiant créé |
| true | `200` | SUCCESS | NISS : OK |
| false | `30039` | BAD_REQUEST | `modeEnregistrement` requis |
| false | `30040` | BAD_REQUEST | Validation SSIN |
| false | `30041` | BAD_REQUEST | Validation cfNum |
| false | `30042` | BAD_REQUEST | **Données manquantes : pas de EtudiantDetail fourni** *(≠ sens spec 09)* |
| false | `30060`-`30078` | BAD_REQUEST | Validations détaillées (lastName, firstName, otherFirstName, genderCode, birth, birthDate, birthCountry, localité, deceasedDate, addressStreet, addressBox, addressStreetAdditional, addressPostal, code localité, addressCityAdditional, addressCountry) |
| false | `30067` | BAD_REQUEST | Localité de naissance/adresse `null` |
| false | `30076` | BAD_REQUEST | Code localité invalide/absent (Belgique) ou description vide (hors Belgique) |
| false | `30120` | NOT_FOUND | À la fin si pas trouvé |
| false | `30201` | CONFLICT | SSIN trouvé en DB (étudiant existe déjà) |
| false | `30202` | CONFLICT | SSIN Phonex : plus d'un trouvé |
| false | `30203` | CONFLICT | DETAILS Phonex trouvé, `doubleFlag=false` |
| false | `30204` | CONFLICT | DETAILS Rech BCED : plus d'un trouvé |
| false | `30401` | NOT_ACCEPTABLE | Mutation de NISS détectée |
| false | `30402` | NOT_ACCEPTABLE | Étudiant non enregistrable (RGPD) |
| false | `30443` | BAD_REQUEST | Aucune modification à appliquer |
| false | `30502`/`30503`/`30504` | INTERNAL_SERVER_ERROR | Erreur BCED / trop de résultats / sauvegarde |
| false | `30550`/`50505`-`50509` | INTERNAL_SERVER_ERROR | Authentification / erreurs internes Phonex/BCED/bis |

### Exemples de requête
```xml
<!-- Mode NISS -->
<v11:enregistrerEtudiant xmlns:v11="http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1"
                         xmlns:v12="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1">
  <v11:modeEnregistrement>NISS</v11:modeEnregistrement>
  <v11:doubleFlag>false</v11:doubleFlag>
  <v11:etudiantDetails><v12:niss>99082705172</v12:niss></v11:etudiantDetails>
</v11:enregistrerEtudiant>
```
```xml
<!-- Mode DETAILS (version établissement) -->
<v11:enregistrerEtudiant xmlns:v11="http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1"
                         xmlns:v12="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1">
  <v11:modeEnregistrement>DETAILS</v11:modeEnregistrement>
  <v11:doubleFlag>false</v11:doubleFlag>
  <v11:etudiantDetails>
    <v12:nom>Nom</v12:nom><v12:prenom>Prénom</v12:prenom><v12:sexe>F</v12:sexe>
    <v12:naissance>
      <v12:date>1988-01-01</v12:date><v12:codePays>00150</v12:codePays>
      <v12:localite><v12:code>62063</v12:code><v12:description>Liège</v12:description></v12:localite>
    </v12:naissance>
    <v12:adresse>
      <v12:rue>Rue xxx</v12:rue><v12:numero>12</v12:numero><v12:codePostal>1400</v12:codePostal>
      <v12:localite><v12:code>62063</v12:code><v12:description>Liège</v12:description></v12:localite>
      <v12:codePays>00150</v12:codePays>
    </v12:adresse>
    <v12:codeNationalite>00150</v12:codeNationalite>
  </v11:etudiantDetails>
</v11:enregistrerEtudiant>
```
> ⚠️ **Incohérence d'exemples du manuel** : un exemple de requête DETAILS envoie `codeNationalite>BE` (ISO2) alors que toutes les réponses renvoient `00150` (INS). Le format attendu est le **code INS 5 chiffres** (cf. spec 15). Envoyer `00150`, pas `BE`.

---

## Opération 2 : modifierEtudiant

### Description
Modifie la **version établissement** (`cfwbDetails`). Règles :
- un champ **obligatoire en création reste obligatoire en modification** (doit être présent même inchangé) ;
- un champ **facultatif absent** est interprété comme une **suppression** : sa valeur antérieure est **effacée** après sauvegarde.

Workflow : recherche DB SEPS par `cfNum` → si absent **404 Not Found** ; si trouvé, **`200`** + ressource modifiée (+ version RN si retrouvée).

### Requête — `modifierEtudiant` (type `ModifierEtudiantRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `cfNum` | cfNumType | **oui** | Identification de l'étudiant |
| `etudiantDetails` | EtudiantDetailsType | 0..1 | Détail (voir spec 09) |

> Si `niss` non spécifié : `nom`, `sexe`, `naissance.date`, `naissance.codePays` obligatoires.

### Réponse — `modifierEtudiantReponse` (type `ModifierEtudiantReponseType`)
```
response
└── etudiantDetails : EtudiantType   [obligatoire]
```
> ⚠️ **Nom de l'élément réponse** : `enregistrerEtudiant` renvoie `response/etudiant`, mais `modifierEtudiant` renvoie **`response/etudiantDetails`** (type `EtudiantType` dans les deux cas). Asymétrie confirmée par le XSD.

### Codes de retour
Identiques à `enregistrerEtudiant` (manuel §3.5.2.3.2 → renvoi vers §3.5.1.3.2). Cas notables :
- **`200`** « The student changes have been applied. »
- **`30443`** « No changes detected. » (renvoyé en `info`/`error` selon les cas).

> ⚠️ **Incohérences d'exemples du manuel** : les exemples §3.5.2.4 affichent `success=false` **avec** un `info` code `200` (« changes applied ») et `30443` tantôt en `info` tantôt en `error`. Côté pyetnic : se fier au **code** (`200` = succès, `30443` = pas de changement), pas seulement au flag `success`.

### Exemple de requête
```xml
<v11:modifierEtudiant xmlns:v11="http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1"
                      xmlns:v12="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1">
  <v11:cfNum>8502630-95</v11:cfNum>
  <v11:etudiantDetails>
    <v12:niss>…</v12:niss><v12:nom>NOM</v12:nom><v12:autrePrenom>Prénom</v12:autrePrenom><v12:sexe>F</v12:sexe>
    <v12:naissance>
      <v12:date>2000-01-01</v12:date><v12:codePays>00129</v12:codePays>
      <v12:localite><v12:code>62063</v12:code><v12:description>Liège</v12:description></v12:localite>
    </v12:naissance>
    <v12:adresse>
      <v12:rue>Hellingstraat</v12:rue><v12:numero>xx</v12:numero><v12:codePostal>3620</v12:codePostal>
      <v12:localite><v12:code>73042</v12:code><v12:description>LANAKEN</v12:description></v12:localite>
      <v12:codePays>00150</v12:codePays>
    </v12:adresse>
    <v12:codeNationalite>00150</v12:codeNationalite>
  </v11:etudiantDetails>
</v11:modifierEtudiant>
```

---

## Règles métier clés

- **Deux versions** maintenues : `rnDetails` (autoritaire, RN/BCSS) et `cfwbDetails` (modifiable par l'établissement). `modifierEtudiant` n'agit **que** sur `cfwbDetails`.
- **NISS bis** : si aucune correspondance RN, possibilité de créer un **NISS bis** (numéro de registre BIS) via `createBisFlag=true` (DETAILS) → PUBLISHPERSON. Lien direct avec la circulaire 9593 (registre matricule, identification — spec 14).
- **Doublons** : la déduplication se base sur nom + prénom + sexe + date de naissance. `doubleFlag` arbitre (création forcée vs blocage `30203`).
- **RGPD** : `30402` — certains étudiants ne peuvent être enregistrés (droit à l'oubli / restrictions).
- **codeNationalite / codePays / localite** : codes **INS** (cf. spec 15). Localité belge → `code` obligatoire ; localité étrangère → `description`.

---

## Vérification croisée UML / XSD / PDF

| Élément | XSD | PDF | Statut |
|---|---|---|---|
| `EnregistrerEtudiantRequeteType` (modeEnregistrement, doubleFlag, createBisFlag, etudiantDetails) | ✓ | ✓ | ✅ |
| `ModeEnregistrement` = NISS/DETAILS | ✓ | ✓ | ✅ |
| `etudiantDetails` minOccurs=0 | ✓ | « obligatoire en pratique » (30042) | ⚠️ requis fonctionnellement |
| réponse `enregistrer`=`etudiant` / `modifier`=`etudiantDetails` | ✓ | ✓ (exemples) | ✅ asymétrie réelle |
| `success=false` + info 200 (modifier) | — | exemple | ⚠️ coquille manuel |
| `codeNationalite` = INS 5 chiffres | string libre | « BE » dans 1 exemple | ⚠️ utiliser INS |

---

## Mapping pyetnic

```python
class SepsEnregistrerEtudiantService:
    """SEPS Sauvegarde Étudiant v1 (release 2.1.9) — auth X.509."""
    WSDL = "SEPSEnregistrerEtudiantService_external_v1.wsdl"
    ENDPOINT_TQ   = "https://services-web.tq.etnic.be/seps/enregistrerEtudiant/v1"
    ENDPOINT_PROD = "https://services-web.etnic.be/seps/enregistrerEtudiant/v1"

    def enregistrer_par_niss(self, niss: str, *, double_flag: bool = False) -> Etudiant: ...
    def enregistrer_par_details(self, details: EtudiantDetails, *,
                                double_flag: bool = False, create_bis_flag: bool = True) -> Etudiant: ...
    def modifier(self, cf_num: str, details: EtudiantDetails) -> Etudiant: ...
```
- Réutilise les dataclasses `Etudiant` / `EtudiantDetails` / `Naissance` / `Adresse` de la **spec 09**.
- Exceptions par **(service, code)** : `30042` ≠ sens de la spec 09 ; gérer `30201` (existe déjà → exposer le cfNum), `30203`/`30204` (doublons → exposer la liste de CF), `30401` (mutation NISS), `30402` (RGPD).
- `modeEnregistrement` déduit de l'API (par_niss → `NISS`, par_details → `DETAILS`).

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSEnregistrerEtudiantMessages_external_v1.xsd` | Éléments d'opération + `ModeEnregistrement` | spécifique |
| `etudiant_v1.xsd` / `etudiantDetails_v1.xsd` | Signalétique | = spec 09 (md5 identique) |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
