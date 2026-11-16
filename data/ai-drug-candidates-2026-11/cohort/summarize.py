"""Cohort: join cohort.csv with raw/ctgov_cohort.json; count outcomes, phases and reasons.

Usage: python summarize.py  -> cohort_with_phase.csv, summary.json
Highest phase reached: highest phase label (as in the current list) among matching trials that are not
NOT_YET_RECRUITING or WITHDRAWN. Where no trial is registered on ClinicalTrials.gov, the phase stated in the
company source is used (DOC_PHASE). Strict attrition = discontinued / headline cohort. Broad attrition adds
"superseded" and "unknown".
"""
import csv, json, collections, datetime

RANK = ["Early Phase 1", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2/3", "Phase 3", "Phase 4"]
LAB = {("EARLY_PHASE1",): "Early Phase 1", ("PHASE1",): "Phase 1", ("PHASE1", "PHASE2"): "Phase 1/2",
       ("PHASE2",): "Phase 2", ("PHASE2", "PHASE3"): "Phase 2/3", ("PHASE3",): "Phase 3", ("PHASE4",): "Phase 4"}
NOT_STARTED = {"NOT_YET_RECRUITING", "WITHDRAWN"}
# Company-stated phase where ClinicalTrials.gov has no registration (sources in cohort.csv)
DOC_PHASE = {"DSP-1181": "Phase 1", "DSP-0038": "Phase 1", "DSP-2342": "Phase 1", "EXS4318": "Phase 1"}
# Phase 1 underway per Recursion 10-K filed 2023-02-27, not registered on ClinicalTrials.gov
DOC_START = {"REC-3964": "2023 or earlier (10-K filed 2023-02-27: Phase 1 underway)",
             "DSP-1181": "2020-01 or earlier (Sumitomo: Phase 1 as of 2021-01-28)",
             "DSP-0038": "2021 or earlier (Sumitomo: Phase 1 as of 2022-01-31)",
             "DSP-2342": "2023 or earlier (Sumitomo: Phase 1 as of 2023-10-31)",
             "EXS4318": "2023 or earlier (Exscientia 20-F filed 2023-03-23: in the clinic)"}
AS_OF = "2026-11-16"

ct = json.load(open("raw/ctgov_cohort.json"))
out = []
for r in csv.DictReader(open("cohort.csv")):
    c = ct["candidates"][r["candidate"]]
    started = [t for t in c["trials"] if t["status"] not in NOT_STARTED]
    labs = [LAB.get(tuple(sorted(t["phases"]))) for t in started]
    labs = [l for l in labs if l]
    top = max(labs, key=RANK.index) if labs else DOC_PHASE.get(r["candidate"], "none found")
    starts = sorted(t["start"] for t in started if t["start"])
    first = starts[0] if starts else ""
    if r["candidate"] in DOC_START and (not first or first > "2023-12-31"):
        first = DOC_START[r["candidate"]]
    out.append(dict(r, highest_phase=top, phase_source="ClinicalTrials.gov" if labs else "company document",
                    first_trial_start=first, n_trials=c["n_trials"],
                    trial_statuses=";".join(f'{t["nct"]}:{t["status"]}' for t in c["trials"])))
with open("cohort_with_phase.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

head = [o for o in out if o["tier"] == "headline"]
n = len(head)
disc = [o for o in head if o["outcome"] == "discontinued"]
broad = [o for o in head if o["outcome"] in ("discontinued", "superseded", "unknown")]
S = {
    "as_of": AS_OF,
    "rows": len(out),
    "by_tier": collections.Counter(o["tier"] for o in out),
    "headline_n": n,
    "headline_companies": sorted({o["company"] for o in head}),
    "headline_by_claim": collections.Counter(o["claim"] for o in head),
    "headline_by_outcome": collections.Counter(o["outcome"] for o in head),
    "strict_attrition": f"{len(disc)}/{n} = {100*len(disc)/n:.0f}%",
    "broad_attrition": f"{len(broad)}/{n} = {100*len(broad)/n:.0f}%",
    "discontinued": [(o["candidate"], o["highest_phase"], o["outcome_reason"], o["outcome_date"]) for o in disc],
    "discontinued_by_phase": collections.Counter(o["highest_phase"] for o in disc),
    "discontinued_by_reason": collections.Counter(o["outcome_reason"] for o in disc),
    "headline_by_highest_phase": {p: sum(1 for o in head if o["highest_phase"] == p) for p in RANK + ["none found"]},
    "headline_reached_phase3": [o["candidate"] for o in head if o["highest_phase"] in ("Phase 3", "Phase 4")],
    "explicit_only": {"n": sum(o["claim"] == "explicit" for o in head),
                      "discontinued": sum(o["claim"] == "explicit" and o["outcome"] == "discontinued" for o in head)},
    "other_tiers": [(o["candidate"], o["tier"], o["outcome"], o["highest_phase"]) for o in out if o["tier"] != "headline"],
}
json.dump(S, open("summary.json", "w"), indent=1, default=dict)
print(json.dumps(S, indent=1, default=dict))
for o in out:
    print(f'{o["candidate"][:24]:24} {o["tier"][:12]:12} {o["claim"][:9]:9} {o["highest_phase"]:10} {o["first_trial_start"][:12]:12} {o["outcome"]:12} {o["outcome_reason"]}')
