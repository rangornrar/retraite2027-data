"""Valide v1/scenarios.json avec les mêmes règles que l'app (LecteurScenarios.kt).

    python3 tools/valider.py v1/scenarios.json

Refuse : format inconnu, référence absente ou multiple, id en double, valeur sans source,
barème avec trou ou chevauchement, âge illisible, statut inconnu, et (neutralité)
un candidat dont une clé de paramètre n'est ni précisée ni marquée « unspecified ».
"""
import json
import re
import sys

CLES = ["bareme", "legalAge", "requiredQuarters", "startAgeRules", "earlyRetirement", "decotePerQuarter",
        "decoteMaxQuarters", "fullRateAge", "surcotePerQuarter", "minimumNetMonthly"]
FACULTATIFS_REFERENCE = {"legalAge", "requiredQuarters", "startAgeRules", "minimumNetMonthly"}
erreurs = []


def err(msg):
    erreurs.append(msg)


def mois(txt):
    a, m = txt.split("-")
    return int(a) * 12 + int(m) - 1


def verifier_bareme(sid, regles):
    if not regles:
        return err(f"{sid} : barème vide")
    regles = sorted(regles, key=lambda r: mois(r["bornFrom"]))
    for a, b in zip(regles, regles[1:]):
        if "bornTo" not in a:
            err(f"{sid} : seule la dernière règle peut être sans fin")
        elif mois(b["bornFrom"]) != mois(a["bornTo"]) + 1:
            err(f"{sid} : trou ou chevauchement après {a['bornTo']}")
    if "bornTo" in regles[-1]:
        err(f"{sid} : la dernière règle doit être sans fin")
    for r in regles:
        if not re.fullmatch(r"\d{2}y([0-9]|1[01])m", r["legalAge"]):
            err(f"{sid} : âge illisible {r['legalAge']}")
        if not 120 <= r["requiredQuarters"] <= 200:
            err(f"{sid} : durée requise hors limites")


def main(chemin):
    d = json.load(open(chemin, encoding="utf-8"))
    if d.get("formatVersion") != 1:
        err("formatVersion doit valoir 1")
    scen = d["scenarios"]
    if sum(1 for s in scen if s.get("reference")) != 1:
        err("il faut exactement un scénario de référence")
    ids = [s["id"] for s in scen]
    if len(set(ids)) != len(ids):
        err("identifiants en double")
    for s in scen:
        sid = s["id"]
        if s["type"] not in ("statusQuo", "candidate"):
            err(f"{sid} : type inconnu")
        if s.get("computable", True) is False and not s.get("notComputableReason"):
            err(f"{sid} : raison manquante pour un programme non chiffrable")
        params = s.get("params", {})
        for cle in CLES:
            p = params.get(cle)
            if p is None:
                if s["type"] == "candidate":
                    err(f"{sid}.{cle} : à préciser ou marquer « unspecified » (même grille pour tous)")
                elif s.get("reference") and cle not in FACULTATIFS_REFERENCE:
                    err(f"{sid}.{cle} : la référence doit tout préciser")
                continue
            if "value" in p:
                if "source" not in p:
                    err(f"{sid}.{cle} : valeur sans source")
                if cle == "bareme":
                    verifier_bareme(sid, p["value"])
                if cle == "legalAge" and not re.fullmatch(r"\d{2}y([0-9]|1[01])m", p["value"]):
                    err(f"{sid} : âge illisible {p['value']}")
                if cle == "earlyRetirement":
                    for r in p["value"]:
                        if not 14 <= r["startedBefore"] <= 40:
                            err(f"{sid} : carrière longue, âge de début hors limites")
                        if not re.fullmatch(r"\d{2}y([0-9]|1[01])m", r["age"]):
                            err(f"{sid} : carrière longue, âge illisible {r['age']}")
                        if r.get("bornTo") and mois(r["bornTo"]) < mois(r["bornFrom"]):
                            err(f"{sid} : carrière longue, période inversée")
                if cle == "startAgeRules":
                    for r in p["value"]:
                        if not 14 <= r["startedBefore"] <= 40:
                            err(f"{sid} : âge de début hors limites")
            elif p.get("status") != "unspecified":
                err(f"{sid}.{cle} : statut inconnu")
        for m in s.get("measures", []):
            if "source" not in m:
                err(f"{sid} : mesure sans source « {m['text'][:40]}… »")
    if erreurs:
        print("\n".join("ERREUR " + e for e in erreurs))
        sys.exit(1)
    print(f"OK : {len(scen)} scénarios, publié le {d['publishedAt']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1/scenarios.json")
