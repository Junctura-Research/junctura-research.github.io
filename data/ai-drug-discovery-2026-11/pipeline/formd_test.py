"""Test whether SEC EDGAR full-text search can attribute Form D filings to a
technology. Usage: python -I formd_test.py <outdir>"""
import json, os, sys, time, datetime, requests
out = sys.argv[1]
H = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
URL = "https://efts.sec.gov/LATEST/search-index"
res = {"retrieved": datetime.date.today().isoformat(), "source": URL, "tests": []}
for q in ['"machine learning"', '"quantum computing"', '"artificial intelligence"', 'qubit']:
    r = requests.get(URL, headers=H, params={"q": q, "forms": "D",
        "dateRange": "custom", "startdt": "2024-01-01", "enddt": "2024-12-31"}, timeout=60)
    d = r.json()
    hits = d.get("hits", {})
    sample = [{"names": h["_source"].get("display_names"), "file": h["_id"]} for h in hits.get("hits", [])[:5]]
    res["tests"].append({"q": q, "status": r.status_code, "total": hits.get("total"), "sample": sample})
    print(q, r.status_code, hits.get("total"), sample[:3]); time.sleep(0.5)
json.dump(res, open(os.path.join(out, "formd_test.json"), "w"), indent=1)
