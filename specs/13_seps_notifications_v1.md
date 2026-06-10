# SEPS — Notifications v1 (release 1.0.8)

> Spécification technique et fonctionnelle complète
> Sources : WSDL `SEPSNotificationsService_external_v1.wsdl` + `notification_v1.xsd` + PDF « Services Web SEPS » v2.1.9, §3.3
> Date d'analyse : 2026-06-09 (session 7)
> **Préambule famille SEPS, X.509, SOAP Fault, bloc retour, `cfNumType`** : voir **spec 09**.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Notifications (modifications de signalétique étudiant) |
| Version contrat / release | external **v1** / **1.0.8** *(les autres services SEPS sont en 2.1.9)* |
| Sécurité | WS-Security **X.509** · SOAP 1.1 · synchrone |
| WSDL namespace | `http://ws.etnic.be/seps/notifications/v1` |
| Messages namespace | `http://ws.etnic.be/seps/notifications/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/notification/v1` |
| Binding | `SEPSNotificationsV1ExternalBinding` (document/literal) |
| Opérations | **1** : `lireNotifications` |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/seps/notifications/v1` |
| TQ / PROD | PDF §2.2 | `https://services-web(.tq).etnic.be/seps/notifications/v1` |

> `requestId` en sortie : `wsdl:required="true"`.

### Contrôle d'accès (manuel §3.3.1.1)
- Profil **support** : non limité.
- Profil **établissement** : limité aux notifications de l'établissement.
- Profil **PO** : limité aux établissements du PO.

---

## Description fonctionnelle

Notifie les **modifications de signalétique** survenues sur les étudiants inscrits dans un établissement, **depuis une date donnée (incluse)**. Permet aux applications locales de **se resynchroniser** avec la DB SEPS.

**Workflow type (manuel §3.2.2 — mise à jour des DB locales)** :
1. appeler `lireNotifications(etabId, dateDebut = date de dernière synchro locale)` ;
2. pour chaque notification reçue, appeler `lireEtudiant(cfNum, fromDate = date de la notification)` (spec 09) pour récupérer la signalétique à jour.

---

## Requête — `lireNotifications` (type `LireNotificationsRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `etabId` | xs:string | oui | Identifiant FASE de l'établissement |
| `dateDebut` | xs:date | oui | Date pivot (incluse) |

