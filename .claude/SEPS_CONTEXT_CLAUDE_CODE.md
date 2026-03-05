# Services Web SEPS (ETNIC) — Document de contexte pour le développement

> **Objectif** : fournir à Claude Code le contexte métier, technique et les subtilités qui ne sont **pas déductibles** des fichiers WSDL/XSD. Ce document complète les contrats formels.

---

## 1. Vue d'ensemble

### 1.1 Qu'est-ce que SEPS ?

SEPS = **SIEL Enseignement de Promotion Sociale**. C'est la base de données centrale de la Fédération Wallonie-Bruxelles (FWB) qui gère les inscriptions d'étudiants dans l'enseignement de **promotion sociale** (formation pour adultes).

L'ETNIC (Entreprise des Technologies Numériques de l'Information et de la Communication) est l'organisme public qui héberge et expose ces services web.

### 1.2 Fonctionnalités couvertes

Les services SEPS permettent cinq grandes opérations :

1. **Recherche d'étudiants** dans la DB SEPS et dans les sources authentiques (BCSS — Banque Carrefour de la Sécurité Sociale)
2. **Notification** des modifications de signalétiques aux établissements
3. **Sauvegarde** (création/modification) d'étudiants dans la DB SEPS
4. **Inscription** d'étudiants à des Unités d'Enseignement (UE)
5. **Recherche d'inscriptions** aux UE

### 1.3 Version du service

- **Version documentée** : 2.1.9 (18/01/2023)
- Ces services remplacent une version antérieure datant de 2016.

---

## 2. Architecture technique

### 2.1 Protocole et sécurité

| Aspect | Détail |
|---|---|
| Protocole | **SOAP 1.1** |
| Transport | HTTPS (SSL/TLS 1.0) |
| Authentification | **WS-Security** avec certificat **X.509** |
| Communication | **Synchrone** |

**Point critique pour l'implémentation Python** : avec Zeep, il faut configurer le plugin `BinarySignature` avec le certificat X.509. L'authentification n'est **pas** du type UsernameToken classique mais bien du X.509 binaire.

### 2.2 Endpoints

Deux environnements sont disponibles :

| Env | Base URL |
|---|---|
| **TQ** (test/qualité) | `https://services-web.tq.etnic.be/seps/` |
| **PROD** | `https://services-web.etnic.be/seps/` |

Les chemins par service :

| Service | Chemin | Binding WSDL |
|---|---|---|
| Notification | `notifications/v1` | `SEPSNotificationsServiceV1ExternalBinding` |
| Recherche étudiants | `rechercheEtudiants/v1` | `SEPSRechercheEtudiantsServiceV1ExternalBinding` |
| Sauvegarde étudiant | `enregistrerEtudiant/v1` | `SEPSEnregistrerEtudiantV1ExternalBinding` |
| Sauvegarde inscription | `enregistrerInscription/v1` | `SEPSEnregistrerInscriptionV1ExternalBinding` |
| Recherche inscriptions | `rechercheInscriptions/v1` | `SEPSRechercheInscriptionsV1ExternalBinding` |

**Attention** : dans la documentation originale, il y a une coquille sur le binding de sauvegarde étudiant : `SEPSEnregistrerEtudiantV1ExternalBinding` (manque le "B" de "Binding" dans certaines occurrences : `Externalinding`). Se référer au WSDL pour la valeur exacte.

### 2.3 Identifiant de requête (requestId)

Chaque requête peut (optionnellement) inclure un UUID dans le header SOAP :

```xml
<soapenv:Header xmlns:req="http://etnic.be/types/technical/requestId/v1">
    <req:requestId>e2128df4-c6b4-4daa-b337-5fc536c33463</req:requestId>
</soapenv:Header>
```

Si non fourni, l'ETNIC en génère un et le retourne dans la réponse. **Cet identifiant est indispensable** pour le support technique auprès de l'ETNIC — il faut le logger systématiquement.

### 2.4 Namespaces XML importants

| Usage | Namespace |
|---|---|
| Messages notifications | `http://ws.etnic.be/seps/notifications/messages/v1` |
| Messages recherche étudiants | `http://ws.etnic.be/seps/rechercheEtudiants/messages/v1` |
| Messages sauvegarde étudiant | `http://ws.etnic.be/seps/enregistrerEtudiant/messages/v1` |
| Messages inscription | `http://ws.etnic.be/seps/enregistrerInscription/messages/v1` |
| Messages recherche inscriptions | `http://ws.etnic.be/seps/rechercheInscriptions/messages/v1` |
| Types étudiant | `http://enseignement.cfwb.be/types/seps/etudiant/v1` |
| Types détails étudiant | `http://enseignement.cfwb.be/types/seps/etudiantDetails/v1` |
| Types inscription | `http://enseignement.cfwb.be/types/seps/inscription/v1` |
| Types notification | `http://enseignement.cfwb.be/types/seps/notification/v1` |
| Types techniques (addressing) | `http://etnic.be/types/technical/addressing/v2` |
| Types techniques (authorisation) | `http://etnic.be/types/technical/authorisation/v2` |
| Types techniques (response) | `http://etnic.be/types/technical/ResponseStatus/v3` |
| Types techniques (requestId) | `http://etnic.be/types/technical/requestId/v1` |

