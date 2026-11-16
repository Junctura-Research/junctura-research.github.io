"""Checks: re-check, on the Note's as-of date, the facts the Note states about the present.

Usage: python status_check.py raw -> raw/status_check.json
1. ClinicalTrials.gov API v2: status, phase, start and estimated primary completion of the Phase 3 trials
   of the three AI candidates at Phase 3 in the current list.
2. openFDA Drugs@FDA: approvals under the generic names of those candidates (same query as the current list's
   fda_check.py).
3. Europe PMC: publication record of the AlphaFold 2 paper (date used in the Note's vintage limitation).
"""
import json, sys, datetime, requests

out = {"retrieved": datetime.date.today().isoformat(), "trials": {}, "fda": {}, "alphafold2": {}}
FIELDS = ",".join(["protocolSection.identificationModule.briefTitle", "protocolSection.statusModule.overallStatus",
                   "protocolSection.statusModule.startDateStruct", "protocolSection.statusModule.primaryCompletionDateStruct",
                   "protocolSection.designModule.phases", "protocolSection.sponsorCollaboratorsModule.leadSponsor"])
for nct in ["NCT07687459", "NCT07516093", "NCT07276724", "NCT07359846"]:
    p = requests.get(f"https://clinicaltrials.gov/api/v2/studies/{nct}", params={"fields": FIELDS}, timeout=60).json()["protocolSection"]
    out["trials"][nct] = {"title": p["identificationModule"]["briefTitle"], "status": p["statusModule"]["overallStatus"],
                          "start": p["statusModule"]["startDateStruct"], "primary_completion": p["statusModule"].get("primaryCompletionDateStruct"),
                          "phases": p["designModule"]["phases"], "sponsor": p["sponsorCollaboratorsModule"]["leadSponsor"]["name"]}
for n in ["rentosertib", "bexobrutideg", "GB-0895"]:
    q = f'openfda.generic_name:"{n}" OR products.active_ingredients.name:"{n.upper()}" OR products.brand_name:"{n}"'
    r = requests.get("https://api.fda.gov/drug/drugsfda.json", params={"search": q, "limit": 5}, timeout=60)
    out["fda"][n] = {"http": r.status_code, "n": r.json().get("meta", {}).get("results", {}).get("total", 0)}
# Added after the adversarial review: Phase 3 trials of two borderline candidates (current-list tier), and
# zasocitinib's FDA review status (company release).
out["borderline_phase3"] = {}
for term in ["RLY-2608", "aleniglipron"]:
    st = requests.get("https://clinicaltrials.gov/api/v2/studies", params={"query.intr": term, "pageSize": 100,
                      "fields": "NCTId,Phase,OverallStatus,StartDate,LeadSponsorName"}, timeout=60).json()["studies"]
    out["borderline_phase3"][term] = [{"nct": s["protocolSection"]["identificationModule"]["nctId"],
                                       "status": s["protocolSection"]["statusModule"]["overallStatus"],
                                       "start": s["protocolSection"]["statusModule"].get("startDateStruct", {}).get("date")}
                                      for s in st if "PHASE3" in (s["protocolSection"].get("designModule", {}).get("phases") or [])]
import re
TK = "https://www.takeda.com/newsroom/newsreleases/2026/fda-priority-review-zasocitinib-psoriasis/"
tk = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", requests.get(TK, headers={"User-Agent": "Junctura Research"}, timeout=60).text))
m = re.search(r"The Prescription Drug User Fee Act \(PDUFA\) target action date is in the first quarter of calendar year 2027", tk)
out["zasocitinib"] = {"url": TK, "pdufa_sentence_found": bool(m), "sentence": m.group(0) if m else None}
j = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                 params={"query": "EXT_ID:38692505 AND SRC:MED", "format": "json", "resultType": "core"}, timeout=60).json()["resultList"]["result"][0]
out["jayatunga2024_abstract"] = {k: j.get(k) for k in ["title", "doi", "firstPublicationDate", "isOpenAccess", "abstractText"]}
d = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                 params={"query": "DOI:10.1038/s41586-021-03819-2", "format": "json", "resultType": "core"}, timeout=60).json()["resultList"]["result"][0]
out["alphafold2"] = {k: d.get(k) for k in ["title", "doi", "pmcid", "firstPublicationDate", "journalTitle"]} | {"journal": d["journalInfo"]["journal"]["title"]}
json.dump(out, open(f"{sys.argv[1]}/status_check.json", "w"), indent=1)
print(json.dumps(out, indent=1))
