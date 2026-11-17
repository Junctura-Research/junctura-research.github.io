"""Coverage searches: apply the outcome and Phase 3 rules to the cohort repair's enlarged cohort. No new data.

Usage (from this folder): python apply_pr25.py -> cohort_30_rules.json
Inputs: ../cohort/cohort_with_phase.csv and new_rows_with_phase.csv (unchanged), via the same headline-16 rule as
../012/recompute.py.
Rules (2026-11-17):
  1. Outcome precedence: regulator action > company/partner stop statement > registry status > pipeline listing.
     This rule was set after the data were seen. Sensitivity: 20.0% (antibodies 'active').
  2. 'Reached Phase 3 or later' counts only trials run by the sponsor or its development partner. Bebtelovimab's
     highest sponsor/partner trial is Lilly's Phase 2/3 BLAZE-1 record (NCT04427501; Phase 2 BLAZE-4 is NCT04634409; new_rows_with_phase.csv note), so it does not count.
     Bamlanivimab keeps Lilly's Phase 3 (NCT04497987). Sensitivity: 4 of 30 with bebtelovimab.
  3. AC0682 and AC176 are 'unknown' (all trials terminated; undated pipeline listing). Unknown counts in the broad
     rate, not the strict one. Sensitivity: both discontinued (33.3%).
"""
import csv, json, math

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]

LATE_NON_SEC = {"https://generatebiomedicines.com/news/generatebiomedicines-fortifies-leadership-in-generative-ai"}
old = [r for r in csv.DictReader(open("../cohort/cohort_with_phase.csv")) if r["tier"] == "headline"]
head16 = [r for r in old if r["entry_source"] not in LATE_NON_SEC]
new = [r for r in csv.DictReader(open("new_rows_with_phase.csv")) if r["tier"] == "headline"]
enl = head16 + new
assert len(enl) == 30
for r in enl:
    if r["candidate"] in ("AC0682", "AC176"):
        r["outcome"] = "unknown"
SPONSOR_P3 = {"NX-5948 (bexobrutideg)", "ISM001-055 (rentosertib)", "bamlanivimab (LY-CoV555)"}
p3_label = [r["candidate"] for r in enl if r["highest_phase"] in ("Phase 3", "Phase 4")]
p3_main = [c for c in p3_label if c in SPONSOR_P3]
assert set(p3_main) == SPONSOR_P3 and set(p3_label) - SPONSOR_P3 == {"bebtelovimab (LY-CoV1404)"}

def line(k, n): return {"k": k, "n": n, "pct": round(100 * k / n, 1), "95ci": wilson(k, n)}
n = len(enl)
disc = [r["candidate"] for r in enl if r["outcome"] == "discontinued"]
broad = [r["candidate"] for r in enl if r["outcome"] in ("discontinued", "unknown", "superseded")]
out = {
    "as_of": "2026-11-17", "n": n,
    "by_outcome": {o: sum(r["outcome"] == o for r in enl) for o in ("active", "discontinued", "unknown", "superseded")},
    "strict_main": line(len(disc), n), "discontinued": disc,
    "broad_main": line(len(broad), n), "broad_members_not_discontinued": [c for c in broad if c not in disc],
    "phase3_main_sponsor_or_partner_trials": dict(line(len(p3_main), n), candidates=p3_main),
    "sensitivity": {
        "strict_without_precedence_rule (bamlanivimab, bebtelovimab active)": line(len(disc) - 2, n),
        "strict_AC0682_AC176_discontinued": line(len(disc) + 2, n),
        "phase3_with_investigator_phase4 (bebtelovimab)": line(len(p3_label), n),
    },
    "phase3_tiers_all_current_candidates": {"explicit": 1, "explicit_or_platform": 4, "with_borderline": 6,
        "with_bebtelovimab_sensitivity": {"explicit": 1, "explicit_or_platform": 5, "with_borderline": 7}},
}
json.dump(out, open("cohort_30_rules.json", "w"), indent=1)
print(json.dumps(out, indent=1))