---

## 3. Modèle de données — Types communs

### 3.1 Identifiants clés

#### cfNumType — Numéro de Communauté Française
- **Pattern** : `[0-9]{1,10}\-[0-9]{2}` (ex: `8501889-33`)
- Composé d'un numéro séquentiel + un code de vérification séparés par un tiret
- C'est l'**identifiant unique** d'un étudiant dans la DB SEPS
- **Rôle central** : c'est le cfNum qui permet d'inscrire un étudiant à une UE

#### NissType — Numéro NISS
- **Pattern** : `[0-9]{6}(\-)?[0-9]{3}(\-)?[0-9]{2}` (ex: `99082705172`)
- Peut être le numéro de Registre National ou le numéro de registre des étrangers
- Les tirets sont optionnels dans le pattern
- **Validation modulo 97** côté serveur (erreur 30042 si invalide)

#### LocaliteType
- `code` : code INS à 5 chiffres (`[0-9]{5}`), **obligatoire si localité belge**
- `description` : libellé de la commune/lieu

#### IncompleteDateType
- **Pattern** : `[1-2][0-9]{3}(\-[0-1][0-9]\-[0-3][0-9])?`
- Peut être une date complète (`1951-08-02`) **ou** juste une année (`1970`)
- Utilisé pour les dates de naissance quand seule l'année est connue

### 3.2 EtudiantType — Structure de l'étudiant

Un étudiant possède **deux versions** de ses données :

| Champ | Type | Description |
|---|---|---|
| `cfNum` | cfNumType [0..1] | Identifiant unique SEPS |
| `rnDetail` | EtudiantDetailType [0..1] | Version provenant de la **BCSS/Registre National** |
| `cfwbDetail` | EtudiantDetailType [0..1] | Version provenant de l'**établissement scolaire** |

**Points importants** :
- Les deux versions peuvent être identiques
- La version `cfwbDetail` peut être complétée avec les données BCSS
- Un étudiant peut **ne pas avoir** de version `rnDetail` (cas des étudiants sans NISS connu)
- L'attribut `rnValidityEndDate` sur `rnDetails`/`cfwbDetails` indique la fin de validité des données RN

### 3.3 EtudiantDetailType — Détails signalétiques

| Champ | Type | Cardinalité |
|---|---|---|
| `niss` | NissType | 0..1 |
| `nom` | NomType (string) | 0..1 |
| `prenom` | PrenomType (string, peut être vide) | 0..1 |
| `autrePrenom` | PrenomType | 0..3 (max 3 autres prénoms) |
| `sexe` | SexeType (M/F/X) | 0..1 |
| `naissance` | NaissanceType | 0..1 |
| `deces` | DecesType | 0..1 |
| `adresse` | AdresseType | 0..1 |
| `codeNationalite` | string | 0..1 |

#### NaissanceType
- `date` : IncompleteDateType, **obligatoire**
- `codePays` : code INS à 5 chiffres, **obligatoire**
- `localite` : LocaliteType, obligatoire côté backend

**Subtilité** : pour les naissances à l'étranger, le Registre National ne fournit que le **nom** de la ville (pas de code), donc `localite.code` sera vide et seule `localite.description` sera renseignée.

#### AdresseType
- `rue` : string, **obligatoire**
- `numero` : string max 4 chars, facultatif
- `boite` : string max 4 chars, facultatif
- `extension` : complément d'adresse (ex: "Building Acacias colonne H"), facultatif
- `codePostal` : string, **obligatoire**
- `localite` : LocaliteType, obligatoire côté backend
- `localiteExtension` : lieu-dit etc., facultatif
- `codePays` : code INS à 5 chiffres, **obligatoire**

**Code pays Belgique** : `00150`

---

## 4. Workflows métier

### 4.1 Workflow d'inscription d'un étudiant à une UE

C'est le workflow le plus complexe. Il suit une logique de **résolution progressive** de l'identité de l'étudiant :

