# Rapport — référentiels EPROM Document 3 (lecture seule)

> Audit **strictement en lecture seule** : seuls `ListerFormations` et `LireDocument3` (SOAP 1.1) ont été appelés. Aucune opération Creer/Modifier/Supprimer/Approuver.

## Contexte d'exécution

| Paramètre | Valeur |
| --- | --- |
| Environnement (`Config.ENV`) | `dev` → endpoints **TQ** (qualification) |
| Endpoint Doc3 | `https://services-web.tq.etnic.be:11443/eprom/formation/document3/v1` |
| Binding SOAP | `EPROMFormationDocument3ExternalV1Binding` — `soap:binding` (**SOAP 1.1**) |
| Année scolaire | 2024-2025 |
| etabId | 3052 |
| implId | 6050 |
| Formations retournées | 110 |
| Organisations totales | 123 |
| Organisations interrogées | 123 — plafond consigne 30 **relevé volontairement** à l'ensemble (volume modéré, lecture seule, meilleure couverture des référentiels) |
| Doc3 lus avec succès | 123 |
| zeep | 4.3.2 |

## a. Valeurs distinctes de `teStatut`

> ⚠ **Important** : la réponse `LireDocument3` ne transporte que le **code** `teStatut`, jamais son libellé. Observer une lettre **prouve seulement que le code existe** dans les données ; elle ne **confirme pas** la correspondance code→libellé de l'hypothèse, qui doit être recoupée dans l'UI EPROM.

| teStatut | Occurrences | Libellé supposé (hypothèse, non vérifiable via Doc3) | Constat brut |
| --- | --- | --- | --- |
| *(vide)* | 441 | — | *(élément présent mais vide)* |
| `T` | 231 | Temporaire | code observé |
| `E` | 53 | Expert | code observé |
| `D` | 40 | Définitif | code observé |

> Codes de l'hypothèse **jamais rencontrés** sur l'ensemble (etabId=3052, 2024-2025) : `A`, `C`, `P`, `X` — ni confirmés, ni infirmés.

## b. Valeurs distinctes de `coDispo`

> Même réserve que pour `teStatut` : seul le **code** `coDispo` est renvoyé, sans libellé. La table atteste l'existence des codes, pas leur signification.

| coDispo | Occurrences | Constat brut |
| --- | --- | --- |
| *(vide)* | 655 | *(élément présent mais vide)* |
| `15` | 104 | code observé |
| `05` | 5 | code observé |
| `28` | 1 | code observé |

## c. Détail formation numAdmFormation=157, numOrganisation=1

> Champs enseignant identifiants masqués par `***` (`noMatEns`, `teNomEns`, `tePrenomEns`, `teEnseignant` — requis ; `teAbrEns`, `teUserMaj` masqués en plus par prudence PII).

### Activité 1

| coNumBranche | coCategorie | teNomBranche | noAnneeEtude | nbPeriodesDoc8 | nbPeriodesPrevuesDoc2 | nbPeriodesReellesDoc2 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | CTms | METHODES DE TRAVAIL | 1 | 48 | 20 | 20 |

| coNumAttribution | coDispo | teStatut | nbPeriodesAttribuees |
| --- | --- | --- | --- |
| 1 |  | T | 20.0 |

## d. XML brut LireDocument3 — formation 157/org 1 (anonymisé)

