# pyetnic — Specification

## Overview

**pyetnic** is a Python client for the SOAP web services operated by ETNIC (the IT agency of the Fédération Wallonie-Bruxelles, Belgium). It targets the education sector: EPROM services (Enseignement de Promotion Sociale — adult/continuing education) covering formations, organisations and administrative documents, and SEPS services (student registry, enrolments).

It is used by schools and school management software to interact programmatically with the official ETNIC back-office: listing offered formations, creating/updating a given school-year "organisation" of a formation, filling in the three administrative documents (Document 1 — population, Document 2 — activity periods and external interventions, Document 3 — teacher assignments), and — through SEPS — searching for and registering students and their enrolments.

- Repository: https://github.com/Lapin-Blanc/pyetnic
- Author: Fabien Toune (fabien.toune@eica.be)
- Python ≥ 3.8 (development uses 3.12+)

## ETNIC Services Coverage

| Config key | ETNIC service | WSDL version | Auth |
|---|---|---|---|
| `LISTE_FORMATIONS` | EPROMFormationsListe | v2 | UsernameToken |
| `ORGANISATION` | EPROMFormationOrganisation | v7 | UsernameToken |
| `DOCUMENT1` | EPROMFormationDocument1 | v1 | UsernameToken |
| `DOCUMENT2` | EPROMFormationDocument2 | v1 | UsernameToken |
| `DOCUMENT3` | EPROMFormationDocument3 | v1 | UsernameToken |
| `SEPS_RECHERCHE_ETUDIANTS` | SEPSRechercheEtudiants | v1 | X509 PFX |
| `SEPS_ENREGISTRER_ETUDIANT` | SEPSEnregistrerEtudiant | v1 | X509 PFX |
| `SEPS_ENREGISTRER_INSCRIPTION` | SEPSEnregistrerInscription | v1 | X509 PFX |
| `SEPS_RECHERCHE_INSCRIPTIONS` | SEPSRechercheInscriptions | v1 | X509 PFX |

### EPROM operations

**FormationsListe (v2)**
- `ListerFormationsOrganisables` → `lister_formations_organisables()`
- `ListerFormations` → `lister_formations()`

**Organisation (v7)**
- `LireOrganisation` → `lire_organisation(org_id)`
- `CreerOrganisation` → `creer_organisation(...)`
- `ModifierOrganisation` → `modifier_organisation(org)`
- `SupprimerOrganisation` → `supprimer_organisation(org_id)`

> No `ApprouverOrganisation` operation in this WSDL — approval is done by the inspection side.
> v7 added `reorientation7TP` (optional bool) to Creer/Modifier/Lire.

**Document1 (v1)**
- `LireDocument1` → `lire_document_1(org_id)`
- `ModifierDocument1` → `modifier_document_1(org_id, population_liste?)`
- `ApprouverDocument1` → `approuver_document_1(org_id, population_liste?)`

**Document2 (v1)**
- `LireDocument2` → `lire_document_2(org_id)`
- `ModifierDocument2` → `modifier_document_2(org_id, activite_enseignement_liste?, intervention_exterieure_liste?)`

> TODO: no `ApprouverDocument2` found in WSDL v1 — verify whether a later version exists.

**Document3 (v1)**
- `LireDocument3` → `lire_document_3(org_id)`
- `ModifierDocument3` → `modifier_document_3(org_id, activite_liste)`

### SEPS operations

**RechercheEtudiants (v1)**
- `lireEtudiant` → `lire_etudiant(cf_num, from_date?)`
- `rechercherEtudiants` → `rechercher_etudiants(niss? | nom, prenom?, date_naissance?, sexe?, force_rn_flag?)`

> NISS mutation (error code 30401) raises `NissMutationError(ancien_niss, nouveau_niss)` from `rechercher_etudiants`.

**EnregistrerEtudiant (v1)**
- `enregistrerEtudiant` → `enregistrer_etudiant(mode_enregistrement, etudiant_details?, double_flag?, create_bis_flag?)`
- `modifierEtudiant` → `modifier_etudiant(cf_num, etudiant_details?)`

> `mode_enregistrement`: `"NISS"` or `"DETAILS"`.
> Save types: `EtudiantDetailsSave`, `SepsNaissanceSave`, `SepsAdresseSave`.

**RechercheInscriptions (v1)**
- `rechercherInscriptions` → `rechercher_inscriptions(annee_scolaire?, etab_id?, date_requete?, cf_num?, no_administratif?, no_organisation?)`