```
A) Étudiant connu par cfNum ?
   → OUI : inscrire directement (étape D)
   → NON : passer à B

B) Étudiant connu par NISS ?
   → Appeler rechercheEtudiants par NISS
     → Retrouvé en SEPS ? → inscrire (D)
     → Retrouvé à la BCED ? → enregistrerEtudiant par NISS → inscrire (D)
     → Pas retrouvé → passer à C

C) Recherche par nom/prénom/date naissance/sexe
   → Retrouvé en SEPS ? → inscrire (D)
   → Retrouvé à la BCED ? → enregistrerEtudiant par NISS → inscrire (D)
   → Pas retrouvé → enregistrerEtudiant par détails (DETAILS) → inscrire (D)

D) Inscription via enregistrerInscription avec cfNum + données UE
```

**Conséquence pour l'implémentation** : le code client doit implémenter cette cascade de recherche/création avant de pouvoir inscrire. Il ne faut **jamais** tenter d'inscrire sans cfNum.

### 4.2 Workflow de mise à jour des signalétiques (synchronisation)

```
1. Appeler lireNotification avec etabId + date de dernière synchro
2. Pour chaque notification reçue :
   → Appeler lireEtudiant avec le cfNum + la date de la notification
   → Mettre à jour la base locale
```

---

## 5. Description détaillée des services

### 5.1 Service de Notification (`lireNotification`)

**But** : récupérer les modifications survenues sur les signalétiques des étudiants inscrits dans un établissement depuis une date donnée (incluse).

#### Contrôle d'accès
- Profil support : non limité
- Profil établissement : limité aux notifications de l'établissement
- Profil PO (Pouvoir Organisateur) : limité aux établissements du PO

#### Requête
- `etabId` (string, obligatoire) : identifiant **FASE** de l'établissement
- `dateDebut` (date, obligatoire) : date pivot (incluse)

#### Réponse — NotificationType
| Champ | Type | Description |
|---|---|---|
| `id` | unsignedLong | ID séquentiel de la notification |
| `cfNum` | cfNumType | Étudiant concerné |
| `date` | date | Date de la modification |
| `code` | NotificationCodeType | Type de modification |
| `description` | NotificationDescriptionType | Description textuelle |

#### Codes de notification

| Code | Description |
|---|---|
| `02` | Changement de sexe |
| `04` | Changement de nom/prénom |
| `05` | Changement d'adresse |
| `06` | Changement de nationalité |
| `07` | Changement de NISS |
| `08` | Changement de statut |

#### Codes d'erreur spécifiques
| Code | Description | Label |
|---|---|---|
| 30550 | Authentification | INTERNAL_SERVER_ERROR |
| 30049 | Validation etabId | BAD_REQUEST |
| 30050 | Validation dateFrom | BAD_REQUEST |
| 30105 | Aucune notification trouvée | NOT_FOUND |
| 200 | Notifications trouvées | SUCCESS |

---

### 5.2 Service de Recherche Étudiant

Ce service expose **deux opérations** distinctes sur le même endpoint.

#### 5.2.1 Opération `lireEtudiant`

Recherche par **cfNum** (numéro de communauté française).

**Requête** :
- `cfNum` (cfNumType, obligatoire)
- `fromDate` (date, facultatif — défaut : date du jour)

**Comportement** :
1. Recherche dans DB SEPS
2. Si trouvé avec version RN → retourne les deux versions (ETAB + RN)
3. Si trouvé sans version RN → retourne uniquement la version ETAB
4. Si non trouvé → erreur 30110

**Codes d'erreur** :
| Code | Description | Label |
|---|---|---|
| 30047 | Validation cfNum | BAD_REQUEST |
| 30048 | Validation fromDate | BAD_REQUEST |
| 30501 | Trop de résultats | INTERNAL_SERVER_ERROR |
| 30110 | Non trouvé | NOT_FOUND |
| 200 | Trouvé | SUCCESS |

#### 5.2.2 Opération `rechercheEtudiants`

Recherche par **NISS** ou par **combinaison nom/prénom/date naissance/sexe**.

**Requête** (choice — NISS ou combinaison, pas les deux) :
- `niss` (NissType) — prioritaire si fourni
- Ou bien la combinaison :
  - `nom` (NomType, obligatoire dans ce cas)
  - `prenom` (PrenomType, 0..1)
  - `dateNaissance` (IncompleteDateType, facultatif)
  - `sexe` (SexeType, facultatif)
  - `forceRn` (boolean, facultatif, défaut `false`) — depuis v1.0.7

