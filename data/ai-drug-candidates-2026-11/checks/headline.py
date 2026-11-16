"""Checks: recompute the cohort counts under the fixed cut-off.

Usage: python headline.py  -> headline.json
Input: ../cohort/cohort_with_phase.csv.

Headline (16): 'headline' tier of cohort_with_phase.csv minus rows whose only entry document is a non-SEC document dated
after 2023-12-31. The cohort rule fixed 'documents dated 2019-2023' for non-SEC sources; the only rows
that entered on a 2024 non-SEC document are Generate's two (entry source dated 2024-01-04).
Sensitivity (18): the 'headline' tier of cohort_with_phase.csv.
"""
import csv, json, collections, math


def wilson(k, n, z=1.96):
    """95% Wilson score interval, in percent, one decimal."""
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]

SRC = "../cohort/cohort_with_phase.csv"
LATE_NON_SEC = {"https://generatebiomedicines.com/news/generatebiomedicines-fortifies-leadership-in-generative-ai"}
P3 = {"Phase 3", "Phase 4"}

rows = list(csv.DictReader(open(SRC)))
head18 = [r for r in rows if r["tier"] == "headline"]
head16 = [r for r in head18 if r["entry_source"] not in LATE_NON_SEC]


def first_year(r):
    s = r["first_trial_start"]
    # ClinicalTrials.gov dates start with the year; company-document rows read "2023 or earlier ..." etc.
    return s[:4] + (" or earlier" if "earlier" in s else "")


def stats(h):
    n = len(h)
    oc = collections.Counter(r["outcome"] for r in h)
    disc = [r for r in h if r["outcome"] == "discontinued"]
    broad = [r for r in h if r["outcome"] in ("discontinued", "superseded", "unknown")]
    p3 = [r["candidate"] for r in h if r["highest_phase"] in P3]
    pct = lambda k: round(100 * k / n, 1)
    return {
        "n": n,
        "companies_or_developers": sorted({r["company"] for r in h}),
        "by_claim": collections.Counter(r["claim"] for r in h),
        "by_outcome": oc,
        "strict_attrition": f"{len(disc)}/{n} = {pct(len(disc))}%",
        "strict_attrition_95ci": wilson(len(disc), n),
        "broad_attrition_95ci": wilson(len(broad), n),
        "reached_phase3_95ci": wilson(len(p3), n),
        "broad_attrition": f"{len(broad)}/{n} = {pct(len(broad))}%",
        "discontinued": [(r["candidate"], r["highest_phase"], r["outcome_reason"], r["outcome_date"]) for r in disc],
        "discontinued_by_phase": collections.Counter(r["highest_phase"] for r in disc),
        "reached_phase3": p3,
        "reached_phase3_share": f"{len(p3)}/{n} = {pct(len(p3))}%",
        "by_highest_phase": collections.Counter(r["highest_phase"] for r in h),
        "explicit": {"n": sum(r["claim"] == "explicit" for r in h),
                     "discontinued": sum(r["claim"] == "explicit" and r["outcome"] == "discontinued" for r in h)},
        "platform": {"n": sum(r["claim"] == "platform" for r in h),
                     "discontinued": sum(r["claim"] == "platform" and r["outcome"] == "discontinued" for r in h)},
        "first_trial_year": collections.Counter(first_year(r) for r in h),
        "first_trial_by_candidate": {r["candidate"]: r["first_trial_start"] for r in h},
    }


# Label sensitivity (added after an adversarial review): the calls most open to dispute.
# (a) REC-3964: AI tie is "brute-force approach which utilized phenomics" plus the Recursion OS; outcome wording is
#     "discontinued and/or partnering opportunities are being pursued". Drop it from the cohort.
# (b) DSP-0038 and DSP-2342: "active" rests on a pipeline page that states no phase. Treat both as unknown.
h_a = [r for r in head16 if r["candidate"] != "REC-3964"]
d_a = sum(r["outcome"] == "discontinued" for r in h_a)
h_b = [dict(r, outcome="unknown") if r["candidate"] in ("DSP-0038", "DSP-2342") else r for r in head16]
b_b = sum(r["outcome"] in ("discontinued", "superseded", "unknown") for r in h_b)
sens = {"without_REC-3964": {"n": len(h_a), "discontinued": d_a, "pct": round(100 * d_a / len(h_a), 1), "95ci": wilson(d_a, len(h_a))},
        "DSP-0038_DSP-2342_as_unknown": {"n": len(h_b), "broad": b_b, "pct": round(100 * b_b / len(h_b), 1), "95ci": wilson(b_b, len(h_b))}}

S = {"source": SRC, "as_of": "2026-11-16", "headline_16": stats(head16), "sensitivity_18": stats(head18),
     "excluded_from_headline": [r["candidate"] for r in head18 if r not in head16],
     "label_sensitivity_16": sens}
json.dump(S, open("headline.json", "w"), indent=1, default=dict)
print(json.dumps(S, indent=1, default=dict))