**EnregistrerInscription (v1)**
- `enregistrerInscription` → `enregistrer_inscription(inscription_input_data?)`
- `modifierInscription` → `modifier_inscription(inscription_input_data?)`

> Save types: `InscriptionInputDataSave`, `InscriptionInputSave`, `SepsUESave`, `SepsSpecificiteSave`.
> `InscriptionInputDataSave` required fields: `cfNum`, `idEtab`, `idImplantation`, `codePostalLieuCours`, `inscription`.
> `InscriptionInputSave` required fields: `dateInscription`, `statut`.
> `SpecificiteDataInputType` (Save) does **not** have `regulier1` / `regulier5` — do not include them.

## Authentication

Two authentication schemes coexist:

- **EPROM — WSSE UsernameToken.** Credentials from `.env` (`USERNAME`, `PASSWORD`, plus separate dev/prod as per `ENV`). Available in both dev (`ws-tq.etnic.be`) and prod (`ws.etnic.be`).
- **SEPS — X509 BinarySignature.** A PFX bundle (path via `Config.SEPS_PFX_PATH`) is loaded via `cryptography`, extracted in memory (no disk writes), and used to sign outgoing SOAP envelopes through a custom `_EtnicBinarySignature` plugin (subclass of zeep's `MemorySignature`). Response signature verification is intentionally skipped because the ETNIC CA is not publicly distributed. SEPS works **only in production** (`ws.etnic.be`); dev endpoints return `SECU-0104` because the prod certificate is not registered in TQ. Dependencies: `cryptography` (mandatory) + `xmlsec` (optional, extra `pip install pyetnic[seps]`).

### Endpoints

- Organisation (v7): `https://ws{-tq}.etnic.be/eprom/formation/organisation/v7`
- Other EPROM (dev): `https://services-web.tq.etnic.be:11443/eprom/...`
- Other EPROM (prod): `https://services-web.etnic.be:11443/eprom/...`
- SEPS (prod only): `https://ws.etnic.be/seps/...` (GlobalSign, `verify=True`)

SSL verification is disabled in `dev` for EPROM, enabled in `prod`, and always enabled for `x509_pfx` services.

## Business Workflow

```
Créer organisation
    → statut "Encodé école"
    → Doc 1, 2, 3: inaccessible

Inspection approves organisation
    → statut "Approuvé"
    → Doc 1: readable and modifiable
    → Doc 2: readable and modifiable

School approves Doc 1 (ApprouverDocument1)
School approves Doc 2 (no school-side operation — inspection-driven?)
    → Doc 3: accessible (error 20102 otherwise)
```

Notes:

- There is no `ApprouverOrganisation` operation on the school side — approval is the inspection's responsibility.
- In the test environment (tq), created organisations stay in "Encodé école" until manual inspection action, so end-to-end Doc flows cannot be exercised there without out-of-band state changes.

## Critical Business Rules

### `implId` must NEVER be included in Lire/Modifier/Supprimer requests

`OrganisationReqIdCT` (request) has 4 fields only: `anneeScolaire`, `etabId`, `numAdmFormation`, `numOrganisation`.
`OrganisationResIdCT` (server response) additionally contains `implId`.
Only `CreerOrganisation` accepts `implId` in its `id`.

All services implement `_organisation_id_dict()` to build the request id without `implId`. **Never** use `dataclasses.asdict(organisation_id)` directly — that would include `implId=None` and be rejected server-side.

### Document accessibility is workflow-gated

- Doc 1/2/3 inaccessible while organisation is "Encodé école".
- Doc 3 inaccessible (error 20102) unless Doc 1 and Doc 2 are approved.
- `_parse_*_response` methods must guard against `response=None` in the serialized SOAP body and return `None` when the document cannot be read.

### Save vs read types

For each document there are "Save" dataclasses (sent to the server, only the modifiable subset of fields) and "read" dataclasses (received from the server). Do not mix them. Example: `Doc1PopulationLine` vs `Doc1PopulationLineSave`.

### `Doc3ActiviteDetailSave` required fields

```python
@dataclass
class Doc3ActiviteDetailSave:
    coNumBranche: int              # required (XSD has no minOccurs="0")
    noAnneeEtude: str              # required
    enseignantListe: Doc3EnseignantListSave  # required
```

## Data Model

High-level entity map — refer to `pyetnic/services/models.py` for the authoritative definitions.

**Common types.** `StatutDocument`, `OrganisationId`, `OrganisationApercu`, `Organisation`, `Formation`, `FormationsListeResult`.

**Organisation hierarchy.**

```
OrganisationApercu     ← returned by lister_formations() (OrganisationApercuCT)
    id, dateDebut, dateFin
    statutDocumentOrganisation        (StatutDocument | None)
    statutDocumentPopulationPeriodes  (StatutDocument | None) — Doc 1
    statutDocumentDroitsInscription   (StatutDocument | None)
    statutDocumentAttributions        (StatutDocument | None) — Doc 3

Organisation(OrganisationApercu) ← returned by lire_organisation() (FormationOrganisationCT)
    + nombreSemaineFormation, organisationPeriodesSupplOuEPT, ...
    (statutDocumentPopulationPeriodes etc. are always None here — not part of FormationOrganisationCT)
```

**Document 1.** `Doc1PopulationLine`, `Doc1PopulationList`, `Doc1PopulationLineSave`, `Doc1PopulationListSave`, `FormationDocument1`.

**Document 2.** `Doc2Activite*`, `Doc2PeriodeExt*`, `Doc2InterventionExt*` (read and save variants), `FormationDocument2`.

**Document 3.** `Doc3EnseignantDetail`, `Doc3EnseignantList`, `Doc3ActiviteDetail`, `Doc3ActiviteListe` (read) and their `Doc3*Save` counterparts, `FormationDocument3`.

**SEPS students.** `SepsLocalite`, `SepsAdresse`, `SepsNaissance`, `SepsDeces`, `EtudiantDetails`, `Etudiant`; save variants `SepsNaissanceSave`, `SepsAdresseSave`, `EtudiantDetailsSave`.

**SEPS inscriptions (read).** `SepsUE`, `SepsLieuCours`, `SepsDroitInscription`, `SepsExempteDroitInscription`, `SepsDroitInscriptionSpecifique`, `SepsExempteDroitInscriptionSpec`, `SepsAdmission`, `SepsSanction`, `SepsSpecificite`, `Inscription`.

**SEPS inscriptions (save).** `SepsUESave`, `SepsDroitInscriptionSave`, `SepsAdmissionSave`, `SepsSanctionSave`, `SepsSpecificiteSave`, `InscriptionInputSave`, `InscriptionInputDataSave`.

## Error Codes

| Code | Meaning |
|---|---|
| 20102 | Document 3 inaccessible because Doc 1 and/or Doc 2 are not yet approved. |
| 30401 | NISS mutation — an old NISS has been replaced by a new one. Raised as `NissMutationError(ancien_niss, nouveau_niss)` from SEPS `rechercher_etudiants`. |
| SECU-0104 | SEPS call in dev (`tq`) with a prod certificate — the prod X509 is not registered in the TQ environment. SEPS is prod-only. |

TODO: expand this section as new error codes are encountered and handled.

## Environment Configuration

The `.env` file is loaded lazily on first `Config` attribute access. No side effects at `import pyetnic`.

Common keys:

- `ENV` — `dev` or `prod`; drives endpoint selection and SSL behaviour.
- `USERNAME`, `PASSWORD` — EPROM WSSE credentials.
- `ETAB_ID` — establishment id used by integration tests; if unset, integration tests `pytest.skip()`.
- `SEPS_PFX_PATH` — path to the X509 PFX bundle (relative to CWD, resolved via `os.path.abspath`).
- `SEPS_PFX_PASSWORD` — PFX passphrase.

Programmatic override (e.g. from a Django settings module):

```python
from pyetnic.config import Config
Config.ENV = "prod"
Config.USERNAME = "my_user"
Config.PASSWORD = "my_pass"
# → picked up on the next SOAP call
```

`Config._reset()` resets overrides and dotenv state (used by tests).

## Test Environment

- Server: `services-web.tq.etnic.be`
- `etabId=3052`, `implId=6050`
- 2025-2026: 2 organisations created (F327, F328), "Encodé école" → Doc 1/2/3 inaccessible
- 2024-2025: 34 organisations "Approuvé" → Doc 1/2 readable, Doc 3 inaccessible (Doc 1/2 not approved)
- 2023-2024: 119/158 organisations with Doc 3 accessible — this is the reference vintage for Doc 3 tests.
