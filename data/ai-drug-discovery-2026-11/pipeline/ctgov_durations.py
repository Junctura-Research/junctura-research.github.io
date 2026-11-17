"""an earlier step T3: trial durations (start -> actual primary completion) for cohort trials vs a same-source baseline.
Rules fixed in the research record section 2 before data. Usage (from this folder): python ctgov_durations.py
Outputs: raw/ctgov_cohort.json, raw/ctgov_baseline_<phase>.json (API pages, slimmed), cohort_trials.csv, durations.json
"""
import csv, json, re, statistics, time, os, requests
API = "https://clinicaltrials.gov/api/v2/studies"
UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
CANCER = re.compile(r"cancer|neoplas|tumou?r|carcinoma|lymphoma|leuk|myeloma|melanoma|sarcoma|glioma|malignan|oncolog", re.I)
PHASES = {"Phase 1": ["PHASE1"], "Phase 1/2": ["PHASE1", "PHASE2"], "Phase 2": ["PHASE2"]}
FIELDS = ("NCTId,Phase,StartDate,PrimaryCompletionDate,PrimaryCompletionDateType,LeadSponsorClass,LeadSponsorName,"
          "Condition,InterventionType,StudyType,OverallStatus")

def slim(s):
    p = s.get("protocolSection", {})
    st = p.get("statusModule", {}); ds = p.get("designModule", {})
    return {"nct": p.get("identificationModule", {}).get("nctId"), "phases": ds.get("phases", []),
            "study_type": ds.get("studyType"), "start": st.get("startDateStruct", {}).get("date"),
            "pc": st.get("primaryCompletionDateStruct", {}).get("date"),
            "pc_type": st.get("primaryCompletionDateStruct", {}).get("type"),
            "status": st.get("overallStatus"),
            "sponsor_class": p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("class"),
            "sponsor": p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name"),
            "conditions": p.get("conditionsModule", {}).get("conditions", []),
            "itypes": sorted({i.get("type") for i in p.get("armsInterventionsModule", {}).get("interventions", [])})}

def d(x):  # 'YYYY-MM' -> mid-month day 15; 'YYYY-MM-DD' as is
    if not x: return None
    from datetime import date
    parts = [int(v) for v in x.split("-")]
    return date(parts[0], parts[1], parts[2] if len(parts) == 3 else 15)

def months(s):
    a, b = d(s["start"]), d(s["pc"])
    return round((b - a).days / 30.4375, 1) if a and b else None

def label(phases):
    for k, v in PHASES.items():
        if phases == v: return k
    return None

def qualifies(s):
    return (s["study_type"] == "INTERVENTIONAL" and s["sponsor_class"] == "INDUSTRY" and s["pc_type"] == "ACTUAL"
            and label(s["phases"]) and s["start"] and "2019-01-01" <= (s["start"] + "-15")[:10] <= "2023-12-31"
            and ({"DRUG", "BIOLOGICAL"} & set(s["itypes"])))

def summ(xs):
    xs = sorted(xs)
    if not xs: return {"n": 0}
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "median_months": round(statistics.median(xs), 1), "iqr": [round(q[0], 1), round(q[2], 1)]}

# cohort trials
cohort = list(csv.DictReader(open("cohort_32.csv")))
ids = {}
for r in cohort:
    for t in filter(None, r["trials"].split(";")):
        ids.setdefault(t.split(":")[0], []).append(r["candidate"])
if os.path.exists("raw/ctgov_cohort.json"):
    cs = json.load(open("raw/ctgov_cohort.json"))
else:
    cs = []
    for nct in sorted(ids):
        j = requests.get(f"{API}/{nct}", headers=UA, timeout=60).json(); cs.append(slim(j)); time.sleep(0.3)
    json.dump({"retrieved": "2026-11-17", "studies": cs}, open("raw/ctgov_cohort.json", "w"), indent=0)
    cs = {"studies": cs}
cs = cs["studies"]
rows = []
for s in cs:
    rows.append({"nct": s["nct"], "candidates": "; ".join(ids[s["nct"]]), "phase": label(s["phases"]) or "/".join(s["phases"]),
                 "start": s["start"], "primary_completion": s["pc"], "pc_type": s["pc_type"], "status": s["status"],
                 "sponsor": s["sponsor"], "sponsor_class": s["sponsor_class"], "cancer": bool(CANCER.search(" ".join(s["conditions"]))),
                 "months": months(s), "qualifies": bool(qualifies(s))})
w = csv.DictWriter(open("cohort_trials.csv", "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# baseline
out = {"as_of": "2026-11-17", "rule": "interventional; industry lead sponsor; drug or biological intervention; phase label exactly as given; start 2019-01-01..2023-12-31; ACTUAL primary completion date",
       "by_phase": {}}
for ph, codes in PHASES.items():
    fn = f"raw/ctgov_baseline_{ph.replace(' ', '').replace('/', '-')}.json"
    if os.path.exists(fn):
        base = json.load(open(fn))["studies"]
    else:
        term = ("AREA[StudyType]INTERVENTIONAL AND AREA[LeadSponsorClass]INDUSTRY AND AREA[StartDate]RANGE[2019-01-01,2023-12-31] "
                "AND AREA[PrimaryCompletionDateType]ACTUAL AND " + " AND ".join(f"AREA[Phase]{c}" for c in codes))
        base, tok = [], None
        while True:
            prm = {"query.term": term, "fields": FIELDS, "pageSize": 1000, "format": "json"}
            if tok: prm["pageToken"] = tok
            j = requests.get(API, params=prm, headers=UA, timeout=120).json()
            base += [slim(s) for s in j.get("studies", [])]
            tok = j.get("nextPageToken")
            if not tok: break
            time.sleep(0.3)
        json.dump({"retrieved": "2026-11-17", "query.term": term, "studies": base}, open(fn, "w"))
    bq = [s for s in base if qualifies(s) and label(s["phases"]) == ph]
    cq = [s for s in cs if qualifies(s) and label(s["phases"]) == ph]
    cn = lambda s: bool(CANCER.search(" ".join(s["conditions"])))
    out["by_phase"][ph] = {
        "baseline_all": summ([months(s) for s in bq]),
        "baseline_cancer": summ([months(s) for s in bq if cn(s)]),
        "cohort_all": summ([months(s) for s in cq]),
        "cohort_cancer": summ([months(s) for s in cq if cn(s)]),
        "cohort_trials": [s["nct"] for s in cq], "baseline_records_downloaded": len(base)}
# pooled early-phase (all three labels)
allb = []; allc = []
for ph in PHASES:
    fn = f"raw/ctgov_baseline_{ph.replace(' ', '').replace('/', '-')}.json"
    allb += [s for s in json.load(open(fn))["studies"] if qualifies(s) and label(s["phases"]) == ph]
allc = [s for s in cs if qualifies(s)]
out["pooled_phase1_1-2_2"] = {"baseline_all": summ([months(s) for s in allb]), "cohort_all": summ([months(s) for s in allc]),
    "baseline_cancer": summ([months(s) for s in allb if CANCER.search(" ".join(s["conditions"]))]),
    "cohort_cancer": summ([months(s) for s in allc if CANCER.search(" ".join(s["conditions"]))])}
json.dump(out, open("durations.json", "w"), indent=1)
print(json.dumps(out, indent=1))
