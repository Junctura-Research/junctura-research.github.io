"""Cohort repair: recompute the dated cohort with the candidates added this cycle.

Usage: python repair_recompute.py -> new_rows_with_phase.csv, summary.json
Inputs: ../cohort/cohort_with_phase.csv (unchanged), new_rows.csv (build_rows.py), raw/ctgov_candidates.json (ctgov_new.py).
Rules (fixed before outcomes were traced):
  - Headline 16 and variant 18 as in ../checks/headline.py.
  - Enlarged headline = headline 16 + new headline rows (all new rows enter on SEC filings or on non-SEC documents dated
    2019-2023, so each also joins the variant).
  - Highest phase: highest phase label among matching ClinicalTrials.gov trials that have started (not
    NOT_YET_RECRUITING or WITHDRAWN); company-stated phase where none (DOC_PHASE). Reached Phase 3 = Phase 3 or Phase 4
    (the checks). Strict = discontinued; broad adds superseded and unknown. 95% Wilson intervals as in the checks.
"""
import csv, json, collections, math

RANK = ["Early Phase 1", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2/3", "Phase 3", "Phase 4"]
LAB = {("EARLY_PHASE1",): "Early Phase 1", ("PHASE1",): "Phase 1", ("PHASE1", "PHASE2"): "Phase 1/2",
       ("PHASE2",): "Phase 2", ("PHASE2", "PHASE3"): "Phase 2/3", ("PHASE3",): "Phase 3", ("PHASE4",): "Phase 4"}
NOT_STARTED = {"NOT_YET_RECRUITING", "WITHDRAWN"}
P3 = {"Phase 3", "Phase 4"}
LATE_NON_SEC = {"https://generatebiomedicines.com/news/generatebiomedicines-fortifies-leadership-in-generative-ai"}
CT_KEY = {"AU-007 (imneskibart)": "AU-007", "ADG126 (muzastotug)": "ADG126", "bamlanivimab (LY-CoV555)": "bamlanivimab",
          "bebtelovimab (LY-CoV1404)": "bebtelovimab", "PHI-101 (lasmotinib)": "PHI-101"}


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def pct(k, n): return round(100 * k / n, 1)


old = list(csv.DictReader(open("../cohort/cohort_with_phase.csv")))
for r in old: r["origin"] = "the original cohort"
head18 = [r for r in old if r["tier"] == "headline"]
head16 = [r for r in head18 if r["entry_source"] not in LATE_NON_SEC]

ct = json.load(open("raw/ctgov_candidates.json"))
new = []
for r in csv.DictReader(open("new_rows.csv")):
    trials = ct[CT_KEY.get(r["candidate"], r["candidate"])]["trials"]
    started = [t for t in trials if t["status"] not in NOT_STARTED]
    labs = [l for l in (LAB.get(tuple(sorted(t["phases"]))) for t in started) if l]
    top = max(labs, key=RANK.index) if labs else (r["doc_phase"] or "none found")
    top_nct = [t["nct"] for t in started if LAB.get(tuple(sorted(t["phases"]))) == top]
    starts = sorted(t["start"] for t in started if t["start"])
    new.append(dict(r, highest_phase=top, highest_phase_trials=";".join(top_nct),
                    phase_source="ClinicalTrials.gov" if labs else "company document",
                    first_trial_start=starts[0] if starts else "", n_trials=len(trials),
                    trial_statuses=";".join(f'{t["nct"]}:{t["status"]}' for t in trials)))
with open("new_rows_with_phase.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(new[0].keys())); w.writeheader(); w.writerows(new)

new_head = [r for r in new if r["tier"] == "headline"]
for r in new_head:  # entry rule check: trial by 2023-12-31
    assert r["first_trial_start"] and r["first_trial_start"][:10] <= "2023-12-31", r["candidate"]


def stats(h):
    n = len(h)
    disc = [r for r in h if r["outcome"] == "discontinued"]
    broad = [r for r in h if r["outcome"] in ("discontinued", "superseded", "unknown")]
    p3 = [r["candidate"] for r in h if r["highest_phase"] in P3]
    return {
        "n": n, "by_claim": collections.Counter(r["claim"] for r in h),
        "by_outcome": collections.Counter(r["outcome"] for r in h),
        "strict": f"{len(disc)}/{n} = {pct(len(disc), n)}%", "strict_95ci": wilson(len(disc), n),
        "broad": f"{len(broad)}/{n} = {pct(len(broad), n)}%", "broad_95ci": wilson(len(broad), n),
        "reached_phase3": p3, "reached_phase3_share": f"{len(p3)}/{n} = {pct(len(p3), n)}%",
        "reached_phase3_95ci": wilson(len(p3), n),
        "discontinued": [(r["candidate"], r["highest_phase"], r["outcome_reason"], r["outcome_date"]) for r in disc],
        "discontinued_by_phase": collections.Counter(r["highest_phase"] for r in disc),
        "by_highest_phase": collections.Counter(r["highest_phase"] for r in h),
        "explicit": {"n": sum(r["claim"] == "explicit" for r in h),
                     "discontinued": sum(r["claim"] == "explicit" and r["outcome"] == "discontinued" for r in h)},
        "platform": {"n": sum(r["claim"] == "platform" for r in h),
                     "discontinued": sum(r["claim"] == "platform" and r["outcome"] == "discontinued" for r in h)},
        "companies": len({r["company"].split(" (")[0] for r in h}),
    }


def strict_line(h):
    n = len(h); k = sum(r["outcome"] == "discontinued" for r in h)
    return {"n": n, "discontinued": k, "pct": pct(k, n), "95ci": wilson(k, n)}


def setout(h, names, outcome):
    return [dict(r, outcome=outcome) if r["candidate"] in names else r for r in h]


enl = head16 + new_head
var = head18 + new_head
m2_only = head16 + [r for r in new_head if r["origin"].startswith("m2")]
cos_new = sorted({r["company"] for r in new_head})
abcl = {"bamlanivimab (LY-CoV555)", "bebtelovimab (LY-CoV1404)", "TAK-920/DNL919"}
sens = {
    "audit_ten_plus_PHI101_only (no completeness additions)": strict_line(m2_only),
    "audit_ten_only (no PHI-101, no completeness additions)": strict_line([r for r in m2_only if not r["candidate"].startswith("PHI-101")]),
    "AC0682_AC176_discontinued (all trials terminated)": strict_line(setout(enl, {"AC0682", "AC176"}, "discontinued")),
    "bamlanivimab_bebtelovimab_active (AbCellera table 'Marketed, EUA')": strict_line(setout(enl, {"bamlanivimab (LY-CoV555)", "bebtelovimab (LY-CoV1404)"}, "active")),
    "ADG106_active (investigator trials recruiting)": strict_line(setout(enl, {"ADG106"}, "active")),
    "without_AbCellera_three (pandemic antibodies and partner program)": strict_line([r for r in enl if r["candidate"] not in abcl]),
    "without_REC-3964 (the checks sensitivity)": strict_line([r for r in enl if r["candidate"] != "REC-3964"]),
    "all_flagged_against (AC0682, AC176 discontinued; ADG116 unknown)": strict_line(setout(setout(enl, {"AC0682", "AC176"}, "discontinued"), {"ADG116"}, "unknown")),
}
p3_alt = {"bebtelovimab_not_counted (its Phase 4 label is an investigator-led comparison of authorized antibodies)":
          f"{len([r for r in enl if r['highest_phase'] in P3 and not r['candidate'].startswith('bebtelovimab')])}/{len(enl)}",
          "variant_bebtelovimab_not_counted": f"{len([r for r in var if r['highest_phase'] in P3 and not r['candidate'].startswith('bebtelovimab')])}/{len(var)}"}

# Phase 3 tier counts across all current AI-linked candidates (the checks Note table: 1 explicit, 3 explicit or
# platform, 5 with borderline), with bamlanivimab in the platform tier.
tiers_before = {"explicit": 1, "explicit_or_platform": 3, "with_borderline": 5}
p3_new = [r for r in new if r["highest_phase"] in P3 and r["tier"] == "headline"]
add_platform = [r["candidate"] for r in p3_new if r["claim"] == "platform"]
add_explicit = [r["candidate"] for r in p3_new if r["claim"] == "explicit"]
tiers_after = {"explicit": tiers_before["explicit"] + len(add_explicit),
               "explicit_or_platform": tiers_before["explicit_or_platform"] + len(add_explicit) + len(add_platform),
               "with_borderline": tiers_before["with_borderline"] + len(add_explicit) + len(add_platform),
               "added": add_explicit + add_platform,
               "note": "bebtelovimab reaches the Phase 3-or-later set only through a Phase 4 investigator-led trial label; "
                       "without it the counts are 1, 4 and 6. MDR-001 (company-stated Phase 3, registry not yet "
                       "recruiting) is not counted (registry status rule)."}

S = {"as_of": "2026-11-17", "headline_16_unchanged": stats(head16), "variant_18_unchanged": stats(head18),
     "enlarged_headline": stats(enl), "enlarged_variant": stats(var),
     "new_headline_rows": [(r["candidate"], r["claim"], r["origin"], r["first_trial_start"], r["highest_phase"], r["outcome"]) for r in new_head],
     "new_rows_alone": stats(new_head), "new_companies": cos_new,
     "other_tier_rows": [(r["candidate"], r["tier"], r["outcome"], r["highest_phase"]) for r in new if r["tier"] != "headline"],
     "strict_sensitivities_enlarged": sens, "phase3_sensitivity_enlarged": p3_alt,
     "phase3_tier_counts_all_candidates": {"before": tiers_before, "after": tiers_after}}
json.dump(S, open("repair_summary.json", "w"), indent=1, default=dict, ensure_ascii=False)
print(json.dumps({k: S[k] for k in ("enlarged_headline", "enlarged_variant", "new_rows_alone", "strict_sensitivities_enlarged",
                                     "phase3_sensitivity_enlarged", "phase3_tier_counts_all_candidates")}, indent=1, default=dict))
for r in new:
    print(f'{r["candidate"][:26]:26} {r["tier"][:10]:10} {r["claim"]:9} {r["first_trial_start"]:11} {r["highest_phase"]:9} {r["highest_phase_trials"][:25]:25} {r["outcome"]}')
