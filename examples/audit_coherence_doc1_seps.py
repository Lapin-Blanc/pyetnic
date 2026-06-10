"""Audit: cross-check declared EPROM Doc 1 population against real SEPS inscriptions.

For a given établissement and school year, compare — per organisation — the
headcount declared in the EPROM Document 1 (population, which drives funding)
with the number of real inscriptions recorded in SEPS. Only discrepancies are
reported.

Aggregate-only: this tool manipulates and prints **counters only**, never any
nominative student data (no NISS, name, address...).

Strategy:
- one bulk SEPS call retrieves every inscription, grouped by (numAdm, numOrg);
  inscriptions whose status is excluded (cancelled, ``AN``) are dropped;
- the Doc 1 is read per organisation, but only for organisations whose
  population/periods document is approved (otherwise Doc 1 is not accessible).

Discrepancy kinds:
- ``MISMATCH``           — approved org, both sides > 0 but differ;
- ``DECLARED_NO_SEPS``   — approved org declares a population, SEPS has none;
- ``SEPS_NO_DECLARED``   — approved org declares 0, SEPS has inscriptions;
- ``NOT_APPROVED``       — org not approved yet (Doc 1 unreadable) but SEPS has
                           inscriptions: the real org status is shown;
- ``ORPHAN_SEPS``        — SEPS inscriptions for an org absent from EPROM.

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

MISMATCH = "MISMATCH"
DECLARED_NO_SEPS = "DECLARED_NO_SEPS"
SEPS_NO_DECLARED = "SEPS_NO_DECLARED"
NOT_APPROVED = "NOT_APPROVED"
ORPHAN_SEPS = "ORPHAN_SEPS"

# SEPS inscription statuses dropped by default: ``AN`` = annulé (cancelled).
DEFAULT_EXCLUDED_STATUSES: tuple[str, ...] = ("AN",)


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
    org_status: str

    @property
    def delta(self) -> int:
        return self.seps - self.doc1


@dataclass
class AuditResult:
    """Outcome of an audit run, including transparency counters."""

    discrepancies: list[Discrepancy]
    organisations_scanned: int
    seps_total: int
    seps_excluded: int
    excluded_statuses: tuple[str, ...]


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


def audit(
    annee_scolaire: str,
    etab_id: int,
    excluded_statuses: tuple[str, ...] = DEFAULT_EXCLUDED_STATUSES,
) -> AuditResult:
    """Return the organisations where Doc 1 and SEPS head-counts differ."""
    year_int = int(annee_scolaire.split("-")[0])
    excluded = set(excluded_statuses)

    # 1) Every SEPS inscription in a single call, grouped by (numAdm, numOrg),
    #    dropping excluded (e.g. cancelled) statuses.
    seps_by_org: Counter[tuple[int, int]] = Counter()
    seps_total = 0
    seps_excluded = 0
    for ins in seps.rechercher_inscriptions(annee_scolaire=year_int, etab_id=etab_id):
        seps_total += 1
        if ins.statut in excluded:
            seps_excluded += 1
            continue
        if ins.ue:
            seps_by_org[(ins.ue.noAdministratif, ins.ue.noOrganisation)] += 1

    # 2) EPROM organisations for the year.
    res = eprom.lister_formations(annee_scolaire=annee_scolaire)
    discrepancies: list[Discrepancy] = []
    accounted: set[tuple[int, int]] = set()
    scanned = 0

    for formation in res.formations:
        for org in formation.organisations:
            scanned += 1
            key = (formation.numAdmFormation, org.id.numOrganisation)
            seps_n = seps_by_org.get(key, 0)
            status = org.statutDocumentPopulationPeriodes
            status_label = status.statut if status else "—"
            approved = bool(status and status.statut == "Approuvé")

            if not approved:
                # Doc 1 not accessible; flag only if SEPS already has inscriptions
                # (real registrations preceding EPROM approval).
                if seps_n:
                    accounted.add(key)
                    discrepancies.append(
                        Discrepancy(key[0], key[1], formation.codeFormation,
                                    formation.libelleFormation, 0, seps_n, NOT_APPROVED, status_label)
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
                            formation.libelleFormation, doc1_n, seps_n, kind, status_label)
            )

    # 3) SEPS inscriptions pointing at an organisation absent from the EPROM catalogue.
    for key, seps_n in seps_by_org.items():
        if key not in accounted:
            discrepancies.append(
                Discrepancy(key[0], key[1], "?",
                            "(organisation absente du catalogue EPROM)", 0, seps_n, ORPHAN_SEPS, "—")
            )

    return AuditResult(discrepancies, scanned, seps_total, seps_excluded, tuple(excluded_statuses))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-check EPROM Doc 1 population vs SEPS inscriptions (discrepancies only)."
    )
    parser.add_argument("--annee", default="2025-2026", help="School year, e.g. 2025-2026")
    parser.add_argument("--etab", type=int, default=3052, help="Établissement id")
    parser.add_argument(
        "--exclure-statuts", nargs="*", metavar="STATUT",
        default=list(DEFAULT_EXCLUDED_STATUSES),
        help="SEPS inscription statuses to ignore (default: AN = cancelled). "
             "Pass with no value to count every status.",
    )
    args = parser.parse_args()

    result = audit(args.annee, args.etab, tuple(args.exclure_statuts))
    header = f"[{args.annee} / etab {args.etab}]"
    excl_codes = ",".join(result.excluded_statuses) or "—"
    seps_line = (f"  SEPS : {result.seps_total} inscriptions, "
                 f"{result.seps_excluded} exclue(s) [{excl_codes}].")

    if not result.discrepancies:
        print(f"{header} Aucune incohérence Doc 1 <-> SEPS sur "
              f"{result.organisations_scanned} organisations. OK")
        print(seps_line)
        return

    by_kind = Counter(d.kind for d in result.discrepancies)
    print(f"{header} {len(result.discrepancies)} incohérence(s) / "
          f"{result.organisations_scanned} org. : {dict(by_kind)}")
    print(seps_line + "\n")
    print(f"  {'UE/org':<12}{'Doc1':>5}{'SEPS':>5}{'delta':>7}  "
          f"{'type':<17}{'statut org':<15}libellé")
    for d in sorted(result.discrepancies, key=lambda x: (x.kind, -abs(x.delta))):
        ue_org = f"{d.num_adm}/{d.num_org}"
        print(f"  {ue_org:<12}{d.doc1:>5}{d.seps:>5}{d.delta:>+7}  "
              f"{d.kind:<17}{d.org_status:<15}{d.label[:32]}")


if __name__ == "__main__":
    main()
