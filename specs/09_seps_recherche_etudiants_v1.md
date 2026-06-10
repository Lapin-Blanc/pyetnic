# SEPS — Recherche Étudiants v1 (release 2.1.9)

> Spécification technique et fonctionnelle complète
> Sources : WSDL `SEPSRechercheEtudiantsService_external_v1.wsdl` + XSD + PDF « Services Web SEPS — Manuel d'utilisation » v2.1.9 (18/01/2023)
> Date d'analyse : 2026-06-09 (session 7)

---

## ⚠️ Famille SEPS — préambule (à lire une fois pour les specs 09 → 13)

**SEPS** = base centrale de données de la **promotion sociale / Enseignement pour Adultes (AGE)**.
Ces services sont une **famille distincte des services EPROM** (specs 01-06) :

| Aspect | EPROM (01-06) | **SEPS (09-13)** |
|---|---|---|
| Domaine | Organisation des formations (école/PO) | **Étudiants & inscriptions** (signalétique, UE) |
| Namespace racine | `enseignement.cfwb.be/types/...` + `services-web.etnic.be/eprom/...` | **`ws.etnic.be/seps/...`** + `enseignement.cfwb.be/types/seps/...` |
| Authentification | WS-Security **UsernameToken** | **WS-Security certificat X.509** (cf. §2.1 manuel) |
| SOAP | 1.1 ou 1.2 | **SOAP 1.1 uniquement** |
| Bloc retour | `AbstractExternalResponseType` (`common/v1`) | `AbstractExternalResponseType` (**`external/v1`** — autre namespace, même forme) |
| Identité métier | `etabId`/`numAdmFormation`/`numOrganisation` | **`cfNum`** (numéro Communauté française de l'étudiant) |

### Plateforme & sécurité (manuel §2.1)
- Canal SSL **TLS** (le manuel mentionne « TLS 1.0 » — à confirmer, probablement relevé à 1.2 côté plateforme).
- **Authentification WS-Security X.509** (BinarySecurityToken + Signature dans l'entête). Voir exemples de réponses signées dans le manuel (§3.3.1.6).
- Échange **synchrone**, **SOAP 1.1**, document/literal.
- Réf. plateforme : « Plateforme Services Web ETNIC — Spécifications techniques » (catalogue SOA ETNIC).

### Identifiant de requête (manuel §2.3) — identique EPROM
Header SOAP `requestId` (UUID), **facultatif en requête**. Si absent, l'ETNIC en génère un.
- WSDL : `wsdl:required="false"` en entrée ; **`true` en sortie** pour Recherche Étudiants, Recherche Inscriptions et Notifications (le serveur renvoie toujours un `requestId`).
- À toujours conserver pour le support ETNIC.

### Erreurs techniques — SOAP Fault (manuel §2.4) ≠ erreurs métier
Deux niveaux d'erreur **distincts** :
1. **SOAP Fault** (erreur technique, transport) : `faultcode` / `faultstring` / `faultactor` / `detail{messageId, code, description fr+en}`.
2. **Erreur métier** : HTTP 200 + corps `success=false` + `messages/error|warning` (code + description). C'est le cas général documenté par opération.

**Codes SOAP Fault les plus courants (communs à toute la famille SEPS)** :

| Code | Description |
|---|---|
| `SECU-0102` | Authentification échouée : aucune info de sécurité reçue (WSS X509 ou UsernameToken) |
| `SECU-0103` | WSS UsernameToken : utilisateur/mot de passe invalide |
| `SECU-0104` | WSS X509 : échec auprès du LDAP |
| `SECU-1101` | Autorisation : profils de sécurité requis absents |
| `ROUT-1001` | Erreur technique du fournisseur de service |
| `VALI-0100` | Validation XSD du message de **requête** échouée |
| `VALI-1100` | Validation XSD du message de **réponse** échouée |

### Bloc retour — `AbstractExternalResponseType` (`external_v1.xsd`)
```
AbstractExternalResponseType (abstract, ns http://etnic.be/types/technical/external/v1)
├── success  : boolean       [obligatoire]   (ns ResponseStatus/v3)
└── messages : messagesType  [0..1]          (ns ResponseStatus/v3)
    ├── error   : MessageType [0..*]   → code (max 10), description [0..1], zone [0..1]
    ├── warning : MessageType [0..*]
    └── info    : MessageType [0..*]
```
> ⚠️ Le code métier de **succès** est porté par `messages/info` (ex. `200`, `201`) ; `success=true`.
> Le code d'« absence de résultat » est souvent porté par `messages/warning` **avec `success=false`** (ex. `30115`, `30103`, `30105`).
> Les exemples de réponses contiennent aussi les namespaces plateforme `addressing/v2` et `authorisation/v2` (wrappers), absents des XSD du contrat.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | SEPS (Enseignement pour Adultes / Promotion sociale) |
| Service | Recherche Étudiants |
| Version contrat | external **v1** |
| Version release / manuel | 2.1.9 (rev 18/01/2023) |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 |
| Sécurité | WS-Security **certificat X.509** |
| WSDL namespace | `http://ws.etnic.be/seps/rechercheEtudiants/v1` |
| Messages namespace | `http://ws.etnic.be/seps/rechercheEtudiants/messages/v1` |
| Binding | `SEPSRechercheEtudiantsV1ExternalBinding` (document/literal) |
| Service WSDL | `service_seps_rechercheEtudiants_external_v1` |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL (`soap:address`) | `https://ws-tq.etnic.be/seps/rechercheEtudiants/v1` |
| TQ | PDF manuel §2.2 | `https://services-web.tq.etnic.be/seps/rechercheEtudiants/v1` |
| PROD | PDF manuel §2.2 | `https://services-web.etnic.be/seps/rechercheEtudiants/v1` |

> ⚠️ **Divergence host WSDL ↔ PDF** : le WSDL pointe `ws-tq.etnic.be`, le PDF documente `services-web(.tq).etnic.be`. Les deux familles d'alias existent côté ETNIC (déjà observé pour EPROM). **Recommandation** : rendre l'URL configurable, utiliser `services-web…` (forme documentée et porteuse du certificat serveur `services-web.test.etnic.be` vu dans les exemples signés).

---

## Description fonctionnelle

Service de **recherche d'un étudiant** (signalétique d'identification) dans la DB SEPS et, à défaut,
dans les **sources authentiques** (BCSS/RN via la BCED). Deux opérations :

1. **lireEtudiant** — recherche **par `cfNum`** (numéro Communauté française), à une date donnée.
2. **rechercherEtudiants** — recherche **par NISS** (privilégiée) **ou** par combinaison **nom / prénom / date de naissance / sexe**.

La DB SEPS contient, pour chaque étudiant, **deux versions** de la signalétique :
- **`rnDetails`** : version issue du **Registre National / BCSS** (si elle existe) ;
- **`cfwbDetails`** : version communiquée par l'**établissement** (applications locales ou SIEL Web), complétable avec les données BCSS.

> Vocabulaire : **BCSS** = Banque Carrefour de la Sécurité Sociale ; **BCED** = Banque Carrefour d'Échange de Données (canal d'accès aux sources authentiques) ; **RN** = Registre National. L'appel aux sources authentiques est nommé « **appel ALIM** » dans le manuel.

