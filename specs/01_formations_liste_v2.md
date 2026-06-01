# EPROM — Formations Liste v2.0

> Spécification technique et fonctionnelle complète
> Sources : WSDL `EpromFormationsListeService_external_v2.wsdl` + PDF Manuel d'utilisation rev2.0 (01-05-2023)
> Date d'analyse : 2026-04-14

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Produit | EPROM |
| Service | Formations Liste |
| Version service | 2.0.0 |
| Domaine | Enseignement - Promotion sociale |
| Type d'échange | Synchrone |
| Format messages | SOAP 1.1 ou SOAP 1.2 |
| Sécurité | WS-Security Username Token Profile |
| WSDL namespace | `http://services-web.etnic.be/eprom/formations/liste/v2` |
| Messages namespace | `http://services-web.etnic.be/eprom/formations/liste/messages/v2` |
| Binding | `EPROMFormationsListeExternalV2Binding` (document/literal) |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/eprom/formations/liste/v2` |
| PROD | page web | `https://ws.etnic.be/eprom/formations/liste/v2` |
| TQ | PDF (TLS 1.2) | `https://services-web.tq.etnic.be:11443/eprom/formations/liste/v2` |
| PROD | PDF (TLS 1.2) | `https://services-web.etnic.be:11443/eprom/formations/liste/v2` |

> **Note** : divergence entre WSDL (`ws-tq.etnic.be`) et PDF (`services-web.tq.etnic.be:11443`).
> Les deux sont fonctionnels. Le PDF rev2.0 a ajouté le port 11443 pour TLS 1.2.

---

## Description fonctionnelle

Le service FormationsListe met à disposition toutes les fonctionnalités de liste
des formations aux utilisateurs gérant les formations de leur établissement.

Il expose deux opérations de consultation (lecture seule, pas de modification) :

