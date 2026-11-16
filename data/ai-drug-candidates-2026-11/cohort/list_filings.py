"""Cohort step 1: list each cohort company's annual and IPO filings dated 2020-01-01 to 2024-04-30.

Usage: python list_filings.py raw   -> raw/filings_index.json
Source: SEC EDGAR submissions API (data.sec.gov/submissions/CIK##########.json).
"""
import json, sys, time, datetime
import requests

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
# The 14 Channel A filers with an AI candidate in the current list (CIKs from ../current-list/candidates.csv),
# plus Eikon and the S-1 filers, checked here for any filing in the window.
CIKS = {
    "Recursion": 1601830, "Exscientia": 1865408, "Schrodinger": 1490978, "Absci": 1672688,
    "Evaxion": 1828253, "Nurix": 1549595, "Compugen": 1119774, "iBio": 1420720,
    "Monte Rosa": 1826457, "Iambic": 1997038, "Generate": 2100782, "Eikon": 1861123,
    "Odyssey": 1882782, "Parabilis": 1657677,
}
FORMS = {"10-K", "20-F", "S-1", "F-1", "10-K/A", "20-F/A"}
START, END = "2020-01-01", "2024-04-30"


def main(out):
    res = {"retrieved": datetime.date.today().isoformat(), "window": [START, END], "companies": {}}
    for name, cik in CIKS.items():
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA, timeout=60)
        r.raise_for_status()
        d = r.json()
        rec = d["filings"]["recent"]
        rows = []
        for i, f in enumerate(rec["form"]):
            if f in FORMS and START <= rec["filingDate"][i] <= END:
                acc = rec["accessionNumber"][i]
                rows.append({"form": f, "date": rec["filingDate"][i], "accession": acc,
                             "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{rec['primaryDocument'][i]}"})
        res["companies"][name] = {"cik": cik, "entity": d["name"], "sic": d.get("sic"), "filings": rows}
        print(name, d["name"], [(x["form"], x["date"]) for x in rows], file=sys.stderr)
        time.sleep(0.2)
    json.dump(res, open(f"{out}/filings_index.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