---

## Types communs SEPS — signalétique étudiant

> Définis dans `cfNum_v1.xsd`, `etudiant_v1.xsd`, `etudiantDetails_v1.xsd`. **Partagés avec la spec 10** (Enregistrer Étudiant). Voir aussi `00_REGISTRE.md`.

### cfNumType (`cfNum_v1.xsd`, ns `…/types/seps/cfNum/v1`)
Identifiant **unique de l'étudiant** dans DB SEPS (« numéro de communauté française »). Deux parties : un entier + un code de contrôle.
- Type : `string`, pattern `[0-9]{1,10}\-[0-9]{2}` — ex. `8501889-33`.

### EtudiantType (`etudiant_v1.xsd`, ns `…/types/seps/etudiant/v1`)
```
EtudiantType
├── cfNum       : cfNumType            [0..1]
├── rnDetails   : EtudiantDetailsType  [0..1]   (version Registre National / BCSS)
└── cfwbDetails : EtudiantDetailsType  [0..1]   (version établissement)
```
> ⚠️ Le texte courant du PDF nomme ces éléments `rnDetail`/`cfwbDetail` (singulier) ; le **XSD et les diagrammes UML (p.8) + tous les exemples** utilisent **`rnDetails`/`cfwbDetails`** (pluriel). → XSD faisant foi.

