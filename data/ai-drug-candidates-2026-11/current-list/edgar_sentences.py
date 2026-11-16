"""Current list, Channel A triage: for each pharma/biotech filer found by edgar_fts.py, download the
latest matching filing and extract sentences where an AI term appears together with a
drug-candidate code (e.g. ABC-123) or the words "product candidate"/"drug candidate".

Usage: python edgar_sentences.py raw
Reads raw/edgar_fts.json; caches filings in raw/filings/ (not committed); writes raw/edgar_sentences.json.
"""
import json, os, re, sys, time, html
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
AI = re.compile(r"\b(artificial intelligence|machine[- ]learning|deep[- ]learning|AI[- ](?:discovered|designed|derived|enabled|driven|powered|based|generated)|generative AI|\bAI\b)", re.I)
CODE = re.compile(r"\b[A-Z]{2,6}-?\d{2,5}[A-Za-z]?\b")
CAND = re.compile(r"(product|drug|clinical|development) candidate", re.I)
NOT_CODE = re.compile(r"^(ASC|ASU|COVID|FORM|IRC|CFR|USC|ISO|IFRS|IAS|SFAS|GAAP|SEC|EU|US|PDUFA|IND|NDA|BLA|CTA|SARS|IL|CD|HER|PD|FY|Q[1-4]|CY|NCT|EGFR|HLA|KRAS|BRCA|TNF|JAK|TYK|BTK|PI3K|CDK|GLP|ITEM|PART|NOTE|RULE|TOPIC|CHAPTER|ARTICLE|SECTION)", re.I)


def text_of(path):
    raw = open(path, "rb").read().decode("utf-8", "ignore")
    t = BeautifulSoup(raw, "lxml").get_text(" ")
    return re.sub(r"\s+", " ", html.unescape(t))


def sentences(t):
    return re.split(r"(?<=[.;])\s+(?=[A-Z•])", t)


def main(out):
    d = json.load(open(f"{out}/edgar_fts.json"))
    os.makedirs(f"{out}/filings", exist_ok=True)
    res = {}
    for cik, f in d["pharma_filers"].items():
        form, date, adsh, fn = f["filings"][0]
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{fn}"
        p = f"{out}/filings/{cik}_{fn}"
        if not os.path.exists(p):
            r = requests.get(url, headers=UA, timeout=120)
            time.sleep(0.15)
            if r.status_code != 200:
                res[cik] = {"name": f["name"], "url": url, "error": r.status_code}
                continue
            open(p, "wb").write(r.content)
        t = text_of(p)
        hits = []
        for s in sentences(t):
            if len(s) > 1500 or not AI.search(s):
                continue
            codes = [c for c in set(CODE.findall(s)) if not NOT_CODE.match(c)]
            if codes or CAND.search(s):
                hits.append({"codes": sorted(codes), "sentence": s.strip()})
        res[cik] = {"name": f["name"], "sics": f["sics"], "form": form, "date": date, "url": url,
                    "n_ai_sentences": sum(1 for s in sentences(t) if AI.search(s)), "hits": hits}
        print(f["name"][:50], len(hits), file=sys.stderr)
    json.dump(res, open(f"{out}/edgar_sentences.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
