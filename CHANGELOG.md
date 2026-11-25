# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [PEP 440](https://peps.python.org/pep-0440/) version
identifiers (a Python-flavoured variant of [Semantic Versioning](https://semver.org/)
that supports `bN` pre-releases).

## [Unreleased]

### Added

- **`Sexe` and `ModeEnregistrement`** (#50), exported from `pyetnic.seps`: the SEPS student
  value sets (`M` / `F` / `X`; `NISS` / `DETAILS`), pinned against the embedded XSD like the
  other SEPS enums. Strings keep working.
- **`EtnicResponseError`** (#52), exported from `pyetnic` and `pyetnic.eprom`: raised when a
  response value does not match its type in the contract (a decimal in an `xs:int`). zeep
  logged such a value and handed `None` on, as if the element were absent, so a
  read-merge-write could erase it. The error carries `values` (each failed element and its
  raw text), `response` (the whole answer, failed values at `None`) and `request_id`. It is
  not a refusal: the deprecated permissive mode does not turn it into `None`. No such value
  has been observed; detection relies on zeep's error log, and a warning is logged once when
  that log is silenced.

### Changed

- **The identifier returned is read** (#51). `lire_organisation`, `modifier_organisation`, the
  readers and writers of Documents 1, 1D, 2 and 3 now return the `id` of the answer, whose
  `implId` the server fills (observed on TQ and in production, 2026-11-25, every reader),
  instead of the caller's `OrganisationId`; a part the answer lacks comes from the caller's.
  `lister_formations` fills `implId` from the request when the answer omits it: the server
  names the implantation only when the request does not, and a request filtered on it lists
  that implantation alone. An `OrganisationId` built without `implId` no longer compares
  equal to the `id` read back; requests are unchanged (`implId` is never sent but to
  `creer_organisation`).

### Deprecated

- **`SoapError` and `TYPES_INTERVENTION_EXTERIEURE` now warn** (#53). Both were documented as
  deprecated since 0.1.0 without a warning; importing or reading them from `pyetnic`,
  `pyetnic.eprom` or `pyetnic.nomenclatures` now emits a `DeprecationWarning` naming the
  replacement (`EtnicTransportError`, the `TypeInterventionExterieure` enum), and they left
  `__all__`. They still work and go in 1.0, with the permissive mode.

### Fixed

- **An enum member goes on the wire as its code** (#50). zeep writes a simple value with
  `str()`, and `str()` of a `(str, Enum)` member is its name: `CodeStatut.DEFINITIVE` was
  sent as `"CodeStatut.DEFINITIVE"` instead of `"DE"`. `SoapClientManager.call_service` now
  replaces every member by its value, at any depth of the request. Code that passed
  `.value` is unaffected.

## [0.3.0b2] - 2026-11-25

Two SEPS writers that keep the fields a modification would otherwise erase. No breaking change.

### Added

- **SEPS writers that keep the fields left out** (#47): `mettre_a_jour_etudiant(cf_num,
  changements)` and `mettre_a_jour_inscription(cf_num, annee_scolaire, etab_id,
  no_administratif, no_organisation, ...)` read the record, apply only the changes given and
  send it complete, since `modifierEtudiant` and `modifierInscription` erase every optional
  field left out; `EtudiantDetailsSave.from_details` and
  `InscriptionInputDataSave.from_inscription` give a record as read, ready to send back.
  Tested in production (2026-11-25): a merge changed only the field given, and a write without
  a field erased it. `regulier3` and `ajournement1Session` cannot be kept: no read returns them.

## [0.3.0b1] - 2026-11-24

The EPROM side catches up with SEPS: Formation Organisation v8, the Document 1D
service, typed errors raised by default, and specs reviewed against the latest manuals.

**Upgrading from 0.2.0b1** (three breaking changes):

1. **EPROM refusals raise.** Readers and writers raise the typed `EtnicBusinessError`
   subclass of the code instead of returning `None` (`FormationsListeResult(success=False)`
   for `lister_formations*`, `False` for `supprimer_organisation`). Catch
   `EtnicDocumentNotAccessibleError` where a document may not be reachable yet (20101,
   20102, 20103), `EtnicBusinessError` for the rest. While migrating, code that still tests
   for `None` can run inside `permissive_errors()`, deprecated and removed in 1.0.
2. **`approuver_document_1` needs the population**:
   `approuver_document_1(org_id, Doc1PopulationListSave.from_document(lire_document_1(org_id)))`.
   A call without it never succeeded (error 20104).
3. **New endpoints.** Every EPROM service is called on `ws.etnic.be` (`ws-tq.etnic.be` on
   TQ), port 443, instead of `services-web(.tq).etnic.be:11443`; a firewall that only
   allowed the old hosts must allow the gateway. Organisation is v8: same functions,
   `Organisation` gains `BESAeSI`.

### Added

- **Contract watch for every service** (#31): `tools/refresh_contracts.py` replaces
  `tools/refresh_seps_contracts.py`. It reads the services from `Config.SERVICES` and
  compares, in canonical form, the embedded WSDL and XSD with the live gateway (whole
  contract where the gateway serves the schemas, WSDL alone where it does not) and with
  the SOA catalogue's contract archive; it also reports a next major version that is
  live, the catalogue's version and endpoints when they differ from pyetnic's, a manual
  revision that the matching spec does not name, and a catalogue service pyetnic does not
  embed. Without `--check` it refreshes the files, creating a new service folder from
  the catalogue archive. A weekly GitHub Actions workflow runs the gateway part
  (`--no-catalogue`: the catalogue closes the connection of the GitHub runners) and opens,
  updates or closes an issue labelled `contract-watch`.
- **Formation Organisation v8** (#32): `Organisation.BESAeSI` and the `BESAeSI` parameter
  of `creer_organisation` (a unit given only for the BES "assistant en soins infirmiers",
  from school year 2026-2027); `TypeInterventionExterieure.BES` (code `G`, new in v8);
  errors 20042 and 30010 routed to `EtnicValidationError`.
- **Document 1D service, "droits d'inscription"** (#33): `lire_document_1d`,
  `modifier_document_1d` and `approuver_document_1d` in `pyetnic.eprom`, with
  `FormationDocument1D` and the `Doc1DDroitInscription*` read, save and approval models;
  `Doc1DDroitInscriptionListAppr.from_document` builds the approval from a read. Its
  contract comes from the catalogue archive. Its life cycle was tested on TQ: the fee is
  refused before the population is approved (error 20112), an approval with other values
  is refused (20104), and the reading is refused before the Doc A is approved (20101,
  production).
- **`ajouter_attributions_document_3`** (#34): adds teacher attributions without deleting
  the others. `modifier_document_3` replaces the teacher list of every branch it sends;
  this writer reads the document, then sends each branch given with its current lines (and
  their `coNumAttribution`, which the server keeps) followed by the new ones. Tested on TQ.
- **`Doc1PopulationListSave.from_document(doc)`** (#34) builds the approval of a Doc 1 from
  a read.
- **Error routing per service**: `map_etnic_error_code_to_class(code, service=None)`
  and `signal_business_error(..., service=None)` take the `Config.SERVICES` name of the
  service that answered, for codes whose meaning depends on it.
- **Every model mirroring an XSD type is checked against it** (`tests/unit/test_models_contract.py`):
  element names, simple types and optional elements, for the EPROM and SEPS models, with the
  deliberate differences listed.

### Changed

- **EPROM services raise on a server refusal by default** (#35, breaking):
  `Config.RAISE_ON_ERROR` is true by default, as SEPS always behaved. A refusal raises the
  typed `EtnicBusinessError` subclass of its code, `lister_formations*` raise instead of
  returning `FormationsListeResult(success=False)` (a transport failure there raises
  `EtnicTransportError`), and `supprimer_organisation` raises instead of returning `False`.
  The pre-0.3.0 behaviour stays available, **deprecated**, inside `permissive_errors()` (new,
  exported from `pyetnic` and `pyetnic.eprom`) or with `Config.RAISE_ON_ERROR = False`; both
  emit a `DeprecationWarning` and go in 1.0. `strict_errors()` keeps working.
- **`approuver_document_1` requires `population_liste`** (#34, breaking): the server
  compares it with the stored population and refused every call without it (error
  20104). A call without it now raises `TypeError` before reaching the server. Pass
  `Doc1PopulationListSave.from_document(lire_document_1(org_id))`.
- **Formation Organisation v8 replaces v7** (#32): the embedded contract, endpoint and
  binding are v8's; v7 is no longer embedded. The functions keep their signatures and
  `Organisation` gains one optional field, last.
- **Every EPROM service is called on the ETNIC gateway** (#32), at the address the SOA
  catalogue announces: `ws.etnic.be` / `ws-tq.etnic.be` instead of
  `services-web(.tq).etnic.be:11443` for Formations Liste and Documents 1 to 3. Reads
  checked on TQ and in production on 2026-11-24.
- **TLS certificates are verified on TQ too** (#32): `Config.get_verify_ssl()` is always
  true; the gateway's certificates chain to a public CA in both environments.
- **`modifier_organisation` documents what the server does with an omitted field**: it
  resets it (a flag to `False`) instead of keeping it (tested on TQ, 2026-11-24). Send the
  organisation as read, changes applied.
- **EPROM specs 01 to 06 reviewed** (#36, docs): every statement is sourced (manual and
  page, contract, dated production or TQ observation, or marked unknown); spec 02 follows
  Organisation v8 (manual rev 6.0), spec 04 the Périodes manual rev 1.4 (intervention type
  `G` "BES" with sub-type `AI`, `J` with `OA`, error 20041), specs 01, 03, 05 and 06 their
  current revision; the manuals' contradictions with the contracts are listed; the
  "Mapping pyetnic" sections describe the current API; regulatory wording is removed. The
  EPROM part of `specs/00_REGISTRE.md` follows (error routing table, gateway endpoints,
  SOAP 1.1 only).
- **Integration tests always run on TQ** (`tests/integration/conftest.py`), whatever
  `.env` says: several of them write.
- **The version has a single source** (#37): `pyproject.toml` reads `pyetnic.__version__`
  (`dynamic`), and the publish workflow checks the tag against it.
- **Packaging** (#37): `CHANGELOG.md` is in the sdist, which carries only the contract files
  of `pyetnic/resources` (a stray local file can no longer slip in) and no bytecode; the
  GitHub Actions run on Node 24 (`actions/checkout@v7`, `actions/setup-python@v7`).

### Deprecated

- **The permissive error mode** (#35): `permissive_errors()` and
  `Config.RAISE_ON_ERROR = False`, which give back the pre-0.3.0 `None` contract, emit a
  `DeprecationWarning` and will be removed in 1.0.

### Removed

- **The Formation Organisation v7 contract** (#32): v8 replaces it; the v7 manual stays in
  `documentation/` for the specs' history.
- **`tools/refresh_seps_contracts.py`** (#31): replaced by `tools/refresh_contracts.py`,
  which covers every service.

### Fixed

- **Error 1545 from Document 2** ("you cannot create a fifth external intervention") is an
  `EtnicValidationError`; it was read as `EtnicAlreadyApprovedError`, its meaning in
  Documents 1 and 1D.
- **Workflow refusals are typed**: 20101 (Doc A not approved, Documents 1 and 1D), 20103
  (Doc 1 population not validated, Document 2) and 20112 / 1546 (Document 1D fee before the
  population is approved) raise `EtnicDocumentNotAccessibleError`, like 20102; 20104 (an
  approval with values that differ from the stored ones) raises `EtnicConcurrencyError`.
  They raised the base `EtnicBusinessError`, which they still derive from.
- **Document 3 refusals are typed** (#36): 1538 and 1574 to 1576 (periods above a ceiling),
  20108 to 20110 (unknown staff number, availability code or status) raise
  `EtnicValidationError` instead of the base `EtnicBusinessError`.
- **`Doc3ActiviteDetail` counters are `Optional[int]`** (#36, audit D7):
  `nbPeriodesDoc8`, `nbPeriodesPrevuesDoc2` and `nbPeriodesReellesDoc2` are `xs:int` in the
  contract and zeep always returned integers; the `float` annotation was wrong.
- **`SepsDeces.date` is annotated `Optional[date]`**: inside its class body the name `date`
  was bound to the default before the annotation was evaluated, which made it `NoneType`.
- **A request that breaks the embedded contract raises `EtnicValidationError`** (#36):
  zeep refuses it before sending (a required element missing, a `[1..*]` list empty, as
  in a Doc 3 write without any branch), and its `ValidationError` escaped as a non-pyetnic
  exception. `except EtnicError` now catches it.
- **`lister_formations*` on a success without `response`** (the contract allows it)
  return an empty list instead of raising `AttributeError`.
- **Error 20041 from Document 2** (an intervention type without the sub-type it imposes,
  new in the Périodes manual rev 1.4) raises `EtnicValidationError`.

## [0.2.0b1] - 2026-11-24

The SEPS module follows the live production contracts. **Upgrading from 0.1.0b2:**
the four SEPS writers return a result object instead of the bare `Etudiant` /
`Inscription`, which is now in `.etudiant` / `.inscription` (see *Changed*).

### Added

- **SEPS Notifications service** (#23): `pyetnic.seps.lire_notifications(etab_id, date_debut)`
  returns `SepsNotification` (`id`, `cfNum`, `date`, `code`, `description`), the identity
  changes of an establishment's students since a date; `CodeNotification` names the codes
  (02, 04, 05, 06, 07 and 08, new in manual 2.3). Its live contract is embedded and refreshed
  by `tools/refresh_seps_contracts.py`. Authentication is X509: production refuses the
  UsernameToken the catalogue announces (2026-11-24).
- **SEPS models follow the live production contract** (#22). Read: `Inscription.audit`
  (`SepsAudit`: `dateCreation`, `utilisateurCreation`, `dateModification`,
  `utilisateurModification`), `Etudiant.bisCreated`, `SepsSpecificite.regulier3`, `montant`
  on `SepsDroitInscription` and `SepsDroitInscriptionSpecifique`, and on `SepsSanction`
  `pourcentageAttribue`, `codeSectionFlag`, `codeSection`, `point`, `ajournement1Session`.
  Write: `SepsSpecificiteSave.regulier3` (production `enregistrerInscription` only),
  `InscriptionInputSave.fse`, and the same fee and sanction fields. Enums:
  `CodeAdmission.AUCUN`, `ValorisationAcquis.C50`, `MotifExemptionSpec.C50`; every SEPS enum
  is now checked against the embedded XSD.
- **SEPS write results** (#21), exported from `pyetnic.seps`: `SepsMessage`,
  `SepsEcritureResult`, `EnregistrerEtudiantResult` (`cree` for 201, `fusionne` for 200,
  `bis_cree`), `ModifierEtudiantResult`, `InscriptionResult` (`plus_de_4_ue` for 30051).
- **Typed SEPS refusals** (#20), exported from `pyetnic.seps`: `SepsValidationError`
  (the manual's BAD_REQUEST codes, also an `EtnicValidationError`), `SepsNotFoundError`
  (NOT_FOUND, also an `EtnicNotFoundError`) with `SepsUeInconnueError` (30100, 30101) and
  `SepsEtudiantInconnuError` (30011, 30120), `SepsConflictError` with
  `SepsInscriptionExisteError` (30200), `SepsEtudiantExisteError` (30201, `cf_num`) and
  `SepsDoublonsError` (30202-30204, `cf_nums`, `niss`), `SepsAucuneModificationError`
  (30443). `TropDeResultatsError` also covers 30503.
- **`tools/refresh_seps_contracts.py`** refetches the SEPS contracts from the live
  services and rewrites their imports to the local files; `--check` reports the
  drift without writing.

### Changed

- **`SepsSanction.codeSanction` is optional** (#22), as in the live contract.
- **SEPS specs rebuilt from the June 2026 manuals, the live contracts and production
  facts** (#24, docs only): specs 09 to 15 and the SEPS part of `specs/00_REGISTRE.md`
  now follow the user manuals Enregistrer Étudiants 2.3, Enregistrer and Recherche
  Inscriptions 2.4 and Notifications 2.3 (the 2.1.9 manual stays the only source for
  Recherche Étudiants), the production contracts embedded in `pyetnic/resources`, and
  dated production observations: inscriptions accepted before the Doc A is approved,
  SEPS learning EPROM organisations with a delay, deleted organisations purging their
  inscriptions, `dateRequete` as a point-in-time read, 30103 not telling an unknown UE
  from an empty one, a NISS search returning a student without CF number, 30502 for a
  name search that finds nobody. The manual's contradiction on `doubleFlag` in NISS mode
  is documented as unresolved, with a safe practice. Each "Mapping pyetnic" section
  describes the current API instead of the old proposals. `rechercher_inscriptions` and
  its read dataclasses are reclassified **stable** in `docs/PUBLIC_API_SURFACE.md`: a
  consuming application uses them in production.
- **The SEPS writers return the server's code and messages** (#21, construction symbols):
  `enregistrer_etudiant` returns `EnregistrerEtudiantResult`, `modifier_etudiant`
  `ModifierEtudiantResult`, `enregistrer_inscription` and `modifier_inscription`
  `InscriptionResult`, instead of the bare `Etudiant` / `Inscription` (now in `.etudiant` /
  `.inscription`). A creation (201) and a merge with an existing record (200) can be told
  apart, and 30051 is no longer lost.
- **`SepsEtnicError` derives from `EtnicBusinessError`** (#20): `except EtnicBusinessError`
  and `except EtnicError` now catch SEPS refusals too. Names, constructors and the existing
  subclasses are unchanged; a SEPS error carries `request_id` when the answer has one.
- **The embedded SEPS contracts come from the live production services**
  (`https://ws.etnic.be/seps/<service>/v1?wsdl` and the schemas it imports), not
  from the SOA catalogue, whose "2.1" archives lag behind (checked 2026-11-24). The
  new schemas add, all optional: `audit` (creation and modification date and user)
  on every inscription, `bisCreated` on the student, `montant` on both enrolment
  fees, the input flag `fse`, `pourcentageAttribue`, `codeSectionFlag`,
  `codeSection` and `point` on the sanction, the admission code `AUCUN` and the
  codes `C50`; `enregistrerInscription` alone also has `regulier3` and
  `ajournement1Session` (user manual 2.4). Production's `rechercheInscriptions`
  still serves the schema without these two, and TQ lags behind production.
  Requests built with the previous contracts stay valid. Folder names are kept.
- **Documentation of server behaviour observed in production** (docs only, no code
  change): Doc 3 ceiling, `coDispo` wire format, skeleton documents, error 20108,
  organisation creation and deletion, errors 20010 and 20030, document statuses,
  Doc 1 and Doc 2 field mappings. Each statement says how often it was observed.
- **Open points settled by tests on the ETNIC test environment (TQ)**: Doc 2 updates
  line by line, its first write sets "Encodé école", errors 20101 and 20103 before
  a document is reachable, organisation numbering (highest + 1),
  `nombreSemaineFormation` capped at 40, the 20011 bound.
- **`lister_formations` and `lister_formations_organisables` have docstrings**
  warning that a permissive-mode failure looks like an empty result.
- **Examples and tests use fictitious establishment and implantation numbers**
  (`1234` / `5678`), and the package metadata no longer carries an email address.

### Fixed

- **A SEPS refusal carried as a warning was swallowed** (#20). The inscription services
  read only `messages.error`, so `success=false` with the warning 30101 (seen in production,
  2026-11-10) returned `None`, like a success without data. One check now serves the seven
  SEPS operations: `success=false` raises whether the code is an error or a warning; reads
  return `None` / `[]` on their "nothing found" codes (30110, 30115; 30102, 30103).
- **README: the Doc 1 approval example** now reads the population back and sends
  it with `approuver_document_1`; the bare call always failed with error 20104.
- **README: the Doc 3 example** no longer sends `coNumAttribution`, which targets
  nothing.
- **Docs: wrong statements corrected.** The 1574 ceiling ignores lines carrying a
  `coDispo`; `coDispo` codes travel on two digits (`05`, not `5`);
  `statutDocumentPopulationPeriodes` covers Doc 1 and Doc 2; the Doc 1 bounds of
  `Dem` / `Min` / `Exm` are the pupils counted once, not `nbElevePl`; An1 / An2 are
  civil years.

## [0.1.0b2] - 2026-11-10

### Added

- **12 SEPS inscription nomenclature enums**, pinned against `inscription_v1.xsd`
  and exported from `pyetnic.seps`: `CodeStatut`, `Indicateur`, `IndicateurX`,
  `MotifExemption`, `MotifExemptionSpec`, `TypeEnseignement`, `TitreDelivre`,
  `Equivalence`, `ValorisationAcquis`, `ValorisationAcquisSanction`,
  `StatutFinFormation`, `CodeNiveau`.
- **`SepsSpecificiteSave.regulier1` / `regulier5`** input fields — the inscription
  input element is typed `SpecificiteDataType` (which carries them), not the dead
  `SpecificiteDataInputType`.

### Changed

- **Examples use the public namespaces only** (`pyetnic.eprom`, `pyetnic.config`)
  instead of `pyetnic.services.*`, and configure logging themselves.
- **The writers' docstrings say what the server really does**, as seen in
  production: `modifier_document_3` replaces the teacher list of every branch it
  sends; `approuver_document_1` needs the population sent back (error 20104);
  `creer_organisation` gets its number in declaration order; `lire_organisation`
  never carries the document statuses; `lire_document_2` is `None` until the
  Doc 1 population is validated; the SEPS modifiers erase every optional field
  left out. No signature changes.
- **"Doc A" is the organisation**: error 20102 and the workflow documentation
  no longer read it as the Doc 1 population.

### Removed

- **`pyetnic.log_config`** (internal): it called `logging.basicConfig()`, which a
  library must never do. Applications configure logging.
- **Regulatory and school-specific material** from the repository: circular
  analyses, the financing calculation spec and its PE/PEP demo scripts, and the
  production test reports of one establishment. pyetnic documents the ETNIC SOAP
  contracts; derived computations belong to the consuming applications.

### Security

- **Documentation examples use fictitious identifiers only.** The README example
  carried a teacher staff number copied from an ETNIC manual, and so did the
  description of every release from 0.0.4 to 0.1.0b1, which are withdrawn from
  PyPI. The repository history was rewritten on 2026-11-10: clones made earlier
  must be re-cloned.

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

[Unreleased]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.3.0b2...HEAD
[0.3.0b2]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.3.0b1...v0.3.0b2
[0.3.0b1]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.2.0b1...v0.3.0b1
[0.2.0b1]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.1.0b2...v0.2.0b1
[0.1.0b2]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.1.0b1...v0.1.0b2
[0.1.0b1]: https://github.com/Lapin-Blanc/pyetnic/compare/v0.0.12...v0.1.0b1
