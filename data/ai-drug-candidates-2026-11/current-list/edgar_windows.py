"""Current list, Channel A triage step 2: for every cached latest filing, find drug-candidate codes
(e.g. REC-617, ISM001-055) that appear within 300 characters of both an AI/ML term and a
discovery verb (discovered, designed, identified, generated, optimized, derived, engineered).
Output is a review queue; every candidate kept in candidates.csv was confirmed by reading the
filing text, not by this script alone.

Usage: python edgar_windows.py raw
Reads raw/edgar_sentences.json and raw/filings/; writes raw/edgar_windows.json.
"""
import json, re, sys, os, html, warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

AI = re.compile(r"artificial intelligence|machine[- ]learning|deep[- ]learning|generative|\bAI\b|\bML\b|AI[-/]", re.I)
VERB = re.compile(r"discover|design|identif|generat|optimi[sz]|deriv|engineer", re.I)
CODE = re.compile(r"\b[A-Z]{2,7}[- ]?\d{2,6}[A-Za-z]?\b")
NOT = re.compile(r"^(ASC|ASU|COVID|FORM|IRC|CFR|USC|ISO|IFRS|IAS|SFAS|SEC|PDUFA|SARS|IL|CD|HER|PD|FY|CY|NCT|EGFR|HLA|KRAS|BRCA|TNF|JAK|TYK|BTK|CDK|GLP|ITEM|PART|NOTE|RULE|TOPIC|SECTION|ISIN|EUR|USD|DKK|CHF|GBP|NLRP|PRMT|KIF|MEK|RBM|PKC|FGFR|PIK|ERBB|MAT|WRN|SOS|SHP|STING|TEAD|PCSK|LPA|APOC|ANGPTL|MALT|ENPP|IRAK|ALK|ROS|RET|MET|KIT|PDGFR|VEGF|FLT|NRG|ART|DLL|TROP|CLDN|GPRC|MASP|CCR|CXCR|TSLP|STAT|IRF|NOD|RIPK|TL|TLR|GPR|HPK|USP|BCL|MCL|AKT|ATR|ATM|PARP|POL|DNA|RNA|ADAR|GBA|LRRK|APOE|SOD|HTT|MAPT|SNCA|ACVR|BMP|FXI|FXII|PSMA|SSTR|GLUT|SGLT|DPP|PPAR|THR|FGF|FAP|CTLA|LAG|TIGIT|TIM|OX|ICOS|IFN|IGF|HIF|EZH|BET|BRD|CBP|KAT|LSD|MDM|SMARCA|NSD|DOT|MLL|WDR|EP|DGK|CSF|PI|AR|ER|PR|GR|MR|HSD|CYP|UGT|OATP|MRP|BCRP|PGP|TRPV|TRPA|NAV|KV|CAV|HCN|GABA|NMDA|AMPA|MGLU|D2|HT)$", re.I)


def text_of(p):
    raw = open(p, "rb").read().decode("utf-8", "ignore")
    return re.sub(r"\s+", " ", html.unescape(BeautifulSoup(raw, "lxml").get_text(" ")))


def main(out):
    s = json.load(open(f"{out}/edgar_sentences.json"))
    res = {}
    for cik, v in s.items():
        fn = v["url"].rsplit("/", 1)[1]
        p = f"{out}/filings/{cik}_{fn}"
        if not os.path.exists(p):
            continue
        t = text_of(p)
        codes = {}
        for m in CODE.finditer(t):
            c = m.group(0)
            if NOT.match(re.split(r"[- ]?\d", c)[0]):
                continue
            w = t[max(0, m.start() - 300):m.end() + 300]
            if AI.search(w) and VERB.search(w):
                codes.setdefault(c, []).append(w)
        if codes:
            res[cik] = {"name": v["name"], "form": v["form"], "date": v["date"], "url": v["url"],
                        "codes": {c: {"n": len(ws), "window": ws[0]} for c, ws in codes.items()}}
    json.dump(res, open(f"{out}/edgar_windows.json", "w"), indent=1)
    print(len(res), "filers with candidate codes near AI discovery language", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
