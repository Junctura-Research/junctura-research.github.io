"""US patent applications per pairing per filing year, USPTO Open Data Portal,
invention-title match. Usage: python -I patents_uspto.py <outdir>"""
import json, os, sys, time, datetime, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from realms import REALMS, PAIRS, or_group

out = sys.argv[1]
URL = "https://api.uspto.gov/api/v1/patent/applications/search"
H = {"X-API-KEY": os.environ["USPTO_API_KEY"]}
F = "applicationMetaData.inventionTitle"
res = {"retrieved": datetime.date.today().isoformat(), "source": URL,
       "field": F, "pairs": {}}
for a, b in PAIRS:
    q = f"{F}:{or_group(REALMS[a])} AND {F}:{or_group(REALMS[b])}"
    by = {}
    for y in range(2019, 2026):
        for attempt in range(5):
            r = requests.get(URL, headers=H, params={"q": q, "limit": 1,
                "rangeFilters": f"applicationMetaData.filingDate {y}-01-01:{y}-12-31"}, timeout=60)
            if r.status_code == 429:
                time.sleep(5); continue
            break
        if r.status_code == 404:  # ODP returns 404 for zero hits
            by[str(y)] = 0
        else:
            r.raise_for_status(); by[str(y)] = r.json()["count"]
        time.sleep(1)
    res["pairs"][f"{a} x {b}"] = {"query": q, "by_filing_year": by}
    print(a, b, by, flush=True)
json.dump(res, open(os.path.join(out, "uspto_patents.json"), "w"), indent=1)
