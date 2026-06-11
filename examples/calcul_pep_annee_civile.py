"""Compute the weighted student-periods (PEP) of a civil year and write a markdown report.

This is a demonstration script, not a supported API: the financing engine is
intentionally kept OUT of pyetnic (see specs/21_calcul_encadrement_dotation.md §7).
It reproduces the official dotation assessment base (validated at +0.46 % against
the host screen 55L for civil year 2025, session 9ter).

Method — arrete GCF 22/11/2002 art. 3-4:
  1. general cases: PE x pedagogical coefficient x level coefficient, line by line
  2. autonomy share: prorated on the course structure of the *dossier pedagogique*
     (nbPeriodeBranche), NOT on the civil-year slice (two-school-year organisations)
  3. organic limitation: the Doc 2 "real" columns only carry the dotation share
     (external interventions live in their own block) — confirmed by host report 4
  4. particular cases (EPT, supervision, follow-up): periods x average PEP/period

Civil year N = An2 real periods of school year N-1/N + An1 real periods of N/N+1.

Usage: python calcul_pep_annee_civile.py 2025 [-o rapport.md]
"""

import argparse
import csv
import logging
import re
from datetime import date
from pathlib import Path

from pyetnic.eprom import lire_document_2, lire_organisation, lister_formations

CSV_PATH = Path(__file__).resolve().parents[1] / "specs/referentiels/coefficients_ponderation_coCategorie.csv"

NIVEAU = {"1": ("B", 1.0), "2": ("A", 1.25), "3": ("C", 1.5)}