1. **ListerFormationsOrganisables** — liste les formations organisables dans l'établissement
   (retourne les formations sans les détails d'organisation)
2. **ListerFormations** — liste les formations organisables dans l'établissement avec,
   pour chaque formation organisée, la liste des organisations et le statut des documents

L'identifiant FASE de l'implantation est facultatif : s'il est omis, la liste couvre
l'ensemble des implantations de l'établissement.

---

## Opération 1 : ListerFormationsOrganisables

### SOAP Action
`http://services-web.etnic.be/eprom/formations/liste/v2/ListerFormationsOrganisables`

### Requête

**Type** : `ListerFormationsOrganisablesRequeteCT`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `anneeScolaire` | AnneeScolaireST (string, `\d{4}-\d{4}`) | oui | Année scolaire (ex: `"2015-2016"`) |
| `etabId` | EtabIdST (int) | oui | Identifiant FASE de l'établissement |
| `implId` | ImplIdST (int) | non | Identifiant FASE de l'implantation |

**Header SOAP** : `requestId` — UUID au format standard. Optionnel en requête,
**obligatoire en réponse** (généré par l'ETNIC si non fourni en entrée).

### Réponse

**Type** : `ListerFormationsOrganisablesReponseCT` extends `AbstractExternalResponseType`

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `success` | boolean | oui | `true` si la requête a abouti |
| `messages` | messagesType | non | Bloc erreurs/warnings/infos |
| `response` | responseType | non | Présent uniquement si `success=true` |
| `response/formation` | FormationCT | 1..* | Liste des formations |

**Comportement spécifique** : le champ `organisation` de `FormationCT` est **ignoré**
(non renvoyé). Seuls `numAdmFormation`, `libelleFormation`, `codeFormation` sont présents.

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
    xmlns="http://services-web.etnic.be/eprom/formations/liste/messages/v1"
    xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3">
  <status:success>true</status:success>
  <response>
    <formation>
      <p367:numAdmFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">32</p367:numAdmFormation>
      <p367:libelleFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">EP.INT.CONSEILER EN COMMUNIC &amp; GESTION RESSOURCES HUMAINES</p367:libelleFormation>
      <p367:codeFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">9614I10U35C1</p367:codeFormation>
    </formation>
    <formation>
      <p367:numAdmFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">43</p367:numAdmFormation>
      <p367:libelleFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">INTRODUCTION A LA SECURITE AU TRAVAIL</p367:libelleFormation>
      <p367:codeFormation xmlns:p367="http://enseignement.cfwb.be/types/formation/v1">761001U31C1</p367:codeFormation>
    </formation>
  </response>
</ListerFormationsOrganisablesReponse>
```

---

## Opération 2 : ListerFormations

### SOAP Action
`http://services-web.etnic.be/eprom/formations/liste/v2/ListerFormations`

### Requête

**Type** : `ListerFormationsRequeteCT` — structure identique à ListerFormationsOrganisables

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `anneeScolaire` | AnneeScolaireST | oui | Année scolaire |
| `etabId` | EtabIdST | oui | Identifiant FASE de l'établissement |
| `implId` | ImplIdST | non | Identifiant FASE de l'implantation |

### Réponse

**Type** : `ListerFormationsReponseCT` extends `AbstractExternalResponseType`

Structure identique à ListerFormationsOrganisables **sauf** :
le champ `organisation` de `FormationCT` est **renseigné** avec la liste complète
des organisations et leurs statuts de documents.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `success` | boolean | oui | |
| `messages` | messagesType | non | |
| `response` | responseType | non | |
| `response/formation` | FormationCT | 1..* | Formations avec organisations |
| `response/formation/organisation` | OrganisationApercuCT | 0..* | Organisations avec statuts documents |

### Détail OrganisationApercuCT (dans ce contexte)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `implId` | ImplIdST | non | Renvoyé si la recherche portait sur une implantation |
| `numOrganisation` | int | oui | Numéro de l'organisation |
| `dateDebutOrganisation` | date | oui | Date début |
| `dateFinOrganisation` | date | oui | Date fin |
| `statutDocumentOrganisation` | StatutCT | non | Statut du document Organisation |
| `statutDocumentPopulationPeriodes` | StatutCT | non | Statut du document Population/Périodes |
| `statutDocumentDroitsInscription` | StatutCT | non | Statut du document Droits d'inscription |
| `statutDocumentAttributions` | StatutCT | non | Statut du document Attributions (Doc 3) |

### Exemple de réponse XML (succès, simplifié)

```xml
<ListerFormationsReponse ...>
  <status:success>true</status:success>
  <response>
    <formation>
      <p367:numAdmFormation>43</p367:numAdmFormation>
      <p367:libelleFormation>INTRODUCTION A LA SECURITE AU TRAVAIL</p367:libelleFormation>
      <p367:codeFormation>761001U31C1</p367:codeFormation>
      <p367:organisation xmlns:p237="http://enseignement.cfwb.be/types/formation/organisation/v2">
        <p237:numOrganisation>1</p237:numOrganisation>
        <p237:dateDebutOrganisation>2015-10-01</p237:dateDebutOrganisation>
        <p237:dateFinOrganisation>2016-01-30</p237:dateFinOrganisation>
        <p237:statutDocumentOrganisation>
          <p237:statut>Approuvé</p237:statut>
          <p237:dateStatut>2015-10-07</p237:dateStatut>
        </p237:statutDocumentOrganisation>
        <p237:statutDocumentPopulationPeriodes>
          <p237:statut>Encodé école</p237:statut>
          <p237:dateStatut>2015-11-19</p237:dateStatut>
        </p237:statutDocumentPopulationPeriodes>
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
  </response>
</ListerFormationsReponse>
```

---

## Codes d'erreur spécifiques

| Success | Code | Description | Scénario |
|---|---|---|---|
| `true` | *(aucun)* | Exécution de la requête sans erreur | Tout OK, `response` présent |
| `false` | `00009` | Aucun enregistrement correspondant à vos critères de recherche | Année/établissement sans formations |
| `false` | `00025` | Problème de sécurité. Veuillez contacter votre administrateur. | Credentials invalides ou droits insuffisants |
| `false` | `00999` | Erreur sql : | Erreur interne ETNIC |
| `false` | `30001` | Numéro d'établissement incorrect | `etabId` inexistant |
| `false` | `30002` | Numéro d'implantation incorrect | `implId` inexistant ou pas lié à l'établissement |
| `false` | `30007` | Paramètre anneeScolaire incorrect (xxxx-xxxx) | Format invalide |

---

## Règles métier (extraites du PDF)

1. **Implantation facultative** : si `implId` est omis, la liste retournée concerne
   l'ensemble des implantations de l'établissement.

2. **Différence ListerFormationsOrganisables vs ListerFormations** :
   - `ListerFormationsOrganisables` : retourne uniquement les 3 champs de base de chaque formation
     (numAdm, libellé, code). Le champ `organisation` est ignoré.
   - `ListerFormations` : retourne les mêmes formations PLUS la liste complète des organisations
     de chaque formation, avec les statuts des 4 types de documents.

3. **Statuts de documents** : les 4 statuts (organisation, population/périodes,
   droits inscription, attributions) peuvent être absents si le document n'a pas encore
   été créé/encodé pour cette organisation.

4. **Valeurs de statut** : `"Encodé école"`, `"Encodé PO"`, `"Approuvé"` — ces valeurs
   sont des strings libres dans le XSD mais contraintes fonctionnellement.

5. **RequestId** : UUID optionnel en requête (endpoint EPROM). Si non fourni, l'ETNIC
   en génère un dans la réponse. Doit être communiqué au support ETNIC en cas de problème.

---

## Fichiers XSD du contrat

| Fichier | Rôle | Partagé avec d'autres services |
|---|---|---|
| `EpromFormationsListeMessages_external_v2.xsd` | Messages requête/réponse | non (spécifique) |
| `Formation_v2.xsd` | FormationCT, FormationEpsocCT (*) | potentiellement |
| `FormationOrganisation_v2.xsd` | OrganisationApercuCT, OrganisationIdCT, StatutCT | oui (Organisation, Documents) |
| `AnneeScolaire_v1.xsd` | AnneeScolaireST | oui (tous services) |
| `Etablissement_v1.xsd` | EtabIdST, ImplIdST, CodeUniteST | oui (tous services) |
| `ResponseStatus_v3.xsd` | success, messages, MessageType | oui (tous services) |
| `Common_v1.xsd` | AbstractExternalResponseType | oui (tous services) |
| `requestId_v1.xsd` | UUIDType | oui (tous services) |
| `Addressing_v2.xsd` | AddressingCT (endpoint Ecole uniquement) | oui (tous services) |
| `Authorisation_v2.xsd` | AuthorisationCT (DEPRECATED) | oui (tous services) |

> (*) `FormationEpsocCT` est défini dans le XSD mais **non référencé** par les opérations
> de Formations Liste v2. Il ajoute un champ `dateFermeture` (date, optionnel) par rapport
> à `FormationCT`. Probablement utilisé par un autre service — à vérifier en session 2.

---

## Mapping vers pyetnic existant

| Élément spec | Code pyetnic actuel | Notes refonte |
|---|---|---|
| `ListerFormationsOrganisables` | `FormationsListeService.lister_formations_organisables()` | OK |
| `ListerFormations` | `FormationsListeService.lister_formations()` | OK |
| `FormationCT` | `Formation` dataclass (models.py) | OK |
| `OrganisationApercuCT` | `OrganisationApercu` dataclass | OK |
| `StatutCT` | `StatutDocument` dataclass | OK |
| Codes d'erreur | catch-all `except Exception` → `FormationsListeResult(False)` | **À refondre** : exceptions typées |
| `FormationsListeResult` | wrapper avec `__bool__`, `__iter__` | **À refondre** : lever exceptions au lieu de wrapper |
