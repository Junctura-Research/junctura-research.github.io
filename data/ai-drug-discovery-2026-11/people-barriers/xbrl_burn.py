"""an earlier step B2: latest fiscal-year net cash used in operating activities, and cash, cash equivalents and
marketable securities where tagged, from SEC XBRL company facts (data.sec.gov/api/xbrl/companyfacts).
Usage (from repo root): python3 analysis/015/xbrl_burn.py   Writes burn.csv.
"""
import csv, json, os, time
import requests

UA = {"User-Agent": "Junctura Research juncturaresearch@gmail.com"}
HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, "raw", "latest_index.json")))
OPCF = ["NetCashProvidedByUsedInOperatingActivities"]
CASH = ["CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]
SECS = ["MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "ShortTermInvestments",
        "MarketableSecuritiesNoncurrent", "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent", "LongTermInvestments"]


def val(facts, tags, acc, period_end, duration):
    for tax in ("us-gaap", "ifrs-full"):
        for t in tags:
            node = facts.get(tax, {}).get(t)
            if not node:
                continue
            for unit, items in node["units"].items():
                for it in items:
                    if it.get("accn") == acc and it.get("end") == period_end and (("start" in it) == duration):
                        if duration:
                            days = (time.mktime(time.strptime(it["end"], "%Y-%m-%d")) -
                                    time.mktime(time.strptime(it["start"], "%Y-%m-%d"))) / 86400
                            if days < 340:
                                continue
                        return it["val"], unit, t
    return None, None, None


def main():
    out = []
    for name, c in IDX["companies"].items():
        f = c["filing"]
        if not f:
            continue
        r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c['cik']:010d}.json", headers=UA, timeout=90)
        time.sleep(0.2)
        facts = r.json()["facts"] if r.status_code == 200 else {}
        opcf, unit, t1 = val(facts, OPCF + ["CashFlowsFromUsedInOperatingActivities"], f["accession"], f["period"], True)
        cash, _, t2 = val(facts, CASH + ["CashAndCashEquivalents"], f["accession"], f["period"], False)
        secs = 0.0
        tagged = []
        for t in SECS:
            v, _, tt = val(facts, [t], f["accession"], f["period"], False)
            if v is not None:
                secs += v; tagged.append(tt)
        out.append({"company": name, "form": f["form"], "period": f["period"], "unit": unit or "",
                    "op_cash_flow": opcf if opcf is not None else "not tagged", "op_tag": t1 or "",
                    "cash": cash if cash is not None else "not tagged", "cash_tag": t2 or "",
                    "securities_tagged": secs, "securities_tags": ";".join(tagged)})
        print(out[-1])
    with open(os.path.join(HERE, "burn.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


if __name__ == "__main__":
    main()
