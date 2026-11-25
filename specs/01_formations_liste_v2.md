# EPROM — Formations Liste v2.0

> Spécification technique et fonctionnelle complète
> Sources : contrat embarqué dans `pyetnic/resources/EPROM_Formations_Liste_2.0/` (WSDL `EpromFormationsListeService_external_v2.wsdl` + 10 XSD), identique au WSDL servi par la passerelle et à l'archive du catalogue SOA (relevé du 2026-11-24 ; la passerelle ne sert pas les XSD, importés en relatif) + PDF Manuel d'utilisation rev2.0 (01-05-2023, édité le 10-05-2023, 18 pages, `ETNIC_EpromFormationsListe_v2.0.0_Manuel_d_utilisation_rev2.0.pdf`) + observations datées en production et sur TQ.
> Le contrat prime sur le manuel pour les types et les cardinalités.
> Date d'analyse : 2026-04-14 ; revue contre le manuel et le contrat le 2026-11-24

---

## Métadonnées

| Propriété | Valeur | Source |
|---|---|---|
| Produit | EPROM | manuel rev 2.0, page de garde |
| Service | Formations Liste | manuel rev 2.0, page de garde |
| Version service | 2.0.0 | manuel rev 2.0, page de garde |
| Révision document | 2.0 (01-05-2023) | manuel rev 2.0, historique |
| Domaine | Enseignement - Promotion sociale | manuel rev 2.0, objectifs du document |
| Type d'échange | Synchrone | manuel rev 2.0, §2.1 |
| Format messages | SOAP 1.1 | manuel rev 2.0, §2.2 ; contrat : binding `http://schemas.xmlsoap.org/wsdl/soap/` seul |
| Sécurité | WS-Security : certificat X.509 ou login / mot de passe ; pyetnic envoie un UsernameToken | manuel rev 2.0, §2.1 ; code (`soap_client.py`) |
| Transport | TLS 1.0 ou TLS 1.2 | manuel rev 2.0, §2.1 |
| WSDL namespace | `http://services-web.etnic.be/eprom/formations/liste/v2` | contrat : `EpromFormationsListeService_external_v2.wsdl` |
| Messages namespace | `http://services-web.etnic.be/eprom/formations/liste/messages/v2` | contrat : `EpromFormationsListeMessages_external_v2.xsd` |
| Binding | `EPROMFormationsListeExternalV2Binding` (document/literal) | contrat ; manuel rev 2.0, §2.2.1 |
| Binding « Ecole » (déprécié) | `EPROMFormationsListeV2EcoleBinding`, absent du WSDL externe | manuel rev 2.0, §2.2.2 ; contrat |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | contrat (`soap:address` du WSDL) + catalogue SOA | `https://ws-tq.etnic.be/eprom/formations/liste/v2` |
| PROD | catalogue SOA | `https://ws.etnic.be/eprom/formations/liste/v2` |
| TQ | manuel rev 2.0, §2.2.1 | `https://services-web.tq.etnic.be/eprom/formations/liste/v2` |
| PROD | manuel rev 2.0, §2.2.1 | `https://services-web.etnic.be/eprom/formations/liste/v2` |

> pyetnic appelle `ws.etnic.be` / `ws-tq.etnic.be` depuis 0.3.0, certificat TLS vérifié dans les deux
> environnements (lectures vérifiées sur TQ et en production, 2026-11-24). Le manuel ne connaît que
> `services-web(.tq).etnic.be` et demande d'y ajouter le port `11443` pour TLS 1.2 (manuel rev 2.0,
> §2.2) ; pyetnic appelait ces adresses jusqu'à 0.2, sans pouvoir vérifier le certificat de TQ
> (CHANGELOG, section [Unreleased]). Leur disponibilité actuelle n'a pas été revérifiée (inconnu).
>
> **Endpoint générique « Ecole »** (déprécié ; manuel rev 2.0, §2.2.2 et §3.1.2.2) :
> - TQ : `https://services-web.tq.etnic.be/ecole`
> - PROD : `https://services-web.etnic.be/ecole`
> - WS-Addressing : Action = `eprom:formationsListeV2?mode=sync`, To = `http://services-web.etnic.be/eprom`

