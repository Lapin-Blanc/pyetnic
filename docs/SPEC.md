# pyetnic — Specification

## Overview

**pyetnic** is a Python client for the SOAP web services operated by ETNIC (the IT agency of the Fédération Wallonie-Bruxelles, Belgium). It targets the education sector: EPROM services (Enseignement pour adultes, formerly Enseignement de promotion sociale; the EPROM identifiers keep the old name) covering formations, organisations and administrative documents, and SEPS services (student registry, enrolments).

It is used by schools and school management software to interact programmatically with the official ETNIC back-office: listing offered formations, creating/updating a given school-year "organisation" of a formation, filling in the three administrative documents (Document 1 — population, Document 2 — activity periods and external interventions, Document 3 — teacher assignments), and — through SEPS — searching for and registering students and their enrolments.

- Repository: https://github.com/Lapin-Blanc/pyetnic
- Author: Fabien Toune (https://github.com/Lapin-Blanc)
- Python ≥ 3.10 (CI matrix 3.10–3.13; development on 3.12+)

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
| `SEPS_NOTIFICATIONS` | SEPSNotifications | v1 (catalogue 1.0.8) | X509 PFX |

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

> There is no `ApprouverDocument2`: the administration approves Doc 2 (switch `swAppD2`). The
> school's work on Doc 2 ends with `modifier_document_2`.

**Document3 (v1)**
- `LireDocument3` → `lire_document_3(org_id)`
- `ModifierDocument3` → `modifier_document_3(org_id, activite_liste)`

### SEPS operations

**RechercheEtudiants (v1)**
- `lireEtudiant` → `lire_etudiant(cf_num, from_date?)`
- `rechercherEtudiants` → `rechercher_etudiants(niss? | nom, prenom?, date_naissance?, sexe?, force_rn_flag?)`

> NISS mutation (error code 30401) raises `NissMutationError(ancien_niss, nouveau_niss)` from `rechercher_etudiants`.

> **Refusals (every SEPS operation).** `success=false` is a refusal whether its code comes as an
> `error` or as a `warning`: production answered `enregistrerInscription` with only the warning
> 30101 (2026-11-10). SEPS always raises a `SepsEtnicError` subclass chosen by the code (see the
> error table); reads return `None` / `[]` on their "nothing found" codes (`lireEtudiant`,
> `rechercherEtudiants`: 30110, 30115; `rechercherInscriptions`: 30102, 30103). A `success=false`
> carrying only the info 200 or 201 is a success (the manual's `modifierEtudiant` example).

**EnregistrerEtudiant (v1)**
- `enregistrerEtudiant` → `enregistrer_etudiant(mode_enregistrement, etudiant_details?, double_flag?, create_bis_flag?)`
- `modifierEtudiant` → `modifier_etudiant(cf_num, etudiant_details?)`

> `mode_enregistrement`: `"NISS"` or `"DETAILS"`.
> Save types: `EtudiantDetailsSave`, `SepsNaissanceSave`, `SepsAdresseSave`.
> Returns `EnregistrerEtudiantResult` / `ModifierEtudiantResult`: the student as the server sends it
> back, `code` and `messages` (service version excluded). `cree` is code 201, a new CF number
> (production, NISS mode, 2026-11-24: info 201 « L'étudiant est sauvé »); `fusionne` is code 200,
> attached to an existing establishment record that keeps its CF (manual 2.3). `bis_cree` reads
> `bisCreated` (`O` / `N`), a field of the live contract.

**RechercheInscriptions (v1)**
- `rechercherInscriptions` → `rechercher_inscriptions(annee_scolaire?, etab_id?, date_requete?, cf_num?, no_administratif?, no_organisation?)`

**Notifications (v1)**
- `lireNotifications` -> `lire_notifications(etab_id, date_debut)` -> `List[SepsNotification]`

> Identity changes of the establishment's students since `date_debut` (inclusive): code 02 sex,
> 04 name, 05 address, 06 nationality, 07 NISS, 08 status (`CodeNotification`). 30105 (none found)
> gives `[]`. Authentication is X509 like the other SEPS services: the catalogue announces a
> UsernameToken profile, but production refuses the EPROM credentials (SECU-1101) and accepts the
> certificate (2026-11-24). Code 08, added by manual 2.3, comes without `description`: the contract
> has none for it (2026-11-24). A `date_debut` in the future answers `success=true` with 30050 and
> 30105: `[]`, the two codes logged (2026-11-24).

**EnregistrerInscription (v1)**
- `enregistrerInscription` → `enregistrer_inscription(inscription_input_data?)`
- `modifierInscription` → `modifier_inscription(inscription_input_data?)`

> Both return `InscriptionResult`: the inscription as the server sends it back, `code` and `messages`.
> `plus_de_4_ue` reports 30051 ("Ok création mais inscrit dans plus de 4 UEs", a success). The
> manual's successful `enregistrerInscription` example carries no message: `code` is then `None`.

> Save types: `InscriptionInputDataSave`, `InscriptionInputSave`, `SepsUESave`, `SepsSpecificiteSave`.
> `InscriptionInputDataSave` required fields: `cfNum`, `idEtab`, `idImplantation`, `codePostalLieuCours`, `inscription`.
> `InscriptionInputSave` required fields: `dateInscription`, `statut`.
> The inscription input element is typed `SpecificiteDataType`, which carries `regulier1` / `regulier5`;
> the catalogue XSD also defined a `SpecificiteDataInputType` without them, used by no element, which the
> live contract no longer has. `SepsSpecificiteSave` follows `SpecificiteDataType`.
> Fields of the live contract (#22): `regulier3` (accepted by production's `enregistrerInscription`
> only: `rechercherInscriptions` and TQ do not know it yet, 2026-11-24), `montant` on both fees,
> `InscriptionInputSave.fse` (server default true: FSE fields required when the UE is FSE and the
> student regular at the 1/10; false relaxes them), the sanction's `pourcentageAttribue`,
> `codeSectionFlag`, `codeSection`, `point` (integrated tests) and `ajournement1Session`;
> `codeSanction` is optional. Read side: `Inscription.audit` (`SepsAudit`), `Etudiant.bisCreated`.

## Authentication

Two authentication schemes coexist:

- **EPROM — WSSE UsernameToken.** Credentials from `.env` (`USERNAME`, `PASSWORD`, plus separate dev/prod as per `ENV`). Available in both dev (`ws-tq.etnic.be`) and prod (`ws.etnic.be`).
- **SEPS - X509 BinarySignature.** A PFX bundle (path via `Config.SEPS_PFX_PATH`) is loaded via `cryptography` (extra `[seps]`), extracted in memory (no disk writes), and used to sign outgoing SOAP envelopes through a custom `_EtnicBinarySignature` plugin (subclass of zeep's `MemorySignature`). Response signature verification is intentionally skipped because the ETNIC CA is not publicly distributed. SEPS works **only in production** (`ws.etnic.be`); dev endpoints return `SECU-0104` because the prod certificate is not registered in TQ. Dependencies: `cryptography` (mandatory) + `xmlsec` (optional, extra `pip install pyetnic[seps]`).

### Endpoints

- Organisation (v7): `https://ws{-tq}.etnic.be/eprom/formation/organisation/v7`
- Other EPROM (dev): `https://services-web.tq.etnic.be:11443/eprom/...`
- Other EPROM (prod): `https://services-web.etnic.be:11443/eprom/...`
- SEPS (prod only): `https://ws.etnic.be/seps/...` (GlobalSign, `verify=True`)

SSL verification is disabled in `dev` for EPROM, enabled in `prod`, and always enabled for `x509_pfx` services.

## Business Workflow

```
Doc A  creer_organisation                     -> "Encodé école"
       the administration approves it          -> "Approuvé" (no school-side operation)

Doc 1  modifier_document_1 (population), then approuver_document_1 -> swAppPopD1 = True
       the approval must carry back the population as read (error 20104 otherwise)

Doc 2  exists once the Doc 1 population is validated (error 20103 before that)
       modifier_document_2: the school's work ends here; its first write sets
       the status to "Encodé école" (tested on TQ, 2026-11-10)
       the administration approves Doc 1 and Doc 2 together (swAppD1 + swAppD2);
       later writes are refused (error 1530)

Doc 3  reachable once Doc A and Doc 2 are approved (error 20102 otherwise)
       modifier_document_3: no approval switch, encoding is all the school does
```

Notes:

- There is no `ApprouverOrganisation` operation on the school side — approval is the inspection's responsibility.
- In the test environment (tq), created organisations stay in "Encodé école" until manual inspection action, so their documents cannot be reached. Organisations of past school years whose Doc A is already approved in the test data can be used instead: on them, Doc 1 encoding and validation and Doc 2 writes work (tested on TQ, 2026-11-10).

### SEPS: enrolling a student

An inscription needs the student's `cfNum`. Never call `enregistrer_inscription` without
one: resolve the identity first, in this order.

```
A) cfNum known?                       -> enrol (D)
B) NISS known? rechercher_etudiants(niss=...)
     found in SEPS                    -> enrol (D)
     found at the BCED only           -> enregistrer_etudiant(mode "NISS") -> enrol (D)
     not found                        -> C
C) rechercher_etudiants(nom, prenom, date_naissance, sexe)
     found in SEPS                    -> enrol (D)
     found at the BCED only           -> enregistrer_etudiant(mode "NISS") -> enrol (D)
     not found                        -> enregistrer_etudiant(mode "DETAILS") -> enrol (D)
D) enregistrer_inscription(cfNum + UE data)
```

## Critical Business Rules

### `implId` must NEVER be included in Lire/Modifier/Supprimer requests

`OrganisationReqIdCT` (request) has 4 fields only: `anneeScolaire`, `etabId`, `numAdmFormation`, `numOrganisation`.
`OrganisationResIdCT` (server response) additionally contains `implId`.
Only `CreerOrganisation` accepts `implId` in its `id`.

All services build the request id with `organisation_request_id()` (`services/_helpers.py`), which leaves `implId` out. **Never** use `dataclasses.asdict(organisation_id)` directly - that would include `implId=None` and be rejected server-side.

### Document accessibility is workflow-gated

- Doc 1/2/3 inaccessible while organisation is "Encodé école" (Doc 1: error 20101).
- Doc 2 inaccessible (error 20103) until the Doc 1 population is validated (`swAppPopD1`).
- Doc 3 inaccessible (error 20102) unless Doc A (the organisation) and Doc 2 are approved.
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
    statutDocumentPopulationPeriodes  (StatutDocument | None) - Doc 1 and Doc 2 together
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

**SEPS inscriptions (save).** `SepsUESave`, `SepsSpecificiteSave`, `InscriptionInputSave`, `InscriptionInputDataSave`. (No `*Save` variant exists for `SepsDroitInscription` / `SepsAdmission` / `SepsSanction` — those are read-only models.)

## Error Codes

| Code | Meaning |
|---|---|
| 1574 | Doc 3: total attributed periods exceed the periods organised. The ceiling is the **real** periods of Doc 2 once filled, not the planned ones. Lines carrying a `coDispo` do not count toward the total (observed in production, 2026-09). The `$1` of the message announced 72,00 for 80 periods sent without `coDispo` (observed once, 2026-09-22, unexplained). |
| 20101 | `LireDocument1` before the Doc A is approved. Server text: « Le "Doc A" doit être approuvé pour pouvoir accéder au document suivant » (tested on TQ, 2026-11-10). Not mapped in `exceptions.py`: `None` in permissive mode, a plain `EtnicBusinessError` under `strict_errors()`. |
| 20102 | Document 3 inaccessible until Doc A (the organisation) and Doc 2 are approved. Server text: « Les "Doc A" et "Doc 2" doivent être approuvés pour pouvoir accéder au "Doc 3" ». |
| 20103 | `LireDocument2` before the Doc 1 population is validated. Server text: « Le "Doc 1" doit être approuvé pour pouvoir accéder au document suivant »; the school's validation (`swAppPopD1`) is enough, `swAppD1` may still be false (tested on TQ, 2026-11-10). Not mapped in `exceptions.py`: `None` in permissive mode, a plain `EtnicBusinessError` under `strict_errors()`. |
| 20104 | Doc 1 approval refused: the population sent differs from the stored one, or none was sent. Send back the lines just read. |
| 20108 | Doc 3: « Le numéro de matricule d'enseignement n°$1 est incorrect ». Also returned for a well-formed staff number when the teacher is not (yet) in the EPROM teacher referential, which is fed outside these services; the same payload passes once the referential is updated (observed in production: refused 2026-09-21, accepted 2026-09-22). A write refused with 20108 leaves nothing behind (observed twice on blank documents). |
| 30100, 30101 | SEPS: no such UE (`SepsUeInconnueError`). 30101 came as a warning 18 minutes after the organisation was declared in EPROM (production, 2026-11-10): SEPS receives organisations with a delay. Inscriptions on organisations whose Doc A was not yet approved were accepted (production, 2026-09-30, approval 2026-10-23). |
| 30011, 30120 | SEPS: no student for this CF / no person for this NISS at the national register (`SepsEtudiantInconnuError`). |
| 30200 | SEPS: the student is already enrolled in this UE (`SepsInscriptionExisteError`). |
| 30201 | SEPS: the student already exists (`SepsEtudiantExisteError`, the CF number from the description in `cf_num`). |
| 30202, 30203, 30204 | SEPS: possible duplicates (`SepsDoublonsError`, the CF numbers in `cf_nums`, the NISS in `niss`). |
| 30401 | NISS mutation — an old NISS has been replaced by a new one. Raised as `NissMutationError(ancien_niss, nouveau_niss)` from SEPS `rechercher_etudiants`. |
| 30443 | SEPS: nothing to change (`SepsAucuneModificationError`), as an error or as an info. |
| 30501, 30503 | SEPS: too many results (`TropDeResultatsError`). |
| 30502 | SEPS: error calling the BCED (national register). `rechercherEtudiants` by name answers it, as an error, for a person found nowhere: « Une erreur s'est produite dans le processus, veuillez réessayer plus tard » (production, 2026-11-24, three requests). Raised as the base `SepsEtnicError`, not turned into an empty result: the code also covers real BCED failures. |
| 30550 | SEPS: authentication (`SepsAuthError`). |
| other SEPS 300xx | `SepsValidationError` for the manual's BAD_REQUEST codes, `SepsNotFoundError` for NOT_FOUND, the base `SepsEtnicError` otherwise. |
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

- EPROM server: `services-web.tq.etnic.be` (`ENV=dev`). SEPS has no usable test
  environment: it runs in production only (see `SECU-0104`).
- Organisations created there stay "Encodé école": documents 1, 2 and 3 cannot be reached
  on a fresh organisation. Past school years with approved organisations are the only way to
  exercise the documents: on 2025-2026 organisations whose Doc A is approved, Doc 1 encoding
  and validation and Doc 2 writes work (tested 2026-11-10). A Doc 1 validation cannot be undone.
- To settle an undocumented wire value, probe empirically: create an organisation on TQ,
  read it back, then delete it. Error `30004` and the letter codes of the external
  intervention types were settled this way.
- Integration tests read the establishment from `DEFAULT_ETABID` and skip without it.

## XSD Verification Procedure

Before implementing or modifying a service, always check the WSDL/XSD in
`pyetnic/resources/` (each service has its own folder, e.g.
`pyetnic/resources/EPROM_Document_3_1.0/xsd/`). Verify:

1. **Required fields** — elements without `minOccurs="0"` must NOT be `Optional` in the
   dataclass (no default value).
2. **Optional fields** — elements with `minOccurs="0"` are `Optional[T] = None`.
3. **`OrganisationReqIdCT` vs `OrganisationResIdCT`** — the request id has 4 fields (no
   `implId`); the response id adds `implId`. Never send `implId` in Lire/Modifier/Supprimer.
4. **Exact element names** — Python attribute names keep the XSD camelCase verbatim
   (e.g. `activiteListe`, not `activiteList`).

Python class names mirror the XSD type names exactly (e.g. `Doc2ActiviteEnseignementLine`
← `Doc2ActiviteEnseignementLineCT`). Method parameters use `snake_case` even though the SOAP
fields are `camelCase`.

```bash
# Read a service's WSDL and matching XSD:
cat "pyetnic/resources/EPROM_Document_3_1.0/EpromFormationDocument3Service_external_v1.wsdl"
cat "pyetnic/resources/EPROM_Document_3_1.0/xsd/EpromFormationDocument3_external_v1.xsd"
```
