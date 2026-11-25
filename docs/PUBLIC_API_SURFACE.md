# Public API Surface

> **Status**: Authoritative reference for `BACKWARDS_COMPAT.md`
> **Last reviewed**: 2026-11-24 for 0.3.0b1 (EPROM: #32 to #36; SEPS read functions: #24); first classification at Sprint 0

This document enumerates every symbol exported from `pyetnic` and classifies it as either **stable** (subject to the backwards compatibility rules) or **construction** (free to evolve).

Classification is based on actual production use at the time of Sprint 0. A symbol is **stable** if it is demonstrably used in:

- Author's production scripts (school administrative tools)
- `examples/extrait_profs.py`, `examples/print_doc2.py`, `examples/print_doc3.py`
- Author's downstream projects (EtnicSearch, Atelier Analyse)

A symbol is **construction** otherwise. Construction symbols are still exported for forward compatibility, but their signatures and behaviors may change at any minor version until 1.0.0.

---

## `pyetnic.eprom` — EPROM namespace

### Stable — Functions

| Symbol | Notes |
|---|---|
| `lister_formations` | Used in production scripts |
| `lister_formations_organisables` | Used in production scripts |
| `lire_organisation` | Used in production scripts |
| `creer_organisation` | Used in production scripts |
| `modifier_organisation` | Used in production scripts |
| `supprimer_organisation` | Used in production scripts |
| `lire_document_1` | Used in production scripts |
| `modifier_document_1` | Used in production scripts |
| `approuver_document_1` | Used in production scripts. `population_liste` required since 0.3.0 (#34): the server refused every call without it (20104) |
| `lire_document_2` | Used in production scripts |
| `modifier_document_2` | Used in production scripts |
| `lire_document_3` | Used in production scripts |
| `modifier_document_3` | Used in production scripts |

### Stable — Dataclasses

| Symbol | Notes |
|---|---|
| `OrganisationId` | Constructed by callers |
| `Organisation` | Returned by `lire_organisation`, `creer_organisation`, `modifier_organisation`. Gained `BESAeSI` (last field) in 0.3.0, Organisation v8 |
| `OrganisationApercu` | Returned by `lister_formations` |
| `Formation` | Returned by `lister_formations` |
| `FormationsListeResult` | Returned by `lister_formations*` |
| `StatutDocument` | Nested in `OrganisationApercu` |
| `Doc1PopulationLine` | Nested in `FormationDocument1` (read) |
| `Doc1PopulationList` | Nested in `FormationDocument1` (read) |
| `Doc1PopulationLineSave` | Constructed by callers for `modifier_document_1` |
| `Doc1PopulationListSave` | Constructed by callers |
| `FormationDocument1` | Returned by `lire_document_1`, `modifier_document_1`, `approuver_document_1` |
| `Doc2ActiviteEnseignementLine` | Read model |
| `Doc2ActiviteEnseignementList` | Read model |
| `Doc2ActiviteEnseignementDetail` | Read model |
| `Doc2PeriodeExtLine` | Read model |
| `Doc2PeriodeExtList` | Read model |
| `Doc2InterventionExtLine` | Read model |
| `Doc2InterventionExtList` | Read model |
| `Doc2ActiviteEnseignementLineSave` | Constructed by callers |
| `Doc2ActiviteEnseignementListSave` | Constructed by callers |
| `Doc2PeriodeExtLineSave` | Constructed by callers |
| `Doc2PeriodeExtListSave` | Constructed by callers |
| `Doc2InterventionExtLineSave` | Constructed by callers |
| `Doc2InterventionExtListSave` | Constructed by callers |
| `FormationDocument2` | Returned by `lire_document_2`, `modifier_document_2` |
| `Doc3EnseignantDetail` | Read model |
| `Doc3EnseignantList` | Read model |
| `Doc3ActiviteDetail` | Read model |
| `Doc3ActiviteListe` | Read model |
| `Doc3EnseignantDetailSave` | Constructed by callers |
| `Doc3EnseignantListSave` | Constructed by callers |
| `Doc3ActiviteDetailSave` | Constructed by callers |
| `Doc3ActiviteListeSave` | Constructed by callers |
| `FormationDocument3` | Returned by `lire_document_3`, `modifier_document_3` |

### Construction - Writer helpers (#34)

| Symbol | Notes |
|---|---|
| `ajouter_attributions_document_3` | Reads Doc 3, then writes the branches given with their current lines plus the new ones |
| `Doc1PopulationListSave.from_document` | Classmethod: the population of a Doc 1 read, for `approuver_document_1` |

### Construction - Document 1D (droits d'inscription, #33)

| Symbol | Notes |
|---|---|
| `lire_document_1d`, `modifier_document_1d`, `approuver_document_1d` | Functions, new in 0.3.0 |
| `FormationDocument1D`, `Doc1DDroitInscriptionLine`, `Doc1DDroitInscriptionList` | Read models |
| `Doc1DDroitInscriptionLineSave`, `Doc1DDroitInscriptionListSave` | Write models (`modifier_document_1d`) |
| `Doc1DDroitInscriptionLineAppr`, `Doc1DDroitInscriptionListAppr` | Approval models; `Doc1DDroitInscriptionListAppr.from_document` |

### Stable — Constants

| Symbol | Notes |
|---|---|
| `TYPES_INTERVENTION_EXTERIEURE` | Used in form dropdowns. **Legacy** list constant, deprecated in favor of the `TypeInterventionExterieure` Enum. Will be removed in 1.0.0. |

### Stable — Nomenclatures (Enums)

All use `(str, Enum)` base — members compare equal to their raw string value.

| Symbol | Notes |
|---|---|
| `TypeInterventionExterieure` | Intervention types for organisations (14 codes, `G` added in 0.3.0). Exported from `pyetnic.eprom`. |
| `CodeAdmission` | Admission codes. Exported from `pyetnic.eprom` and `pyetnic.seps`. |
| `CodeSanction` | Sanction codes. Exported from `pyetnic.eprom` and `pyetnic.seps`. |
| `MotifAbandon` | Abandon reasons. Exported from `pyetnic.eprom` and `pyetnic.seps`. |
| `DureeInoccupation` | Inoccupation duration codes. Exported from `pyetnic.eprom` and `pyetnic.seps`. |
| `SituationMenage` | Household situation codes. Exported from `pyetnic.eprom` and `pyetnic.seps`. |
| `CodeStatut` | Inscription status (DE/AN). Exported from `pyetnic.seps`. |
| `Indicateur` | Boolean indicator (O/N). Exported from `pyetnic.seps`. |
| `IndicateurX` | Ternary indicator (O/N/X). Exported from `pyetnic.seps`. |
| `MotifExemption` | DI exemption reasons (C01-C07). Exported from `pyetnic.seps`. |
| `MotifExemptionSpec` | DIS exemption reasons (C01-C13, non-EEC). Exported from `pyetnic.seps`. |
| `TypeEnseignement` | Education type (9 codes). Exported from `pyetnic.seps`. |
| `TitreDelivre` | Delivered titles (23 codes). Exported from `pyetnic.seps`. |
| `Equivalence` | Foreign-title equivalence (C01-C04). Exported from `pyetnic.seps`. |
| `ValorisationAcquis` | Prior-learning valorisation at admission. Exported from `pyetnic.seps`. |
| `ValorisationAcquisSanction` | Prior-learning valorisation at sanction. Exported from `pyetnic.seps`. |
| `StatutFinFormation` | End-of-training status (C01-C06, FSE). Exported from `pyetnic.seps`. |
| `CodeNiveau` | UE level code (SI/SS/SC/SL). Exported from `pyetnic.seps`. |

All SEPS inscription enums are pinned against `inscription_v1.xsd`.

### Stable — Exceptions

| Symbol | Notes |
|---|---|
| `EtnicError` | Base class, catch to handle any pyetnic error |
| `EtnicTransportError` | Network/SOAP-level failures |
| `EtnicBusinessError` | Server-side refusals (`success=False`) |
| `EtnicDocumentNotAccessibleError` | Document not yet reachable in the workflow (e.g. error 20102) |
| `EtnicNotFoundError` | Resource not found (e.g. error 00009) |
| `EtnicValidationError` | Input rejected by validation (most `20xxx`/`30xxx` codes, `4004`-`4012`, …) |
| `EtnicAlreadyApprovedError` | Document already approved: by the administration (1530) or, for Documents 1 and 1D, by the school (1545) |
| `EtnicConcurrencyError` | Record modified since read (00011), or an approval sent with values that differ from the stored ones (20104): re-read and retry |
| `SoapError` | **Deprecated** alias for `EtnicTransportError`. Will be removed in 1.0.0 |

---

## `pyetnic.seps` — SEPS namespace

### Stable — Functions (read only)

| Symbol | Notes |
|---|---|
| `lire_etudiant` | Used or planned for use in reading student records |
| `rechercher_etudiants` | Used for searches |
| `rechercher_inscriptions` | Promoted from construction (#24): used in production by a consuming application. Returns `[]` on 30102 / 30103 |

### Stable — Exceptions

| Symbol | Notes |
|---|---|
| `SepsEtnicError` | Base class, may be caught by callers |
| `SepsAuthError` | Subclass, may be caught |
| `NissMutationError` | Subclass with `ancien_niss`/`nouveau_niss` attrs, may be caught and inspected |
| `TropDeResultatsError` | Subclass, may be caught |

`SepsEtnicError` derives from `EtnicBusinessError` (#20): `except EtnicBusinessError` catches SEPS
refusals too. Every SEPS operation raises on `success=false`, whether the code comes as an error or
as a warning.

### Construction — Exceptions

Added by #20, not yet caught by a production caller.

| Symbol | Notes |
|---|---|
| `SepsValidationError` | BAD_REQUEST codes; also an `EtnicValidationError` |
| `SepsNotFoundError` | NOT_FOUND codes on writes; also an `EtnicNotFoundError` |
| `SepsUeInconnueError` | 30100, 30101 |
| `SepsEtudiantInconnuError` | 30011, 30120 |
| `SepsConflictError` | CONFLICT codes |
| `SepsInscriptionExisteError` | 30200 |
| `SepsEtudiantExisteError` | 30201, `cf_num` |
| `SepsDoublonsError` | 30202-30204, `cf_nums`, `niss` |
| `SepsAucuneModificationError` | 30443 |

### Stable — Dataclasses (read only)

| Symbol | Notes |
|---|---|
| `Etudiant` | Returned by `lire_etudiant`, `rechercher_etudiants` |
| `EtudiantDetails` | Nested in `Etudiant` |
| `SepsAdresse` | Nested |
| `SepsLocalite` | Nested |
| `SepsNaissance` | Nested |
| `SepsDeces` | Nested |
| `Inscription` | Returned by `rechercher_inscriptions`; promoted with it (#24) |
| `SepsUE` | Nested in `Inscription` |
| `SepsLieuCours` | Nested |
| `SepsSpecificite` | Nested |
| `SepsDroitInscription` | Nested |
| `SepsExempteDroitInscription` | Nested |
| `SepsDroitInscriptionSpecifique` | Nested |
| `SepsExempteDroitInscriptionSpec` | Nested |
| `SepsAdmission` | Nested |
| `SepsSanction` | Nested |

Adding optional fields to these read models (as the live SEPS contracts do) is a backwards-compatible change.

### Construction — Functions (write)

The following functions are **exported but not in production use**. They may be refactored, renamed, have their signatures changed, or be rewritten without notice until 1.0.0.

| Symbol | Notes |
|---|---|
| `enregistrer_etudiant` | Never used in production. Signature and behavior may change. |
| `modifier_etudiant` | Never used in production. |
| `enregistrer_inscription` | Never used in production. |
| `modifier_inscription` | Never used in production. |
| `mettre_a_jour_etudiant`, `mettre_a_jour_inscription` | Read, merge the changes given, write the complete record (#47); `EtudiantDetailsSave.from_details`, `InscriptionInputDataSave.from_inscription` |

### Construction — Notifications (#23)

| Symbol | Notes |
|---|---|
| `lire_notifications` | `lireNotifications`; X509 like the other SEPS services |
| `SepsNotification` | `id`, `cfNum`, `date`, `code`, `description` (absent for code 08) |
| `CodeNotification` | 02, 04, 05, 06, 07, 08 (manual 2.3; the contract only declares two digits) |

### Construction — Dataclasses (write)

| Symbol | Notes |
|---|---|
| `EtudiantDetailsSave` | Construction — input to `enregistrer_etudiant` / `modifier_etudiant` |
| `SepsAdresseSave` | Construction |
| `SepsNaissanceSave` | Construction |
| `InscriptionInputDataSave` | Construction |
| `InscriptionInputSave` | Construction |
| `SepsUESave` | Construction |
| `SepsSpecificiteSave` | Construction |

### Construction — Dataclasses (write results, #21)

The four SEPS writers return these. A refusal raises a `SepsEtnicError` instead: a result is always a success.

| Symbol | Notes |
|---|---|
| `SepsMessage` | One message of the answer: `niveau` (`error` / `warning` / `info`), `code`, `description` |
| `SepsEcritureResult` | Base: `code`, `messages`, `avertissements`, `a_le_code()` |
| `EnregistrerEtudiantResult` | `etudiant`, `bis_cree`, `cree` (201), `fusionne` (200) |
| `ModifierEtudiantResult` | `etudiant` |
| `InscriptionResult` | `inscription`, `plus_de_4_ue` (30051); returned by `enregistrer_inscription` and `modifier_inscription` |

### Construction - Dataclasses (inscription read, #22)

| Symbol | Notes |
|---|---|
| `SepsAudit` | `Inscription.audit`: creation and modification date and user kept by the server. Read in production (2026-11-24), no production caller yet |

---

## `pyetnic.config` — Configuration

### Stable

| Symbol | Notes |
|---|---|
| `Config` | The class itself |
| `Config.ENV` | Attribute |
| `Config.USERNAME` | Attribute (dynamic, depends on ENV) |
| `Config.PASSWORD` | Attribute (dynamic) |
| `Config.ANNEE_SCOLAIRE` | Attribute |
| `Config.ETAB_ID` | Attribute (type change allowed: `str` → `int` is a widening acceptable change per Sprint 2 Q4) |
| `Config.IMPL_ID` | Attribute (same) |
| `Config.SEPS_PFX_PATH` | Attribute |
| `Config.SEPS_PFX_PASSWORD` | Attribute |
| `Config.load_from_dotenv()` | Method |
| `Config.validate()` | Method |
| `Config.get_verify_ssl()` | Method (always true since 0.3.0) |
| `Config.RAISE_ON_ERROR` | Attribute, a `ContextVar`: true by default since 0.3.0; setting it false is deprecated (removed in 1.0) |

### Stable — Environment variables

| Variable | Purpose |
|---|---|
| `ENV` | `dev` or `prod` |
| `DEV_USERNAME`, `DEV_PASSWORD` | Dev credentials |
| `PROD_USERNAME`, `PROD_PASSWORD` | Prod credentials |
| `DEFAULT_SCHOOLYEAR` | Default school year |
| `DEFAULT_ETABID` | Default etabId |
| `DEFAULT_IMPLID` | Default implId |
| `SEPS_PFX_PATH` | PFX certificate path |
| `SEPS_PFX_PASSWORD` | PFX password |

---

## `pyetnic` — Top-level

### Stable

| Symbol | Notes |
|---|---|
| `pyetnic.eprom` | Namespace |
| `pyetnic.seps` | Namespace |
| `pyetnic.Config` | Re-exported |
| `pyetnic.__version__` | Version string |
| `strict_errors` | Context manager, also in `pyetnic.eprom`: raise inside the block (the default since 0.3.0) |
| `permissive_errors` | Context manager, also in `pyetnic.eprom`, new in 0.3.0 and **deprecated**: `None` instead of an exception inside the block; removed in 1.0 |

---

## Explicitly NOT stable (internal)

The following are internal implementation details. Direct imports from these modules are **not supported** and may break at any time:

- `pyetnic.soap_client` — internal SOAP client manager
- `pyetnic.services.*` — internal service classes (`OrganisationService`, `Document1Service`, etc.)
- `pyetnic.services.models` — if you need models, import from `pyetnic.eprom` or `pyetnic.seps`
- `pyetnic.cli` — internal CLI entry point

If a user needs something from these modules, the correct action is to open an issue and have it properly exported through the stable namespace.

---

## Review cadence

This document should be reviewed at the start of every sprint. If a symbol's production status has changed (newly used, or deprecated), update its classification here before starting the sprint work.