### EtudiantDetailsType (`etudiantDetails_v1.xsd`, ns `…/types/seps/etudiantDetails/v1`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `niss` | NISSType | 0..1 | NISS (RN) ou n° registre des étrangers |
| `nom` | NomType (1..80) | 0..1 | Nom |
| `prenom` | PrenomType (0..50) | 0..1 | Prénom (peut être vide) |
| `autrePrenom` | PrenomType | 0..3 | Autres prénoms (jusqu'à 3) |
| `sexe` | SexeType | 0..1 | `M` / `F` / `X` |
| `naissance` | NaissanceType | 0..1 | Date + pays + localité de naissance |
| `deces` | DecesType | 0..1 | Date de décès |
| `adresse` | AdresseType | 0..1 | Adresse de résidence |
| `codeNationalite` | string | 0..1 | Code INS nationalité (= `CO_NATIO_ID` zero-paddé 5, cf. spec 15) |

**NISSType** : `string`, pattern `[0-9]{6}(\-)?[0-9]{3}(\-)?[0-9]{2}` (ex. `99082705172`). Contrôle **mod 97** côté serveur (erreur `30042`/`30040`).
**SexeType** : énumération `M` (masculin) / `F` (féminin) / `X` (autre).
**IncompleteDateType** : `string`, pattern `[1-2][0-9]{3}(\-[0-1][0-9]\-[0-3][0-9])?` — date complète `AAAA-MM-JJ` **ou année seule** `AAAA` (ex. `1970`). Sert aux dates de naissance partiellement connues.

**NaissanceType**
```
NaissanceType
├── date     : IncompleteDateType  [obligatoire]
├── codePays : string              [obligatoire]   code INS pays (5 chiffres, ex. 00150=Belgique ; cf. spec 15)
└── localite : LocaliteType        [0..1]          obligatoire côté back-end
```
> Remarque manuel : pour une naissance **à l'étranger**, le RN ne renvoie que le **nom** de la ville (`localite/description`), pas de code INS.

**AdresseType**
```
AdresseType
├── rue               : string        [obligatoire]
├── numero            : string        [0..1]  (max ~4 car.)
├── boite             : string        [0..1]  (max ~4 car.)
├── extension         : string        [0..1]  (complément, ex. nom de résidence)
├── codePostal        : string        [obligatoire]
├── localite          : LocaliteType  [0..1]  obligatoire côté back-end
├── localiteExtension : string        [0..1]  (lieu-dit…)
└── codePays          : string        [obligatoire]  code INS pays (5 chiffres)
```

**LocaliteType** : `code` [0..1] (code **INS 5 chiffres** si commune/district belge, pattern `[0-9]{5}` — cf. spec 15) + `description` [0..1] (libellé).
**DecesType** : `date` (`xs:date`, obligatoire).

> ⚠️ **Champs de réponse présents HORS XSD** (observés dans les exemples du manuel) — le XSD n'est **pas exhaustif** en sortie :
> - attribut `rnValidityEndDate` (date) sur `rnDetails`/`cfwbDetails` (ex. `rnValidityEndDate="2039-11-27"`) ;
> - élément `codeEtatCivil` dans `cfwbDetails` (ex. `<codeEtatCivil>C12</codeEtatCivil>`).
> → Côté pyetnic : parser tolérant (ne pas planter sur des éléments/attributs non déclarés).

---

## Opération 1 : lireEtudiant

### Description
Recherche un étudiant **à une date donnée** sur base de son `cfNum`. Si la date n'est pas fournie, **date du jour** par défaut. Retourne la version établissement et, si elle existe, la version RN/BCSS.

### Requête — `lireEtudiant` (type `LireEtudiantRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `cfNum` | cfNumType | oui | Identification de l'étudiant |
| `fromDate` | xs:date | non | Date pivot (incluse). Défaut = date du jour |

### Réponse — `lireEtudiantReponse` (type `LireEtudiantReponseType` extends `AbstractExternalResponseType`)
```
response
└── etudiant : EtudiantType   [obligatoire dans le wrapper response, response [0..1]]
```

### Codes de retour (manuel §3.4.1.3.2)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Students found |
| false | `30047` | BAD_REQUEST | Validation `cfNum` |
| false | `30048` | BAD_REQUEST | Validation `fromDate` |
| false | `30110` | NOT_FOUND | Pas trouvé (fin de traitement) |
| false | `30115` | NOT_FOUND | No student found for those search criteria (warning) |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Exemple de requête
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://etnic.be/types/technical/requestId/v1"
                  xmlns:v11="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1">
  <soapenv:Header>
    <v1:requestId>e2128df4-c6b4-4daa-b337-5fc536c33463</v1:requestId>
  </soapenv:Header>
  <soapenv:Body>
    <v11:lireEtudiant>
      <v11:cfNum>8501889-33</v11:cfNum>
      <v11:fromDate>2020-05-01</v11:fromDate>
    </v11:lireEtudiant>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse (simplifié, anonymisé)
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
      <ns5:cfNum>8501889-33</ns5:cfNum>
      <ns5:rnDetails rnValidityEndDate="2039-11-27">
        <ns6:niss>…</ns6:niss>
        <ns6:nom>XXXXXX</ns6:nom><ns6:prenom>xxxx</ns6:prenom><ns6:autrePrenom>Karim</ns6:autrePrenom>
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
        <!-- mêmes champs ; peut contenir codeEtatCivil (ex. C12), hors XSD -->
      </ns5:cfwbDetails>
    </ns3:etudiant>
  </ns3:response>
</ns3:lireEtudiantReponse>
```

---

## Opération 2 : rechercherEtudiants

### Description
Recherche par **NISS** (privilégiée) **ou** par combinaison **nom/prénom/date de naissance/sexe** (uniquement si NISS absent). Si l'étudiant n'est pas en DB SEPS, recherche à la **BCSS** via la BCED (appel ALIM). Depuis la **v1.0.7**, un flag `forceRn` permet de **forcer** la recherche RN lors d'une recherche par nom (recherche SEPS préalable malgré tout conseillée).

### Requête — `rechercherEtudiants` (type `RechercherEtudiantsRequeteType`)

Structure **`xs:choice`** :
```
rechercherEtudiants
├── (choix A) niss : NISSType                       [obligatoire]
└── (choix B) séquence :
    ├── forceRnFlag   : boolean             [0..1]   (XSD ; PDF/exemples = "forceRn", défaut false depuis V1.0.7)
    ├── nom           : NomType             [obligatoire]
    ├── prenom        : PrenomType          [0..1]
    ├── dateNaissance : IncompleteDateType  [0..1]   (AAAA-MM-JJ ou AAAA)
    └── sexe          : SexeType            [0..1]
```
> ⚠️ **Divergences** : XSD `forceRnFlag` vs PDF `forceRn` ; le XSD place `forceRnFlag` **en tête** de la séquence (avant `nom`). Respecter l'ordre XSD à la sérialisation.

### Réponse — `rechercherEtudiantsReponse` (type `RechercherEtudiantsReponseType`)
```
response
└── etudiant : EtudiantType   [0..*]   (liste — recherche par nom peut renvoyer plusieurs résultats)
```

### Codes de retour (manuel §3.4.2.3.2)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Students found |
| false | `30042` | BAD_REQUEST | Validation SSIN — ex. « Invalid national number ! (incorrect mod 97) » |
| false | `30043` | BAD_REQUEST | Validation LastName |
| false | `30044` | BAD_REQUEST | Validation FirstName |
| false | `30045` | BAD_REQUEST | Validation Birthdate |
| false | `30046` | BAD_REQUEST | Validation GenderCode |
| false | `30115` | NOT_FOUND | No student found for those search criteria |
| false | `30401` | NOT_ACCEPTABLE | Mutation détectée (NISS muté) |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30502` | INTERNAL_SERVER_ERROR | Erreur de l'appel BCED |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Workflows (diagrammes manuel §3.4.2)
- **Par NISS** : recherche DB SEPS → si présent, retour ; sinon **appel ALIM** (BCSS) avec NISS → si NISS nouveau, retour avec **mutation de NISS** ; si rien, « non trouvé ».
- **Par nom** : recherche DB SEPS sur nom_rech/DN/sexe (+ recherche **Phonex ETNIC** si rien) ; si `forceRn`, lance la recherche **BCED par nom** (subset `getPerson` / `SearchByName`). Plusieurs résultats → liste ; pour chacun, fusion données RN/BCSS + établissement.

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
<!-- Par NISS -->
<v11:rechercherEtudiants xmlns:v11="http://ws.etnic.be/seps/rechercheEtudiants/messages/v1">
  <v11:niss>99082705172</v11:niss>
</v11:rechercherEtudiants>
```

---

## Vérification croisée UML / XSD / PDF

| Élément | XSD | PDF texte | UML (p.8) | Statut |
|---|---|---|---|---|
| `EtudiantType` (cfNum, rnDetails, cfwbDetails) | ✓ | `rnDetail`/`cfwbDetail` (singulier) | `rnDetails`/`cfwbDetails` | ⚠️ nom : XSD+UML pluriel font foi |
| `EtudiantDetailsType` 9 champs | ✓ | ✓ | ✓ | ✅ conforme |
| `rechercherEtudiants` choice niss / (nom…) | ✓ | ✓ | ✓ | ✅ ; `forceRnFlag` vs `forceRn` ⚠️ |
| `rnValidityEndDate` (attribut), `codeEtatCivil` | ✗ absent | présents en exemple | — | ⚠️ réponse HORS contrat XSD |
| Réponse `lireEtudiant` = 1 ; `rechercherEtudiants` = liste | ✓ | ✓ | — | ✅ |

---

## Mapping pyetnic

```python
class SepsRechercheEtudiantsService:
    """SEPS Recherche Étudiants v1 (release 2.1.9) — auth X.509."""
    WSDL = "SEPSRechercheEtudiantsService_external_v1.wsdl"
    ENDPOINT_TQ   = "https://services-web.tq.etnic.be/seps/rechercheEtudiants/v1"
    ENDPOINT_PROD = "https://services-web.etnic.be/seps/rechercheEtudiants/v1"

    def lire_etudiant(self, cf_num: str, from_date: date | None = None) -> Etudiant: ...
    def rechercher_etudiants(self, *, niss: str | None = None,
                             nom: str | None = None, prenom: str | None = None,
                             date_naissance: str | None = None, sexe: str | None = None,
                             force_rn: bool = False) -> list[Etudiant]: ...
```
```python
@dataclass
class EtudiantDetails:
    niss: str | None = None
    nom: str | None = None
    prenom: str | None = None
    autre_prenom: list[str] = field(default_factory=list)   # max 3
    sexe: str | None = None                                  # M/F/X
    naissance: Naissance | None = None
    deces: date | None = None
    adresse: Adresse | None = None
    code_nationalite: str | None = None                      # INS 5 chiffres
    # tolérer en lecture : rn_validity_end_date (attribut), code_etat_civil (hors XSD)

@dataclass
class Etudiant:
    cf_num: str | None = None
    rn_details: EtudiantDetails | None = None     # version Registre National / BCSS
    cfwb_details: EtudiantDetails | None = None   # version établissement
```
- **Exceptions typées par (service, code)** — un même code change de sens selon le service (ex. `30042` = « Validation SSIN » ici, mais « pas d'EtudiantDetail fourni » à l'enregistrement, spec 10).
- Parser **tolérant** aux champs hors XSD (`rnValidityEndDate`, `codeEtatCivil`).
- Codes pays/communes/nationalités : valider/résoudre via les référentiels de la **spec 15**.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSRechercheEtudiantsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `etudiant_v1.xsd` | `EtudiantType` | = spec 10 (md5 identique) |
| `etudiantDetails_v1.xsd` | `EtudiantDetailsType` + sous-types | = spec 10 (md5 identique) |
| `cfNum_v1.xsd` | `cfNumType` | toute la famille SEPS |
| `external_v1.xsd` | `AbstractExternalResponseType` | toute la famille SEPS |
| `ResponseStatus_v3.xsd` | `success`/`messages` | = EPROM (md5 identique) |
| `requestId_v1.xsd` | header `requestId` | = EPROM (md5 identique) |
