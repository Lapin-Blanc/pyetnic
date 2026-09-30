# Examples

Operational scripts showing real-world usage of pyetnic against live ETNIC services. They
import only the public namespaces (`pyetnic.eprom`, `pyetnic.seps`, `pyetnic.config`).

## Contents

- **`extrait_profs.py`** - extracts the list of teachers from Document 3 for a given school year.
- **`print_doc2.py`** - writes a formatted Excel view of Document 2 (periods of teaching activity). Needs the `excel` extra.
- **`print_doc3.py`** - writes a formatted Excel view of Document 3 (teacher assignments). Needs the `excel` extra.
- **`audit_coherence_doc1_seps.py`** - cross-checks the Doc 1 population of each organisation
  against the SEPS inscriptions and reports the discrepancies only. Needs the `seps` extra and
  a production `.env` (SEPS runs in production only).

These scripts require a valid `.env` with ETNIC credentials (`pyetnic init-config` generates
the template). Adapt `etab_id`, `num_adm_formation`, etc. to your own establishment.

Computations derived from the documents (student-periods, staffing, allocation of periods)
are deliberately out of scope: see "Out of scope" in `docs/ARCHITECTURE.md`.
