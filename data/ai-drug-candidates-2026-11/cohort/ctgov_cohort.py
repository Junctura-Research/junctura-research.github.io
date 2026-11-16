"""Cohort: ClinicalTrials.gov API v2 lookups for the dated cohort.

Usage:
  python ctgov_cohort.py sponsors raw    # trials led by each of the 17 companies, start date <= 2023-12-31 -> raw/ctgov_sponsors_2023.json
  python ctgov_cohort.py candidates raw  # every term in cohort.csv `ctgov_terms`, all dates -> raw/ctgov_cohort.json

Matching rule as in the current list (../current-list/ctgov.py): a trial matches a candidate only if the
term appears in its intervention list, punctuation ignored.
"""
import csv, json, re, sys, datetime, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "current-list"))
from ctgov import get, top_phase  # same fields and paging as the current list

SPONSORS = {
    "Recursion": ["Recursion"], "Exscientia": ["Exscientia"], "Schrodinger": ["Schrodinger", "Schrödinger"],
    "Absci": ["Absci"], "Evaxion": ["Evaxion"], "Nurix": ["Nurix"], "Compugen": ["Compugen"],
    "iBio": ["iBio"], "Monte Rosa": ["Monte Rosa"], "Iambic": ["Iambic"], "Generate": ["Generate Biomedicines"],
    "Eikon": ["Eikon"], "Odyssey": ["Odyssey Therapeutics"], "Parabilis": ["Parabilis", "FogPharma", "Fog Pharma"],
    "Insilico Medicine": ["Insilico"], "BenevolentAI": ["BenevolentAI", "Benevolent"], "Enveda": ["Enveda"],
}
CUTOFF = "2023-12-31"


def main(mode, out):
    today = datetime.date.today().isoformat()
    if mode == "sponsors":
        res = {"retrieved": today, "cutoff_start_date": CUTOFF, "companies": {}}
        for co, terms in SPONSORS.items():
            trials = {}
            for term in terms:
                for t in get({"query.spons": term}):
                    if t["start"] and t["start"][:10] <= CUTOFF:
                        trials[t["nct"]] = t
            res["companies"][co] = sorted(trials.values(), key=lambda t: t["start"])
            print(co, len(trials), file=sys.stderr)
        json.dump(res, open(f"{out}/ctgov_sponsors_2023.json", "w"), indent=1)
    else:
        res = {"retrieved": today, "candidates": {}}
        for row in csv.DictReader(open("cohort.csv")):
            terms = [x.strip() for x in row["ctgov_terms"].split(";") if x.strip()]
            trials = {}
            for term in terms:
                key = re.sub(r"[^a-z0-9]", "", term.lower())
                for t in get({"query.intr": f'"{term}"'}):
                    if key in re.sub(r"[^a-z0-9]", "", " ".join(t["interventions"]).lower()):
                        trials[t["nct"]] = t
            tv = list(trials.values())
            starts = sorted(t["start"] for t in tv if t["start"])
            res["candidates"][row["candidate"]] = {
                "terms": terms, "n_trials": len(tv), "top_phase": top_phase(tv),
                "first_start": starts[0] if starts else None,
                "statuses": sorted({t["status"] for t in tv}), "trials": tv}
            print(row["candidate"], len(tv), top_phase(tv), starts[:1], sorted({t["status"] for t in tv}), file=sys.stderr)
        json.dump(res, open(f"{out}/ctgov_cohort.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
