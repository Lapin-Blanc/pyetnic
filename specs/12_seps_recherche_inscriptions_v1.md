# SEPS — Recherche Inscriptions (aux UEs) v1 (release 2.1.9)

> Spécification technique et fonctionnelle complète
> Sources : WSDL `SEPSRechercheInscriptionsService_external_v1.wsdl` + `inscription_v1.xsd` + PDF « Services Web SEPS » v2.1.9, §3.7
> Date d'analyse : 2026-06-09 (session 7)
> **Préambule famille SEPS, X.509, SOAP Fault, bloc retour** : voir **spec 09**. **Énumérations & sous-types d'inscription** : voir **spec 11** (XSD `inscription_v1.xsd` identique, md5).

---

## Métadonnées

| Propriété | Valeur |
|---|---|
| Service | Recherche des Inscriptions aux UEs |
| Version contrat / release | external **v1** / **2.1.9** |
| Sécurité | WS-Security **X.509** · SOAP 1.1 · synchrone |
| WSDL namespace | `http://ws.etnic.be/seps/rechercheInscriptions/v1` |
| Messages namespace | `http://ws.etnic.be/seps/rechercheInscriptions/messages/v1` |
| Types namespace | `http://enseignement.cfwb.be/types/seps/inscription/v1` |
| Binding | `SEPSRechercheInscriptionsV1ExternalBinding` (document/literal) |
| Opérations | **1** : `rechercherInscriptions` |

### Endpoints

| Env | Source | URL |
|---|---|---|
| TQ | WSDL | `https://ws-tq.etnic.be/seps/rechercheInscriptions/v1` |
| TQ / PROD | PDF §2.2 | `https://services-web(.tq).etnic.be/seps/rechercheInscriptions/v1` |

> `requestId` en sortie : `wsdl:required="true"` (le serveur renvoie toujours un requestId).

### Contrôle d'accès (manuel §3.7)
- Profil **support** : non limité.
- Profil **établissement** : limité aux inscriptions du/des établissement(s). **Si un seul** profil établissement → `etabId` **facultatif** ; **si plusieurs** → `etabId` **obligatoire** (erreur `30052`).
- Profil **PO** : limité aux établissements du PO.

---

## Description fonctionnelle

Recherche les inscriptions aux UE selon des critères. **Au moins un** parmi `anneeScolaire`, `cfNum`, `noAdministratif`/`noOrganisation` (id UE) doit être fourni (sinon `30036`).
La **date de demande** (`dateRequete`) sélectionne la **situation la plus récente** (enregistrement ou modification) à cette date ; défaut = date du jour.

---

## Requête — `rechercherInscriptions` (type `RechercherInscriptionsRequeteType`)

| Champ | Type | Card. | Description |
|---|---|---|---|
| `anneeScolaire` | xs:integer | 0..1 | Millésime (ex. 2018). *(≥1 des critères requis)* |
| `etabId` | xs:integer | 0..1 | Id FASE établissement (oblig. si multi-profil) |
| `dateRequete` | xs:date | 0..1 | Date pivot ; défaut = aujourd'hui |
| `cfNum` | cfNumType | 0..1 | Identifie l'étudiant |
| `noAdministratif` | ShortType | 0..1 | N° administratif UE |
| `noOrganisation` | ShortType | 0..1 | N° d'organisation UE |

> ⚠️ **Nom** : XSD `dateRequete` ; le tableau PDF écrit `dateRequest`. → XSD fait foi (`dateRequete`).

---

## Réponse — `rechercherInscriptionsReponse` (type `RechercherInscriptionsReponseType`)
```
response
└── inscription : InscriptionType   [0..*]   (liste)
```

