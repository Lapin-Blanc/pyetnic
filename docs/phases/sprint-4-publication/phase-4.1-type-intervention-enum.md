# Phase 4.1 — Fix `typeInterventionExterieure` Enum values (correctness)

## Context

The H9 Enum `TypeInterventionExterieure` (`pyetnic/nomenclatures.py`) stores **long French
labels** (`"Convention"`, `"Agence Qualité"`, …). A live dev-server write/echo probe on
2026-06-01 proved this is **wrong**:

- `creer_organisation(typeInterventionExterieure="Convention")` → **rejected, code `30004`**
  ("Le type d'intervention extérieure est incorrect").
- `creer_organisation(typeInterventionExterieure="C")` → **accepted**, read back as `"C"`.

ETNIC wants the **single-letter code**, not the label. Authoritative table:
`specs/02_formation_organisation_v7.md` §"Valeurs de typeInterventionExterieure" (validated
2025-06-10). The field is a free `xs:string` (not XSD-validated), so the Enum is convenience
only — but its values must be the ones ETNIC accepts.

This is **not a breaking change**: the Enum was added in Sprint 2 (H9), so it does not exist in
the published `0.0.12`; and the old label values never worked against ETNIC.

## Objective

Replace the 13 Enum **values** (labels → single-letter codes), fix the now-falsified docstrings,
and pin the values with tests. Member **names are unchanged** — only the right-hand-side values.

## Tasks

### 1. Swap the 13 values in `pyetnic/nomenclatures.py`

| Member (unchanged) | Old value | New value |
|---|---|---|
| `PERSONNEL_NON_CHARGE_DE_COURS` | "Personnel non chargé de cours" | `"A"` |
| `OCTROI_PERIODES_SUPPLEMENTAIRES_BONUS` | "Octroi périodes supplémentaires-bonus" | `"B"` |
| `CONVENTION` | "Convention" | `"C"` |
| `DISCRIMINATIONS_POSITIVES` | "Discriminations positives" | `"D"` |
| `EHR` | "EHR" | `"E"` |
| `FONDS_EUROPEENS` | "Fonds Européens" | `"F"` |
| `FORMATION_PUBLICS_INFRA_SCOLARISES` | "Formation des publics infra scolarisés" | `"I"` |
| `REORIENTATION_7TQ_7P` | "Réorientation 7TQ/7P" | `"J"` |
| `OCTROI_PERIODES_CABINET_PROJETS_TRANSVER` | "Octroi périodes cabinet-projets transver" | `"K"` |
| `FORMATIONS_CONTINUEES` | "Formations continuées" | `"P"` |
| `AGENCE_QUALITE` | "Agence Qualité" | `"Q"` |
| `UNION_EUROPEENNE` | "Union Européenne" | `"U"` |
| `VALIDATION_DES_COMPETENCES` | "Validation des compétences" | `"V"` |

Note: codes `R` (Récupération périodes) and `S` (CISCO Système) are **removed** by ETNIC and
have no current member — do **not** add them. Reading a legacy org with value `"R"`/`"S"` still
works (the dataclass stores the raw string; the Enum simply has no member for it).

### 2. Fix the falsified docstrings

In `nomenclatures.py`:
- Module docstring (~lines 14-16): drop "these labels are what ETNIC expects verbatim" — replace
  with "single-letter codes from the Organisation v7 manual (validated 2025-06-10); the XSD type
  is a free `xs:string` so they are not contract-validated".
- Class docstring + usage example (~lines 22-25): change `= "Convention"` to `= "C"`.

`TYPES_INTERVENTION_EXTERIEURE` is derived from the Enum (`[m.value for m in …]`), so it updates
automatically — verify, do not hand-edit.

### 3. Update the pinned assertions in `tests/unit/test_nomenclatures.py`

Lines ~19/27/28 assert `== "Convention"` (value and `(str, Enum)` equality both directions).
Change them to `"C"`. These are your **red→green** signal.

### 4. Add a drift-guard regression test

Add a test that pins the full name→letter mapping (a dict literal compared against
`{m.name: m.value for m in TypeInterventionExterieure}`) so a future edit cannot silently
reintroduce labels.

### 5. (Optional) Promote the probe to a guarded integration test

Move `/tmp/probe_tie.py` into `tests/integration/eprom/test_type_intervention_integration.py`,
gated on `Config.ETAB_ID`/`IMPL_ID` like the existing org fixture, asserting `"Convention"` →
`EtnicBusinessError(code="30004")` and `"C"` → accepted. Optionally spot-check `"Q"` and the new
`"J"` while you have the dev server, to confirm the spec table beyond `"C"`.

### 6. Verify

`.venv/bin/pytest tests/regression/ tests/unit/` — green.

## Constraints

- Member **names** unchanged; only values. `(str, Enum)` semantics preserved.
- **Do not** confuse this field with Document 2's `coCatCol` (a separate two-level
  type/sub-type system — see `specs/04_formation_periodes_v1.md`).
- One commit: `fix(sprint-4): phase 4.1 — correct typeInterventionExterieure Enum to letter codes`.

## Validation

- [ ] 13 Enum values are single letters (A,B,C,D,E,F,I,J,K,P,Q,U,V)
- [ ] `nomenclatures.py` docstrings no longer claim labels are expected verbatim
- [ ] `TYPES_INTERVENTION_EXTERIEURE` now lists letters (auto-derived)
- [ ] `test_nomenclatures.py` assertions updated to `"C"`
- [ ] Drift-guard test added
- [ ] (optional) Integration probe promoted; `"Convention"` → 30004 confirmed
- [ ] Suite green