---

## Description fonctionnelle

Le service FormationsListe met à disposition toutes les fonctionnalités de liste
des formations aux utilisateurs gérant les formations de leur établissement (manuel rev 2.0, §3.1.1).

Il expose deux opérations de consultation, sans écriture (manuel rev 2.0, §1.1 ; contrat : deux
opérations) :

1. **ListerFormationsOrganisables** - liste les formations organisables dans l'établissement
   (retourne les formations sans les détails d'organisation)
2. **ListerFormations** - liste les formations organisables dans l'établissement avec,
   pour chaque formation organisée, la liste des organisations et le statut des documents

L'identifiant FASE de l'implantation est facultatif : s'il est omis, la liste couvre
l'ensemble des implantations de l'établissement (manuel rev 2.0, §3.1.1).

---

## Opération 1 : ListerFormationsOrganisables

### SOAP Action
`http://services-web.etnic.be/eprom/formations/liste/v2/ListerFormationsOrganisables` (contrat : WSDL)

### Requête

**Type** : `ListerFormationsOrganisablesRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `anneeScolaire` | AnneeScolaireST (string, `\d{4}-\d{4}`) | oui | Année scolaire (ex: `"2015-2016"`) |
| `etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `implId` | ImplIdST (int) | non | Identifiant FASE de l'implantation |

(contrat : `EpromFormationsListeMessages_external_v2.xsd`, `AnneeScolaire_v1.xsd`,
`Etablissement_v1.xsd` ; manuel rev 2.0, §3.1.3.1)

**Header SOAP** : `requestId`, UUID (contrat : `requestId_v1.xsd`). Optionnel en requête,
**obligatoire en réponse** (contrat : `wsdl:required` du WSDL) ; l'ETNIC en attribue un si la
requête n'en porte pas, à joindre à toute demande de support (manuel rev 2.0, §2.3, endpoint
spécifique EPROM seulement).

### Réponse

**Type** : `ListerFormationsOrganisablesReponseCT` extends `AbstractExternalResponseType`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `success` | boolean | oui | `true` si la requête a abouti |
| `messages` | messagesType | non | Bloc erreurs/warnings/infos |
| `response` | responseType | non | Porte la liste en cas de succès (exemple du manuel, §3.1.3.4) |
| `response/formation` | FormationCT | 1..* | Liste des formations ; le manuel dit « de 0 à plusieurs » (§3.1.3.2), le contrat exige au moins une formation dans `response` |

(contrat : `EpromFormationsListeMessages_external_v2.xsd`, `Formation_v2.xsd`, `Common_v1.xsd`)

**Comportement spécifique** : le champ `organisation` de `FormationCT` est **ignoré**
(manuel rev 2.0, §3.1.3.2). Seuls `numAdmFormation`, `libelleFormation`, `codeFormation` figurent
dans l'exemple de réponse du manuel (§3.1.3.4).

### Exemple de requête XML

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v1="http://services-web.etnic.be/eprom/formations/liste/messages/v2">
  <soapenv:Header/>
  <soapenv:Body>
    <v1:ListerFormationsOrganisables>
      <v1:anneeScolaire>2015-2016</v1:anneeScolaire>
      <v1:etabId>41</v1:etabId>
      <v1:implId>66</v1:implId>
    </v1:ListerFormationsOrganisables>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse XML (succès, simplifié)

```xml
<ListerFormationsOrganisablesReponse
    xmlns="http://services-web.etnic.be/eprom/formations/liste/messages/v2"
    xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:p367="http://enseignement.cfwb.be/types/formation/v2">
  <status:success>true</status:success>
  <response>
    <formation>
      <p367:numAdmFormation>32</p367:numAdmFormation>
      <p367:libelleFormation>EP.INT. CONSEILLER EN COMMUNIC &amp; GESTION RESSOURCES HUMAINES</p367:libelleFormation>
      <p367:codeFormation>961410U35C1</p367:codeFormation>
    </formation>
    <formation>
      <p367:numAdmFormation>43</p367:numAdmFormation>
      <p367:libelleFormation>INTRODUCTION A LA SECURITE AU TRAVAIL</p367:libelleFormation>
      <p367:codeFormation>761001U31C1</p367:codeFormation>
    </formation>
  </response>
</ListerFormationsOrganisablesReponse>
```

