"""Checks: check whether the current list's code-name search missed later-phase trials registered under a generic name.

Found during the checks: RLY-2608's Phase 3 trial (NCT06982521) names the drug only as 'zovegalisib', so the current list
recorded RLY-2608 at Phase 2. This script repeats the check for every current-list candidate.
Usage: python generic_name_check.py raw -> raw/generic_name_check.json
Method: for each candidate, fetch each matched trial's interventions (name + otherNames) from ClinicalTrials.gov
API v2. Any name that contains the candidate's code (or appears with it as an otherName), and is not already a
search term, is searched with query.intr. Reports the highest phase across all trials found (started trials only).
"""
import csv, json, sys, time, requests

RANK = {"EARLY_PHASE1": 0, "PHASE1": 1, "PHASE2": 2, "PHASE3": 3, "PHASE4": 4}
API = "https://clinicaltrials.gov/api/v2/studies"
ct = json.load(open("../current-list/raw/ctgov_candidates.json"))
cands = ct.get("candidates", ct)
rows = {r["candidate"]: r for r in csv.DictReader(open("../current-list/candidates_with_phase.csv"))}
out = {}
for name, c in cands.items():
    terms = {t.lower() for t in c["terms"]}
    extra = set()
    for t in c["trials"]:
        iv = requests.get(f'{API}/{t["nct"]}', params={"fields": "protocolSection.armsInterventionsModule.interventions"},
                          timeout=60).json()["protocolSection"].get("armsInterventionsModule", {}).get("interventions", [])
        time.sleep(0.2)
        for i in iv:
            names = [i["name"]] + i.get("otherNames", [])
            if any(any(term in n.lower() for term in terms) for n in names):
                extra |= {n.strip() for n in names if n.strip().lower() not in terms}
    found = {}
    for e in sorted(extra):
        for s in requests.get(API, params={"query.intr": f'"{e}"', "pageSize": 100,
                              "fields": "NCTId,Phase,OverallStatus,StartDate"}, timeout=60).json().get("studies", []):
            p = s["protocolSection"]
            found[p["identificationModule"]["nctId"]] = {"phases": p.get("designModule", {}).get("phases") or [],
                                                         "status": p["statusModule"]["overallStatus"], "via": e}
        time.sleep(0.2)
    started = [v for k, v in found.items() if v["status"] not in ("NOT_YET_RECRUITING", "WITHDRAWN")]
    top = max((RANK.get(ph, -1) for v in started for ph in v["phases"]), default=-1)
    out[name] = {"claim": rows.get(name, {}).get("claim"), "current_list_top": c["top_phase"], "extra_names": sorted(extra),
                 "extra_top": [k for k, v in RANK.items() if v == top][0] if top >= 0 else None,
                 "new_trials": {k: v for k, v in found.items() if k not in {t["nct"] for t in c["trials"]}}}
    print(name, out[name]["claim"], c["top_phase"], "->", out[name]["extra_top"], sorted(extra)[:4])
json.dump(out, open(f"{sys.argv[1]}/generic_name_check.json", "w"), indent=1)
