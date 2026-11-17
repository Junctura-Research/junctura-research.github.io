"""Cohort repair: ClinicalTrials.gov API v2 queries for the cohort repair.

Usage: python ctgov_new.py raw   -> raw/ctgov_sponsors_2023.json, raw/ctgov_candidates.json, raw/ctgov_phase3.json

1. sponsors: every trial led by (or with as collaborator) each new company, started on or before 2023-12-31
   (completeness check: other candidates at the same companies).
2. candidates: intervention search for each tested candidate's codes and names (the current list/004 matching rule:
   the term appears in the trial's intervention names or other names).
3. phase3: Phase 3 (incl. Phase 2/3) trials led by each company in the coverage audit's significant list (Rule 0 "in") not
   searched in the checks, plus the the coverage audit gap companies, plus Lilly trials naming AbCellera-co-discovered antibodies.
   Sponsor match: the lead sponsor's name contains the search term (case-insensitive), to drop fuzzy matches.
"""
import json, sys, time, requests

API = "https://clinicaltrials.gov/api/v2/studies"
FIELDS = ("NCTId,BriefTitle,Phase,OverallStatus,StartDate,InterventionName,InterventionOtherName,"
          "LeadSponsorName,CollaboratorName,WhyStopped,LastUpdatePostDate")
NEW_COS = {"MindRank AI": ["MindRank"], "Accutar Biotechnology": ["Accutar"], "Biolojic Design / Aulos": ["Aulos", "Biolojic"],
           "Adagene": ["Adagene"], "AbCellera (and Lilly)": ["AbCellera"], "Pharos iBio": ["Pharos"]}
CANDIDATES = {
    "MDR-001": ["MDR-001", "MDR001"],
    "AC0682": ["AC0682", "AC682"], "AC176": ["AC176", "AC0176"], "AC699": ["AC699", "AC0699"], "AC676": ["AC676", "AC0676"],
    "AU-007": ["AU-007", "AU007"],
    "ADG126": ["ADG126", "muzastotug"], "ADG106": ["ADG106"], "ADG116": ["ADG116"],
    "bamlanivimab": ["bamlanivimab", "LY-CoV555", "LY3819253"],
    "bebtelovimab": ["bebtelovimab", "LY-CoV1404", "LY3853113"],
    "PHI-101": ["PHI-101", "PHI101"],
    # completeness-check additions (found from sponsor searches and filings this cycle)
    "TAK-920/DNL919": ["DNL919", "TAK-920"], "ADG206": ["ADG206"], "ADG104": ["ADG104"], "ADG125": ["ADG125", "BC006"],
}
P3_COS = {  # the coverage audit significant list (Rule 0 "in") minus the 17 companies searched in the checks, plus gap companies
    "AbCellera": ["AbCellera"], "Adagene": ["Adagene"], "Anew Labs": ["Anew"], "Atomwise": ["Atomwise"],
    "BigHat Biosciences": ["BigHat"], "BullFrog AI": ["BullFrog"], "Chai Discovery": ["Chai Discovery"], "Creyon Bio": ["Creyon"],
    "Dyno Therapeutics": ["Dyno Therapeutics"], "Earendil Labs": ["Earendil"], "Envisagenics": ["Envisagenics"],
    "Genesis Therapeutics": ["Genesis Therapeutics"], "Healx": ["Healx"], "insitro": ["insitro"], "Isomorphic Labs": ["Isomorphic"],
    "Kiromic BioPharma": ["Kiromic"], "Kymera": ["Kymera"], "METiS TechBio": ["METiS"], "MindRank AI": ["MindRank"],
    "MindWalk": ["MindWalk"], "Nabla Bio": ["Nabla"], "Pharos iBio": ["Pharos"], "Profluent": ["Profluent"],
    "Relation Therapeutics": ["Relation Therapeutics"], "Soley Therapeutics": ["Soley"], "Superluminal Medicines": ["Superluminal"],
    "Valo Health": ["Valo Health"], "Xaira": ["Xaira"], "XtalPi": ["XtalPi"], "Accutar Biotechnology": ["Accutar"],
    "Biolojic Design": ["Biolojic"], "Aulos Bioscience": ["Aulos"],
}


