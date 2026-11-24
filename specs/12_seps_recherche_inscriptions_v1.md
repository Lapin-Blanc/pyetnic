# SEPS - Recherche Inscriptions (aux UE) v1

> Spécification technique et fonctionnelle complète
> Sources :
> - **Manuel** : « Services Web SEPS - Recherche inscriptions » **2.4** (version de service 2.4.0 ; historique jusqu'à la rev 16.0 du 18/06/2026, la page de garde indiquant encore 15.0 / 10-06-2026 ; `ETNIC_Services_Web_SIEL_SEPS_RechercheInscriptions_v2.4_Manuel_d_utilisation_rev16.0.pdf`), §2, §3.1 (types), §3.2 (service). Remplace le manuel général 2.1.9 (18/01/2023, §3.7) comme référence.
> - **Contrat** : WSDL + XSD servis par la production (`https://ws.etnic.be/seps/rechercheInscriptions/v1?wsdl`), embarqués dans `pyetnic/resources/SEPS_Recherche_Inscriptions_2.1/` (relevé du 2026-11-24).
> - **Observations de production** (datées dans le texte).
>
> Première analyse : 2026-06-09 (session 7). Refonte : 2026-11-24 (#24).
> **Préambule famille SEPS** (X.509, endpoints, SOAP Fault, bloc retour) : voir **spec 09**. **Énumérations et sous-types d'inscription** : voir **spec 11**.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Recherche des inscriptions aux UE |
| Version contrat / manuel | external **v1** / manuel **2.4** (service 2.4.0) |
| Sécurité | WS-Security X.509 · SOAP 1.1 · synchrone · TLS 1.2 et 1.3 (manuel 2.4, §2.1) |
| WSDL namespace | `http://ws.etnic.be/seps/rechercheInscriptions/v1` |
| Messages namespace | `http://ws.etnic.be/seps/rechercheInscriptions/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/inscription/v1` |
| Binding | `SEPSRechercheInscriptionsV1ExternalBinding` (document/literal) |
| Opérations | **1** : `rechercherInscriptions` |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | manuel 2.4, §2.2 | `https://ws-tq.etnic.be/seps/rechercheInscriptions/v1` |
| PROD | manuel 2.4, §2.2 | `https://ws.etnic.be/seps/rechercheInscriptions/v1` |
| PROD | contrat de production (`soap:address`) | `https://ws.etnic.be:443/seps/rechercheInscriptions/v1` |

> `requestId` en sortie : `wsdl:required="true"` (le serveur renvoie toujours un `requestId`).

### Contrôle d'accès (manuel 2.4, §3.2)
- Profil **support** : non limité.
- Profil(s) **établissement** : recherche limitée aux inscriptions du ou des établissements. **Un seul** profil établissement : `etabId` **facultatif** ; **plusieurs** : `etabId` **obligatoire** (`30052`).
- Profil **PO** : recherche limitée aux établissements du PO.

---

## Description fonctionnelle (manuel 2.4, §3.2.1.1.1)

Recherche des inscriptions aux UE selon des critères. **Au moins un** parmi `anneeScolaire`, `cfNum` et l'identifiant d'UE (`noAdministratif` / `noOrganisation`) doit être fourni (sinon `30036`). L'historique du manuel signale un « changement dans les combinaisons des paramètres » et l'« ajout d'un code erreur » sans les détailler ; le texte du paragraphe est inchangé depuis 2.1.9.

**Date de demande** (`dateRequete`) : « on recherche la **situation la plus récente** (date d'enregistrement ou de modification) **par rapport à cette date** ». Sans date, date du jour.

### `dateRequete` : ce que la production montre

- **Elle rend l'état à cette date**, ce qui permet d'auditer le passé. Observé en production : pour des inscriptions dont `audit.dateCreation` est le 2026-09-30, `dateRequete` 2026-09-29 rend **0** inscription et `dateRequete` 2026-09-30 les rend **toutes** (organisations dont le Doc A n'a été approuvé que le 2026-10-23 ; spec 11).
- **La suppression d'une organisation purge ses inscriptions** : elles n'apparaissent à **aucune** `dateRequete`, même antérieure à la suppression (vérifié le 2026-11-24). L'historique ne survit donc pas à la suppression de l'organisation.

---

## Requête - `rechercherInscriptions` (type `RechercherInscriptionsRequeteType`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `anneeScolaire` | xs:integer | 0..1 | Millésime (ex. 2026). Au moins un des critères requis |
| `etabId` | xs:integer | 0..1 | Id FASE de l'établissement (obligatoire pour un compte multi-profil) |
| `dateRequete` | xs:date | 0..1 | Date pivot ; défaut = aujourd'hui |
| `cfNum` | cfNumType | 0..1 | Identifie l'étudiant |
| `noAdministratif` | ShortType | 0..1 | N° administratif de l'UE |
| `noOrganisation` | ShortType | 0..1 | N° d'organisation de l'UE |

> Le tableau du manuel écrit `dateRequest` (avec un type décalé d'une ligne) ; le diagramme du même manuel et le contrat écrivent `dateRequete` (`date`). Le contrat fait foi.

---

## Réponse - `rechercherInscriptionsReponse` (type `RechercherInscriptionsReponseType`)
```
response [0..1]
└── inscription : InscriptionType   [0..*]   (liste)
```

### InscriptionType - vue complète d'une inscription (sortie)
> Type **de sortie**, plus riche que `InscriptionInputType`. Également renvoyé par `enregistrerInscription` / `modifierInscription` (spec 11).

```
InscriptionType
├── cfNum           : cfNumType            [obligatoire]
├── anneeScolaire   : xs:integer           [0..1]
├── idEtab          : xs:integer           [0..1]
├── idImplantation  : xs:integer           [0..1]
├── dateInscription : DateType (string≤10) [0..1]
├── lieuCours       : LieuCoursType        [0..1]
├── statut          : CodeStatutType       [0..1]   DE / AN
├── ue              : UEType               [0..1]
├── specificite     : SpecificiteDataType  [0..1]   (spec 11)
└── audit           : AuditType            [0..1]   (contrat de production ; absent des manuels)
```

**AuditType** (contrat de production, tous les champs `xs:string` obligatoires dans le bloc). Observé en production (2026-11-24) : chacune des 17 inscriptions d'une organisation lue par `rechercherInscriptions` porte son bloc ; `dateCreation` / `dateModification` au format `AAAA-MM-JJTHH:MM:SS` sans fuseau ; `utilisateurCreation` / `utilisateurModification` portent un identifiant d'utilisateur, le même pour toutes les inscriptions d'un même envoi (sa nature n'est pas documentée) :
```
AuditType
├── dateCreation            : xs:string
├── utilisateurCreation     : xs:string
├── dateModification        : xs:string
└── utilisateurModification : xs:string
```
- Les manuels n'en parlent pas. **Observé en production** : les inscriptions renvoyées par `rechercherInscriptions` portent ce bloc ; `dateCreation` y donne le jour de l'enregistrement côté SEPS. Format exact des dates et contenu des champs utilisateur : non documentés.

**`SpecificiteDataType` ici** : le contrat de production de **ce** service ne porte **ni `regulier3` ni `SanctionType.ajournement1Session`**, que le manuel Recherche Inscriptions 2.4 liste pourtant en sortie (§3.1.4.3) et que le contrat d'`enregistrerInscription` porte (spec 11). Que les réponses de production les contiennent quand même : non observé.

**LieuCoursType** : `codePostal` [0..1] + `ville` [0..1]. Le manuel montre aussi des éléments vides (`<codePostal/>`, `<ville/>`).

**UEType** (sortie, plus riche que `UEInputType`) :
| Champ | Type | Card. | Description |
|---|---|---|---|
| `noAdministratif` | ShortType | oblig. | N° administratif de l'UE |
| `noOrganisation` | ShortType | oblig. | N° d'organisation de l'UE |
| `label` | TextType (≤250) | 0..1 | Libellé de l'UE |
| `code` | TextType | 0..1 | Code du cours, ex. `202600000012340042100001` (fictif) |
| `codeNiveau` | CodeNiveauType | 0..1 | `SI` / `SS` / `SC` / `SL` |
| `nombreSemaine` | ShortType | 0..1 | Nombre de semaines |
| `dateDebut` | DateType | 0..1 | Date de début de l'UE |
| `dateFin` | DateType | 0..1 | Date de fin de l'UE |
| `fse` | IndicateurType | 0..1 | UE FSE ou non (`O` / `N`) |
| `noOrganisationPrecedent` | TextType | 0..1 | N° de l'organisation précédente |
| `activiteDeFormation` | IndicateurType | 0..1 | UE = activité de formation |

> `ue.fse` conditionne l'obligation des champs FSE de `specificite` (spec 11).
> **Composition de `code`** (déduite des trois exemples des manuels, non documentée) : année (4 chiffres) + `idEtab` (10) + `noAdministratif` (5) + `noOrganisation` (5), soit 24 chiffres ; ex. `2026` `0000001234` `00421` `00001`. La version précédente de cette spec donnait 4 chiffres au numéro administratif, ce qui ne tombe pas juste.

### Codes de retour (manuel 2.4, §3.2.1.3.2)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Ok (« Inscriptions found » dans l'exemple) |
| false | `30036` | BAD_REQUEST | Invalid input parameters combination (aucun critère) |
| false | `30037` | BAD_REQUEST | Validation de la date de requête |
| false | `30041` | BAD_REQUEST | Validation `cfNum` |
| false | `30049` | BAD_REQUEST | Validation `etabId` |
| false | `30052` | BAD_REQUEST | Please enter an etabId, you have a multi profile account |
| false | `30103` | NOT_FOUND | No inscription found (en **warning** dans l'exemple : « No inscription found for those criteria ») |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

> Tableau identique à celui du manuel 2.1.9 (§3.7.1.3.2).

### `30103` : ce que la production montre
Observé en production (2026-11-24) : `rechercherInscriptions` répond `30103` (warning) pour « aucune inscription » **que l'UE existe ou non dans SEPS**. Ce service ne permet donc pas de distinguer une UE inconnue de SEPS d'une UE sans inscrit. Pour savoir si SEPS connaît une organisation, seul `enregistrerInscription` répond `30101` (spec 11).

### Exemple de requête (identifiant fictif)
```xml
<v11:rechercherInscriptions xmlns:v11="http://ws.etnic.be/seps/rechercheInscriptions/messages/v1">
  <v11:anneeScolaire>2026</v11:anneeScolaire>
  <v11:etabId>1234</v11:etabId>
</v11:rechercherInscriptions>
```

### Exemple de réponse (extrait, une inscription ; d'après le manuel, identifiants fictifs)
```xml
<ns3:rechercherInscriptionsReponse
    xmlns:ns3="http://ws.etnic.be/seps/rechercheInscriptions/messages/v1"
    xmlns:ns4="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns5="http://enseignement.cfwb.be/types/seps/inscription/v1">
  <ns4:success>true</ns4:success>
  <ns4:messages><ns4:info><ns4:code>200</ns4:code><ns4:description>Inscriptions found</ns4:description></ns4:info></ns4:messages>
  <ns3:response>
    <ns3:inscription>
      <ns5:cfNum>1234567-89</ns5:cfNum>
      <ns5:anneeScolaire>2026</ns5:anneeScolaire>
      <ns5:idEtab>1234</ns5:idEtab><ns5:idImplantation>5678</ns5:idImplantation>
      <ns5:dateInscription>2026-09-15</ns5:dateInscription>
      <ns5:lieuCours><ns5:codePostal>1020</ns5:codePostal><ns5:ville>BRUXELLES</ns5:ville></ns5:lieuCours>
      <ns5:statut>DE</ns5:statut>
      <ns5:ue>
        <ns5:noAdministratif>421</ns5:noAdministratif><ns5:noOrganisation>1</ns5:noOrganisation>
        <ns5:label>PROJET D'ANALYSE ET DE CONCEPTION</ns5:label>
        <ns5:code>202600000012340042100001</ns5:code>
        <ns5:codeNiveau>SC</ns5:codeNiveau><ns5:nombreSemaine>24</ns5:nombreSemaine>
        <ns5:dateDebut>2026-09-21</ns5:dateDebut><ns5:dateFin>2027-02-28</ns5:dateFin>
        <ns5:fse>N</ns5:fse>
      </ns5:ue>
      <ns5:specificite>
        <ns5:regulier1>O</ns5:regulier1><ns5:regulier5>O</ns5:regulier5>
        <ns5:admission><ns5:codeAdmission>AUTRE</ns5:codeAdmission><ns5:valorisationAcquis>C10</ns5:valorisationAcquis></ns5:admission>
      </ns5:specificite>
      <!-- en production : un bloc audit (dateCreation, utilisateurCreation, dateModification, utilisateurModification) -->
    </ns3:inscription>
  </ns3:response>
</ns3:rechercherInscriptionsReponse>
```

---

## Vérification croisée manuel / contrat

| Élément | Contrat de production | Manuel 2.4 | Statut |
|---|---|---|---|
| Requête : 6 critères, au moins 1 requis | ✓ | ✓ (§3.2.1.1.1) | conforme |
| `dateRequete` | `dateRequete` | `dateRequest` (tableau) / `dateRequete` (diagramme) | le contrat fait foi |
| `InscriptionType` | 10 champs (avec `audit`) | 9 champs | `audit` : contrat seulement |
| `SpecificiteDataType.regulier3`, `SanctionType.ajournement1Session` | absents | listés | divergence (ils sont au contrat d'`enregistrerInscription`) |
| `UEType` (11 champs) | ✓ | ✓ | conforme |
| Réponse = liste `inscription [0..*]` | ✓ | ✓ | conforme |

---

## Mapping pyetnic

Fonction publique de `pyetnic.seps`, **stable** depuis #24 (utilisée en production par une application cliente ; `docs/PUBLIC_API_SURFACE.md`) :

```python
def rechercher_inscriptions(annee_scolaire: int | None = None, etab_id: int | None = None,
                            date_requete: str | None = None, cf_num: str | None = None,
                            no_administratif: int | None = None,
                            no_organisation: int | None = None) -> list[Inscription]: ...
```

- Seuls les critères fournis sont envoyés. pyetnic ne vérifie pas la règle « au moins un critère » ni la règle multi-profil : le serveur répond `30036` / `30052`, qui lèvent `SepsValidationError`.
- **Résultat vide** : `[]` sur `30102` et `30103`. Ce `[]` ne dit pas si l'UE existe (voir plus haut).
- **Refus** : tout autre `success=false`, en `error` comme en `warning`, lève une sous-classe de `SepsEtnicError` (`SepsValidationError`, `TropDeResultatsError` pour `30501`, `SepsAuthError` pour `30550`, `SepsUeInconnueError` si le serveur répondait `30100` / `30101`).
- `date_requete` (`AAAA-MM-JJ`) permet de relire l'état d'une date passée, dans la limite de la purge à la suppression d'une organisation.

Modèles (dataclasses, noms des champs = noms XSD) :

| Classe | Champs |
|---|---|
| `Inscription` | `cfNum`, `anneeScolaire`, `idEtab`, `idImplantation`, `dateInscription`, `lieuCours`, `statut`, `ue`, `specificite`, `audit` |
| `SepsAudit` | `dateCreation`, `utilisateurCreation`, `dateModification`, `utilisateurModification` |
| `SepsUE` | `noAdministratif`, `noOrganisation`, `label`, `code`, `codeNiveau`, `nombreSemaine`, `dateDebut`, `dateFin`, `fse`, `noOrganisationPrecedent`, `activiteDeFormation` |
| `SepsLieuCours` | `codePostal`, `ville` |
| `SepsSpecificite` | `regulier1`, `regulier3`, `regulier5`, `droitInscription`, `droitInscriptionSpecifique`, `dureeInoccupation`, `situationMenage`, `enfantACharge`, `difficulteHandicap`, `difficulteAutre`, `admission`, `sanction` |
| `SepsDroitInscription`, `SepsExempteDroitInscription`, `SepsDroitInscriptionSpecifique`, `SepsExempteDroitInscriptionSpec`, `SepsAdmission`, `SepsSanction` | voir spec 11 |

Les mêmes modèles de lecture servent au résultat des écritures (`InscriptionResult.inscription`, spec 11).

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSRechercheInscriptionsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `inscription_v1.xsd` | `InscriptionType` (avec `AuditType`), `UEType`, `LieuCoursType`, énumérations | diffère de la version de la spec 11 : sans `regulier3` ni `ajournement1Session` |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
