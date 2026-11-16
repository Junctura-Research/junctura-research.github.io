"""Current list: join candidates.csv with raw/ctgov_candidates.json and count by phase, claim and channel.

Usage: python summarize.py   -> writes candidates_with_phase.csv and summary.json, prints tables.
Highest phase: each trial is labeled by its phase list (PHASE1+PHASE2 = "Phase 1/2"); the candidate's
highest phase is the highest trial label. Candidates with no matching trial are "none found".
"AI candidates" = claim explicit or platform; computational, indication and borderline rows are excluded.
"""
import csv, json, collections

RANK = ["Early Phase 1", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2/3", "Phase 3", "Phase 4"]
LAB = {("EARLY_PHASE1",): "Early Phase 1", ("PHASE1",): "Phase 1", ("PHASE1", "PHASE2"): "Phase 1/2",
       ("PHASE2",): "Phase 2", ("PHASE2", "PHASE3"): "Phase 2/3", ("PHASE3",): "Phase 3", ("PHASE4",): "Phase 4"}
STOP = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}

ct = json.load(open("raw/ctgov_candidates.json"))
rows = list(csv.DictReader(open("candidates.csv")))
out = []
for r in rows:
    c = ct["candidates"][r["candidate"]]
    labs = [LAB.get(tuple(sorted(t["phases"]))) for t in c["trials"]]
    labs = [l for l in labs if l]
    top = max(labs, key=RANK.index) if labs else "none found"
    stopped = [t["nct"] for t in c["trials"] if t["status"] in STOP]
    active = [t["nct"] for t in c["trials"] if t["status"] in {"RECRUITING", "ACTIVE_NOT_RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION"}]
    out.append(dict(r, n_trials=c["n_trials"], highest_phase=top, n_active=len(active),
                    stopped_trials=";".join(stopped),
                    ai_candidate="yes" if r["claim"] in ("explicit", "platform") else "no"))
with open("candidates_with_phase.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)

ai = [o for o in out if o["ai_candidate"] == "yes"]
reg = [o for o in ai if o["highest_phase"] != "none found"]
S = {
    "rows": len(out),
    "by_claim": collections.Counter(o["claim"] for o in out),
    "ai_candidates": len(ai),
    "ai_with_registered_trial": len(reg),
    "ai_by_channel": collections.Counter(o["channel"] for o in ai),
    "ai_with_trial_by_channel": collections.Counter(o["channel"] for o in reg),
    "ai_companies": sorted({o["company"].split(" (")[0].split(" /")[0] for o in ai}),
    "ai_by_phase": {p: sum(1 for o in ai if o["highest_phase"] == p) for p in RANK + ["none found"]},
    "ai_by_phase_explicit": {p: sum(1 for o in ai if o["highest_phase"] == p and o["claim"] == "explicit") for p in RANK + ["none found"]},
    "ai_by_step": collections.Counter(o["ai_step"] for o in ai),
    "ai_with_stopped_trial": [o["candidate"] for o in reg if o["stopped_trials"]],
    "phase3": [(o["candidate"], o["claim"], o["ai_step"]) for o in out if o["highest_phase"] in ("Phase 3", "Phase 4")],
}
S["ai_companies_n"] = len(S["ai_companies"])
json.dump(S, open("summary.json", "w"), indent=1, default=dict)
print(json.dumps(S, indent=1, default=dict))
for o in out:
    print(f'{o["candidate"][:26]:26} {o["channel"]} {o["claim"]:13} {o["ai_step"]:15} {o["highest_phase"]:11} trials={o["n_trials"]} active={o["n_active"]} stopped={o["stopped_trials"]}')