### InscriptionType — vue complète d'une inscription (sortie)
> Type **de sortie** (plus riche que `InscriptionInputType`). Également renvoyé par enregistrer/modifier (spec 11).

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
└── specificite     : SpecificiteDataType  [0..1]   (voir spec 11)
```

**LieuCoursType** : `codePostal` [0..1] + `ville` [0..1].

**UEType** (sortie, plus riche que `UEInputType`) :
| Champ | Type | Card. | Description |
|---|---|---|---|
| `noAdministratif` | ShortType | oblig. | N° administratif UE |
| `noOrganisation` | ShortType | oblig. | N° d'organisation UE |
| `label` | TextType(≤250) | 0..1 | Libellé de l'UE |
| `code` | TextType | 0..1 | Code du cours (ex. `201800000001670032000001`) |
| `codeNiveau` | CodeNiveauType | 0..1 | `SI`/`SS`/`SC`/`SL` |
| `nombreSemaine` | ShortType | 0..1 | Nombre de semaines |
| `dateDebut` | DateType | 0..1 | Date de début UE |
| `dateFin` | DateType | 0..1 | Date de fin UE |
| `fse` | IndicateurType | 0..1 | UE FSE ou non (`O`/`N`) |
| `noOrganisationPrecedent` | TextType | 0..1 | N° de l'organisation précédente |
| `activiteDeFormation` | IndicateurType | 0..1 | UE = activité de formation |

> Le champ **`ue.fse`** conditionne l'obligation des champs FSE de `specificite` (cf. spec 11). Le **`code`** UE encode l'année + idEtab + noAdmin + noOrga (ex. `2018 0000000167 0032 00001`).

### Codes de retour (manuel §3.7.1.3.2)

| Success | Code | Label | Description |
|---|---|---|---|
| true | `200` | SUCCESS | Inscriptions found |
| false | `30036` | BAD_REQUEST | Combinaison de paramètres invalide (aucun critère) |
| false | `30037` | BAD_REQUEST | Validation de la date de requête |
| false | `30041` | BAD_REQUEST | Validation `cfNum` |
| false | `30049` | BAD_REQUEST | Validation `etabId` |
| false | `30052` | BAD_REQUEST | Compte multi-profil : `etabId` requis |
| false | `30103` | NOT_FOUND | Aucune inscription trouvée (warning) |
| false | `30501` | INTERNAL_SERVER_ERROR | Trop de résultats |
| false | `30550` | INTERNAL_SERVER_ERROR | Authentification (interne) |

### Exemple de requête
```xml
<v11:rechercherInscriptions xmlns:v11="http://ws.etnic.be/seps/rechercheInscriptions/messages/v1">
  <v11:anneeScolaire>2018</v11:anneeScolaire>
  <v11:etabId>167</v11:etabId>
</v11:rechercherInscriptions>
```

### Exemple de réponse (extrait, 1 inscription)
```xml
<ns3:rechercherInscriptionsReponse
    xmlns:ns3="http://ws.etnic.be/seps/rechercheInscriptions/messages/v1"
    xmlns:ns4="http://etnic.be/types/technical/ResponseStatus/v3"
    xmlns:ns5="http://enseignement.cfwb.be/types/seps/inscription/v1">
  <ns4:success>true</ns4:success>
  <ns4:messages><ns4:info><ns4:code>200</ns4:code><ns4:description>Inscriptions found</ns4:description></ns4:info></ns4:messages>
  <ns3:response>
    <ns3:inscription>
      <ns5:cfNum>8500264-57</ns5:cfNum>
      <ns5:anneeScolaire>2018</ns5:anneeScolaire>
      <ns5:idEtab>167</ns5:idEtab><ns5:idImplantation>516</ns5:idImplantation>
      <ns5:dateInscription>2018-09-15</ns5:dateInscription>
      <ns5:lieuCours><ns5:codePostal>1020</ns5:codePostal><ns5:ville>BRUXELLES</ns5:ville></ns5:lieuCours>
      <ns5:statut>DE</ns5:statut>
      <ns5:ue>
        <ns5:noAdministratif>320</ns5:noAdministratif><ns5:noOrganisation>1</ns5:noOrganisation>
        <ns5:label>BACHELIER : STAGE D'INSERTION SOCIOPROFESSIONNELLE</ns5:label>
        <ns5:code>201800000001670032000001</ns5:code>
        <ns5:codeNiveau>SC</ns5:codeNiveau><ns5:nombreSemaine>38</ns5:nombreSemaine>
        <ns5:dateDebut>2018-09-17</ns5:dateDebut><ns5:dateFin>2019-06-30</ns5:dateFin>
        <ns5:fse>N</ns5:fse>
      </ns5:ue>
      <ns5:specificite>
        <ns5:regulier1>O</ns5:regulier1><ns5:regulier5>O</ns5:regulier5>
        <ns5:admission><ns5:codeAdmission>AUTRE</ns5:codeAdmission><ns5:valorisationAcquis>C10</ns5:valorisationAcquis></ns5:admission>
      </ns5:specificite>
    </ns3:inscription>
  </ns3:response>
