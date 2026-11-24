# SEPS - Recherche Étudiants v1

> Spécification technique et fonctionnelle complète
> Sources :
> - **Contrat** : WSDL + XSD servis par la production (`https://ws.etnic.be/seps/rechercheEtudiants/v1?wsdl`), embarqués dans `pyetnic/resources/SEPS_Recherche_Etudiants_2.1/` (relevé du 2026-11-24).
> - **Manuel** : « Services Web SEPS - Manuel d'utilisation » **2.1.9** (18/01/2023), §3.4. C'est la seule source pour ce service : le lien du catalogue SOA vers le manuel « Recherche Étudiants » 2.3 (`ETNIC_Services_Web_SIEL_SEPS_RechercheEtudiants_v2.3_Manuel_d_utilisation_rev10.0.pdf`, rev 10.0) renvoie une erreur 404 (constat de novembre 2026, revérifié le 2026-11-24).
> - Manuel « Enregistrer Étudiants » **2.3** (rev 10.0, 10/06/2026), §2 et §3.1, pour la plateforme et les types communs qu'il partage avec ce service.
> - **Observations de production** (datées dans le texte).
>
> Première analyse : 2026-06-09 (session 7). Refonte : 2026-11-24 (#24).
> Conventions : « manuel » = ce que dit le PDF ; « contrat » = le WSDL/XSD de production ; « observé en production (date) » = un comportement constaté ; « inconnu » = rien ne permet de trancher.

---

## Famille SEPS - préambule (à lire une fois pour les specs 09 à 13)

**SEPS** est la base centrale de données de l'enseignement de promotion sociale (Enseignement pour Adultes). Ces services forment une **famille distincte des services EPROM** (specs 01 à 06) :

| Aspect | EPROM (01-06) | SEPS (09-13) |
|---|---|---|
| Domaine | Organisation des formations (école/PO) | Étudiants et inscriptions (signalétique, UE) |
| Namespace racine | `enseignement.cfwb.be/types/...` + `services-web.etnic.be/eprom/...` | `ws.etnic.be/seps/...` + `enseignement.cfwb.be/types/seps/...` |
| Authentification | WS-Security UsernameToken | WS-Security certificat X.509 (manuels 2.3/2.4, §2.1) ; Notifications : voir spec 13 |
| SOAP | 1.1 ou 1.2 | SOAP 1.1 uniquement |
| Bloc retour | `AbstractExternalResponseType` (`common/v1`) | `AbstractExternalResponseType` (`external/v1`, autre namespace, même forme) |
| Identité métier | `etabId`/`numAdmFormation`/`numOrganisation` | `cfNum` (numéro Communauté française de l'étudiant) |

### Plateforme et sécurité
- **Manuel 2.3/2.4, §2.1** : canal SSL en **TLS 1.2 et 1.3** (le manuel 2.1.9 disait « TLS 1.0 ») ; authentification WS-Security avec **certificat X.509** ; échange synchrone ; SOAP 1.1, document/literal. Référence plateforme : « Plateforme Services Web ETNIC - Spécifications techniques - Rev2.0 » (catalogue SOA).
- **Endpoints (manuels 2.3/2.4, §2.2)** : TQ `https://ws-tq.etnic.be/seps/<service>/v1`, PROD `https://ws.etnic.be/seps/<service>/v1`. Le manuel 2.1.9 donnait `services-web(.tq).etnic.be/seps/...` : forme abandonnée. Observé le 2026-11-24 : `services-web.tq.etnic.be/seps/...` ne répond pas (délai dépassé).
- **TQ et certificat de production** : observé en production (2026-11-24), le certificat X.509 de production est refusé sur TQ par une SOAP Fault **`SECU-0102`** (« aucune information de sécurité reçue »). `docs/SPEC.md` consigne `SECU-0104` pour le même cas (observation antérieure). Dans les deux cas, SEPS ne peut pas être exercé sur TQ avec le certificat de production : il n'y a pas d'environnement de test utilisable sans certificat TQ.

### Identifiant de requête (manuel 2.3, §2.3)
Header SOAP `requestId` (UUID), **facultatif en requête** : si absent, l'ETNIC en génère un et le renvoie dans l'entête de réponse. À conserver pour le support ETNIC.
- Contrat : `wsdl:required="false"` en entrée ; `true` en sortie pour Recherche Étudiants, Recherche Inscriptions et Notifications ; `false` en sortie pour les deux services d'enregistrement.

### Erreurs techniques (SOAP Fault, manuel 2.3, §2.4) et erreurs métier
Deux niveaux distincts :
1. **SOAP Fault** (technique, transport) : `faultcode` / `faultstring` / `faultactor` / `detail{messageId, code, description fr+en}`.
2. **Erreur métier** : HTTP 200, corps `success=false` et `messages/error|warning` (code + description). C'est le cas documenté par opération.

| Code SOAP Fault | Description (manuel 2.3, §2.4.2) |
|---|---|
| `SECU-0102` | Authentification échouée : aucune information de sécurité reçue (WSS X509 ou UsernameToken) |
| `SECU-0103` | WSS UsernameToken : utilisateur ou mot de passe invalide |
| `SECU-0104` | WSS X509 : échec auprès du LDAP |
| `SECU-1101` | Autorisation : profils de sécurité requis absents |
| `ROUT-1001` | Erreur technique du fournisseur de service |
| `VALI-0100` | Validation XSD du message de **requête** échouée |
| `VALI-1100` | Validation XSD du message de **réponse** échouée |

### Bloc retour - `AbstractExternalResponseType` (`external_v1.xsd`)
```
AbstractExternalResponseType (abstract, ns http://etnic.be/types/technical/external/v1)
├── success  : boolean       [obligatoire]   (ns ResponseStatus/v3)
└── messages : messagesType  [0..1]          (ns ResponseStatus/v3)
    ├── error   : MessageType [0..*]   -> code (max 10), description [0..1], zone [0..1]
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```
- **Manuel** : le code de succès est porté par `messages/info` (`200`, `201`) avec `success=true` ; l'absence de résultat arrive souvent en `messages/warning` **avec `success=false`** (`30115`, `30103`, `30105`). Certains exemples du manuel montrent `success=false` avec un seul `info` (`200` ou `30443`, spec 10).
- **Observé en production (2026-11-10)** : `enregistrerInscription` a répondu `success=false` avec **pour seul message le warning `30101`**. Un warning peut donc porter un refus.
- **Observé en production (2026-11-24)** : la réponse peut contenir un `info` supplémentaire portant la **version du service** (code `2.4.6`, description « version »), sans valeur métier.
- Les exemples de réponses contiennent aussi les namespaces plateforme `addressing/v2` et `authorisation/v2`, absents des XSD du contrat.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | SEPS (Enseignement pour Adultes / promotion sociale) |
| Service | Recherche Étudiants |
| Version contrat | external **v1** (dossier `SEPS_Recherche_Etudiants_2.1`) |
| Version manuel | 2.1.9 (18/01/2023) ; aucun manuel plus récent accessible |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security certificat X.509 |
| WSDL namespace | `http://ws.etnic.be/seps/rechercheEtudiants/v1` |
| Messages namespace | `http://ws.etnic.be/seps/rechercheEtudiants/messages/v1` |
| Binding | `SEPSRechercheEtudiantsV1ExternalBinding` (document/literal) |
| Service WSDL | `service_seps_rechercheEtudiants_external_v1` |

### Endpoints

| Env | Source | URL |
|---|---|---|
| PROD | contrat de production (`soap:address`) | `https://ws.etnic.be:443/seps/rechercheEtudiants/v1` |
| TQ | contrat servi par TQ (`soap:address`) | `https://ws-tq.etnic.be:443/seps/rechercheEtudiants/v1` |
| TQ / PROD | manuels 2.3/2.4 des autres services, §2.2 | `https://ws(-tq).etnic.be/seps/rechercheEtudiants/v1` |
| TQ / PROD | manuel 2.1.9, §2.2 (obsolète) | `https://services-web(.tq).etnic.be/seps/rechercheEtudiants/v1` |

pyetnic appelle `https://ws.etnic.be/seps/rechercheEtudiants/v1` (`ENV=prod`) ou `https://ws-tq.etnic.be/...` (`ENV=dev`, inutilisable avec un certificat de production, voir le préambule).

---

## Description fonctionnelle

Service de **recherche d'un étudiant** (signalétique d'identification) dans la DB SEPS et, à défaut, dans les **sources authentiques** (BCSS/RN via la BCED). Deux opérations (manuel 2.1.9, §3.4) :

1. **lireEtudiant** : recherche **par `cfNum`**, à une date donnée.
2. **rechercherEtudiants** : recherche **par NISS** (privilégiée) **ou** par combinaison **nom / prénom / date de naissance / sexe**.

La DB SEPS garde, pour chaque étudiant, **deux versions** de la signalétique :
- **`rnDetails`** : version issue du **Registre national / BCSS**, si elle existe ;
- **`cfwbDetails`** : version communiquée par l'**établissement** (applications locales ou SIEL Web), complétable avec les données BCSS.

> Vocabulaire : **BCSS** = Banque Carrefour de la Sécurité Sociale ; **BCED** = Banque Carrefour d'Échange de Données (canal d'accès aux sources authentiques) ; **RN** = Registre national. L'appel aux sources authentiques est nommé « **appel ALIM** » dans les manuels.

