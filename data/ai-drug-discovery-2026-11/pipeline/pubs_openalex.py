"""Publications per pairing per year from OpenAlex (title and abstract search).
Usage: python -I pubs_openalex.py <outdir>"""
import json, os, sys, time, datetime, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from realms import REALMS, PAIRS, or_group

out = sys.argv[1]
key = os.environ.get("OPENALEX_API_KEY")
results = {"retrieved": datetime.date.today().isoformat(), "source": "https://api.openalex.org/works", "pairs": {}}
for a, b in PAIRS:
    q = f"{or_group(REALMS[a])} AND {or_group(REALMS[b])}"
    params = {"filter": f"title_and_abstract.search:{q},publication_year:2019-2025",
              "group_by": "publication_year", "per_page": 200}
    if key:
        params["api_key"] = key
    r = requests.get("https://api.openalex.org/works", params=params, timeout=60)
    r.raise_for_status()
    d = r.json()
    counts = {g["key"]: g["count"] for g in d["group_by"]}
    results["pairs"][f"{a} x {b}"] = {"query": q, "by_year": counts}
    print(a, b, counts, flush=True)
    time.sleep(0.3)
json.dump(results, open(os.path.join(out, "openalex_pubs.json"), "w"), indent=1)
