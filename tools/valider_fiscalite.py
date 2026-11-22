"""Valide v1/fiscalite.json avec les mêmes règles que l'app (LecteurFiscalite.kt).

    python3 tools/valider_fiscalite.py v1/fiscalite.json v1/scenarios.json

Refuse : format inconnu, loi actuelle incomplète, paramètre inconnu, valeur sans source, barème non
croissant ou sans dernière tranche ouverte, taux hors [0, 1], volet ou thème inconnu, mesure sans source,
et un candidat inconnu de scenarios.json. Un candidat de scenarios.json sans volet fiscal
est signalé sans bloquer la publication.
"""
import json
import sys

CLES = ["csgSalary", "irBrackets", "irDecote", "workExpenses", "qfCap", "qfFullShareSecondChild",
        "irExemptUnderAge", "youngChildReduction", "wealthTax", "topFortunes", "inheritance",
        "corporateTax", "csb", "exceptionalContribution", "reinvestedCoefficient", "youngFounderExemptionYears",
        "newCompanyMoratoriumYears", "cvae", "c3s", "cfeCoefficient", "cfeIndustrialExempt", "dividendTax"]
VOLETS = {"SALAIRE", "IMPOT_REVENU", "PATRIMOINE", "SUCCESSION", "IMPOT_SOCIETES", "PRODUCTION"}
THEMES = {"REVENU", "PATRIMOINE", "CONSOMMATION", "SOCIETES", "PRODUCTION"}
erreurs = []


def bareme(sid, t):
    if not t or "upTo" in t[-1] or any("upTo" not in x for x in t[:-1]):
        erreurs.append(f"{sid} : barème sans dernière tranche ouverte")
    hauts = [x["upTo"] for x in t if "upTo" in x]
    if hauts != sorted(set(hauts)):
        erreurs.append(f"{sid} : barème non croissant")
    if any(not 0 <= x["rate"] <= 1 for x in t):
        erreurs.append(f"{sid} : taux hors limites")


def verifier(s, reference):
    sid = s["id"]
    for cle, p in s.get("params", {}).items():
        if cle not in CLES:
            erreurs.append(f"{sid} : paramètre inconnu {cle}")
            continue
        if "value" not in p:
            erreurs.append(f"{sid}.{cle} : valeur absente")
            continue
        if not p.get("source"):
            erreurs.append(f"{sid}.{cle} : valeur sans source")
        val = p["value"]
        if cle == "irBrackets":
            bareme(sid, val)
        if cle == "inheritance":
            bareme(sid, val["brackets"])
        if cle == "wealthTax" and val is not None:
            bareme(sid, val["brackets"])
        if cle in ("topFortunes", "exceptionalContribution", "dividendTax") and any(not 0 <= x["rate"] <= 1 for x in val):
            erreurs.append(f"{sid}.{cle} : taux hors limites")
        if cle == "cvae" and val is not None:
            ca = [x["turnover"] for x in val["points"]]
            if ca != sorted(set(ca)):
                erreurs.append(f"{sid} : CVAE, points non croissants")
    for v in s.get("notComputable", {}):
        if v not in VOLETS:
            erreurs.append(f"{sid} : volet inconnu {v}")
    for mes in s.get("measures", []):
        if mes["theme"] not in THEMES:
            erreurs.append(f"{sid} : thème inconnu {mes['theme']}")
        if not mes.get("source"):
            erreurs.append(f"{sid} : mesure sans source ({mes['text'][:40]})")
    if reference:
        manquantes = [c for c in CLES if c not in s["params"]]
        if manquantes:
            erreurs.append(f"Loi actuelle incomplète : {manquantes}")


def main(chemin, chemin_scenarios):
    d = json.load(open(chemin, encoding="utf-8"))
    if d.get("formatVersion") != 1:
        erreurs.append("formatVersion inconnu")
    verifier(d["reference"], True)
    ids = [c["id"] for c in d["candidates"]]
    if len(ids) != len(set(ids)):
        erreurs.append("identifiant en double")
    for c in d["candidates"]:
        verifier(c, False)
    retraite = {s["id"] for s in json.load(open(chemin_scenarios, encoding="utf-8"))["scenarios"] if s["type"] == "candidate"}
    if set(ids) - retraite:
        erreurs.append(f"candidats absents de scenarios.json : {set(ids) - retraite}")
    if retraite - set(ids):
        # Pas bloquant : l'app affiche le volet retraite ; à compléter avec tools/generer_fiscalite.py.
        print(f"Attention : sans volet fiscal : {sorted(retraite - set(ids))}")
    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"OK : loi actuelle + {len(ids)} candidats")


if __name__ == "__main__":
    main(*(sys.argv[1:3] if len(sys.argv) > 2 else ["v1/fiscalite.json", "v1/scenarios.json"]))