def get_all(params):
    out, token = [], None
    while True:
        p = dict(params, pageSize=200, fields=FIELDS)
        if token: p["pageToken"] = token
        j = requests.get(API, params=p, timeout=60).json()
        out += j.get("studies", [])
        token = j.get("nextPageToken")
        time.sleep(0.25)
        if not token: return out


def rec(s):
    p = s["protocolSection"]; arms = p.get("armsInterventionsModule", {}).get("interventions", [])
    sp = p.get("sponsorCollaboratorsModule", {})
    return {"nct": p["identificationModule"]["nctId"], "title": p["identificationModule"]["briefTitle"],
            "phases": p.get("designModule", {}).get("phases") or [], "status": p["statusModule"]["overallStatus"],
            "start": p["statusModule"].get("startDateStruct", {}).get("date", ""),
            "why_stopped": p["statusModule"].get("whyStopped", ""),
            "last_update": p["statusModule"].get("lastUpdatePostDateStruct", {}).get("date", ""),
            "lead": sp.get("leadSponsor", {}).get("name", ""), "collaborators": [c["name"] for c in sp.get("collaborators", [])],
            "interventions": [i["name"] for i in arms], "other_names": sum((i.get("otherNames", []) for i in arms), [])}


def main(raw):
    # 1. sponsors, trials started by 2023-12-31
    spons = {}
    for co, terms in NEW_COS.items():
        hits = {}
        for t in terms:
            for s in get_all({"query.spons": t}):
                r = rec(s)
                names = [r["lead"]] + r["collaborators"]
                if any(t.lower() in n.lower() for n in names) and r["start"] and r["start"][:10] <= "2023-12-31":
                    hits[r["nct"]] = r
        spons[co] = hits
        print("SPONSOR", co, len(hits))
        for r in sorted(hits.values(), key=lambda r: r["start"]):
            print("   ", r["nct"], r["start"], r["status"], r["phases"], r["lead"][:30], r["interventions"][:3])
    json.dump(spons, open(f"{raw}/ctgov_sponsors_2023.json", "w"), indent=1)
    # 2. candidates
    cands = {}
    for c, terms in CANDIDATES.items():
        hits = {}
        for t in terms:
            for s in get_all({"query.intr": t}):
                r = rec(s)
                blob = " ".join(r["interventions"] + r["other_names"]).lower().replace("-", "").replace(" ", "")
                if t.lower().replace("-", "").replace(" ", "") in blob:
                    hits[r["nct"]] = r
        cands[c] = {"terms": terms, "n_trials": len(hits), "trials": sorted(hits.values(), key=lambda r: r["start"])}
        print("CAND", c, len(hits))
        for r in cands[c]["trials"]:
            print("   ", r["nct"], r["start"], r["status"], r["phases"], r["lead"][:30], r["why_stopped"][:80])
    json.dump(cands, open(f"{raw}/ctgov_candidates.json", "w"), indent=1)
    # 3. Phase 3 sponsor search
    p3 = {}
    for co, terms in P3_COS.items():
        hits = {}
        for t in terms:
            for s in get_all({"query.lead": t}):
                r = rec(s)
                if t.lower() in r["lead"].lower() and "PHASE3" in r["phases"]:
                    hits[r["nct"]] = r
        p3[co] = hits
        for r in hits.values():
            print("P3", co, r["nct"], r["start"], r["status"], r["phases"], r["lead"][:30], r["interventions"][:3])
    lilly = {}
    for t in CANDIDATES["bamlanivimab"] + CANDIDATES["bebtelovimab"]:
        for s in get_all({"query.intr": t}):
            r = rec(s)
            if "PHASE3" in r["phases"]:
                lilly[r["nct"]] = r
    p3["Lilly trials naming AbCellera-co-discovered antibodies"] = lilly
    for r in lilly.values():
        print("P3 Lilly/AbCellera", r["nct"], r["start"], r["status"], r["phases"], r["lead"][:30], r["interventions"][:3])
    json.dump(p3, open(f"{raw}/ctgov_phase3.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