**Comportement recherche par NISS** :
1. Recherche dans DB SEPS
2. Si trouvé → retourne les données
3. Sinon → appel ALIM (interrogation BCSS) avec le NISS
4. Si trouvé à la BCED → inscription aux mutations + retourne les données RN/BCSS
5. **Si mutation de NISS détectée** → retourne code 30401 avec le nouveau NISS (très important à gérer !)
6. Sinon → non trouvé

**Comportement recherche par nom** :
1. Recherche dans DB SEPS sur NOM_RECH./DN/SEXE, puis recherche phonétique (Phonex ETNIC)
2. Si `forceRn` = true → va directement à la BCED (recherche par nom)
3. Si trouvé en SEPS → retourne les données
4. Si non trouvé en SEPS → recherche par nom à la BCED
5. Si trouvé à la BCED → retourne les données RN/BCSS

**Point critique — Mutation de NISS (code 30401)** : quand un NISS a été remplacé par un nouveau (cas fréquent avec les numéros BIS remplacés par un vrai numéro de Registre National), le service retourne le **nouveau NISS** dans le message d'erreur. Le code client doit parser ce message et relancer la recherche avec le nouveau NISS.

**Codes d'erreur spécifiques** :
| Code | Description | Label |
|---|---|---|
| 30042 | Validation NISS (modulo 97 invalide) | BAD_REQUEST |
| 30043 | Validation nom | BAD_REQUEST |
| 30044 | Validation prénom | BAD_REQUEST |
| 30045 | Validation date naissance | BAD_REQUEST |
| 30046 | Validation sexe | BAD_REQUEST |
| 30401 | **Mutation de NISS détectée** | NOT_ACCEPTABLE |
| 30502 | Erreur appel BCED | INTERNAL_SERVER_ERROR |
| 30115 | Non trouvé | NOT_FOUND |
| 30501 | Trop de résultats | INTERNAL_SERVER_ERROR |
| 200 | Trouvé | SUCCESS |

---

### 5.3 Service de Sauvegarde Étudiant

Deux opérations : `enregistrerEtudiant` (création) et `modifierEtudiant` (modification).

#### 5.3.1 Opération `enregistrerEtudiant`

**Deux modes** d'enregistrement via le paramètre `modeEnregistrement` (énumération : `NISS` ou `DETAILS`) :

##### Mode NISS

**Requête** :
- `modeEnregistrement` = `NISS`
- `doubleFlag` (boolean, défaut `false`)
- `etudiantDetails.niss` : le NISS de l'étudiant