> Valeurs de l'exemple du manuel (§3.1.3.4), espaces de noms du contrat. Les exemples du manuel
> (§3.1.3.3 à §3.1.4.4) portent ceux de la version 1 du service (`.../liste/messages/v1`,
> `.../types/formation/v1`) et leurs réponses l'en-tête WS-Addressing
> `eprom:formationsListeV1?mode=sync` : ils ont été capturés sur l'endpoint « Ecole » de la v1.

---

## Opération 2 : ListerFormations

### SOAP Action
`http://services-web.etnic.be/eprom/formations/liste/v2/ListerFormations` (contrat : WSDL)

### Requête

**Type** : `ListerFormationsRequeteCT` - structure identique à ListerFormationsOrganisables
(contrat : `EpromFormationsListeMessages_external_v2.xsd`). Le manuel (§3.1.4.1 et §3.1.4.2)
nomme par erreur la requête et la réponse `ListerFormationsOrganisablesRequeteCT` /
`ListerFormationsOrganisablesReponseCT` et reprend le diagramme de ListerFormationsOrganisables.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `anneeScolaire` | AnneeScolaireST | oui | Année scolaire |
| `etabId` | EtabIdST | oui | Identifiant FASE de l'établissement |
| `implId` | ImplIdST | non | Identifiant FASE de l'implantation |

### Réponse

**Type** : `ListerFormationsReponseCT` extends `AbstractExternalResponseType`

Structure identique à ListerFormationsOrganisables **sauf** :
le champ `organisation` de `FormationCT` est **renseigné** avec la liste complète
des organisations et leurs statuts de documents (manuel rev 2.0, §3.1.4.2).

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `success` | boolean | oui | |
| `messages` | messagesType | non | |
| `response` | responseType | non | |
| `response/formation` | FormationCT | 1..* | Formations avec organisations |
| `response/formation/organisation` | OrganisationApercuCT | 0..* | Organisations avec statuts documents |

(contrat : `EpromFormationsListeMessages_external_v2.xsd`, `Formation_v2.xsd` ; le manuel donne
aussi `formation` « de 0 à plusieurs », §3.1.4.2)

### Détail OrganisationApercuCT (dans ce contexte)

(contrat : `FormationOrganisation_v2.xsd` ; manuel rev 2.0, §3.1.4.2)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `implId` | ImplIdST | non | Le manuel le dit renvoyé « si la recherche porte sur l'ensemble des implantations de l'établissement » (§3.1.4.2). Renvoyé sur **chaque** organisation quand la requête omet `implId`, **jamais** quand elle le porte (84 organisations sur TQ, 101 en production, année 2025-2026, observé sur TQ et en production, 2026-11-25 ; absent avec `implId` aussi sur TQ le 2026-11-10), comme le manuel le laisse attendre |
| `numOrganisation` | int | oui | Numéro de l'organisation |
| `dateDebutOrganisation` | date | oui | Date début |
| `dateFinOrganisation` | date | oui | Date fin |
| `statutDocumentOrganisation` | StatutCT | non | Statut du Doc A, l'organisation (manuel rev 2.0, §3.1.4.2) |
| `statutDocumentPopulationPeriodes` | StatutCT | non | Le manuel le rattache au Doc 2 (§3.1.4.2) ; il couvre le Document 1 (Population) et le Document 2 (Périodes), voir ci-dessous |
| `statutDocumentDroitsInscription` | StatutCT | non | Statut du Doc 1D, droits d'inscription (manuel rev 2.0, §3.1.4.2 ; service de la spec 06), voir ci-dessous |
| `statutDocumentAttributions` | StatutCT | non | Statut du Doc 3, attributions (manuel rev 2.0, §3.1.4.2) ; absent jusqu'à la première écriture du Doc 3, puis « Encodé école » (observé en production sur 2025-2026, spec 05) |