> ⚠️ `etabId` est typé **`xs:string`** ici (alors qu'il est `xs:integer` dans les services Inscription). Conserver une chaîne numérique.

---

## Réponse — `lireNotificationsReponse` (type `LireNotificationsReponseType`)
```
response
└── notification : NotificationType   [0..*]   (liste)
```

### NotificationType (`notification_v1.xsd`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `id` | xs:unsignedLong | oblig. | Id de la notification (séquence) |
| `cfNum` | cfNumType | oblig. | Étudiant concerné |
| `date` | xs:date | oblig. | Date de la modification |
| `code` | NotificationCodeType | oblig. | Type de modification (2 chiffres) |
| `description` | NotificationDescriptionType | 0..1 | Libellé de la modification |

**NotificationCodeType** : `string`, pattern `\d{2}`. Valeurs documentées (manuel §3.3.1.4) :
| Code | Signification | Description (enum XSD) |
|---|---|---|
| `02` | Changement de sexe | `MODIF ETUDIANT:CHANGEMENT SEXE` |
| `04` | Changement de nom/prénom | `MODIF ETUDIANT:CHANGEMENT NOM/PRENOM` |
| `05` | Changement d'adresse | `MODIF ETUDIANT:CHANGEMENT ADRESSE` |
| `06` | Changement de nationalité | `MODIF ETUDIANT:CHANGEMENT NATIONALITE` |
| `07` | Changement de NISS | `MODIF ETUDIANT:CHANGEMENT NISS` |
| `08` | Changement de statut | *(aucune valeur correspondante dans l'enum XSD)* |

> ⚠️ **Divergences NotificationCode/Description** :
> - `code` est un **pattern libre `\d{2}`** (pas d'énumération XSD) ; le PDF documente 6 valeurs (02/04/05/06/07/08), **non contiguës** (pas de 01/03).
> - **`NotificationDescriptionType`** (enum XSD) ne contient que **5 valeurs** : SEXE, NOM/PRENOM, ADRESSE, NATIONALITE, NISS. La valeur **« CHANGEMENT STATUT » (code 08) manque** dans l'enum → une notification code `08` pourrait ne pas avoir de `description` mappable. Parser tolérant requis.

### Codes de retour (manuel §3.3.1.5)

| Success | Code | Label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Notifications found |
| false | `30049` | BAD_REQUEST | Validation `etabId` |
| false | `30050` | BAD_REQUEST | Validation `dateFrom` (dateDebut) |
| false | `30105` | NOT_FOUND | Aucune notification pour etabId/dateFrom (warning) |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Exemple de requête
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v11="http://ws.etnic.be/seps/notifications/messages/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v11:lireNotifications>
      <v11:etabId>167</v11:etabId>
      <v11:dateDebut>2020-02-07</v11:dateDebut>
    </v11:lireNotifications>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse (extrait, header X.509 omis)
```xml
<ns3:lireNotificationsReponse
    xmlns:ns3="http://ws.etnic.be/seps/notifications/messages/v1"
    xmlns:ns4="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns5="http://enseignement.cfwb.be/types/seps/notification/v1">
  <ns4:success>true</ns4:success>
  <ns4:messages><ns4:info><ns4:code>200</ns4:code><ns4:description>Notifications found</ns4:description></ns4:info></ns4:messages>
  <ns3:response>
    <ns3:notification>
      <ns5:id>25</ns5:id><ns5:cfNum>8500264-57</ns5:cfNum>
      <ns5:date>2020-02-24</ns5:date>
      <ns5:code>05</ns5:code><ns5:description>MODIF ETUDIANT:CHANGEMENT ADRESSE</ns5:description>
    </ns3:notification>
    <ns3:notification>
      <ns5:id>33</ns5:id><ns5:cfNum>8500264-57</ns5:cfNum>
      <ns5:date>2020-02-24</ns5:date>
      <ns5:code>04</ns5:code><ns5:description>MODIF ETUDIANT:CHANGEMENT NOM/PRENOM</ns5:description>
    </ns3:notification>
  </ns3:response>
</ns3:lireNotificationsReponse>
```
Exemple d'absence (warning) : `success=false` + `warning` code `30105` « No notification found for etabId : 0 and dateFrom : 2020-02-07 ».

---

## Vérification croisée UML / XSD / PDF

| Élément | XSD | PDF | Statut |
|---|---|---|---|
| Requête `etabId` (string) + `dateDebut` (date) | ✓ | ✓ | ✅ |
| `NotificationType` (id, cfNum, date, code, description) | ✓ | ✓ | ✅ |
| `code` | pattern `\d{2}` | 6 valeurs (02-08) | ⚠️ pattern libre ; pas d'enum |
| `description` enum | 5 valeurs | 6 (dont « STATUT ») | ⚠️ « STATUT » (08) absent enum |
| Réponse = liste `notification [0..*]` | ✓ | ✓ | ✅ |

---

## Mapping pyetnic

```python
class SepsNotificationsService:
    """SEPS Notifications v1 (release 1.0.8) — auth X.509."""
    WSDL = "SEPSNotificationsService_external_v1.wsdl"
    ENDPOINT_TQ   = "https://services-web.tq.etnic.be/seps/notifications/v1"
    ENDPOINT_PROD = "https://services-web.etnic.be/seps/notifications/v1"

    def lire(self, etab_id: str, date_debut: date) -> list[Notification]: ...

@dataclass
class Notification:
    id: int
    cf_num: str
    date: date
    code: str                 # "02".."08" (pattern \d{2})
    description: str | None = None
```
- **Pattern de synchro** : stocker la `date` de la dernière notification traitée → prochain `dateDebut`. Pour chaque notif, appeler `lireEtudiant(cf_num, from_date=notif.date)` (spec 09).
- Mapper `code` → enum interne **tolérant** (prévoir le code `08`/« STATUT » non présent dans l'enum XSD).
- Exceptions par **(service, code)** ; `30105` = absence (≈ liste vide), à traiter comme « pas d'erreur fonctionnelle ».

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSNotificationsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `notification_v1.xsd` | `NotificationType` + enums | spécifique |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
