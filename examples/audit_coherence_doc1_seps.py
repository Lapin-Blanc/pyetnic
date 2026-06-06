"""Audit: cross-check declared EPROM Doc 1 population against real SEPS inscriptions.

For a given établissement and school year, compare — per organisation — the
headcount declared in the EPROM Document 1 (population, which drives funding)
with the number of real inscriptions recorded in SEPS. Only discrepancies are
reported.

Aggregate-only: this tool manipulates and prints **counters only**, never any
nominative student data (no NISS, name, address...).

Strategy:
- one bulk SEPS call retrieves every inscription, grouped by (numAdm, numOrg);
- the Doc 1 is read per organisation, but only for organisations whose
  population/periods document is approved (otherwise Doc 1 is not accessible).

Usage:
    python examples/audit_coherence_doc1_seps.py --annee 2025-2026 --etab 3052

Requires a production-configured ``.env`` (EPROM credentials + SEPS X509 PFX).
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass

import pyetnic.eprom as eprom
import pyetnic.seps as seps

# Discrepancy kinds
MISMATCH = "MISMATCH"  # both sides > 0 but differ
DECLARED_NO_SEPS = "DECLARED_NO_SEPS"  # Doc 1 declares a population, SEPS has none
SEPS_NO_DECLARED = "SEPS_NO_DECLARED"  # SEPS has inscriptions, Doc 1 declares none / not approved


@dataclass
class Discrepancy:
    """A single organisation where Doc 1 and SEPS head-counts disagree."""

    num_adm: int
    num_org: int
    code: str
    label: str
    doc1: int
    seps: int
    kind: str

    @property
    def delta(self) -> int:
        return self.seps - self.doc1


def _doc1_headcount(org_id: object) -> int | None:
    """Total declared head-count (H+F summed over every study-year line).

    Returns ``None`` when the document cannot be read despite an approved status
    (the organisation is then skipped rather than reported as a false 0).
    """
    try:
        with eprom.strict_errors():
            doc1 = eprom.lire_document_1(org_id)
    except eprom.EtnicError:
        return None
    if not doc1 or not doc1.populationListe or not doc1.populationListe.population:
        return 0
    return sum(
        (line.nbEleveTotHom or 0) + (line.nbEleveTotFem or 0)
        for line in doc1.populationListe.population
    )


def audit(annee_scolaire: str, etab_id: int) -> list[Discrepancy]:
    """Return the list of organisations where Doc 1 and SEPS head-counts differ."""
    year_int = int(annee_scolaire.split("-")[0])

    # 1) Every SEPS inscription in a single call, grouped by (numAdm, numOrg).
    seps_by_org: Counter[tuple[int, int]] = Counter()
    for ins in seps.rechercher_inscriptions(annee_scolaire=year_int, etab_id=etab_id):
        if ins.ue:
            seps_by_org[(ins.ue.noAdministratif, ins.ue.noOrganisation)] += 1

    # 2) EPROM organisations for the year.
    res = eprom.lister_formations(annee_scolaire=annee_scolaire)
    discrepancies: list[Discrepancy] = []
    accounted: set[tuple[int, int]] = set()

    for formation in res.formations:
        for org in formation.organisations:
            key = (formation.numAdmFormation, org.id.numOrganisation)
            seps_n = seps_by_org.get(key, 0)
            status = org.statutDocumentPopulationPeriodes
            approved = bool(status and status.statut == "Approuvé")

            if not approved:
                # Doc 1 is not accessible; only worth flagging if SEPS has inscriptions
                # (EPROM encoding lagging behind real registrations).
                if seps_n:
                    accounted.add(key)
                    discrepancies.append(
                        Discrepancy(key[0], key[1], formation.codeFormation,
                                    formation.libelleFormation, 0, seps_n, SEPS_NO_DECLARED)
                    )
                continue

            accounted.add(key)
            doc1_n = _doc1_headcount(org.id)
            if doc1_n is None or doc1_n == seps_n:
                continue
            if seps_n == 0:
                kind = DECLARED_NO_SEPS
            elif doc1_n == 0:
                kind = SEPS_NO_DECLARED
            else:
                kind = MISMATCH
            discrepancies.append(
                Discrepancy(key[0], key[1], formation.codeFormation,
                            formation.libelleFormation, doc1_n, seps_n, kind)
            )

    # 3) SEPS inscriptions pointing at an organisation absent from the EPROM catalogue.
    for key, seps_n in seps_by_org.items():
        if key not in accounted:
            discrepancies.append(
                Discrepancy(key[0], key[1], "?",
                            "(organisation absente du catalogue EPROM)", 0, seps_n, SEPS_NO_DECLARED)
            )
    return discrepancies


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-check EPROM Doc 1 population vs SEPS inscriptions (discrepancies only)."
    )
    parser.add_argument("--annee", default="2025-2026", help="School year, e.g. 2025-2026")
    parser.add_argument("--etab", type=int, default=3052, help="Établissement id")
    args = parser.parse_args()

    discrepancies = audit(args.annee, args.etab)
    header = f"[{args.annee} / etab {args.etab}]"
    if not discrepancies:
        print(f"{header} Aucune incohérence Doc 1 <-> SEPS. OK")
        return

    by_kind = Counter(d.kind for d in discrepancies)
    print(f"{header} {len(discrepancies)} incohérence(s) Doc 1 <-> SEPS : {dict(by_kind)}\n")
    print(f"  {'UE/org':<12}{'Doc1':>6}{'SEPS':>6}{'delta':>7}  {'type':<17}libellé")
    for d in sorted(discrepancies, key=lambda x: (x.kind, -abs(x.delta))):
        ue_org = f"{d.num_adm}/{d.num_org}"
        print(f"  {ue_org:<12}{d.doc1:>6}{d.seps:>6}{d.delta:>+7}  {d.kind:<17}{d.label[:38]}")


if __name__ == "__main__":
    main()
