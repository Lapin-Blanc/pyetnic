# SEPS - Enregistrer (Sauvegarde) Étudiant v1

> Spécification technique et fonctionnelle complète
> Sources :
> - **Manuel** : « Services Web SEPS - Enregistrer étudiant » **2.3** (version de service 2.3.0, rev 10.0, 10/06/2026, `ETNIC_Services_Web_SIEL_SEPS_EnregistrerEtudiants_v2.3_Manuel_d_utilisation_rev10.0.pdf`), §2 et §3.3. Remplace le manuel général 2.1.9 (18/01/2023, §3.5) comme référence.
> - **Contrat** : WSDL + XSD servis par la production (`https://ws.etnic.be/seps/enregistrerEtudiant/v1?wsdl`), embarqués dans `pyetnic/resources/SEPS_Enregistrer_Etudiant_2.1/` (relevé du 2026-11-24).
> - **Observations de production** (datées dans le texte).
>
> Première analyse : 2026-06-09 (session 7). Refonte : 2026-11-24 (#24).
> **Préambule famille SEPS** (sécurité X.509, endpoints, SOAP Fault, bloc retour) et **types de la signalétique** : voir **spec 09**. `etudiant_v1.xsd` et `etudiantDetails_v1.xsd` sont identiques octet pour octet dans les deux dossiers.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Enregistrer / Sauvegarde Étudiant |
| Version contrat / manuel | external **v1** / manuel **2.3** (service 2.3.0) |
| Sécurité | WS-Security X.509 · SOAP 1.1 · synchrone · TLS 1.2 et 1.3 (manuel 2.3, §2.1) |
| WSDL namespace | `http://ws.etnic.be/seps/enregistrerEtudiant/v1` |
| Messages namespace | `http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1` |
| Binding | `SEPSEnregistrerEtudiantV1ExternalBinding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | manuel 2.3, §2.2 | `https://ws-tq.etnic.be/seps/enregistrerEtudiant/v1` |
| PROD | manuel 2.3, §2.2 | `https://ws.etnic.be/seps/enregistrerEtudiant/v1` |
| PROD | contrat de production (`soap:address`) | `https://ws.etnic.be:443/seps/enregistrerEtudiant/v1` |

> `requestId` en sortie : `wsdl:required="false"` pour ce service (contrairement aux services de recherche).
> SEPS ne s'exerce pas sur TQ avec le certificat de production (spec 09, préambule) : tout ce qui suit vient des manuels ou de la production.

---

## Description fonctionnelle

Sauvegarde des étudiants dans la **DB SEPS** (manuel 2.3, §3.3). Deux opérations :

1. **enregistrerEtudiant** : création d'un nouvel étudiant, en mode **NISS** ou **DETAILS**.
2. **modifierEtudiant** : modification de la **version établissement** (`cfwbDetails`) d'un étudiant existant.

Workflow d'inscription (manuel 2.3, §3.2.1) : un étudiant n'est inscrit à une UE qu'avec son `cfNum`. Sans `cfNum`, chercher par NISS (spec 09) ; s'il est en SEPS, l'inscrire ; s'il n'est qu'à la BCED, l'enregistrer par NISS ; sinon chercher par nom ; s'il n'est nulle part, l'enregistrer par nom (mode DETAILS).

---

## Opération 1 : enregistrerEtudiant

### Requête - `enregistrerEtudiant` (type `EnregistrerEtudiantRequeteType`, manuel 2.3 §3.3.1.2.1)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `modeEnregistrement` | ModeEnregistrement | **obligatoire** | Énumération **`NISS`** / **`DETAILS`** |
| `doubleFlag` | boolean | 0..1 | Flag doublon. **Défaut `false`** |
| `createBisFlag` | boolean | 0..1 | Flag création d'un BIS. **Défaut `true`**, « uniquement pour la création de type DETAILS » (depuis 2.0) |
| `etudiantDetails` | EtudiantDetailsType | 0..1 | Signalétique (spec 09) |

> `etudiantDetails` est `minOccurs=0` au contrat mais requis en pratique (`30042` « Données manquantes : pas de EtudiantDetail fourni »).

**Champs obligatoires de `etudiantDetails` si le NISS n'est pas fourni** (manuel 2.3, §3.3.1.2.1) :
- `nom` et `sexe` (« le genre ») ;
- `naissance.date` et `naissance.codePays`, plus `naissance.localite.code` si le pays est la Belgique, **sinon** `naissance.localite.description` ;
- `adresse` : `rue`, `codePostal`, `codePays` (et `localite.description` si le pays n'est pas la Belgique) ;
- `codeNationalite`.

> Le contrat de production a rendu `adresse.rue` et `adresse.codePays` facultatifs (spec 09). La règle ci-dessus reste celle du manuel : un enregistrement DETAILS sans eux passe la validation XSD et sera tranché par le serveur (`30071`, `30078` probables, non observés).

### Mode NISS (manuel 2.3, §3.3.1.1.1, diagramme p. 11)

Ce que dit le **diagramme** :
1. Recherche du NISS en DB SEPS. **Trouvé** -> erreur **`30201`** « exist : N°CF ».
2. **Aucun** -> **appel ALIM** (BCSS) avec le NISS, avec inscription aux mutations (désinscription ultérieure s'il n'y a pas d'inscription à une UE). **Aucun** -> **`30120`** Not Found.
3. **Un trouvé** -> test du **flag doublon** :
   - **[False]** -> création directe, **sans** vérification de doublon : **`201`** et la nouvelle ressource (version RN + version établissement recopiée) ;
   - **[True]** -> **vérification de doublon** : aucun -> **`201`** ; **un** doublon -> **fusion** -> **`200`** et la ressource modifiée avec la version RN retrouvée ; **plusieurs** -> **`30203`** avec la liste des CF.
4. Note du diagramme : en cas de mutation de NISS, « retourner 406 Not acceptable - Description = Mutation NISS : le nouveau NISS » (code **`30401`**).

Ce que dit le **texte** juste après (p. 12) : `doubleFlag` « permet de **forcer la création d'un doublon** » s'il vaut `true` ; s'il vaut `false` (défaut), une vérification cherche un étudiant de même nom, prénom, sexe et date de naissance : aucun -> sauvegarde ; un -> la version RN est liée à la version établissement préexistante (fusion) ; plusieurs -> `30203` avec la liste des CF.

> **Contradiction non résolue.** Le diagramme et le texte donnent au flag des sens **opposés** : selon le diagramme, `true` déclenche la vérification et la fusion ; selon le texte, `false` les déclenche et `true` force un doublon. La version précédente de cette spec retenait la lecture du texte comme un fait : rien ne permet de trancher.
>
> **Pratique sûre** : avant tout enregistrement par NISS, **chercher par nom** (`rechercherEtudiants` avec nom, date de naissance et sexe, spec 09). Si cette recherche ne trouve aucune fiche SEPS, aucun doublon n'existe et les deux valeurs du flag donnent `201` selon les deux lectures. S'il en existe une, inscrire cet étudiant par son `cfNum` plutôt que d'en créer un second.

**Codes en mode NISS : diagramme contre tableau.**
- Le tableau des codes (§3.3.1.3.2) dit `200` « SSIN OK » et `201` « DETAILS CREATED », comme si `200` était le succès du mode NISS et `201` celui du mode DETAILS. Le diagramme NISS dit `201` pour une création et `200` pour une fusion.
- **Observé en production (2026-11-24, un cas)** : mode NISS, `doubleFlag=false`, personne inconnue de SEPS -> `success=true`, `info 201` « L'étudiant est sauvé » et un second `info` portant la version du service (`2.4.6`, « version »). L'observation suit le **diagramme** (`201` = création, nouveau `cfNum`).
- Plusieurs doublons en mode NISS : le diagramme dit **`30203`**, le tableau associe ce cas à **`30202`** « SSIN Rech Phonex Plus d'un trouvé ». Non observé.

**Forme de la liste des CF** : l'exemple `30203` du manuel 2.3 (p. 12) porte la liste dans la description : « The student you are trying to register already exists ([1234567-89;2345678-9;3456789-1]) » (numéros remplacés par des fictifs, forme conservée). Deux des trois numéros de l'exemple n'ont **qu'un chiffre de contrôle**, contrairement au pattern `cfNumType` : un analyseur de cette description doit accepter un ou deux chiffres.

### Mode DETAILS (manuel 2.3, §3.3.1.1.2, diagrammes p. 12-13)

Ici le diagramme, le texte et le tableau concordent :
1. Recherche par nom (nom de recherche / date de naissance / sexe) en DB SEPS.
   - **Plusieurs** -> **409** avec la liste des CF (**`30203`**).
   - **Un** et `doubleFlag=false` -> **409** avec le CF trouvé (**`30203`**, « DETAILS Rech phonex trouvé doubleFlag false ») ;
   - **Un** et `doubleFlag=true` -> le doublon est **tracé**, **`201`** et un nouvel étudiant « doublon » **sans version RN/BCSS**.
2. **Aucun** en DB SEPS -> recherche par nom à la **BCED** :
   - **Plusieurs** -> **409** avec la liste des NISS retrouvés (**`30204`** « DETAILS Rech BCED plus d'1 trouvé ») ;
   - **Un** -> appel ALIM avec le NISS trouvé -> **`201`** (version RN/BCSS + version établissement recopiée) ;
   - **Aucun** et `createBisFlag=true` (défaut depuis 2.0) -> appel BCED **PUBLISHPERSON** (création d'un **NISS bis**), puis ALIM avec ce nouveau NISS -> **`201`** (version Bis + version établissement recopiée) ; la réponse porte `bisCreated=O` (exemple §3.3.1.4.1) ;
   - **Aucun** et `createBisFlag=false` -> **`201`** et une version établissement **sans** version RN (comportement d'avant 2.0).

### Réponse - `enregistrerEtudiantReponse` (type `EnregistrerEtudiantReponseType`)
```
response [0..1]
└── etudiant : EtudiantType   [0..1]   (cfNum, bisCreated, rnDetails, cfwbDetails ; spec 09)
```

### Codes de retour (manuel 2.3, §3.3.1.3.2, p. 16-17)

| Code | Description (manuel) | Error label |
|---|---|---|
| `201` | DETAILS CREATED | CREATED |
| `200` | SSIN OK | SUCCESS |
| `30550` | Authentification | INTERNAL_SERVER_ERROR |
| `30039` | The registration mode is required | BAD_REQUEST |
| `30040` | Validation SSIN | BAD_REQUEST |
| `30041` | Validation cfNum | BAD_REQUEST |
| `30042` | Données manquantes : pas de EtudiantDetail fourni | BAD_REQUEST |
| `30503` | SSIN si trop de résultats | INTERNAL_SERVER_ERROR |
| `30201` | SSIN si trouvé en db | CONFLICT |
| `50505` | SSIN Rech Phonex Erreur en sauvegarde | INTERNAL_SERVER_ERROR |
| `30202` | SSIN Rech Phonex Plus d'un trouvé | CONFLICT |
| `30120` | A la fin si pas trouvé | NOT_FOUND |
| `30203` | DETAILS Rech phonex trouvé doubleFlag false | CONFLICT |
| `30502` | Si erreur de l'appel BCED | INTERNAL_SERVER_ERROR |
| `50508` | DETAILS Rech phonex trouvé doubleFlag true (si prob array) | INTERNAL_SERVER_ERROR |
| `50509` | An error has occured during the bis creation + erreur du service bced | INTERNAL_SERVER_ERROR |
| `50507` | DETAILS Rech phonex trouvé erreur sauvegarde | INTERNAL_SERVER_ERROR |
| `30204` | DETAILS Rech BCED plus d'1 Trouvé | CONFLICT |
| `50506` | DETAILS Rech BCED 1 Trouvé (si prob array) ; listé deux fois, la seconde pour « erreur sauvegarde » | INTERNAL_SERVER_ERROR |
| `30060` | Validation lastName | BAD_REQUEST |
| `30061` | Validation firstName | BAD_REQUEST |
| `30062` | Validation otherFirstName | BAD_REQUEST |
| `30063` | Validation genderCode | BAD_REQUEST |
| `30064` | Validation Birth | BAD_REQUEST |
| `30065` | validation birthDate | BAD_REQUEST |
| `30066` | validation birthCountry | BAD_REQUEST |
| `30067` | validation localité : localité de naissance ou de l'adresse `null` | BAD_REQUEST |
| `30068` | validation deceasedDate | BAD_REQUEST |
| `30071` | validation addressStreet | BAD_REQUEST |
| `30073` | validation addressBox | BAD_REQUEST |
| `30074` | validation addressStreetAdditional | BAD_REQUEST |
| `30075` | validation addressPostal | BAD_REQUEST |
| `30076` | Code de localité invalide ou absent pour une localité belge, ou description vide pour une localité hors Belgique | BAD_REQUEST |
| `30077` | validation addressCityAdditional | BAD_REQUEST |
| `30078` | validation addressCountry | BAD_REQUEST |
| `30443` | Aucune modification à appliquer | BAD_REQUEST |
| `30503` | Erreur si trop de résultats (listé une seconde fois) | INTERNAL_SERVER_ERROR |
| `30504` | Erreur à la sauvegarde | INTERNAL_SERVER_ERROR |
| `30401` | Mutation de Niss détectée | NOT_ACCEPTABLE |

> **Écart avec le manuel 2.1.9** : le code **`30402`** (« The student cannot be registered as per GDPRD », étudiant non enregistrable au titre du RGPD) a **disparu** du tableau 2.3. L'historique du manuel porte « Modification de l'intitulé du code 30402 et suppression du code 30403 » (service 2.0.10) sans dire pourquoi 30402 n'est plus listé. Le reste du tableau est identique à 2.1.9.

### Exemples de requête
```xml
<!-- Mode NISS (valeur masquée) -->
<v11:enregistrerEtudiant xmlns:v11="http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1"
                         xmlns:v12="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1">
  <v11:modeEnregistrement>NISS</v11:modeEnregistrement>
  <v11:doubleFlag>false</v11:doubleFlag>
  <v11:etudiantDetails><v12:niss>xxxxxxxxxxx</v12:niss></v11:etudiantDetails>
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
> **Exemple du manuel toujours incohérent** : l'exemple DETAILS du manuel 2.3 (§3.3.1.2.2.2) envoie encore `<codeNationalite>BE</codeNationalite>` (ISO2), alors que toutes les réponses portent le code INS `00150` et que l'historique annonce « Correction exemple BE : 00150 ». Le format attendu est le **code INS à 5 chiffres** (spec 15) : envoyer `00150`, pas `BE`.

### Exemple de réponse réussie (d'après le manuel 2.3, §3.3.1.4.1, identifiants fictifs)
```xml
<ns3:enregistrerEtudiantReponse
    xmlns:ns3="http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1"
    xmlns:ns4="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1"
    xmlns:ns5="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns6="http://enseignement.cfwb.be/types/seps/etudiant/v1">
  <ns5:success>true</ns5:success>
  <ns5:messages><ns5:info><ns5:code>201</ns5:code><ns5:description>The student is registered.</ns5:description></ns5:info></ns5:messages>
  <ns3:response>
    <ns3:etudiant>
      <ns6:cfNum>1234567-89</ns6:cfNum>
      <ns6:bisCreated>O</ns6:bisCreated>
      <ns6:rnDetails><!-- signalétique RN (ou Bis) --></ns6:rnDetails>
      <ns6:cfwbDetails><!-- version établissement recopiée --></ns6:cfwbDetails>
    </ns3:etudiant>
  </ns3:response>
</ns3:enregistrerEtudiantReponse>
```
> Le texte de l'`info 201` diffère entre le manuel (« The student is registered. ») et la production (« L'étudiant est sauvé », 2026-11-24) : se fier au code.

---

## Opération 2 : modifierEtudiant

### Description (manuel 2.3, §3.3.2.1)
Modifie la **version établissement** (`cfwbDetails`). Règles :
- un champ **obligatoire en création reste obligatoire en modification** : il doit être présent même inchangé ;
- un champ **facultatif absent** vaut **suppression** : sa valeur antérieure est **effacée** après la sauvegarde. Il faut donc renvoyer la fiche complète, telle que lue, avec les changements.

Workflow : recherche DB SEPS par `cfNum` ; absent -> **404 Not Found** (le code client correspondant n'est pas donné) ; trouvé -> **`200`** et la ressource modifiée, avec la version RN si elle existe.

### Requête - `modifierEtudiant` (type `ModifierEtudiantRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `cfNum` | cfNumType | **oui** | Identification de l'étudiant |
| `etudiantDetails` | EtudiantDetailsType | 0..1 | Détail (spec 09) |

> Manuel 2.3, §3.3.2.2.1 : si le NISS n'est pas fourni, `nom`, `sexe`, `naissance.date` et `naissance.codePays` sont obligatoires.

### Réponse - `modifierEtudiantReponse` (type `ModifierEtudiantReponseType`)
```
response
└── etudiantDetails : EtudiantType   [obligatoire]
```
> **Nom de l'élément réponse** : `enregistrerEtudiant` renvoie `response/etudiant`, mais `modifierEtudiant` renvoie **`response/etudiantDetails`** (type `EtudiantType` dans les deux cas). Asymétrie du contrat.

### Codes de retour
Ceux d'`enregistrerEtudiant` (manuel 2.3, §3.3.2.3.2 renvoie au §3.3.1.3.2). Cas notables :
- **`200`** « The student changes have been applied. »
- **`30443`** « No changes detected. »

> **Exemples du manuel** (§3.3.2.4) : le succès est montré avec `success=false` **et** un `info 200` ; le cas « aucun changement » avec `success=false` et un `info 30443`. Se fier au **code**, pas au seul flag `success`.

---

## Règles métier clés

- **Deux versions** : `rnDetails` (RN/BCSS) et `cfwbDetails` (modifiable par l'établissement). `modifierEtudiant` n'agit **que** sur `cfwbDetails`.
- **NISS bis** : sans correspondance au RN, le mode DETAILS crée un **NISS bis** (`createBisFlag=true`, défaut) via PUBLISHPERSON ; la réponse le signale par `bisCreated=O`.
- **Doublons** : la déduplication porte sur nom, prénom, sexe et date de naissance. En mode DETAILS, `doubleFlag=true` crée un doublon tracé sans version RN. En mode NISS, le sens du flag est contradictoire dans le manuel (voir plus haut).
- **Mutation de NISS** : `30401`, le nouveau NISS dans la description.
- **codeNationalite / codePays / localite** : codes **INS** (spec 15). Localité belge -> `code` obligatoire ; localité étrangère -> `description`.

---

## Vérification croisée manuel / contrat

| Élément | Contrat de production | Manuel 2.3 | Statut |
|---|---|---|---|
| `EnregistrerEtudiantRequeteType` (modeEnregistrement, doubleFlag, createBisFlag, etudiantDetails) | ✓ | ✓ | conforme |
| `ModeEnregistrement` = NISS / DETAILS | ✓ | ✓ | conforme |
| `etudiantDetails` minOccurs=0 | ✓ | « facultative », requis en pratique (30042) | requis fonctionnellement |
| `EtudiantType.bisCreated` | `xs:string` [0..1] | exemple de réponse seulement | nouveau |
| `AdresseType.rue` / `codePays` | facultatifs | obligatoires (sans NISS) | contrat assoupli |
| réponse `enregistrer` = `etudiant` / `modifier` = `etudiantDetails` | ✓ | ✓ (exemples) | asymétrie réelle |
| `doubleFlag` en mode NISS | - | diagramme et texte opposés | non résolu |
| `200` / `201` en mode NISS | - | tableau : 200 NISS, 201 DETAILS ; diagramme : 201 création, 200 fusion | production : 201 pour une création (2026-11-24) |
| `success=false` + `info 200` (modifier) | - | exemple | se fier au code |
| `codeNationalite` = INS 5 chiffres | string libre | « BE » dans un exemple | utiliser INS |

---

## Mapping pyetnic

Fonctions publiques de `pyetnic.seps` (construction, `docs/PUBLIC_API_SURFACE.md`) :

```python
def enregistrer_etudiant(mode_enregistrement: str,               # "NISS" | "DETAILS"
                         etudiant_details: EtudiantDetailsSave | None = None,
                         double_flag: bool | None = None,
                         create_bis_flag: bool | None = None) -> EnregistrerEtudiantResult: ...
def modifier_etudiant(cf_num: str,
                      etudiant_details: EtudiantDetailsSave | None = None) -> ModifierEtudiantResult: ...
```

- Un paramètre laissé à `None` n'est pas envoyé : le serveur applique alors ses défauts (`doubleFlag=false`, `createBisFlag=true`).
- Types d'envoi : `EtudiantDetailsSave`, `SepsNaissanceSave`, `SepsAdresseSave` (`rue`, `codePostal`, `codePays` y restent requis, comme dans le manuel), `SepsLocalite`, `SepsDeces`.
- **Résultat** (toujours un succès) :
  - `EnregistrerEtudiantResult` : `etudiant` (tel que renvoyé), `code`, `messages` (version du service exclue), `bis_cree` (`bisCreated` lu : `True` pour `O`, `False` pour `N`, `None` s'il est absent), `cree` (code `201`, nouveau `cfNum`), `fusionne` (code `200`, rattaché à une fiche existante qui garde son `cfNum`) ;
  - `ModifierEtudiantResult` : `etudiant`, `code`, `messages`. Un `success=false` qui ne porte que l'`info 200` est traité comme un succès (exemple du manuel).
- **Refus** : tout `success=false` lève une sous-classe de `SepsEtnicError`, que le code arrive en `error`, en `warning` ou seul en `info` : `SepsEtudiantExisteError` pour `30201` (`cf_num` lu dans la description), `SepsDoublonsError` pour `30202` / `30203` / `30204` (`cf_nums`, et `niss` pour la liste de la BCED ; un ou deux chiffres de contrôle acceptés), `SepsEtudiantInconnuError` pour `30120`, `NissMutationError` pour `30401`, `SepsAucuneModificationError` pour `30443`, `TropDeResultatsError` pour `30503`, `SepsValidationError` pour `30039`-`30042` et `30060`-`30080`, `SepsAuthError` pour `30550` ; `30502`, `30504` et `505xx` lèvent la classe de base.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSEnregistrerEtudiantMessages_external_v1.xsd` | Éléments d'opération + `ModeEnregistrement` | spécifique |
| `etudiant_v1.xsd` / `etudiantDetails_v1.xsd` | Signalétique (avec `bisCreated`, adresse assouplie) | = spec 09 (md5 identique) |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