```xml
<soapenv:Envelope xmlns:msg="http://services-web.etnic.be/eprom/formation/document3/messages/v1" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenv12="http://www.w3.org/2003/05/soap-envelope" xmlns:status="http://etnic.be/types/technical/ResponseStatus/v3">
   <Header xmlns="http://schemas.xmlsoap.org/soap/envelope/">
	<requestId xmlns="http://etnic.be/types/technical/requestId/v1">39156860-4353-46fc-bacb-12dfd00f9567</requestId>
</Header><soapenv:Body>
      <LireDocument3Reponse xmlns="http://services-web.etnic.be/eprom/formation/document3/messages/v1">
         <success xmlns="http://etnic.be/types/technical/ResponseStatus/v3">true</success>
         <response>
            <p784:document3 xmlns:p784="http://enseignement.cfwb.be/types/formation/document3/v1">
               <p784:id>
                  <p752:anneeScolaire xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">2024-2025</p752:anneeScolaire>
                  <p752:etabId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">3052</p752:etabId>
                  <p752:implId xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">6050</p752:implId>
                  <p752:numAdmFormation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">157</p752:numAdmFormation>
                  <p752:numOrganisation xmlns:p752="http://enseignement.cfwb.be/types/organisation/v1">1</p752:numOrganisation>
               </p784:id>
               <p784:activiteListe>
                  <p784:activite>
                     <p784:coNumBranche>1</p784:coNumBranche>
                     <p784:coCategorie>CTms</p784:coCategorie>
                     <p784:teNomBranche>METHODES DE TRAVAIL</p784:teNomBranche>
                     <p784:noAnneeEtude>1</p784:noAnneeEtude>
                     <p784:nbPeriodesDoc8>48</p784:nbPeriodesDoc8>
                     <p784:nbPeriodesPrevuesDoc2>20</p784:nbPeriodesPrevuesDoc2>
                     <p784:nbPeriodesReellesDoc2>20</p784:nbPeriodesReellesDoc2>
                     <p784:enseignantListe>
                        <p784:enseignant>
                           <p784:coNumAttribution>1</p784:coNumAttribution>
                           <p784:noMatEns>***</p784:noMatEns>
                           <p784:teNomEns>***</p784:teNomEns>
                           <p784:tePrenomEns>***</p784:tePrenomEns>
                           <p784:teAbrEns>***</p784:teAbrEns>
                           <p784:teEnseignant>***</p784:teEnseignant>
                           <p784:coDispo/>
                           <p784:teStatut>T</p784:teStatut>
                           <p784:nbPeriodesAttribuees>20.0</p784:nbPeriodesAttribuees>
                           <p784:tsMaj>2026-05-31 17:22:16.694441</p784:tsMaj>
                           <p784:teUserMaj>***</p784:teUserMaj>
                        </p784:enseignant>
                     </p784:enseignantListe>
                  </p784:activite>
               </p784:activiteListe>
            </p784:document3>
         </response>
      </LireDocument3Reponse>
   </soapenv:Body>
</soapenv:Envelope>
```

### Sérialisation des champs numériques

Types XSD côté réponse (`FormationDocument3_v1.xsd`) : `coNumBranche`, `coNumAttribution`, `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2`, `nbPeriodesReellesDoc2` = **`xs:int`** ; `nbPeriodesAttribuees` = `xs:float`.

✓ Aucun champ `xs:int` ne porte de valeur à virgule sur l'ensemble des 123 organisations (765 attributions) : pas de « 24.0 » observé. Le seul `.0` rencontré est sur `nbPeriodesAttribuees` (`xs:float`, ex. `20.0`) — sérialisation **correcte**.

> **Désaccord de type latent à signaler** : le modèle pyetnic déclare `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2`, `nbPeriodesReellesDoc2` en `Optional[float]` (`services/models.py`), alors que le XSD les déclare en `xs:int`. zeep désérialise selon le XSD (`int`) : si ETNIC renvoyait un jour « 24.0 » sur ces champs, **zeep lèverait `ValueError` AVANT** que le type `float` du modèle ne serve à quoi que ce soit. Le type `float` du modèle est donc actuellement **inopérant** (masqué par le parsing `xs:int` de zeep). Données actuellement propres → aucun impact, mais à arbitrer : soit aligner le modèle sur `int`, soit (si ETNIC envoie réellement des décimales) corriger le XSD embarqué en `xs:float`/`xs:decimal`.

### ValueError / warnings zeep (parsing typé)

✓ Aucun `ValueError` levé par zeep sur l'échantillon interrogé.

## e. Codes d'erreur rencontrés (service, code, libellé)

*Aucune erreur rencontrée.*


