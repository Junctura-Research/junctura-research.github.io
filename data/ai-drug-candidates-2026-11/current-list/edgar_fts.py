"""Current list, Channel A: SEC EDGAR full-text search for AI drug-discovery language.

Usage: python edgar_fts.py raw
Writes raw/edgar_fts.json: every hit (filer, CIK, SIC, form, date, accession) per query,
then the list of distinct filers whose SIC is in the pharma/biotech set.
"""
import json, sys, time, datetime
import requests

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
URL = "https://efts.sec.gov/LATEST/search-index"
FORMS = "10-K,20-F,S-1,F-1"
START, END = "2024-01-01", "2026-11-15"
QUERIES = [
    '"AI-discovered"',
    '"AI-designed"',
    '"AI-derived"',
    '"AI-enabled drug discovery"',
    '"AI-driven drug discovery"',
    '"machine learning" "drug discovery"',
    '"artificial intelligence" "drug discovery"',
]
SIC_KEEP = {"2834", "2836", "8731", "2835"}


def search(q):
    hits, frm = [], 0
    while True:
        r = requests.get(URL, params={"q": q, "forms": FORMS, "dateRange": "custom",
                                      "startdt": START, "enddt": END, "from": frm},
                         headers=UA, timeout=60)
        r.raise_for_status()
        d = r.json()
        batch = d["hits"]["hits"]
        total = d["hits"]["total"]["value"]
        for h in batch:
            s = h["_source"]
            hits.append({"id": h["_id"], "ciks": s.get("ciks"), "names": s.get("display_names"),
                         "sics": s.get("sics"), "form": s.get("form"), "file_date": s.get("file_date"),
                         "adsh": s.get("adsh")})
        frm += len(batch)
        time.sleep(0.2)
        if not batch or frm >= total or frm >= 10000:
            return total, hits


def main(out):
    res = {"retrieved": datetime.date.today().isoformat(), "url": URL, "forms": FORMS,
           "start": START, "end": END, "queries": {}}
    filers = {}
    for q in QUERIES:
        total, hits = search(q)
        res["queries"][q] = {"total": total, "hits": hits}
        for h in hits:
            sics = set(h["sics"] or [])
            if sics & SIC_KEEP:
                cik = h["ciks"][0]
                f = filers.setdefault(cik, {"name": h["names"][0], "sics": sorted(sics), "queries": set(), "filings": set()})
                f["queries"].add(q)
                f["filings"].add((h["form"], h["file_date"], h["adsh"], h["id"].split(":")[1]))
        print(q, total, file=sys.stderr)
    res["pharma_filers"] = {k: {"name": v["name"], "sics": v["sics"], "queries": sorted(v["queries"]),
                                "filings": sorted(v["filings"], key=lambda x: x[1], reverse=True)}
                            for k, v in sorted(filers.items(), key=lambda kv: kv[1]["name"])}
    json.dump(res, open(f"{out}/edgar_fts.json", "w"), indent=1)
    print(len(filers), "pharma/biotech filers", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
