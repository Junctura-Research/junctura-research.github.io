"""Coverage searches: add the two Drug Farm candidates found by the coverage searches to the the outcome rules cohort and recompute.

Usage (from this folder): python cohort_013.py -> drug_farm_rows.csv (new rows), cohort_32_before_recheck.json
Inputs: cohort_30_rules.json (apply_rules.py) for the 30-candidate baseline; saved texts in raw/sources/.
Entry rule (the original cohort and repair): tied to AI (explicit or platform) in a company document dated 2019-2023, and in a started
trial by 2023-12-31. Outcome rule with the outcome precedence rule: regulator action > company/partner stop statement >
registry status > pipeline listing. Phase 3 counts sponsor or partner trials only.
"""
import csv, json, math

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]
def line(k, n): return {"k": k, "n": n, "pct": round(100 * k / n, 1), "95ci": wilson(k, n)}

AI_SENTENCE = "IDInVivo platform combines breakthrough technologies in genetics and AI to discover new treatments."
NEW = [
 dict(candidate="DF-003", company="Drug Farm", tier="headline", claim="platform",
      entry_source="https://www.biospace.com/drug-farm-doses-first-patient-in-phase-1-trial-for-alpk1-inhibitor-df-003",
      entry_file="raw/sources/founding_drugfarm_df003_2023.txt", entry_date="2023-09-19",
      entry_quote="DF-003, the 2 nd compound from IDInVivo and MedChem5 platform to enter clinical trials | " + AI_SENTENCE,
      first_trial="2023-09-15 (NCT05997641, Phase 1)", highest_phase="Phase 1",
      phase_source="ClinicalTrials.gov NCT05997641 (ACTIVE_NOT_RECRUITING), NCT06395285 (Phase 1, RECRUITING, start 2025-05-27); raw/ctgov_drugfarm.json",
      outcome="active", outcome_basis="registry: sponsor trial recruiting (no regulator action or stop statement found)"),
 dict(candidate="DF-006", company="Drug Farm", tier="headline", claim="platform",
      entry_source="https://www.eatg.org/hiv-news/drug-farm-doses-first-patient-in-part-3-of-phase-1-chronic-hepatitis-b-trial/",
      entry_file="raw/sources/check_drugfarm_df006_2023_eatg.txt", entry_date="2023-09-26",
      entry_quote="it has dosed the first chronic hepatitis B patient in Part 3 of its Phase 1 clinical trial (ANZCTR Trial ID: ACTRN12621000592842 ) | " + AI_SENTENCE,
      first_trial="by 2023-09-26 (ACTRN12621000592842; Part 3 dosed 2023-09-26; earlier parts' start not read)", highest_phase="Phase 1",
      phase_source="company release 2023-09-26 (ANZCTR returned HTTP 403 to scripted requests)",
      outcome="active", outcome_basis="pipeline listing on current site (raw/sources/founding_r0_drugfarm_appjs.txt: DF-006, Hepatitis B); registry unreadable; no stop statement found"),
]
for r in NEW:
    t = " ".join(open(r["entry_file"], encoding="utf-8").read().split())
    for q in r["entry_quote"].split(" | "):
        assert " ".join(q.split()) in t, (r["candidate"], q)
with open("drug_farm_rows.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(NEW[0])); w.writeheader(); w.writerows(NEW)

b = json.load(open("cohort_30_rules.json"))
n = b["n"] + len(NEW)
k_strict = b["strict_main"]["k"]           # both new rows active
k_broad = b["broad_main"]["k"]
k_p3 = b["phase3_main_sponsor_or_partner_trials"]["k"]
out = {"as_of": "2026-11-17", "n": n, "added": [r["candidate"] for r in NEW],
       "by_claim": {"explicit": 12, "platform": 18 + 2},
       "strict_main": line(k_strict, n), "broad_main": line(k_broad, n),
       "phase3_main_sponsor_or_partner_trials": line(k_p3, n),
       "sensitivity": {"strict_without_precedence_rule": line(k_strict - 2, n),
                       "strict_AC0682_AC176_discontinued": line(k_strict + 2, n),
                       "strict_DF-006_unknown_counts_broad_only": line(k_strict, n),
                       "broad_DF-006_unknown (registry unread, undated listing)": line(k_broad + 1, n),
                       "phase3_with_investigator_phase4 (bebtelovimab)": line(k_p3 + 1, n),
                       "baseline_30_without_Drug_Farm": b["strict_main"]},
       "companies": 18}
json.dump(out, open("cohort_32_before_recheck.json", "w"), indent=1)
print(json.dumps(out, indent=1))
