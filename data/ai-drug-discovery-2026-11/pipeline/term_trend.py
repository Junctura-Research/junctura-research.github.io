"""an earlier step Part B: count tool-generation phrases in each cached annual report.

Usage: python3 term_trend.py
Inputs:  raw/annual_index.json, raw/annual/*.htm (from fetch_annual.py), terms.py
Outputs: term_counts.csv (one row per filing), term_trend.csv (share of companies mentioning each generation, by fiscal year),
         first_mention.csv, raw/match_sentences.json (every matched sentence, for the precision sample)
Fiscal year = year of the filing's reportDate (period).
"""
import json, os, re, warnings
import pandas as pd
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from terms import PATTERNS, GENERATIONS

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *f: os.path.join(HERE, *f)


def text_of(path):
    soup = BeautifulSoup(open(path, "rb").read(), "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display:\s*none", re.I)):  # inline XBRL header
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))


def sentences(txt):
    return re.split(r"(?<=[.;:!?])\s+(?=[A-Z(•●])", txt)


def main():
    idx = json.load(open(P("raw", "annual_index.json")))
    rows, matches = [], []
    for co, info in idx["companies"].items():
        for f in info["filings"]:
            path = P(f["file"])
            if not os.path.exists(path):
                continue
            txt = text_of(path)
            sents = sentences(txt)
            row = {"company": co, "form": f["form"], "filed": f["filed"], "period": f["period"],
                   "fiscal_year": int(f["period"][:4]), "url": f["url"], "words": len(txt.split())}
            for g, pat in PATTERNS.items():
                hits = [s for s in sents if pat.search(s)]
                row[g + "_matches"] = sum(len(pat.findall(s)) for s in hits)
                row[g + "_sentences"] = len(hits)
                for s in hits:
                    matches.append({"company": co, "fiscal_year": row["fiscal_year"], "generation": g,
                                    "term": pat.search(s).group(0), "sentence": s[:1200], "url": f["url"]})
            rows.append(row)
    df = pd.DataFrame(rows).sort_values(["company", "fiscal_year"])
    # One annual report per company and fiscal year (keep the latest filed if amended or duplicated)
    df = df.drop_duplicates(["company", "fiscal_year"], keep="last")
    df.to_csv(P("term_counts.csv"), index=False)
    gens = list(GENERATIONS) + ["computational"]
    trend = []
    for fy, g in df.groupby("fiscal_year"):
        r = {"fiscal_year": fy, "companies": len(g), "company_list": "; ".join(g.company)}
        for gen in gens:
            n = int((g[gen + "_sentences"] > 0).sum())
            r[gen + "_companies"] = n
            r[gen + "_share"] = round(n / len(g), 3)
        trend.append(r)
    pd.DataFrame(trend).to_csv(P("term_trend.csv"), index=False)
    fm = []
    for co, g in df.groupby("company"):
        r = {"company": co, "years_covered": f"{g.fiscal_year.min()}-{g.fiscal_year.max()}"}
        for gen in gens:
            yrs = g[g[gen + "_sentences"] > 0].fiscal_year
            r[gen + "_first_year"] = int(yrs.min()) if len(yrs) else ""
        fm.append(r)
    pd.DataFrame(fm).to_csv(P("first_mention.csv"), index=False)
    json.dump(matches, open(P("raw", "match_sentences.json"), "w"), indent=0)
    print(pd.DataFrame(trend).drop(columns="company_list").to_string(index=False))
    print(pd.DataFrame(fm).to_string(index=False))


if __name__ == "__main__":
    main()
