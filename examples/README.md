# Examples

These are operational scripts written during development. They demonstrate real-world usage of pyetnic against live ETNIC services.

## Contents

- **`extrait_profs.py`** — extracts the list of teachers from Document 3 for a given school year.
- **`print_doc2.py`** — prints a formatted view of Document 2 (periods of teaching activity).
- **`print_doc3.py`** — prints a formatted view of Document 3 (teacher assignments).
- **`calcul_pep_annee_civile.py`** — computes the weighted student-periods (PEP, dotation
  assessment base) of a civil year and writes a markdown report. Validated at +0.46 % against
  the official host figures for 2025 (see `specs/21_calcul_encadrement_dotation.md`).
- **`calcul_pe_encadrement.py`** — estimates the raw student-periods (PE, staffing side) of a
  civil year. Validated at ±1 % against the official host figures for 2025.

The two financing scripts are demonstrations, not a supported API: by design the financing
engine lives **outside** pyetnic (spec 21 §7) — pyetnic stays a faithful SOAP client.

These scripts require a valid `.env` with ETNIC credentials. Adapt `etab_id`, `num_adm_formation`, etc. to your own establishment.
