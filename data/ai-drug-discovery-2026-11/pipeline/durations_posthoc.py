"""an earlier step T3 post-hoc checks (chosen after the main durations were seen; labeled post hoc in the notebook):
(1) completed trials only, both groups; (2) cohort without COVID-19 antibody trials. Usage: python durations_posthoc.py
"""
import json, re, statistics, importlib.util
spec = importlib.util.spec_from_file_location("cd", "ctgov_durations.py")
src = open("ctgov_durations.py").read().split("# cohort trials")[0]
ns = {}; exec(src, ns)
qualifies, months, label, CANCER = ns["qualifies"], ns["months"], ns["label"], ns["CANCER"]
cs = json.load(open("raw/ctgov_cohort.json"))["studies"]
base = []
for ph in ("Phase1", "Phase1-2", "Phase2"):
    base += json.load(open(f"raw/ctgov_baseline_{ph}.json"))["studies"]
base = [s for s in base if qualifies(s)]
seen = set(); b2 = []
for s in base:
    if s["nct"] not in seen: seen.add(s["nct"]); b2.append(s)
base = b2
cq = [s for s in cs if qualifies(s)]
COVID = lambda s: "COVID" in " ".join(s["conditions"]).upper() or "SARS" in " ".join(s["conditions"]).upper()
med = lambda xs: {"n": len(xs), "median_months": round(statistics.median(xs), 1) if xs else None}
ca = lambda s: bool(CANCER.search(" ".join(s["conditions"])))
out = {
 "completed_only": {"baseline_all": med([months(s) for s in base if s["status"] == "COMPLETED"]),
                    "cohort_all": med([months(s) for s in cq if s["status"] == "COMPLETED"]),
                    "baseline_cancer": med([months(s) for s in base if s["status"] == "COMPLETED" and ca(s)]),
                    "cohort_cancer": med([months(s) for s in cq if s["status"] == "COMPLETED" and ca(s)])},
 "cohort_without_covid": med([months(s) for s in cq if not COVID(s)]),
 "baseline_without_covid": med([months(s) for s in base if not COVID(s)]),
 "baseline_terminated_share_pct": round(100*sum(s["status"]=="TERMINATED" for s in base)/len(base),1),
 "baseline_cancer_terminated_share_pct": round(100*sum(s["status"]=="TERMINATED" for s in base if ca(s))/sum(ca(s) for s in base),1),
 "cohort_status_counts": {st: sum(s["status"] == st for s in cq) for st in sorted({s["status"] for s in cq})},
}
json.dump(out, open("durations_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