**Comportement** :
1. Recherche en DB SEPS par NISS
2. Si trouvé → **erreur 30201** (l'étudiant existe déjà, retourne le cfNum)
3. Sinon → appel ALIM BCSS avec le NISS
4. Si non trouvé à la BCSS → erreur 30120
5. Si trouvé → vérification doublon (sauf si `doubleFlag=true`)
   - Pas de doublon → création (code 201)
   - 1 doublon → fusion avec la version existante (code 200)
   - N doublons → erreur 30203 avec la liste des cfNum

**Attention mutation NISS** : si une mutation est détectée lors de l'appel ALIM, code **30401** (NOT_ACCEPTABLE) avec le nouveau NISS dans la description.

##### Mode DETAILS

**Requête** :
- `modeEnregistrement` = `DETAILS`
- `doubleFlag` (boolean, défaut `false`)
- `createBisFlag` (boolean, défaut `true` — depuis v2.0)
- `etudiantDetails` : les données complètes de l'étudiant

**Champs obligatoires si pas de NISS** :
- `nom` et `sexe`
- Naissance : `date`, `codePays`, et soit `localite.code` (si Belgique) soit `localite.description` (si étranger)
- Adresse : `rue`, `codePostal`, `codePays`, et `localite.description` si pays non belge
- `codeNationalite`

**Comportement** :
1. Recherche par nom en DB SEPS (phonétique)
2. Si trouvé(s) en SEPS → erreur 30203/409 avec liste des cfNum
3. Si non trouvé → recherche par nom à la BCED
4. Si 1 trouvé à la BCED → appel ALIM avec le NISS trouvé → création
5. Si plusieurs trouvés → erreur 30204 avec liste des NISS
6. Si aucun trouvé à la BCED :
   - Si `createBisFlag=true` → **création d'un numéro BIS** via le service BCED PUBLISHPERSON → création
   - Si `createBisFlag=false` → création sans version RN (version établissement uniquement)

**Le flag `createBisFlag`** est très important : il permet de créer un numéro BIS (numéro temporaire de la BCSS) pour les personnes qui n'ont pas de NISS belge. Par défaut à `true` depuis la version 2.0.

##### Codes d'erreur sauvegarde étudiant

| Code | Description | Label |
|---|---|---|
| 30039 | Mode d'enregistrement requis | BAD_REQUEST |
| 30040 | Validation NISS | BAD_REQUEST |
| 30042 | Données manquantes (pas de détail fourni) | BAD_REQUEST |
| 30201 | L'étudiant existe déjà (retourne le cfNum) | CONFLICT |
| 30202 | Plus d'un trouvé (recherche phonétique NISS) | CONFLICT |
| 30203 | Doublons trouvés (recherche phonétique DETAILS) | CONFLICT |
| 30204 | Plus d'un trouvé à la BCED | CONFLICT |
| 30120 | Non trouvé (à la BCSS/BCED) | NOT_FOUND |
| 30401 | Mutation de NISS | NOT_ACCEPTABLE |
| 30402 | Étudiant non enregistrable (RGPD) | NOT_ACCEPTABLE |
| 30443 | Aucune modification à appliquer | BAD_REQUEST |
| 30060–30078 | Validations des champs individuels | BAD_REQUEST |
| 201 | Créé | CREATED |
| 200 | OK (modification/fusion) | SUCCESS |

#### 5.3.2 Opération `modifierEtudiant`

Modification de la **version établissement** d'un étudiant existant.

**Requête** :
- `cfNum` (obligatoire)
- `etudiantDetails` (les données à modifier)

**Règle critique** : un champ **obligatoire en création reste obligatoire en modification**, même s'il n'a pas changé. Un champ facultatif **non présent** dans la requête sera **effacé** (mis à null) après la sauvegarde.

**Si pas de NISS fourni** dans les détails, alors `nom`, `sexe`, `naissance.date` et `naissance.codePays` sont obligatoires.

---

### 5.4 Service d'inscription à une UE

#### Contrôle d'accès
- Profil support : non limité
- Profil établissement : limité au périmètre du/des profil(s)
- Profil PO : limité aux établissements du PO

#### 5.4.1 Opération `enregistrerInscription`

**Requête** (InscriptionInputDataType) :
- `cfNum` (obligatoire)
- `idEtab` (integer, obligatoire) — ID FASE de l'établissement
- `idImplantation` (integer, obligatoire) — ID FASE de l'implantation
- `codePostalLieuCours` (string, obligatoire) — code postal du lieu du cours
- `inscription` (InscriptionInputType, obligatoire) — voir ci-dessous

#### InscriptionInputType (données de l'inscription)

| Champ | Type | Obligatoire | Notes |
|---|---|---|---|
| `dateInscription` | date | Oui | |
| `statut` | CodeStatutType | Oui | `DE` (définitive) ou `AN` (annulée) |
| `anneeScolaire` | integer | Oui | Erreur 30101 si absent |
| `ue` | UEInputType | Oui | Erreur 30100 si absent |
| `specificite` | SpecificiteDataType | Oui | Erreur 30025 si absent |

#### UEInputType
- `noAdministratif` (ShortType, obligatoire) : numéro administratif de l'UE
- `noOrganisation` (ShortType, obligatoire) : numéro d'organisation de l'UE

#### SpecificiteDataType (données spécifiques de l'inscription)

| Champ | Type | Obligatoire | Condition |
|---|---|---|---|
| `regulier1` | IndicateurType (O/N) | Non | Défaut N. Défaut O si inscription après validation. Non modifiable si UE validée au 1/10ème |
| `regulier5` | IndicateurType (O/N) | Non | Défaut N. Non modifiable si UE validée au 5/10ème |
| `droitInscription` | DroitInscriptionType | Non | |
| `droitInscriptionSpecifique` | DroitInscriptionSpecifiqueType | Non | **Uniquement si nationalité hors CEE** (erreur 30023 sinon) |
| `dureeInoccupation` | DureeInoccupationType | Conditionnel | **Uniquement si UE FSE, alors obligatoire** |
| `situationMenage` | SituationMenageType | Conditionnel | **Uniquement si UE FSE, alors obligatoire** |
| `enfantACharge` | IndicateurType | Non | Uniquement si UE FSE |
| `difficulteHandicap` | IndicateurXType (O/N/X) | Conditionnel | **Uniquement si UE FSE, alors obligatoire** |
| `difficulteAutre` | IndicateurXType (O/N/X) | Conditionnel | **Uniquement si UE FSE, alors obligatoire** |
| `admission` | AdmissionType | Oui | Erreur 30025 si absent |
| `sanction` | SanctionType | Non | |

**Important — UE FSE** : certains champs ne sont pertinents et/ou obligatoires que si l'UE est financée par le **Fonds Social Européen** (FSE). Le champ `fse` dans UEType (réponse) indique si c'est le cas. Si des champs FSE sont fournis pour une UE non-FSE → erreur 30022. Si des champs FSE obligatoires manquent pour une UE FSE → erreur 30021.

**Règle sur `regulier1`/`regulier5`** : ces indicateurs ne peuvent plus être modifiés une fois que l'UE a été validée au 1er ou 5ème dixième respectivement (erreurs 30079/30080).

**Contrainte d'âge** : l'étudiant doit avoir au moins **15 ans** au début de l'UE (erreur 30024).

#### 5.4.2 Opération `modifierInscription`

Même structure de requête que `enregistrerInscription`.

**Règles de modification** :
- Un champ obligatoire reste obligatoire
- Un champ facultatif non présent sera **effacé** après la sauvegarde
- On ne peut **pas modifier** une inscription annulée (code 30016)
- On ne peut **pas créer** une inscription avec statut annulé (code 30017)
- On ne peut **pas annuler** une inscription si le flag 1/10ème est posé (code 30070)

---

### 5.5 Service de Recherche des Inscriptions

#### Contrôle d'accès
- Profil support : non limité
- Profil établissement (unique) : `etabId` non obligatoire
- Profil établissement (multiple) : `etabId` **obligatoire** (erreur 30052 sinon)
- Profil PO : limité aux établissements du PO

#### Requête
Tous les paramètres sont facultatifs, **mais au moins un parmi** `anneeScolaire`, `cfNum`, ou `noAdministratif`+`noOrganisation` doit être présent (erreur 30036 sinon).

| Champ | Type | Description |
|---|---|---|
| `anneeScolaire` | integer | Année scolaire |
| `etabId` | integer | ID FASE établissement |
| `dateRequest` | date | Date de situation (défaut : aujourd'hui) |
| `cfNum` | cfNumType | Identifiant étudiant |
| `noAdministratif` | ShortType | N° admin de l'UE |
| `noOrganisation` | ShortType | N° organisation de l'UE |

#### InscriptionType (réponse)

| Champ | Type | Description |
|---|---|---|
| `cfNum` | cfNumType | Identifiant étudiant |
| `anneeScolaire` | integer | |
| `idEtab` | integer | ID FASE établissement |
| `idImplantation` | integer | ID FASE implantation |
| `dateInscription` | date | |
| `lieuCours` | LieuCoursType | Code postal + ville |
| `statut` | CodeStatutType | DE ou AN |
| `ue` | UEType | Détails complets de l'UE |
| `specificite` | SpecificiteDataType | |

#### UEType (détails UE dans la réponse)

| Champ | Type | Description |
|---|---|---|
| `noAdministratif` | ShortType | |
| `noOrganisation` | ShortType | |
| `label` | TextType | Libellé de l'UE |
| `code` | TextType | Code du cours (format long) |
| `codeNiveau` | CodeNiveauType | SI/SS/SC/SL |
| `nombreSemaine` | ShortType | |
| `dateDebut` | date | |
| `dateFin` | date | |
| `fse` | IndicateurType | O/N — indique si UE FSE |
| `noOrganisationPrecedent` | TextType | N° organisation précédente |
| `activiteDeFormation` | IndicateurType | |

Les niveaux (`codeNiveau`) :
- `SI` : Secondaire inférieur
- `SS` : Secondaire supérieur
- `SC` : Supérieur court
- `SL` : Supérieur long

---

## 6. Énumérations de référence (valeurs métier)

### 6.1 Admission (AdmissionType)

| CodeAdmission | Description | Champs conditionnels |
|---|---|---|
| `REUSSITE` | Certificat réussite UE | Aucun champ additionnel (erreur 30026 sinon) |
| `TITREBEL` | Titre d'études en Belgique | `typeEnseignement` + `titreDelivre` obligatoires |
| `TITREETR` | Titre d'études hors Belgique | `equivalence` obligatoire |
| `AUTRE` | Autres | `valorisationAcquis` obligatoire |

### 6.2 TypeEnseignementType (si admission TITREBEL)

`PRI`, `SIPE`, `SSPE`, `SIPS`, `SSPS`, `SCPE`, `SLPE`, `SCPS`, `SLPS`

### 6.3 TitreDelivreType — dépend du typeEnseignement

La compatibilité titre/type d'enseignement est validée côté serveur (erreur 30035 si incohérent).

Exemples de combinaisons valides :
- Primaire / SIPS → `CEB`
- SIPE / SIPS → `CE1D`, `CESI`
- SSPE / SSPS → `CE2D`
- SCPE / SCPS → `BES`, `BACH`, `BACHSPE`
- SLPE / SLPS → `MAST`
- SSPS → `CESS`, `CQINF`, `CQSUP`

### 6.4 EquivalenceType (si admission TITREETR)

| Code | Description |
|---|---|
| `C01` | Équivalence secondaire inférieur |
| `C02` | Équivalence secondaire supérieur |
| `C03` | Équivalence supérieur |
| `C04` | Équivalence CEB |

### 6.5 ValorisationAcquisType (si admission AUTRE)

`C01` à `C04` (admission/dispense V1-V4 formelle), `C10` (VANFI test/épreuve), `C20` (VANFI dossier), `C30` (autres), `C40` (aucun titre requis)

### 6.6 Sanction (SanctionType)

| CodeSanction | Champs conditionnels |
|---|---|
| `RE` (Réussite) | `valorisationAcquisSanction` obligatoire |
| `AB` (Abandon) | `motifAbandon` obligatoire |
| `EH` (Échec) | Aucun |

#### ValorisationAcquisSanctionType (si RE)
`C00` (Réussite), `C01`-`C04` (valorisation acquis formels V1-V4), `C05` (VANFI test/épreuves)

#### MotifAbandonType (si AB)
`TPS` (temps), `PRO` (professionnel), `FAM` (familial), `SAN` (santé), `ATT` (ne correspond pas aux attentes), `MEM` (mise à l'emploi), `FMJ` (force majeure), `NUM` (fracture numérique), `AUT` (autres), `INC` (inconnu)

#### StatutFinFormationType (uniquement si FSE, alors obligatoire)
`01` (mise à l'emploi), `02` (poursuite formation PI), `03` (poursuite formation hors PI), `04` (aide recherche emploi), `05` (réorientation), `06` (fin sans suite)

### 6.7 Droits d'inscription

#### DroitInscriptionType
- `indicateurDroitInscription` (O/N) : si le droit doit être perçu
- `exempte` (facultatif) : si l'étudiant est exempté
  - `indicateurExempteDroitInscription` (O/N) : **exclusif** par rapport à `indicateurDroitInscription` (erreur 30033 si les deux sont à O)
  - `motifExemption` : C01-C07

Motifs d'exemption : C01 (mineur obligation scolaire), C02 (chômeur complet indemnisé), C03 (handicap reconnu), C04 (revenu d'intégration), C05 (personnel enseignant en recyclage), C06 (obligation autorité publique), C07 (autre)

#### DroitInscriptionSpecifiqueType
Même structure. **Uniquement pour nationalité hors CEE** (erreur 30023 sinon).

Motifs d'exemption spécifique : C01-C13 (voir document source pour le détail complet)

### 6.8 DureeInoccupationType (UE FSE uniquement)

| Code | Description |
|---|---|
| `C00` | < 6 mois |
| `C06` | > 6 mois et < 12 mois |
| `C12` | > 12 et < 24 mois |
| `C24` | > 24 mois |

### 6.9 SituationMenageType (UE FSE uniquement)

| Code | Description |
|---|---|
| `ISOL` | Isolé |
| `SSEM` | Ménage sans emploi |
| `A1EM` | Ménage avec au moins un emploi |
| `X` | N'accepte pas de préciser |

---

## 7. Structure des réponses SOAP

### 7.1 Pattern général des réponses

Toutes les réponses suivent le même pattern (héritage de `AbstractExternalResponseType`) :

```xml
<success>true|false</success>
<messages>
    <info|warning|error>
        <code>XXXXX</code>
        <description>Message texte</description>
        <zone>optionnel</zone>
    </info|warning|error>
</messages>
<response>
    <!-- données métier -->
</response>
```

**Important** : le champ `success` est un **boolean**. Même en cas de `success=false`, la réponse peut contenir des données (ex: modification sans changement retourne les données actuelles avec code 30443).

### 7.2 Erreurs techniques (SOAP Faults)

Les erreurs techniques sont des SOAP Faults standard :

| Code | Description |
|---|---|
| SECU-0102 | Pas d'information de sécurité (WSS X509 ou UsernameToken) |
| SECU-0103 | WSS UsernameToken échoué (user/password invalide) |
| SECU-0104 | WSS X509 échoué auprès du LDAP |
| SECU-1101 | Pas les profils de sécurité requis |
| ROUT-1001 | Erreur technique du fournisseur |
| VALI-0100 | Validation XSD de la requête échouée |
| VALI-1100 | Validation XSD de la réponse échouée |

---

## 8. Glossaire des identifiants et codes

| Terme | Description |
|---|---|
| **FASE** | Fichier Administratif et Signalétique des Établissements — base de référence des établissements scolaires en FWB |
| **cfNum** / **N°CF** | Numéro de Communauté Française — identifiant unique étudiant dans SEPS |
| **NISS** | Numéro d'Identification de la Sécurité Sociale (= registre national ou registre des étrangers) |
| **BIS** | Numéro BIS — numéro temporaire attribué par la BCSS aux personnes non inscrites au Registre National |
| **BCSS** / **BCED** | Banque Carrefour de la Sécurité Sociale / Banque Carrefour d'Échange de Données |
| **ALIM** | Appel d'alimentation — interrogation des sources authentiques (BCSS) |
| **UE** | Unité d'Enseignement |
| **FSE** | Fonds Social Européen — certaines UE sont financées FSE et ont des champs obligatoires supplémentaires |
| **PO** | Pouvoir Organisateur — l'organisation qui gère un ou plusieurs établissements |
| **DB SEPS** | Base de données centrale de la promotion sociale (gérée par l'AGE) |
| **INS** | Institut National de Statistique — codes standardisés pour communes/pays (ONSS, Statbel) |
| **Phonex** | Algorithme de recherche phonétique utilisé par l'ETNIC |

---

## 9. Pièges et subtilités pour l'implémentation

### 9.1 Gestion des mutations de NISS

Le code 30401 (`NOT_ACCEPTABLE`) indique qu'un NISS a été remplacé. Le nouveau NISS est contenu dans le **message de description**. Il faut parser cette description pour en extraire le nouveau NISS et relancer l'opération.

### 9.2 Comportement d'effacement en modification

Pour `modifierEtudiant` et `modifierInscription` : les champs facultatifs **non présents** dans la requête seront **effacés**. Il faut donc toujours renvoyer l'intégralité des données, pas seulement les champs modifiés.

### 9.3 Doublon et flag doubleFlag

La détection de doublons se fait sur la combinaison nom/prénom/sexe/date de naissance. Si `doubleFlag=false` (défaut), le service refuse de créer un doublon. À `true`, il crée malgré tout mais trace le doublon.

### 9.4 Codes INS pour les pays

Le code INS pour la Belgique est `00150`. Les codes pays et communes sont disponibles dans le catalogue SOA de l'ETNIC. Pour les localités belges, le code INS à 5 chiffres de la commune est obligatoire. Pour les localités étrangères, seule la description textuelle est attendue.

### 9.5 Incohérences dans la documentation

- Le binding `SEPSEnregistrerEtudiantV1ExternalBinding` apparaît parfois comme `Externalinding` (typo sans "B")
- L'opération `enregistrerInscription` est parfois nommée `enregisterIncription` (fautes d'orthographe dans le WSDL original — vérifier le WSDL fourni)

### 9.6 WS-Security et headers de réponse

Les réponses incluent des headers WS-Security complets avec `BinarySecurityToken`, `Timestamp`, et `Signature`. Le client doit pouvoir valider ou au minimum tolérer ces headers. Avec Zeep, utiliser le plugin approprié pour la gestion X.509.

### 9.7 Ordre de priorité des recherches

La recherche par NISS est **toujours prioritaire** sur la recherche par nom/prénom/DN/sexe. Le service applique cette priorité automatiquement : si un NISS est fourni en même temps que des critères nominatifs, seul le NISS est utilisé.

### 9.8 Dates incomplètes

Le type `IncompleteDateType` accepte soit une date complète `AAAA-MM-JJ` soit juste une année `AAAA`. Ce cas se présente réellement en production pour des étudiants dont seule l'année de naissance est connue. Le code client doit gérer les deux formats.

---

## 10. Résumé des services et opérations

| Service | Opération | Action SOAP | Input principal | Output principal |
|---|---|---|---|---|
| Notifications | `lireNotification` | `lireNotifications` | etabId + dateDebut | Liste de NotificationType |
| Recherche étudiants | `lireEtudiant` | `lireEtudiant` | cfNum (+ fromDate) | EtudiantType |
| Recherche étudiants | `rechercheEtudiants` | `rechercherEtudiants` | NISS ou nom/prénom/DN/sexe | Liste de EtudiantType |
| Sauvegarde étudiant | `enregistrerEtudiant` | `enregistrerEtudiant` | mode + détails | EtudiantType |
| Sauvegarde étudiant | `modifierEtudiant` | `modifierEtudiant` | cfNum + détails | EtudiantType |
| Inscription UE | `enregistrerInscription` | `enregistrerInscription` | cfNum + UE + spécificités | InscriptionType |
| Inscription UE | `modifierInscription` | `modifierInscription` | cfNum + UE + spécificités | InscriptionType |
| Recherche inscriptions | `rechercherInscriptions` | `rechercherInscriptions` | Critères combinés | Liste de InscriptionType |
