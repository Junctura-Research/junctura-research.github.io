"""Print the Note's 32-row cohort table (markdown) from cohort_32_final.csv.
Columns: candidate, company, AI claim tier, highest phase (trials run by the sponsor or its development partner),
outcome as of 2026-11-17, first trial (date only; the explanatory note in brackets is in the CSV).
Usage (from this folder): python note_table.py [path to cohort_32_final.csv]"""
import csv, sys
path = sys.argv[1] if len(sys.argv) > 1 else "cohort_32_final.csv"
rows = list(csv.DictReader(open(path, encoding="utf-8")))
assert len(rows) == 32
TIER = {"explicit": "Explicit", "platform": "Platform only"}
print("| Candidate | Company | AI claim | Highest phase | Outcome | First trial |")
print("| --- | --- | --- | --- | --- | --- |")
for r in rows:
    first = r["first_trial"].split(" (")[0]
    print(f"| {r['candidate']} | {r['company']} | {TIER[r['tier']]} | {r['highest_phase_sponsor']} | {r['outcome'].capitalize()} | {first} |")
