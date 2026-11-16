"""Current list: ClinicalTrials.gov API v2 lookups.

Usage:
  python ctgov.py sponsors raw        # all trials led by each Channel B company -> raw/ctgov_sponsors.json
  python ctgov.py candidates raw      # every search term in candidates.csv     -> raw/ctgov_candidates.json

Candidate search uses query.intr (intervention field) for each term in the `ctgov_terms` column
(semicolon-separated). Highest phase = highest phase across all returned trials whose
intervention list contains the term.
"""
import csv, json, sys, time, datetime, re
import requests

API = "https://clinicaltrials.gov/api/v2/studies"
FIELDS = ("NCTId,BriefTitle,Phase,OverallStatus,LeadSponsorName,InterventionName,"
          "StartDate,LastUpdatePostDate,WhyStopped")
SPONSORS = {  # Channel B companies, in seed order (raw/channel_b_seed.json), with sponsor strings
    "Insilico Medicine": ["Insilico"],
    "Atomwise": ["Atomwise"],
    "BenevolentAI": ["BenevolentAI", "Benevolent"],
    "Isomorphic Labs": ["Isomorphic"],
    "Xaira Therapeutics": ["Xaira"],
    "XtalPi": ["XtalPi"],
    "insitro": ["insitro"],
    "Owkin": ["Owkin"],
    "Pathos AI": ["Pathos"],
    "Healx": ["Healx"],
    "Enveda": ["Enveda"],
    "Cradle": ["Cradle Bio"],
    "Valo Health": ["Valo Health"],
    "Chai Discovery": ["Chai Discovery"],
    "Iktos": ["Iktos"],
}
ORDER = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"]


def get(params):
    out, token = [], None
    while True:
        p = dict(params, fields=FIELDS, pageSize=100)
        if token:
            p["pageToken"] = token
        r = requests.get(API, params=p, headers={"User-Agent": "Junctura Research"}, timeout=60)
        r.raise_for_status()
        d = r.json()
        for s in d.get("studies", []):
            ps = s["protocolSection"]
            out.append({
                "nct": ps["identificationModule"]["nctId"],
                "title": ps["identificationModule"]["briefTitle"],
                "phases": ps.get("designModule", {}).get("phases", []),
                "status": ps["statusModule"]["overallStatus"],
                "why_stopped": ps["statusModule"].get("whyStopped"),
                "start": ps["statusModule"].get("startDateStruct", {}).get("date"),
                "last_update": ps["statusModule"].get("lastUpdatePostDateStruct", {}).get("date"),
                "sponsor": ps["sponsorCollaboratorsModule"]["leadSponsor"]["name"],
                "interventions": [i["name"] for i in ps.get("armsInterventionsModule", {}).get("interventions", [])],
            })
        token = d.get("nextPageToken")
        time.sleep(0.3)
        if not token:
            return out


def top_phase(trials):
    ph = [p for t in trials for p in t["phases"] if p in ORDER]
    return max(ph, key=ORDER.index) if ph else None


def main(mode, out):
    today = datetime.date.today().isoformat()
    if mode == "sponsors":
        res = {"retrieved": today, "api": API, "companies": {}}
        for co, terms in SPONSORS.items():
            trials = {}
            for term in terms:
                for t in get({"query.spons": term}):
                    trials[t["nct"]] = t
            res["companies"][co] = list(trials.values())
            print(co, len(trials), file=sys.stderr)
        json.dump(res, open(f"{out}/ctgov_sponsors.json", "w"), indent=1)
    else:
        res = {"retrieved": today, "api": API, "candidates": {}}
        for row in csv.DictReader(open("candidates.csv")):
            terms = [x.strip() for x in row["ctgov_terms"].split(";") if x.strip()]
            trials = {}
            for term in terms:
                key = re.sub(r"[^a-z0-9]", "", term.lower())
                for t in get({"query.intr": f'"{term}"'}):
                    names = re.sub(r"[^a-z0-9]", "", " ".join(t["interventions"]).lower())
                    if key in names:
                        trials[t["nct"]] = t
            res["candidates"][row["candidate"]] = {
                "terms": terms, "n_trials": len(trials), "top_phase": top_phase(trials.values()),
                "statuses": sorted({t["status"] for t in trials.values()}), "trials": list(trials.values())}
            print(row["candidate"], len(trials), top_phase(trials.values()), file=sys.stderr)
        json.dump(res, open(f"{out}/ctgov_candidates.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