> **`statutDocumentPopulationPeriodes`** (observé en production, puis testé sur TQ le 2026-11-10) :
> - absent (`None` dans pyetnic) tant que le Doc 2 n'a pas été écrit : un Doc 1 encodé seul, non
>   validé, le laisse absent (observé en production le 2026-09-18, testé sur TQ), et la population
>   validée (`swAppPopD1` vrai, `swAppD1` faux) aussi (testé sur TQ, 2026-11-10) ;
> - « Encodé école » dès la **première écriture du Doc 2** (`ModifierDocument2`), avec `dateStatut`
>   au jour de cette écriture, tant que `swAppD2` est faux (testé sur TQ, 2026-11-10) ;
> - « Approuvé » quand `swAppD1` et `swAppD2` sont vrais (observé en production, date non relevée).
>
> **`statutDocumentDroitsInscription`** : absent pour toutes les organisations 2026-2027 de
> l'établissement, « Approuvé » pour toutes celles de 2025-2026 et de 2024-2025 (observé en
> production, 2026-11-24) ; il apparaît en « Encodé école » à la première écriture du Doc 1D et le
> reste après l'approbation de la population par l'école (testé sur TQ, 2026-11-24, spec 06).
>
> **`dateStatut`** : « date de la dernière màj du statut » (manuel rev 2.0, §3.1.4.2) ; elle date
> l'entrée dans le statut, pas la dernière modification ; c'est le `tsMaj` de chaque document qui date la
> dernière écriture (observé une fois, 2026-09-18).
>
> **Présence dans la liste** : une organisation créée y apparaît aussitôt (observé en production,
> 2026-06-11) ; une organisation supprimée en disparaît sans trace (observé en production,
> 2026-09-30, spec 02).

### Exemple de réponse XML (succès, simplifié)

```xml
<ListerFormationsReponse
    xmlns="http://services-web.etnic.be/eprom/formations/liste/messages/v2"
    xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:p367="http://enseignement.cfwb.be/types/formation/v2"
    xmlns:p237="http://enseignement.cfwb.be/types/formation/organisation/v2">
  <status:success>true</status:success>
  <response>
    <formation>
      <p367:numAdmFormation>43</p367:numAdmFormation>
      <p367:libelleFormation>INTRODUCTION A LA SECURITE AU TRAVAIL</p367:libelleFormation>
      <p367:codeFormation>761001U31C1</p367:codeFormation>
      <p367:organisation>
        <p237:numOrganisation>1</p237:numOrganisation>
        <p237:dateDebutOrganisation>2016-02-09</p237:dateDebutOrganisation>
        <p237:dateFinOrganisation>2016-03-09</p237:dateFinOrganisation>
        <p237:statutDocumentOrganisation>
          <p237:statut>Approuvé</p237:statut>
          <p237:dateStatut>2016-02-24</p237:dateStatut>
        </p237:statutDocumentOrganisation>
        <p237:statutDocumentPopulationPeriodes>
          <p237:statut>Approuvé</p237:statut>
          <p237:dateStatut>2016-02-23</p237:dateStatut>
        </p237:statutDocumentPopulationPeriodes>
        <p237:statutDocumentDroitsInscription>
          <p237:statut>Approuvé</p237:statut>
          <p237:dateStatut>2016-02-17</p237:dateStatut>
        </p237:statutDocumentDroitsInscription>
        <p237:statutDocumentAttributions>
          <p237:statut>Encodé école</p237:statut>
          <p237:dateStatut>2016-02-17</p237:dateStatut>
        </p237:statutDocumentAttributions>
      </p367:organisation>
      <p367:organisation>
        <p237:numOrganisation>2</p237:numOrganisation>
        <p237:dateDebutOrganisation>2016-02-20</p237:dateDebutOrganisation>
        <p237:dateFinOrganisation>2016-02-24</p237:dateFinOrganisation>
        <p237:statutDocumentOrganisation>
          <p237:statut>Encodé école</p237:statut>
          <p237:dateStatut>2016-02-09</p237:dateStatut>
        </p237:statutDocumentOrganisation>
      </p367:organisation>
    </formation>
    <formation>
      <p367:numAdmFormation>44</p367:numAdmFormation>
      <p367:libelleFormation>LEGISLATION EN MATIERE DE SECURITE</p367:libelleFormation>
      <p367:codeFormation>761002U31C1</p367:codeFormation>
    </formation>
  </response>
</ListerFormationsReponse>
```

