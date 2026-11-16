"""Current list, Channel B seed: count how many cached Channel A filings name each AI drug-discovery
company that does not file 10-K/20-F/S-1/F-1 reports with the SEC (private, or listed outside the US).
The candidate list of names is fixed below and was written before counting; it holds companies
commonly described as AI drug-discovery companies plus every non-SEC AI company seen while
reading Channel A filings. Output ranks them by number of filings naming them.

Usage: python seed_channel_b.py raw
"""
import glob, re, sys, json, html, warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

NAMES = ["Insilico", "BenevolentAI", "Isomorphic", "XtalPi", "insitro", "Verge Genomics", "Valo Health",
         "Xaira", "Chai Discovery", "Atomwise", "BPGbio", "Healx", "Iktos", "Genesis Therapeutics", "Terray",
         "Enveda", "Formation Bio", "Owkin", "Aqemia", "Cradle", "Pathos", "myNEO", "ZipBio", "AstralBio",
         "Receptor.AI", "Syntekabio", "GT Apeiron", "Charm Therapeutics", "Variational AI", "Deep Genomics",
         "Exscientia", "Generate Biomedicines", "Iambic", "Absci", "Recursion"]


def main(out):
    counts = {n: [] for n in NAMES}
    for p in glob.glob(f"{out}/filings/*"):
        t = BeautifulSoup(open(p, "rb").read().decode("utf-8", "ignore"), "lxml").get_text(" ")
        for n in NAMES:
            if re.search(re.escape(n), t, re.I):
                counts[n].append(p.rsplit("/", 1)[1])
    res = sorted(((n, len(v), v) for n, v in counts.items()), key=lambda x: -x[1])
    json.dump(res, open(f"{out}/channel_b_seed.json", "w"), indent=1)
    for n, c, _ in res:
        print(c, n)


if __name__ == "__main__":
    main(sys.argv[1])
