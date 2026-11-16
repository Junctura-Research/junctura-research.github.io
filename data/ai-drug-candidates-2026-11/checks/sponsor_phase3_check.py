"""Checks: list every Phase 3 trial led by each of the 17 the current list AI companies (ClinicalTrials.gov API v2,
lead-sponsor search), so a Phase 3 trial registered under a generic name cannot be missed.
Usage: python sponsor_phase3_check.py raw -> raw/sponsor_phase3_check.json
Companies: the 17 with an AI candidate in the current list (../current-list/summary.json, ai_companies)."""
import json, sys, time, requests
companies = {"Absci": ["Absci"], "BenevolentAI": ["Benevolent"], "Compugen": ["Compugen"], "Eikon Therapeutics": ["Eikon"],
    "Enveda": ["Enveda"], "Evaxion": ["Evaxion"], "Exscientia": ["Exscientia"], "Generate Biomedicines": ["Generate Biomedicines"],
    "Iambic Therapeutics": ["Iambic"], "Insilico Medicine": ["Insilico"], "Monte Rosa": ["Monte Rosa"], "Nurix": ["Nurix"],
    "Odyssey Therapeutics": ["Odyssey Therapeutics"], "Parabilis Medicines": ["Parabilis", "FogPharma"], "Recursion": ["Recursion"],
    "Schrodinger": ["Schrodinger", "Schrödinger"], "iBio": ["iBio"]}
out = {}
for co, v in companies.items():
    terms = v
    hits = {}
    for term in terms:
        for s in requests.get("https://clinicaltrials.gov/api/v2/studies", params={"query.lead": term, "pageSize": 200,
                              "fields": "NCTId,BriefTitle,Phase,OverallStatus,StartDate,InterventionName,LeadSponsorName"}, timeout=60).json().get("studies", []):
            p = s["protocolSection"]
            if "PHASE3" in (p.get("designModule", {}).get("phases") or []):
                hits[p["identificationModule"]["nctId"]] = {"title": p["identificationModule"]["briefTitle"], "status": p["statusModule"]["overallStatus"],
                    "start": p["statusModule"].get("startDateStruct", {}).get("date"), "sponsor": p["sponsorCollaboratorsModule"]["leadSponsor"]["name"],
                    "interventions": [i["name"] for i in p.get("armsInterventionsModule", {}).get("interventions", [])]}
        time.sleep(0.2)
    out[co] = hits
    for k, h in hits.items(): print(co, k, h["status"], h["start"], h["sponsor"], h["interventions"][:3])
json.dump(out, open(f"{sys.argv[1]}/sponsor_phase3_check.json", "w"), indent=1)