---

## Types communs SEPS - signalétique étudiant

> Définis dans `cfNum_v1.xsd`, `etudiant_v1.xsd`, `etudiantDetails_v1.xsd`. **Partagés avec la spec 10** (Enregistrer Étudiant) : fichiers identiques octet pour octet dans les deux dossiers (md5 vérifié le 2026-11-24). Voir aussi `00_REGISTRE.md` §7.4.

### cfNumType (`cfNum_v1.xsd`, ns `…/types/seps/cfNum/v1`)
Identifiant **unique de l'étudiant** dans la DB SEPS (« numéro de communauté française »). Deux parties : un entier et un code de contrôle (manuel 2.3, §3.1.1).
- Type : `string`, pattern `[0-9]{1,10}\-[0-9]{2}`, ex. `1234567-89` (fictif).
- Le manuel 2.3 (p. 12) montre pourtant, dans la description d'un `30203`, des numéros à **un seul** chiffre de contrôle (spec 10). Un numéro lu dans une description de message ne suit donc pas forcément le pattern.

### EtudiantType (`etudiant_v1.xsd`, ns `…/types/seps/etudiant/v1`)
```
EtudiantType
├── cfNum       : cfNumType            [0..1]
├── bisCreated  : xs:string            [0..1]   (contrat de production ; absent du contrat du catalogue 2.1)
├── rnDetails   : EtudiantDetailsType  [0..1]   (version Registre national / BCSS)
└── cfwbDetails : EtudiantDetailsType  [0..1]   (version établissement)
```
- **`bisCreated`** : nouveau dans le contrat de production. Le manuel 2.3 ne le décrit pas dans son tableau (§3.1.8) mais l'exemple de réponse `enregistrerEtudiant` (§3.3.1.4.1) porte `<bisCreated>O</bisCreated>` : un NISS bis a été créé (spec 10). Valeurs vues dans le manuel : `O`. `N` est supposé par analogie avec `IndicateurType`, non observé.
- Le texte des manuels nomme les éléments `rnDetail` / `cfwbDetail` (singulier) ; le XSD, les diagrammes et tous les exemples utilisent `rnDetails` / `cfwbDetails`. Le XSD fait foi.
- Manuel 2.3, §3.1.8 : les deux versions peuvent être identiques ; « parfois, un étudiant ne dispose pas de version rnDetail ».

