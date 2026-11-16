"""Cohort step 2: from each 2020-01-01..2024-04-30 filing, extract
(a) candidate codes that appear in a sentence with a clinical-stage word, and
(b) sentences that join an AI / machine-learning term with a candidate code or "product candidate"/"pipeline".

Usage: python edgar_cohort.py raw   -> raw/edgar_cohort.json
Filings are cached in raw/filings/ (not committed). Amendments (/A) are skipped.
A review queue only: the cohort itself is hand-built in cohort.csv from these sentences.
"""
import json, os, re, sys, time
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
CODE = re.compile(r"\b([A-Z]{2,5}-?\d{2,6}[A-Z]?)\b")
CLIN = re.compile(r"Phase\s?(1|2|3|I{1,3})|first patient|dosed|clinical trial|clinical-stage|IND\b", re.I)
AI = re.compile(r"artificial intelligence|machine[- ]learning|\bAI\b|deep learning|neural network|generative", re.I)
NOISE = {"COVID-19", "SARS", "ISO-9001", "ASC-842", "ASU", "NASDAQ", "CFR"}


def text_of(url, path):
    if not os.path.exists(path):
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        open(path, "wb").write(r.content)
        time.sleep(0.2)
    html = open(path, "rb").read()
    t = BeautifulSoup(html, "lxml").get_text(" ")
    return re.sub(r"\s+", " ", t)


def main(out):
    idx = json.load(open(f"{out}/filings_index.json"))
    os.makedirs(f"{out}/filings", exist_ok=True)
    res = {"source": "raw/filings_index.json", "companies": {}}
    for co, c in idx["companies"].items():
        recs = []
        for f in c["filings"]:
            if f["form"].endswith("/A"):
                continue
            path = f"{out}/filings/{f['accession']}.htm"
            t = text_of(f["url"], path)
            sents = re.split(r"(?<=[.;])\s+(?=[A-Z])", t)
            clin_codes, ai_sents = {}, []
            for s in sents:
                codes = [x for x in CODE.findall(s) if x not in NOISE and not x.startswith("ASU")]
                if codes and CLIN.search(s):
                    for x in codes:
                        clin_codes[x] = clin_codes.get(x, 0) + 1
                if AI.search(s) and (codes or re.search(r"product candidate|pipeline|clinical", s, re.I)) and len(s) < 1200:
                    ai_sents.append(s.strip())
            recs.append({"form": f["form"], "date": f["date"], "url": f["url"],
                         "clinical_codes": dict(sorted(clin_codes.items(), key=lambda kv: -kv[1])),
                         "n_ai_sentences": len(ai_sents), "ai_sentences": ai_sents[:80]})
            print(co, f["form"], f["date"], len(clin_codes), len(ai_sents), file=sys.stderr)
        res["companies"][co] = recs
    json.dump(res, open(f"{out}/edgar_cohort.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