> Valeurs de l'exemple du manuel (§3.1.4.4, deux premières organisations de la formation 43),
> espaces de noms du contrat (voir la note de l'opération 1).

---

## Codes d'erreur spécifiques

| Success | Code | Description (manuel rev 2.0, §4) | Scénario |
|---|---|---|---|
| `true` | *(aucun)* | Exécution de la requête sans erreur | `response` porte les formations |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | aucune formation pour ces critères (déduit du libellé) |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | identifiants refusés ou compte sans droit sur l'établissement (déduit du libellé) |
| `false` | `00999` | Erreur sql : | erreur interne du serveur (libellé) |
| `false` | `30001` | Numéro d'établissement incorrect | `etabId` inconnu (déduit du libellé) |
| `false` | `30002` | Numéro d'implantation incorrect | `implId` inconnu ou étranger à l'établissement (déduit du libellé) |
| `false` | `30007` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | année mal formée (libellé) ; aussi une année bien formée que le serveur ne connaît pas : `ListerFormations` sur `2030-2031` (testé sur TQ, 2026-11-24) |

---

## Règles métier (manuel rev 2.0 et observations)

1. **Implantation facultative** : si `implId` est omis, la liste retournée concerne
   l'ensemble des implantations de l'établissement (manuel rev 2.0, §3.1.1).

2. **Différence ListerFormationsOrganisables vs ListerFormations** (manuel rev 2.0, §3.1.3.2 et
   §3.1.4.2) :
   - `ListerFormationsOrganisables` : retourne uniquement les 3 champs de base de chaque formation
     (numAdm, libellé, code). Le champ `organisation` est ignoré.
   - `ListerFormations` : retourne les mêmes formations PLUS la liste complète des organisations
     de chaque formation, avec les statuts des 4 documents (Doc A, Doc 2, Doc 1D, Doc 3 selon le
     manuel).

3. **Statuts de documents** : les 4 statuts sont facultatifs (contrat : `FormationOrganisation_v2.xsd`).
   Les trois statuts de documents restent absents tant que le Doc 2, le Doc 1D ou le Doc 3, selon le
   cas, n'a pas été écrit (voir ci-dessus, observé en production et testé sur TQ). Un
   `statutDocumentOrganisation` absent n'est pas documenté (inconnu).

4. **Valeurs de statut** : `"Encodé école"`, `"Encodé PO"`, `"Approuvé"` (manuel rev 2.0, §3.1.4.2) ;
   `statut` est un `xs:string` sans énumération (contrat : `FormationOrganisation_v2.xsd`). Les
   observations consignées ici ne portent que « Encodé école » et « Approuvé ».

5. **RequestId** : UUID optionnel en requête (endpoint EPROM). Si non fourni, l'ETNIC
   en génère un dans la réponse. Doit être communiqué au support ETNIC en cas de problème
   (manuel rev 2.0, §2.3).

---

## Fichiers XSD du contrat

| Fichier | Rôle | Partagé avec d'autres services |
|---|---|---|
| `EpromFormationsListeMessages_external_v2.xsd` | Messages requête/réponse | non (spécifique) |
| `Formation_v2.xsd` | FormationCT, FormationEpsocCT (*) | non : propre à Formations Liste parmi les contrats embarqués |
| `FormationOrganisation_v2.xsd` | OrganisationApercuCT, OrganisationIdCT, StatutCT, FormationOrganisationCT | non : Organisation v8 a son `FormationOrganisation_v8.xsd`, les Documents utilisent `Organisation_v1.xsd` |
| `AnneeScolaire_v1.xsd` | AnneeScolaireST | oui : identique, octet pour octet, à celui des Documents 1, 2 et 3 |
| `Etablissement_v1.xsd` | EtabIdST, ImplIdST, CodeUniteST | oui : idem |
| `ResponseStatus_v3.xsd` | success, messages, MessageType | oui : idem |
| `Common_v1.xsd` | AbstractExternalResponseType | oui : idem |
| `requestId_v1.xsd` | UUIDType | oui : idem |
| `Addressing_v2.xsd` | AddressingCT, référencé seulement par les types internes de `Common_v1.xsd` | oui : idem |
| `Authorisation_v2.xsd` | AuthorisationCT, référencé seulement par `AbstractInternalRequestType` de `Common_v1.xsd` | oui : idem |

(contrat : les 10 XSD de `pyetnic/resources/EPROM_Formations_Liste_2.0/xsd/`, comparés aux autres
contrats embarqués)

> (*) `FormationEpsocCT` est défini dans le XSD mais **non référencé** par les opérations
> de Formations Liste v2. Il ajoute un élément `dateFemeture` (orthographe du contrat ; date,
> optionnel) par rapport à `FormationCT` (contrat : `Formation_v2.xsd`). Aucun contrat embarqué ne
> le référence ; son usage est inconnu.

---

## Mapping pyetnic

| Élément du contrat | pyetnic (`pyetnic.eprom`) |
|---|---|
| `ListerFormationsOrganisables` | `lister_formations_organisables(annee_scolaire=None, etab_id=None, impl_id=None)` -> `FormationsListeResult` |
| `ListerFormations` | `lister_formations(annee_scolaire=None, etab_id=None, impl_id=None)` -> `FormationsListeResult` |
| `FormationCT` | `Formation` (`numAdmFormation`, `libelleFormation`, `codeFormation`, `organisations`) |
| `OrganisationApercuCT` | `OrganisationApercu` (`id`, `dateDebutOrganisation`, `dateFinOrganisation`, les quatre `statutDocument*`) |
| `StatutCT` | `StatutDocument` (`statut`, `dateStatut`) |
| `response` | `FormationsListeResult` (`success`, `formations`, `messages`) : itérable sur `formations`, `len()`, vrai si `success` |

- **Paramètres par défaut** : un argument omis prend `Config.ANNEE_SCOLAIRE`, `Config.ETAB_ID` ou
  `Config.IMPL_ID` (variables `DEFAULT_SCHOOLYEAR`, `DEFAULT_ETABID`, `DEFAULT_IMPLID`) ; la requête
  ne porte `implId` que si l'argument ou `Config.IMPL_ID` est renseigné.
- **`organisations`** : toujours vide pour `lister_formations_organisables`. Pour `lister_formations`,
  chaque `OrganisationApercu.id` est un `OrganisationId` reconstruit (année et établissement de la
  requête, `numAdmFormation` de la formation, `numOrganisation` de la réponse) qui se passe tel quel
  à `lire_organisation` et aux `lire_document_*`. Son `implId` est celui de la réponse, ou, quand la
  requête le porte (et que la réponse le tait), celui de la requête : la liste ne contient alors que
  cette implantation (#51). Il n'est `None` que si ni l'un ni l'autre ne le donne. Un statut absent
  vaut `None`.
- **Erreurs** : depuis 0.3.0, un refus lève la sous-classe d'`EtnicBusinessError` de son code
  (`pyetnic.exceptions`) : `00009` -> `EtnicNotFoundError` ; `30001`, `30002`, `30007` ->
  `EtnicValidationError` ; `00025`, `00999` -> `EtnicBusinessError`. Un échec de transport lève
  `EtnicTransportError` (alias `SoapError`). Hors du mode permissif, un résultat rendu a donc
  toujours `success` vrai.
- **Mode permissif** (`permissive_errors()` ou `Config.RAISE_ON_ERROR = False`, déprécié, retiré en
  1.0) : un refus ou un échec de transport rend `FormationsListeResult(success=False, formations=[],
  messages=[...])`, qui s'itère comme une liste vide : tester `success`.
- Symboles stables (`docs/PUBLIC_API_SURFACE.md`).