### EtudiantDetailsType (`etudiantDetails_v1.xsd`, ns `…/types/seps/etudiantDetails/v1`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `niss` | NISSType | 0..1 | NISS (RN) ou numéro de registre des étrangers |
| `nom` | NomType (1..80) | 0..1 | Nom |
| `prenom` | PrenomType (0..50) | 0..1 | Prénom (peut être vide) |
| `autrePrenom` | PrenomType | 0..3 | Autres prénoms (jusqu'à 3) |
| `sexe` | SexeType | 0..1 | `M` / `F` / `X` |
| `naissance` | NaissanceType | 0..1 | Date, pays et localité de naissance |
| `deces` | DecesType | 0..1 | Date de décès |
| `adresse` | AdresseType | 0..1 | Adresse de résidence |
| `codeNationalite` | string | 0..1 | Code INS nationalité, 5 chiffres (spec 15) |

**NISSType** : `string`, pattern `[0-9]{6}(\-)?[0-9]{3}(\-)?[0-9]{2}`. Contrôle modulo 97 côté serveur (`30042` ici, `30040` à l'enregistrement).
**SexeType** : énumération `M` / `F` / `X` (autre).
**IncompleteDateType** : `string`, pattern `[1-2][0-9]{3}(\-[0-1][0-9]\-[0-3][0-9])?`, date complète `AAAA-MM-JJ` **ou année seule** `AAAA` (manuel 2.3, §3.1.7).

**NaissanceType**
```
NaissanceType
├── date     : IncompleteDateType  [obligatoire]
├── codePays : string              [obligatoire]   code INS pays, 5 chiffres (00150 = Belgique ; spec 15)
└── localite : LocaliteType        [0..1]          « obligatoire (backEnd) » selon le manuel 2.3, §3.1.8.2
```
> Manuel 2.3, §3.1.8.2 : pour une naissance **à l'étranger**, le RN ne renvoie que le **nom** de la ville (`localite/description`), sans code.

**AdresseType**
```
AdresseType
├── rue               : string        [0..1 contrat de production ; obligatoire au catalogue 2.1 et au manuel 2.3]
├── numero            : string        [0..1]  (max 4 caractères selon le manuel)
├── boite             : string        [0..1]  (max 4 caractères selon le manuel)
├── extension         : string        [0..1]  (complément, ex. nom de résidence)
├── codePostal        : string        [obligatoire]
├── localite          : LocaliteType  [0..1]  « obligatoire (backEnd) » selon le manuel 2.3, §3.1.8.4
├── localiteExtension : string        [0..1]  (lieu-dit…)
└── codePays          : string        [0..1 contrat de production ; obligatoire au catalogue 2.1 et au manuel 2.3]
```
> **Changement du contrat de production** (relevé du 2026-11-24, identique sur TQ) : `rue` et `codePays` d'`AdresseType` y sont devenus facultatifs. Le manuel 2.3 (§3.1.8.4, §3.3.1.2.1) les exige toujours pour un enregistrement sans NISS. Une réponse peut donc les omettre sans être invalide ; une requête qui les omet passe la validation XSD mais tombe sous les règles métier de la spec 10.

**LocaliteType** : `code` [0..1] (code **INS 5 chiffres**, obligatoire si la commune ou le district est belge, pattern documenté `[0-9]{5}` mais non porté par le XSD) + `description` [0..1] (libellé).
**DecesType** : `date` (`xs:date`, obligatoire).

> **Champs de réponse hors contrat** (exemples du manuel 2.1.9, §3.4.1.4.1 ; toujours absents du contrat de production) :
> - attribut `rnValidityEndDate` (date) sur `rnDetails` / `cfwbDetails` ;
> - élément `codeEtatCivil` dans `cfwbDetails`.
> Non observés en production à ce jour. pyetnic analyse les réponses en mode non strict (zeep `strict=False`) et ne modélise pas ces champs.

---

## Opération 1 : lireEtudiant

### Description (manuel 2.1.9, §3.4.1.1)
Recherche un étudiant **à une date donnée** sur base de son `cfNum`. Sans date, **date du jour**. Retourne la version établissement et, si elle existe, la version RN/BCSS (diagramme : « [Vers. RN exist] » -> données ETAB et RN/BCSS ; « [Pas de Vers. RN] » -> données ETAB).

### Requête - `lireEtudiant` (type `LireEtudiantRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `cfNum` | cfNumType | oui | Identification de l'étudiant |
| `fromDate` | xs:date | non | Date pivot (incluse). Défaut = date du jour |

### Réponse - `lireEtudiantReponse` (type `LireEtudiantReponseType` extends `AbstractExternalResponseType`)
```
response [0..1]
└── etudiant : EtudiantType   [obligatoire dans response]
```

### Codes de retour (manuel 2.1.9, §3.4.1.3.2)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Students found |
| false | `30047` | BAD_REQUEST | Validation `cfNum` |
| false | `30048` | BAD_REQUEST | Validation `fromDate` |
| false | `30110` | NOT_FOUND | Pas trouvé (fin de traitement) |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

> `30115` (« No student found for those search criteria », warning) n'est pas dans ce tableau mais figure dans l'exemple d'erreur de `lireEtudiant` (§3.4.1.4.2). Les deux codes signifient « rien trouvé ».

### Exemple de requête (identifiant fictif)
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://etnic.be/types/technical/requestId/v1"
                  xmlns:v11="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1">
  <soapenv:Header>
    <v1:requestId>e2128df4-c6b4-4daa-b337-5fc536c33463</v1:requestId>
  </soapenv:Header>
  <soapenv:Body>
    <v11:lireEtudiant>
      <v11:cfNum>1234567-89</v11:cfNum>
      <v11:fromDate>2026-05-01</v11:fromDate>
    </v11:lireEtudiant>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse (simplifié, anonymisé, d'après le manuel 2.1.9 §3.4.1.4.1)
```xml
<ns3:lireEtudiantReponse
    xmlns:ns3="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1"
    xmlns:ns4="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns5="http://enseignement.cfwb.be/types/seps/etudiant/v1"
    xmlns:ns6="http://enseignement.cfwb.be/types/seps/etudiantDetails/v1">
  <ns4:success>true</ns4:success>
  <ns4:messages><ns4:info><ns4:code>200</ns4:code><ns4:description>Students found</ns4:description></ns4:info></ns4:messages>
  <ns3:response>
    <ns3:etudiant>
      <ns5:cfNum>1234567-89</ns5:cfNum>
      <ns5:rnDetails rnValidityEndDate="2039-11-27">
        <ns6:niss>…</ns6:niss>
        <ns6:nom>XXXXXX</ns6:nom><ns6:prenom>xxxx</ns6:prenom>
        <ns6:sexe>M</ns6:sexe>
        <ns6:naissance>
          <ns6:date>198x-0x-06</ns6:date>
          <ns6:codePays>00306</ns6:codePays>
          <ns6:localite><ns6:code/><ns6:description>Kinshasa</ns6:description></ns6:localite>
        </ns6:naissance>
        <ns6:adresse>
          <ns6:rue>rue xxxxxxxx</ns6:rue><ns6:numero>xx</ns6:numero><ns6:codePostal>1400</ns6:codePostal>
          <ns6:localite><ns6:code>25072</ns6:code><ns6:description>Nivelles</ns6:description></ns6:localite>
          <ns6:codePays>00150</ns6:codePays>
        </ns6:adresse>
        <ns6:codeNationalite>00111</ns6:codeNationalite>
      </ns5:rnDetails>
      <ns5:cfwbDetails rnValidityEndDate="2039-11-27">
        <!-- mêmes champs ; peut contenir codeEtatCivil (ex. C12), hors contrat -->
      </ns5:cfwbDetails>
    </ns3:etudiant>
  </ns3:response>
</ns3:lireEtudiantReponse>
```

---

## Opération 2 : rechercherEtudiants

### Description (manuel 2.1.9, §3.4.2.1)
Recherche par **NISS** (privilégiée) **ou** par combinaison **nom/prénom/date de naissance/sexe** (uniquement si le NISS est absent). Si l'étudiant n'est pas en DB SEPS, recherche à la **BCSS** via la BCED (appel ALIM). Depuis la v1.0.7, un flag permet de **forcer** la recherche RN lors d'une recherche par nom ; le manuel conseille malgré tout une recherche SEPS préalable.

### Requête - `rechercherEtudiants` (type `RechercherEtudiantsRequeteType`)

Structure **`xs:choice`** :
```
rechercherEtudiants
├── (choix A) niss : NISSType                       [obligatoire]
└── (choix B) séquence :
    ├── forceRnFlag   : boolean             [0..1]   (manuel : « forceRn », défaut false depuis 1.0.7)
    ├── nom           : NomType             [obligatoire]
    ├── prenom        : PrenomType          [0..1]
    ├── dateNaissance : IncompleteDateType  [0..1]   (AAAA-MM-JJ ou AAAA)
    └── sexe          : SexeType            [0..1]
```
> Le contrat nomme le flag `forceRnFlag` et le place **en tête** de la séquence (avant `nom`) ; le manuel écrit `forceRn`. Le contrat fait foi, ordre compris.

### Réponse - `rechercherEtudiantsReponse` (type `RechercherEtudiantsReponseType`)
```
response [0..1]
└── etudiant : EtudiantType   [0..*]   (liste : une recherche par nom peut renvoyer plusieurs résultats)
```

### Codes de retour (manuel 2.1.9, §3.4.2.3.2)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Students found |
| false | `30042` | BAD_REQUEST | Validation SSIN, ex. « Invalid national number ! (incorrect mod 97) (ssin) » |
| false | `30043` | BAD_REQUEST | Validation LastName |
| false | `30044` | BAD_REQUEST | Validation FirstName |
| false | `30045` | BAD_REQUEST | Validation Birthdate |
| false | `30046` | BAD_REQUEST | Validation GenderCode |
| false | `30115` | NOT_FOUND | No student found for those search criteria |
| false | `30401` | NOT_ACCEPTABLE | Mutation détectée (NISS remplacé) |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30502` | INTERNAL_SERVER_ERROR | Erreur de l'appel BCED (voir l'observation ci-dessous) |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Workflows (diagrammes du manuel 2.1.9, §3.4.2.1)
- **Par NISS** : recherche DB SEPS ; si présent, retour des données ETAB et RN/BCSS ; sinon **appel ALIM** (BCSS) avec le NISS, avec inscription aux mutations ; si un nouveau NISS est signalé, message de **mutation de NISS** ; si rien, « non trouvé » ; sinon retour de la version RN/BCSS.
- **Par nom** : recherche DB SEPS sur nom de recherche/DN/sexe (puis recherche **Phonex ETNIC** si rien) ; avec `forceRnFlag`, recherche **BCED par nom** (`SearchByName`, subset `getPerson`). Plusieurs résultats : liste ; pour chacun, données RN si elles existent en DB, sinon version établissement.

### Comportements observés en production

- **NISS d'une personne inconnue de SEPS mais connue du RN** (observé en production, 2026-11-24, 20 cas) : `success=true`, `info 200`, et **un `etudiant` sans `cfNum` ni `cfwbDetails`, avec seulement `rnDetails`**. L'exemple de réponse du manuel 2.1.9 (§3.4.2.4.1) a déjà cette forme. Pour une personne connue de SEPS, la réponse porte `cfNum`, `cfwbDetails` et `rnDetails`.
  **Conséquence** : un `etudiant` sans `cfNum` n'est **pas** en SEPS. Il faut l'enregistrer (`enregistrerEtudiant` en mode NISS, spec 10) avant de l'inscrire.
- **Recherche par nom d'une personne introuvable partout** (observé en production, 2026-11-24, trois requêtes) : **erreur `30502`** « Une erreur s'est produite dans le processus, veuillez réessayer plus tard. », et non `30115`. `30502` ne distingue donc pas une panne de la BCED d'une absence de résultat.

### Exemples de requête
```xml
<!-- Par combinaison nom/prénom/date/sexe -->
<v11:rechercherEtudiants xmlns:v11="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1">
  <v11:nom>titi</v11:nom>
  <v11:prenom>toto</v11:prenom>
  <v11:dateNaissance>1982-10-13</v11:dateNaissance>
  <v11:sexe>M</v11:sexe>
</v11:rechercherEtudiants>
```
```xml
<!-- Par NISS (valeur masquée) -->
<v11:rechercherEtudiants xmlns:v11="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1">
  <v11:niss>xxxxxxxxxxx</v11:niss>
</v11:rechercherEtudiants>
```

---

## Écarts avec le manuel 2.1.9 et avec le contrat du catalogue

| Élément | Manuel 2.1.9 | Contrat catalogue 2.1 | Contrat de production (2026-11-24) | Statut |
|---|---|---|---|---|
| `EtudiantType.bisCreated` | absent | absent | `xs:string` [0..1] | nouveau ; décrit par l'exemple du manuel 2.3 |
| `AdresseType.rue`, `codePays` | obligatoires | obligatoires | facultatifs | contrat assoupli, manuel 2.3 inchangé |
| `rnDetails` / `cfwbDetails` | texte au singulier | pluriel | pluriel | le XSD fait foi |
| `forceRnFlag` | `forceRn` | `forceRnFlag` en tête | idem | le XSD fait foi |
| `rnValidityEndDate`, `codeEtatCivil` | dans les exemples | absents | absents | hors contrat, non observés |
| TLS | 1.0 | - | - | 1.2 et 1.3 (manuels 2.3/2.4) |
| Endpoints | `services-web(.tq).etnic.be` | `ws-tq.etnic.be` | `ws.etnic.be:443` | `ws(-tq).etnic.be` (manuels 2.3/2.4) |

---

## Mapping pyetnic

Fonctions publiques de `pyetnic.seps` (stables, `docs/PUBLIC_API_SURFACE.md`) :

```python
def lire_etudiant(cf_num: str, from_date: str | None = None) -> Etudiant | None: ...
def rechercher_etudiants(niss: str | None = None, nom: str | None = None,
                         prenom: str | None = None, date_naissance: str | None = None,
                         sexe: str | None = None,
                         force_rn_flag: bool | None = None) -> list[Etudiant]: ...
```

- `rechercher_etudiants` envoie le choix A si `niss` est donné, sinon le choix B (`nom` requis, `ValueError` sinon) ; `force_rn_flag` devient `forceRnFlag`.
- **Résultat vide** : `lire_etudiant` rend `None` et `rechercher_etudiants` rend `[]` sur `30110` et `30115`.
- **Refus** : tout autre `success=false`, que le code arrive en `error` ou en `warning`, lève une sous-classe de `SepsEtnicError` (`docs/SPEC.md`, table des erreurs) : `NissMutationError` pour `30401` (avec `ancien_niss`, `nouveau_niss` lu dans la description), `TropDeResultatsError` pour `30501` / `30503`, `SepsValidationError` pour `30042`, `SepsAuthError` pour `30550`. `30502` lève la classe de base `SepsEtnicError` : il couvre aussi les vraies pannes de la BCED, il n'est pas transformé en liste vide.
- **Codes de validation** : `30043` à `30048` de ce service (nom, prénom, date de naissance, sexe, `cfNum`, `fromDate`) lèvent `SepsValidationError`, comme les autres codes BAD_REQUEST (absents de la liste jusqu'à #24, ils levaient la classe de base).

Modèles (dataclasses, noms des champs = noms XSD) :

| Classe | Champs |
|---|---|
| `Etudiant` | `cfNum`, `bisCreated`, `rnDetails`, `cfwbDetails` |
| `EtudiantDetails` | `niss`, `nom`, `prenom`, `autrePrenom` (liste), `sexe`, `naissance`, `deces`, `adresse`, `codeNationalite` |
| `SepsNaissance` | `date`, `codePays`, `localite` |
| `SepsAdresse` | `rue`, `codePostal`, `codePays`, `numero`, `boite`, `extension`, `localite`, `localiteExtension` |
| `SepsLocalite` | `code`, `description` |
| `SepsDeces` | `date` |

- Un `Etudiant` dont `cfNum` vaut `None` vient du seul RN (voir les comportements observés) : il faut l'enregistrer avant de l'inscrire.
- Codes pays, communes et nationalités : pyetnic ne les valide pas ; les référentiels sont décrits en **spec 15**.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSRechercheEtudiantsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `etudiant_v1.xsd` | `EtudiantType` (avec `bisCreated`) | = spec 10 (md5 identique) |
| `etudiantDetails_v1.xsd` | `EtudiantDetailsType` et sous-types | = spec 10 (md5 identique) |
| `cfNum_v1.xsd` | `cfNumType` | toute la famille SEPS |
| `external_v1.xsd` | `AbstractExternalResponseType` | toute la famille SEPS |
| `ResponseStatus_v3.xsd` | `success`/`messages` | toute la famille SEPS |
| `requestId_v1.xsd` | header `requestId` | toute la famille SEPS |