</ns3:rechercherInscriptionsReponse>
```

---

## Vérification croisée UML / XSD / PDF

| Élément | XSD | PDF | UML (p.11-12) | Statut |
|---|---|---|---|---|
| Requête : 6 critères, ≥1 requis | ✓ | ✓ (§3.7.1.1.1) | — | ✅ |
| `dateRequete` | `dateRequete` | `dateRequest` (tableau) | — | ⚠️ XSD fait foi |
| `InscriptionType` (9 champs) | ✓ | ✓ | ✓ | ✅ |
| `UEType` (11 champs) | ✓ | ✓ | ✓ | ✅ |
| Réponse = liste `inscription [0..*]` | ✓ | ✓ | — | ✅ |

---

## Mapping pyetnic

```python
class SepsRechercheInscriptionsService:
    """SEPS Recherche Inscriptions v1 (release 2.1.9) — auth X.509."""
    WSDL = "SEPSRechercheInscriptionsService_external_v1.wsdl"
    ENDPOINT_TQ   = "https://services-web.tq.etnic.be/seps/rechercheInscriptions/v1"
    ENDPOINT_PROD = "https://services-web.etnic.be/seps/rechercheInscriptions/v1"

    def rechercher(self, *, annee_scolaire: int | None = None, etab_id: int | None = None,
                   date_requete: date | None = None, cf_num: str | None = None,
                   no_administratif: int | None = None, no_organisation: int | None = None
                   ) -> list[Inscription]:
        """Au moins un critère parmi annee_scolaire / cf_num / (no_administratif+no_organisation)."""
```
```python
@dataclass
class UE:
    no_administratif: int; no_organisation: int
    label: str | None = None; code: str | None = None
    code_niveau: str | None = None; nombre_semaine: int | None = None
    date_debut: str | None = None; date_fin: str | None = None
    fse: str | None = None; no_organisation_precedent: str | None = None
    activite_de_formation: str | None = None

@dataclass
class Inscription:
    cf_num: str
    annee_scolaire: int | None = None
    id_etab: int | None = None; id_implantation: int | None = None
    date_inscription: str | None = None
    lieu_cours: LieuCours | None = None
    statut: str | None = None          # DE / AN
    ue: UE | None = None
    specificite: Specificite | None = None   # partagé avec spec 11
```
- Valider côté client la règle « ≥ 1 critère » (évite `30036`) et la règle multi-profil (`etabId` requis → `30052`).
- Dataclasses `Inscription`/`UE`/`Specificite` **partagées** avec la spec 11 (entrée/sortie).

---

## XSD utilisés

| Fichier | Rôle | Partagé |
|---|---|---|
| `SEPSRechercheInscriptionsMessages_external_v1.xsd` | Éléments d'opération | spécifique |
| `inscription_v1.xsd` | `InscriptionType`, `UEType`, `LieuCoursType`, enums | = spec 11 (md5 identique) |
| `cfNum_v1.xsd` / `external_v1.xsd` / `ResponseStatus_v3.xsd` / `requestId_v1.xsd` | communs | famille SEPS |
