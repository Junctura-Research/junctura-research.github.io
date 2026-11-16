"""Current list: check Phase 3 AI candidates against Drugs@FDA (openFDA drugsfda endpoint).
Usage: python fda_check.py raw -> raw/fda_check.json"""
import json, sys, datetime, requests
NAMES = ["rentosertib", "bexobrutideg", "rilvegostomig", "GB-0895", "dexmedetomidine"]
res = {"retrieved": datetime.date.today().isoformat(), "api": "https://api.fda.gov/drug/drugsfda.json", "results": {}}
for n in NAMES:
    q = f'openfda.generic_name:"{n}" OR products.active_ingredients.name:"{n.upper()}" OR products.brand_name:"{n}"'
    r = requests.get(res["api"], params={"search": q, "limit": 5}, timeout=60)
    d = r.json()
    res["results"][n] = {"http": r.status_code, "n": d.get("meta", {}).get("results", {}).get("total", 0),
                         "applications": [x.get("application_number") for x in d.get("results", [])]}
    print(n, res["results"][n])
json.dump(res, open(f"{sys.argv[1]}/fda_check.json", "w"), indent=1)
