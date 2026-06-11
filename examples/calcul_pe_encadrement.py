"""Estimate the raw student-periods (PE, "encadrement" side) of a civil year.

Demonstration script (the financing engine is intentionally kept out of pyetnic).
Validated at ±1 % against the host screen 57D for civil year 2025 (session 9ter).

Rule (reconstructed and validated against official figures):
  PE = sum(periods x students) over every line carrying students — external
       interventions included —
     + (reserved organic periods + IE periods without students) x average PE/period

The residual ±1 % stems from the valuation rule of student-less IE sessions
(VC/convention) and from unpaid registration-fee exclusions, both out of API reach.

Usage: python calcul_pe_encadrement.py 2025
"""

import argparse
import logging

from pyetnic.eprom import lire_document_2, lister_formations


def collecter(annee_scolaire, attr_act, attr_ie):
    out = []
    for formation in lister_formations(annee_scolaire=annee_scolaire):
        for apercu in formation.organisations:
            doc2 = lire_document_2(apercu.id)
            det = doc2.activiteEnseignementDetail if doc2 else None
            lignes = det.activiteEnseignementListe.activiteEnseignement if det and det.activiteEnseignementListe else []
            ie = 0.0
            if doc2 and doc2.interventionExterieureListe:
                for inter in doc2.interventionExterieureListe.interventionExterieure:
                    if inter.periodeListe:
                        ie += sum(getattr(p, attr_ie) or 0.0 for p in inter.periodeListe.periode)
            out.append({
                "eleves_max": max((l.nbEleveC1 or 0 for l in lignes), default=0),
                "lignes": [(l.nbEleveC1 or 0, getattr(l, attr_act) or 0.0) for l in lignes],
                "ie": ie,
            })
    return out


def calculer(annee_civile):
    orgs = collecter(f"{annee_civile - 1}-{annee_civile}", "nbPeriodeReelleAn2", "nbPerAn2") + \
        collecter(f"{annee_civile}-{annee_civile + 1}", "nbPeriodeReelleAn1", "nbPerAn1")

    pe_eleves = per_eleves = 0.0   # organic lines carrying students
    per_reservees = 0.0            # organic lines without students (EPT, etc.)
    pe_ie = per_ie = 0.0           # IE periods of organisations WITH students
    per_ie_sans_eleves = 0.0       # IE periods of organisations WITHOUT students

    for o in orgs:
        for eleves, per in o["lignes"]:
            if per <= 0:
                continue
            if eleves > 0:
                pe_eleves += per * eleves
                per_eleves += per
            else:
                per_reservees += per
        if o["ie"] > 0:
            if o["eleves_max"] > 0:
                pe_ie += o["ie"] * o["eleves_max"]
                per_ie += o["ie"]
            else:
                per_ie_sans_eleves += o["ie"]

    moyenne = (pe_eleves + pe_ie) / (per_eleves + per_ie) if (per_eleves + per_ie) else 0.0
    pe_moyenne = (per_reservees + per_ie_sans_eleves) * moyenne
    return {
        "pe_eleves": pe_eleves, "pe_ie": pe_ie, "pe_moyenne": pe_moyenne,
        "per_reservees": per_reservees, "per_ie_sans_eleves": per_ie_sans_eleves,
        "moyenne": moyenne, "total": pe_eleves + pe_ie + pe_moyenne,
    }


def main():
    parser = argparse.ArgumentParser(description="PE (encadrement) estimate for a civil year (read-only).")
    parser.add_argument("annee_civile", type=int, help="civil year, e.g. 2025")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    r = calculer(args.annee_civile)
    print(f"PE lignes avec élèves (IE comprises) : {r['pe_eleves'] + r['pe_ie']:12.1f}")
    print(f"périodes réservées + IE sans élèves  : {r['per_reservees'] + r['per_ie_sans_eleves']:12.1f}"
          f"  × moyenne {r['moyenne']:.3f} = {r['pe_moyenne']:.1f}")
    print(f"PE TOTAL (encadrement) {args.annee_civile}        : {r['total']:12.1f}")
    print("(estimation ±1 % — IE sans élèves valorisées à la moyenne, DI non payés non exclus)")


if __name__ == "__main__":
    main()
