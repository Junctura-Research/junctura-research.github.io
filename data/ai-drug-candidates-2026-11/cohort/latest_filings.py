"""Cohort step 3: fetch each SEC filer's latest annual report (10-K or 20-F) as of the run date,
to read each cohort candidate's current status.

Usage: python latest_filings.py raw  -> raw/latest_index.json ; filings cached in raw/filings/ (not committed)
"""
import json, sys, time, datetime, os
import requests

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
CIKS = {"Recursion": 1601830, "Schrodinger": 1490978, "Evaxion": 1828253, "Nurix": 1549595,
        "Compugen": 1119774, "Monte Rosa": 1826457, "Generate": 2100782, "Parabilis": 1657677, "Eikon": 1861123}
FORMS = {"10-K", "20-F", "S-1", "S-1/A"}


def main(out):
    res = {"retrieved": datetime.date.today().isoformat(), "companies": {}}
    os.makedirs(f"{out}/filings", exist_ok=True)
    for name, cik in CIKS.items():
        d = requests.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA, timeout=60).json()
        rec = d["filings"]["recent"]
        for i, f in enumerate(rec["form"]):  # newest first
            if f in FORMS:
                acc = rec["accessionNumber"][i]
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{rec['primaryDocument'][i]}"
                path = f"{out}/filings/{acc}.htm"
                if not os.path.exists(path):
                    open(path, "wb").write(requests.get(url, headers=UA, timeout=120).content)
                res["companies"][name] = {"form": f, "date": rec["filingDate"][i], "accession": acc, "url": url}
                print(name, f, rec["filingDate"][i], url, file=sys.stderr)
                break
        time.sleep(0.3)
    json.dump(res, open(f"{out}/latest_index.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
