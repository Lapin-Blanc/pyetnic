# SEPS - Notifications v1

> Spécification technique et fonctionnelle complète
> Sources :
> - **Manuel** : « Services Web SEPS - Notifications » **2.3** (rev 2.0, 10/06/2026), §2 et §3.1. Remplace le manuel général 2.1.9 (18/01/2023, §3.3) comme référence.
> - **Contrat** : WSDL + XSD du catalogue SOA « SEPS_Notifications_1.0.8 ». Le contrat servi par la production (`https://ws.etnic.be/seps/notifications/v1?wsdl`) lui est **identique**, aux emplacements d'import près (relevé du 2026-11-24). Ce contrat était absent de `pyetnic/resources/` au moment de cette refonte.
> - Workflow : manuels « Enregistrer Étudiants » 2.3 et « Enregistrer Inscriptions » 2.4, §3.2.2.
>
> Première analyse : 2026-06-09 (session 7). Refonte : 2026-11-24 (#24).
> **Préambule famille SEPS** (SOAP Fault, bloc retour, `cfNumType`) : voir **spec 09**.

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Notifications (modifications de signalétique des étudiants) |
| Version contrat / manuel | external **v1** (catalogue 1.0.8) / manuel **2.3** |
| Sécurité | voir « Authentification » ci-dessous · SOAP 1.1 · synchrone · TLS 1.2 et 1.3 (manuel 2.3, §2.1) |
| WSDL namespace | `http://ws.etnic.be/seps/notifications/v1` |
| Messages namespace | `http://ws.etnic.be/seps/notifications/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/notification/v1` |
| Binding | `SEPSNotificationsV1ExternalBinding` (document/literal) |
| Opérations | **1** : `lireNotifications` |

### Authentification

<!-- lot4: authentification à confirmer -->

- **Manuel 2.3, §2.1** : WS-Security avec **certificat X.509**, comme les quatre autres services ; ses exemples de réponse (§3.1.1.6) portent un `BinarySecurityToken` X509v3 et une signature.
- **Page du catalogue SOA** : annonce pour ce service un profil **WS-Security UsernameToken**, et X.509 pour les quatre autres.
- Les deux sources divergent ; à confirmer.

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | manuel 2.3, §2.2 | `https://ws-tq.etnic.be/seps/notifications/v1` |
| PROD | manuel 2.3, §2.2 | `https://ws.etnic.be/seps/notifications/v1` |
| PROD | contrat de production (`soap:address`) | `https://ws.etnic.be:443/seps/notifications/v1` |
| TQ | contrat du catalogue (`soap:address`) | `https://ws-tq.etnic.be/seps/notifications/v1` |

> `requestId` en sortie : `wsdl:required="true"`.

### Contrôle d'accès (manuel 2.3, §3.1.1.1)
- Profil **support** : non limité.
- Profil **établissement** : limité aux notifications de l'établissement.
- Profil **PO** : limité aux notifications des établissements du PO.

---

## Description fonctionnelle

Notifie les **modifications de signalétique** survenues sur les étudiants inscrits dans un établissement, **depuis une date donnée (incluse)** (manuel 2.3, §3.1.1.1). Sert aux applications locales à **se resynchroniser** avec la DB SEPS.

**Workflow de mise à jour des DB locales** (manuels 2.3/2.4, §3.2.2) :
1. appeler `lireNotifications(etabId, dateDebut = date de dernière mise à jour locale)` ;
2. pour chaque notification, appeler `lireEtudiant(cfNum, fromDate = date de la notification)` (spec 09) pour relire la signalétique à jour.

---

## Requête - `lireNotifications` (type `LireNotificationsRequeteType`)

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `etabId` | xs:string | oui | Identifiant FASE de l'établissement |
| `dateDebut` | xs:date | oui | Date pivot (incluse) |

> `etabId` est typé **`xs:string`** ici, alors qu'il est `xs:integer` dans les services d'inscription.

---

## Réponse - `lireNotificationsReponse` (type `LireNotificationsReponseType`)
```
response [0..1]
└── notification : NotificationType   [0..*]   (liste)
```

### NotificationType (`notification_v1.xsd`, manuel 2.3 §3.1.1.4)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `id` | xs:unsignedLong | oblig. | Id de la notification (séquence) |
| `cfNum` | cfNumType | oblig. | Étudiant concerné |
| `date` | xs:date | oblig. | Date de la modification |
| `code` | NotificationCodeType | oblig. | Type de modification (2 chiffres) |
| `description` | NotificationDescriptionType | 0..1 | Libellé de la modification (le texte du manuel la dit « obligatoire », son tableau et le contrat `0..1`) |

**NotificationCodeType** : au contrat, `string` de pattern `\d{2}` (pas d'énumération). Le manuel 2.3 la présente comme une énumération :

| Code | Signification (manuel 2.3) | `description` (énumération du contrat) |
|---|---|---|
| `02` | Changement de sexe | `MODIF ETUDIANT:CHANGEMENT SEXE` |
| `04` | Changement de nom/prénom | `MODIF ETUDIANT:CHANGEMENT NOM/PRENOM` |
| `05` | Changement d'adresse | `MODIF ETUDIANT:CHANGEMENT ADRESSE` |
| `06` | Changement de nationalité | `MODIF ETUDIANT:CHANGEMENT NATIONALITE` |
| `07` | Changement de NISS | `MODIF ETUDIANT:CHANGEMENT NISS` |
| `08` | **Changement de statut** | *aucune valeur dans l'énumération* |

> **Code `08`** : documenté par les manuels (l'historique du 2.1.9 porte déjà « Ajout notification code 08 », le 2.3 l'inscrit dans sa liste), mais l'énumération `NotificationDescriptionType` du contrat, inchangée en production au 2026-11-24, n'a que **5 valeurs**. Une notification `08` ne peut donc pas porter de `description` valide selon le contrat : soit elle arrive sans `description`, soit avec une valeur hors énumération. Non observé. Les codes ne sont pas contigus (pas de `01` ni de `03`).

### Codes de retour (manuel 2.3, §3.1.1.5)

| Success | Code | Error label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Notifications found |
| false | `30049` | BAD_REQUEST | Validation `etabId` |
| false | `30050` | BAD_REQUEST | Validation `dateFrom` (= `dateDebut`) |
| false | `30105` | NOT_FOUND | « No notification found for etabId : XXX and dateFrom : AAAA-MM-DD » (warning) |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Exemple de requête (identifiant fictif)
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v11="http://ws.etnic.be/seps/notifications/messages/v1">
  <soapenv:Header/>
  <soapenv:Body>
    <v11:lireNotifications>
      <v11:etabId>1234</v11:etabId>
      <v11:dateDebut>2026-11-01</v11:dateDebut>
    </v11:lireNotifications>
  </soapenv:Body>
</soapenv:Envelope>
```

### Exemple de réponse (extrait du manuel 2.3 §3.1.1.6.1, header WS-Security omis, identifiants fictifs)
```xml
<ns3:lireNotificationsReponse
    xmlns:ns3="http://ws.etnic.be/seps/notifications/messages/v1"
    xmlns:ns4="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns5="http://enseignement.cfwb.be/types/seps/notification/v1">
  <ns4:success>true</ns4:success>
  <ns4:messages><ns4:info><ns4:code>200</ns4:code><ns4:description>Notifications found</ns4:description></ns4:info></ns4:messages>
  <ns3:response>
    <ns3:notification>
      <ns5:id>25</ns5:id><ns5:cfNum>1234567-89</ns5:cfNum>
      <ns5:date>2026-11-03</ns5:date>
      <ns5:code>05</ns5:code><ns5:description>MODIF ETUDIANT:CHANGEMENT ADRESSE</ns5:description>
    </ns3:notification>
    <ns3:notification>
      <ns5:id>33</ns5:id><ns5:cfNum>1234567-89</ns5:cfNum>
      <ns5:date>2026-11-03</ns5:date>
      <ns5:code>04</ns5:code><ns5:description>MODIF ETUDIANT:CHANGEMENT NOM/PRENOM</ns5:description>
    </ns3:notification>
  </ns3:response>
</ns3:lireNotificationsReponse>
```
Absence de résultat (§3.1.1.6.2) : `success=false` et un `warning` `30105` « No notification found for etabId : 0 and dateFrom : 2020-02-07 ».

> Aucune observation de production n'est consignée pour ce service.

---

## Vérification croisée manuel / contrat

| Élément | Contrat (catalogue 1.0.8 = production) | Manuel 2.3 | Statut |
|---|---|---|---|
| Requête `etabId` (string) + `dateDebut` (date) | ✓ | ✓ | conforme |
| `NotificationType` (id, cfNum, date, code, description) | ✓ | ✓ | conforme |
| `code` | pattern `\d{2}` | énumération de 6 valeurs | pattern libre au contrat |
| `description` | énumération de 5 valeurs, [0..1] | « obligatoire », 5 valeurs | `08` sans valeur ; cardinalité 0..1 au contrat |
| Authentification | - | X.509 | page du catalogue : UsernameToken (à confirmer) |
| Réponse = liste `notification [0..*]` | ✓ | ✓ | conforme |

---

## Mapping pyetnic

Fonction publique de `pyetnic.seps` :

```python
def lire_notifications(etab_id, date_debut) -> list[SepsNotification]: ...
```

| Classe | Champs |
|---|---|
| `SepsNotification` | `id`, `cfNum`, `date`, `code`, `description` |

- **Résultat vide** : `[]` sur `30105`.
- **Refus** : tout autre `success=false` lève une sous-classe de `SepsEtnicError` (`SepsValidationError` pour `30049` / `30050`, `SepsAuthError` pour `30550`).
- `code` est une chaîne de 2 chiffres : prévoir `08` et des codes non documentés. `description` peut manquer (contrat `0..1`).
- **Synchronisation** : garder la `date` de la dernière notification traitée comme prochain `date_debut` (la date est incluse : une notification peut revenir deux fois, `id` permet de dédoublonner), puis relire chaque étudiant par `lire_etudiant(cf_num, from_date=notification.date)`.

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSNotificationsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `notification_v1.xsd` | `NotificationType` + types simples | spécifique |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
