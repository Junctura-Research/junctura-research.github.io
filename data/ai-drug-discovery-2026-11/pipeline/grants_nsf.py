"""NSF awards per pairing per award-date year (NSF Awards API keyword search,
boolean). USAspending's keyword filter ORs terms and cannot AND two realms,
so NSF is the fallback named in the plan. NSF caps the keyword at 253
characters; longer queries are split into chunks of terms, award IDs are
collected for each chunk, and the union is counted. Usage: python -I grants_nsf.py <outdir>"""
import json, os, sys, time, datetime, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from realms import REALMS, PAIRS, or_group

out = sys.argv[1]
URL = "https://api.nsf.gov/services/v1/awards.json"
res = {"retrieved": datetime.date.today().isoformat(), "source": URL,
       "note": "dateStart/dateEnd filter on award date", "pairs": {}}
def get(q, y, offset=1, rpp=1):
    r = requests.get(URL, params={"keyword": q, "dateStart": f"01/01/{y}",
        "dateEnd": f"12/31/{y}", "printFields": "id", "rpp": rpp, "offset": offset}, timeout=60)
    r.raise_for_status(); time.sleep(0.3)
    return r.json()["response"]

def chunks(terms, other, limit=250):
    out, cur = [], []
    for t in terms:
        if cur and len(f"{other} AND {or_group(cur + [t])}") > limit:
            out.append(cur); cur = []
        cur.append(t)
    return out + [cur]

for a, b in PAIRS:
    q = f"{or_group(REALMS[a])} AND {or_group(REALMS[b])}"
    by = {}
    for y in range(2020, 2026):
        if len(q) <= 250:
            by[str(y)] = get(q, y)["metadata"]["totalCount"]; continue
        ids = set()
        for ch in chunks(REALMS[b], or_group(REALMS[a])):
            sq = f"{or_group(REALMS[a])} AND {or_group(ch)}"
            off = 1
            while True:
                resp = get(sq, y, off, 25)
                aw = resp.get("award", [])
                ids |= {x["id"] for x in aw}
                if len(aw) < 25: break
                off += 25
        by[str(y)] = len(ids)
    res["pairs"][f"{a} x {b}"] = {"query": q, "by_award_year": by,
        "method": "single query" if len(q) <= 250 else "union of chunked queries"}
    print(a, b, by, flush=True)
json.dump(res, open(os.path.join(out, "nsf_grants.json"), "w"), indent=1)
