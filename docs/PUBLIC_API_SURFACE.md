# Public API Surface

> **Status**: Authoritative reference for `BACKWARDS_COMPAT.md`
> **Last reviewed**: Sprint 0

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
| `approuver_document_1` | Used in production scripts |
| `lire_document_2` | Used in production scripts |
| `modifier_document_2` | Used in production scripts |
| `lire_document_3` | Used in production scripts |
| `modifier_document_3` | Used in production scripts |

### Stable — Dataclasses

| Symbol | Notes |
|---|---|
| `OrganisationId` | Constructed by callers |
| `Organisation` | Returned by `lire_organisation`, `creer_organisation`, `modifier_organisation` |
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

### Stable — Constants

| Symbol | Notes |
|---|---|
| `TYPES_INTERVENTION_EXTERIEURE` | Used in form dropdowns |

---

## `pyetnic.seps` — SEPS namespace

### Stable — Functions (read only)

| Symbol | Notes |
|---|---|
| `lire_etudiant` | Used or planned for use in reading student records |
| `rechercher_etudiants` | Used for searches |

### Stable — Exceptions

| Symbol | Notes |
|---|---|
| `SepsEtnicError` | Base class, may be caught by callers |
| `SepsAuthError` | Subclass, may be caught |
| `NissMutationError` | Subclass with `ancien_niss`/`nouveau_niss` attrs, may be caught and inspected |
| `TropDeResultatsError` | Subclass, may be caught |

### Stable — Dataclasses (read only)

| Symbol | Notes |
|---|---|
| `Etudiant` | Returned by `lire_etudiant`, `rechercher_etudiants` |
| `EtudiantDetails` | Nested in `Etudiant` |
| `SepsAdresse` | Nested |
| `SepsLocalite` | Nested |
| `SepsNaissance` | Nested |
| `SepsDeces` | Nested |

### Construction — Functions (write)

The following functions are **exported but not in production use**. They may be refactored, renamed, have their signatures changed, or be rewritten without notice until 1.0.0.

| Symbol | Notes |
|---|---|
| `enregistrer_etudiant` | Never used in production. Signature and behavior may change. |
| `modifier_etudiant` | Never used in production. |
| `enregistrer_inscription` | Never used in production. |
| `modifier_inscription` | Never used in production. |
| `rechercher_inscriptions` | Never used in production. Even though it's a read operation, it's classified construction because no test harness or production caller exists. |

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

### Construction — Dataclasses (inscription read)

The following are returned by `rechercher_inscriptions`, which is itself classified construction.

| Symbol | Notes |
|---|---|
| `Inscription` | Construction |
| `SepsUE` | Construction |
| `SepsLieuCours` | Construction |
| `SepsSpecificite` | Construction |
| `SepsDroitInscription` | Construction |
| `SepsExempteDroitInscription` | Construction |
| `SepsDroitInscriptionSpecifique` | Construction |
| `SepsExempteDroitInscriptionSpec` | Construction |
| `SepsAdmission` | Construction |
| `SepsSanction` | Construction |

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
| `Config.get_verify_ssl()` | Method |

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

---

## Explicitly NOT stable (internal)

The following are internal implementation details. Direct imports from these modules are **not supported** and may break at any time:

- `pyetnic.soap_client` — internal SOAP client manager
- `pyetnic.services.*` — internal service classes (`OrganisationService`, `Document1Service`, etc.)
- `pyetnic.services.models` — if you need models, import from `pyetnic.eprom` or `pyetnic.seps`
- `pyetnic.log_config` — internal
- `pyetnic.cli` — internal CLI entry point

If a user needs something from these modules, the correct action is to open an issue and have it properly exported through the stable namespace.

---

## Review cadence

This document should be reviewed at the start of every sprint. If a symbol's production status has changed (newly used, or deprecated), update its classification here before starting the sprint work.
