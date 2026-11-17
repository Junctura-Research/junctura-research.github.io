"""Cohort table: assemble the 32-candidate dated cohort (original cohort, repair, Drug Farm, outcome and Phase 3 rules). No new data.
Usage (from this folder): python cohort_32.py -> cohort_32.csv
"""
import csv
LATE = {"https://generatebiomedicines.com/news/generatebiomedicines-fortifies-leadership-in-generative-ai"}
old = [r for r in csv.DictReader(open("../cohort/cohort_with_phase.csv")) if r["tier"] == "headline" and r["entry_source"] not in LATE]
new = [r for r in csv.DictReader(open("new_rows_with_phase.csv")) if r["tier"] == "headline"]
n13 = list(csv.DictReader(open("drug_farm_rows.csv")))
rows = []
for r in old + new + n13:
    out = r["outcome"]
    if r["candidate"] in ("AC0682", "AC176"):
        out = "unknown"  # rule 3
    hp = r["highest_phase"]
    # rule 2: highest sponsor/partner trial. Bebtelovimab's is Lilly's Phase 2/3 BLAZE-1 (NCT04427501);
    # bamlanivimab's is Lilly's Phase 3 (NCT04497987). Phase 4 labels are investigator-led.
    sp = {"bebtelovimab (LY-CoV1404)": "Phase 2/3", "bamlanivimab (LY-CoV555)": "Phase 3"}.get(r["candidate"], hp)
    rows.append({"candidate": r["candidate"], "company": r["company"], "claim": r["claim"], "outcome": out,
                 "highest_phase_registry": hp, "highest_phase_sponsor": sp,
                 "first_trial": r.get("first_trial_start") or r.get("first_trial", ""),
                 "trials": r.get("trial_statuses", "")})
assert len(rows) == 32
assert sum(r["outcome"] == "discontinued" for r in rows) == 8
w = csv.DictWriter(open("cohort_32.csv", "w", newline=""), fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
