"""Combine raw extracts into pairings.csv, and fetch the OpenAlex baseline
(all works with an abstract, by year) to normalize publication growth.
Usage: python -I combine.py <rawdir> <outcsv>"""
import json, os, sys, datetime, requests
import pandas as pd
raw, outcsv = sys.argv[1], sys.argv[2]
P = json.load(open(os.path.join(raw, "openalex_pubs.json")))["pairs"]
T = json.load(open(os.path.join(raw, "uspto_patents.json")))["pairs"]
G = json.load(open(os.path.join(raw, "nsf_grants.json")))["pairs"]

base_path = os.path.join(raw, "openalex_baseline.json")
if not os.path.exists(base_path):
    params = {"filter": "has_abstract:true,publication_year:2019-2025", "group_by": "publication_year"}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    d = requests.get("https://api.openalex.org/works", params=params, timeout=60).json()
    json.dump({"retrieved": datetime.date.today().isoformat(), "filter": params["filter"],
               "by_year": {g["key"]: g["count"] for g in d["group_by"]}}, open(base_path, "w"), indent=1)
B = json.load(open(base_path))["by_year"]
base_growth = B["2025"] / B["2020"]

rows = []
for k in P:
    p, t, g = P[k]["by_year"], T[k]["by_filing_year"], G[k]["by_award_year"]
    rows.append({
        "pairing": k,
        "pubs_2020": p["2020"], "pubs_2025": p["2025"],
        "pubs_2019_2025": sum(p.values()),
        "pubs_growth_2025_vs_2020": round(p["2025"] / p["2020"], 2),
        "pubs_growth_vs_baseline": round(p["2025"] / p["2020"] / base_growth, 2),
        "patent_apps_2019_2023": sum(t[str(y)] for y in range(2019, 2024)),
        "patent_apps_2019_2025": sum(t.values()),
        "nsf_awards_2020_2025": sum(g.values()),
        "nsf_2020_21": g["2020"] + g["2021"], "nsf_2024_25": g["2024"] + g["2025"],
    })
df = pd.DataFrame(rows).sort_values("pubs_2019_2025", ascending=False)
df.to_csv(outcsv, index=False)
print(f"baseline growth 2025/2020 = {base_growth:.2f} ({B['2020']} -> {B['2025']})")
print(df.to_string(index=False))