def charger_bareme():
    coef_ped, groupe = {}, {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            groupe[row["code"]] = row["groupe"]
            if row["coef_pedagogique"]:
                coef_ped[row["code"]] = float(row["coef_pedagogique"])
    return coef_ped, groupe


def coef_niveau(code_formation):
    m = re.search(r"U(\d)\d", code_formation or "")
    if m and m.group(1) in NIVEAU:
        return NIVEAU[m.group(1)]
    return (None, None)


def collecter(annee_scolaire, attr_reel_civil):
    """Read every Doc 2 of a school year; attr_reel_civil selects the civil-year column."""
    out = []
    for formation in lister_formations(annee_scolaire=annee_scolaire):
        for apercu in formation.organisations:
            org = lire_organisation(apercu.id)
            doc2 = lire_document_2(apercu.id)
            lignes = []
            if doc2 and doc2.activiteEnseignementDetail and doc2.activiteEnseignementDetail.activiteEnseignementListe:
                lignes = doc2.activiteEnseignementDetail.activiteEnseignementListe.activiteEnseignement
            out.append({
                "annee": annee_scolaire,
                "num_adm": formation.numAdmFormation,
                "code": formation.codeFormation,
                "libelle": formation.libelleFormation,
                "num_org": apercu.id.numOrganisation,
                "flag_ie": org.typeInterventionExterieure if org else None,
                "lignes": [
                    {"cat": l.coCategorie, "nom": l.teNomBranche,
                     "eleves": l.nbEleveC1 or 0, "per": getattr(l, attr_reel_civil) or 0.0,
                     "branche": l.nbPeriodeBranche or 0.0}
                    for l in lignes
                ],
            })
    return out


def calculer(annee_civile):
    coef_ped, groupe = charger_bareme()
    orgs = collecter(f"{annee_civile - 1}-{annee_civile}", "nbPeriodeReelleAn2") + \
        collecter(f"{annee_civile}-{annee_civile + 1}", "nbPeriodeReelleAn1")

    lignes_ue, avertissements, cas_particuliers, a_confirmer = [], [], [], []
    tot_pe_gen = tot_pep_gen = tot_per = 0.0
    tot_pe_auto = tot_pep_auto = 0.0

    for o in orgs:
        niv, c_niv = coef_niveau(o["code"])
        gen = [l for l in o["lignes"] if groupe.get(l["cat"]) == "cas_general" and l["per"] > 0]
        auto = [l for l in o["lignes"] if groupe.get(l["cat"]) == "autonomie" and l["per"] > 0]
        part = [l for l in o["lignes"] if str(groupe.get(l["cat"], "")).startswith("cas_particulier") and l["per"] > 0]
        conf = [l for l in o["lignes"] if groupe.get(l["cat"]) == "a_confirmer" and l["per"] > 0]
        inconnues = [l for l in o["lignes"] if l["cat"] not in groupe and l["per"] > 0]

        if not (gen or auto or part or conf or inconnues):
            continue
        if c_niv is None and (gen or auto):
            avertissements.append(f"{o['annee']} {o['num_adm']}/org{o['num_org']} : niveau introuvable dans `{o['code']}`")
            continue

        pe_g = pep_g = per_g = 0.0
        for l in gen:
            pe = l["per"] * l["eleves"]
            pe_g += pe
            pep_g += pe * coef_ped[l["cat"]] * c_niv
            per_g += l["per"]
            if l["eleves"] == 0:
                avertissements.append(
                    f"{o['annee']} {o['num_adm']}/org{o['num_org']} : {l['per']:g} pér. réelles sans élèves ({l['cat']})"
                )

        # Autonomy prorata base = dossier pedagogique structure (nbPeriodeBranche)
        dossier = [l for l in o["lignes"] if groupe.get(l["cat"]) == "cas_general" and l["branche"] > 0]
        branche_tot = sum(l["branche"] for l in dossier)
        pe_a = pep_a = 0.0
        for l in auto:
            if branche_tot > 0:
                c_moyen = sum(x["branche"] * coef_ped[x["cat"]] for x in dossier) / branche_tot * c_niv
                pe_a += l["per"] * l["eleves"]
                pep_a += l["per"] * l["eleves"] * c_moyen
            else:
                avertissements.append(
                    f"{o['annee']} {o['num_adm']}/org{o['num_org']} : AUTO {l['per']:g} pér. sans cas généraux au dossier → non comptées"
                )

        cas_particuliers.extend((o, l) for l in part)
        a_confirmer.extend((o, l) for l in conf)
        avertissements.extend(
            f"{o['annee']} {o['num_adm']}/org{o['num_org']} : coCategorie inconnue `{l['cat']}` ({l['per']:g} pér.)"
            for l in inconnues
        )

        tot_pe_gen += pe_g
        tot_pep_gen += pep_g
        tot_per += per_g + sum(l["per"] for l in auto)
        tot_pe_auto += pe_a
        tot_pep_auto += pep_a

        if pe_g or pe_a:
            lignes_ue.append({
                "annee": o["annee"], "num_adm": o["num_adm"], "num_org": o["num_org"],
                "niv": niv, "flag_ie": o["flag_ie"],
                "per": per_g + sum(l["per"] for l in auto),
                "pe": pe_g + pe_a, "pep": pep_g + pep_a, "libelle": o["libelle"],
            })

    moyenne = (tot_pep_gen + tot_pep_auto) / tot_per if tot_per else 0.0
    pep_cp = sum(l["per"] for _, l in cas_particuliers) * moyenne
    return {
        "annee": annee_civile, "lignes_ue": lignes_ue, "cas_particuliers": cas_particuliers,
        "a_confirmer": a_confirmer, "avertissements": avertissements,
        "pe_gen": tot_pe_gen, "pep_gen": tot_pep_gen, "pe_auto": tot_pe_auto,
        "pep_auto": tot_pep_auto, "periodes": tot_per, "moyenne": moyenne,
        "pep_cp": pep_cp, "pep_total": tot_pep_gen + tot_pep_auto + pep_cp,
    }


def rendre_markdown(r):
    n = r["annee"]
    md = [
        f"# Calcul détaillé des périodes-élèves pondérées (PEP) — année civile {n}",
        "",
        f"> Généré le {date.today().isoformat()} par `examples/calcul_pep_annee_civile.py` (pyetnic, lecture seule).",
        "> Méthode : spec 21 (décret 16/04/1991 art. 99 + arrêté GCF 22/11/2002 art. 3-4).",
        "",
        "## Synthèse",
        "",
        "| Grandeur | Valeur |",
        "|---|---:|",
        f"| PE non pondérées (cas généraux + autonomie) | {r['pe_gen'] + r['pe_auto']:,.1f} |",
        f"| Périodes organiques (cas généraux + autonomie) | {r['periodes']:,.1f} |",
        f"| PEP cas généraux | {r['pep_gen']:,.2f} |",
        f"| PEP part d'autonomie | {r['pep_auto']:,.2f} |",
        f"| **Moyenne PEP/période** | **{r['moyenne']:.3f}** |",
        f"| PEP cas particuliers ({sum(l['per'] for _, l in r['cas_particuliers']):g} pér. × moyenne) | {r['pep_cp']:,.2f} |",
        f"| **PEP TOTAL établissement — année civile {n}** | **{r['pep_total']:,.2f}** |",
        "",
        "## Détail par UE — cas généraux + autonomie",
        "",
        f"| Année scol. | UE/org | Niv. | Pér. {n} | PE | PEP | IE |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for u in sorted(r["lignes_ue"], key=lambda u: -u["pep"]):
        md.append(
            f"| {u['annee']} | {u['num_adm']}/{u['num_org']} — {u['libelle'][:48]} | {u['niv']} "
            f"| {u['per']:g} | {u['pe']:g} | {u['pep']:.1f} | {u['flag_ie'] or ''} |"
        )
    md += ["", "## Cas particuliers — valorisés à la moyenne PEP/période", "",
           f"| Année scol. | UE/org | Cat. | Pér. {n} | PEP | Activité |",
           "|---|---|---|---:|---:|---|"]
    for o, l in sorted(r["cas_particuliers"], key=lambda t: (t[0]["num_adm"], t[0]["num_org"])):
        md.append(
            f"| {o['annee']} | {o['num_adm']}/{o['num_org']} — {o['libelle'][:35]} | {l['cat']} "
            f"| {l['per']:g} | {l['per'] * r['moyenne']:.1f} | {l['nom'][:40]} |"
        )
    if r["a_confirmer"]:
        md += ["", "## Catégories à confirmer (PSup/PRET) — non comptées", ""]
        md += [f"- {o['annee']} {o['num_adm']}/org{o['num_org']} : `{l['cat']}` {l['per']:g} pér."
               for o, l in r["a_confirmer"]]
    md += ["", "## Avertissements et limites", ""]
    md += [f"- ⚠️ {w}" for w in r["avertissements"]]
    md += [
        "- Les élèves « redevables DI non en ordre de paiement » ne sont pas exclus (majorant).",
        "- Arrondis officiels (2ᵉ décimale par étape) non répliqués — écart attendu ≈ ±0,5 %.",
        "- Étapes 5-6 de l'arrêté (neutralisation, dépassements) hors périmètre (dotation de référence hors API).",
        "",
    ]
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="PEP computation for a civil year (read-only).")
    parser.add_argument("annee_civile", type=int, help="civil year, e.g. 2025")
    parser.add_argument("-o", "--output", help="markdown output path (default: rapport_pep_<year>.md)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    resultat = calculer(args.annee_civile)
    sortie = Path(args.output or f"rapport_pep_{args.annee_civile}.md")
    sortie.write_text(rendre_markdown(resultat), encoding="utf-8")
    print(f"PEP total {args.annee_civile} : {resultat['pep_total']:.2f} (moyenne {resultat['moyenne']:.3f})")
    print(f"rapport : {sortie}")


if __name__ == "__main__":
    main()
