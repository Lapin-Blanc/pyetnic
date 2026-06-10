# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [PEP 440](https://peps.python.org/pep-0440/) version
identifiers (a Python-flavoured variant of [Semantic Versioning](https://semver.org/)
that supports `bN` pre-releases).

## [Unreleased]

### Added

- **12 SEPS inscription nomenclature enums**, pinned against `inscription_v1.xsd`
  and exported from `pyetnic.seps`: `CodeStatut`, `Indicateur`, `IndicateurX`,
  `MotifExemption`, `MotifExemptionSpec`, `TypeEnseignement`, `TitreDelivre`,
  `Equivalence`, `ValorisationAcquis`, `ValorisationAcquisSanction`,
  `StatutFinFormation`, `CodeNiveau`.
- **`SepsSpecificiteSave.regulier1` / `regulier5`** input fields — the inscription
  input element is typed `SpecificiteDataType` (which carries them), not the dead
  `SpecificiteDataInputType`.

### Fixed

- **SEPS responses no longer fail to parse in production.** The SOAP client now
  builds its `zeep` client with `Settings(strict=False)`, so ETNIC production
  responses carrying elements absent from the embedded WSDL/XSD (e.g. the SEPS
  inscription `audit` block) are tolerated instead of raising `XMLParseError`.
  Applies to all services (EPROM and SEPS).
- **SEPS student services no longer swallow server errors as `None`.**
  `lire_etudiant`, `enregistrer_etudiant` and `modifier_etudiant` now inspect the
  response block and raise the typed SEPS exceptions (e.g. `SepsAuthError`,
  `SepsEtnicError`) instead of returning `None`. "Not found" codes (30110/30115)
  still yield `None`/`[]`.
- **A single `autrePrenom` is no longer split into characters** — `_as_list`
  treats `str`/`bytes` as a scalar element.
- **`creer_organisation` / `modifier_organisation` no longer serialize `None`
  fields** as empty XML elements (which ETNIC reads as "erase"); they are stripped
  like the document services.
- **`FormationsListeResult.messages` is now a flat `List[str]`** on error, instead
  of leaking the raw SOAP `messagesType` dict.
- **`Doc2ActiviteEnseignementLine` field order realigned to the XSD** (`coEtuReg`
  last; the four regroupement fields are required, no misleading `=0` defaults).
- **`extract_error_info` resolves `requestId` from the Common_v2 body attribute**
  (Organisation v7) when no SOAP header value is present.

## [0.1.0b1] - 2026-06-02

First public **beta** of the refactored library. This entry covers the whole
`0.0.12` → `0.1.0` delta: `0.0.12` is the last pre-refactor release on PyPI and
serves as the baseline. As a pre-release, `0.1.0b1` is **not** installed by
default — use `pip install --pre pyetnic`. Existing `0.0.12` users are not
auto-upgraded, so the refactored library can be beta-tested without disruption.

### Added

- **Public `pyetnic.eprom` and `pyetnic.seps` namespaces** as the supported
  import surface. All public functions, data models and exceptions are imported
  from these two namespaces.
- **Opt-in strict error mode.** `strict_errors()` context manager and the
  `Config.RAISE_ON_ERROR` flag make EPROM functions raise typed exceptions
  instead of returning `None`. The flag is backed by a `ContextVar`, so it is
  safe under threads and asyncio (each thread/task sees its own value). The
  default behaviour (return `None` on server error) is unchanged for backwards
  compatibility and is planned to flip to "raise" in `0.2.0`.
- **Typed exception hierarchy** rooted at `EtnicError`:
  `EtnicTransportError` (network/SOAP failures) and `EtnicBusinessError`
  (server-side `success=False` refusals), the latter specialised into
  `EtnicDocumentNotAccessibleError`, `EtnicNotFoundError` and
  `EtnicValidationError`.
- **`EtnicAlreadyApprovedError`** (ETNIC codes 1530 / 1545) and
  **`EtnicConcurrencyError`** (code 00011) exception classes, exported from the
  top-level package and the `eprom` namespace.
- **ETNIC error-code routing.** `map_etnic_error_code_to_class` now maps the
  full ETNIC error catalogue (~60 codes across the EPROM services, via a
  discrete table plus inclusive numeric ranges) onto the specialised
  `EtnicBusinessError` subclasses. Codes that are not client-fixable (00025
  security, 00999 internal SQL) deliberately stay on the base class.
- **Typed nomenclature Enums** (all `(str, Enum)`, so members compare equal to
  their raw string value): `TypeInterventionExterieure`, `CodeAdmission`,
  `CodeSanction`, `MotifAbandon`, `DureeInoccupation`, `SituationMenage`.
- **`py.typed` marker (PEP 561).** The package now ships inline type information
  to downstream type checkers.
- **Optional-dependency extras.** `[seps]` pulls in `xmlsec` for the SEPS X509
  signing path; `[excel]` pulls in `openpyxl`.

### Changed

- **`Config.ETAB_ID` and `Config.IMPL_ID` now return `int`** (previously `str`).
  A widening change: integer identifiers no longer need to be cast at call
  sites.
- **Business-error messages surface the real ETNIC code and description.**
  `str(exc)` now reads `ETNIC error {code}: {description}` (e.g. `ETNIC error
  30004: Le type d'intervention extérieure est incorrect`) instead of a generic
  "response was empty or success=False" placeholder.
- **Request serialization consolidated** behind internal helpers
  (`to_soap_dict`, `organisation_request_id`) shared across the EPROM document
  and SEPS write services.
- **Library logging** uses lazy `%s` formatting throughout, and verbose
  `pformat()` debug dumps are guarded by `logger.isEnabledFor(DEBUG)` so they
  cost nothing when debug logging is off.

### Fixed

- **`TypeInterventionExterieure` Enum values corrected** from long French labels
  to the single-letter codes ETNIC actually accepts
  (`A, B, C, D, E, F, I, J, K, P, Q, U, V`). The previous label values
  (e.g. `"Convention"`) were rejected by ETNIC with code 30004; the letter codes
  (e.g. `"C"`) are accepted. Enum member names are unchanged, and
  `TYPES_INTERVENTION_EXTERIEURE` auto-derives from the corrected values.
- **Single-element zeep collections are normalised correctly.** A shared
  `_as_list()` helper unifies the `None` / single-`dict` / `list` shapes zeep
  returns, fixing parsers that could mis-handle a one-element result (notably
  `lister_formations_organisables` and the Document 1/2/3 readers).
- **SEPS Inscriptions README example** no longer imports three non-existent
  symbols (`SepsDroitInscriptionSave`, `SepsAdmissionSave`, `SepsSanctionSave`),
  which raised `ImportError` on copy-paste.

### Removed

- **`requirements.txt`** — dependencies are declared in `pyproject.toml`;
  install with `pip install pyetnic` plus the extras you need.
- **`openpyxl` from the base dependencies** — moved to the `[excel]` extra. The
  base install is lighter; install `pyetnic[excel]` for the Excel export path.
- **`pyetnic/resources/Codes_Pays.xls`** — an unused 83 KB binary resource.

### Deprecated

- **`SoapError`** — a backwards-compatible alias for `EtnicTransportError`.
  Existing `except SoapError` code keeps working; the alias will be removed in
  `1.0.0`.
- **`TYPES_INTERVENTION_EXTERIEURE`** — the legacy list constant, superseded by
  the `TypeInterventionExterieure` Enum. Scheduled for removal in `1.0.0`.
- **The flat top-level namespace** (`pyetnic.lire_organisation`, …) — no longer
  documented. Import from `pyetnic.eprom` / `pyetnic.seps` instead.

[Unreleased]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.1.0b1...HEAD
[0.1.0b1]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.0.12...v0.1.0b1
