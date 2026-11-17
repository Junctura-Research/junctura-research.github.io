"""an earlier step: hand codes (B1, B2, B4) applied to the extracted sentences, verbatim quote check, summary.
Hand codes were made by reading the class-matched AI sentences in order (rule in the research record).
Usage (from repo root): python3 analysis/015/summary.py
Writes coded.csv, runway_coded.csv, stops.csv, quote_check.json, summary.json.
"""
import csv, json, os, re, statistics
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, "raw", "latest_index.json")))
SENT = {(r["company"], int(r["n"])): r["sentence"] for r in csv.DictReader(open(os.path.join(HERE, "ai_sentences.csv")))}
CLASSES = ["data", "validation", "ai_regulation", "compute_tools"]
# B1 hand codes: sentence number (index in the risk-factor section) kept per class, or None.
CODES = {
    "Recursion":   {"data": 494, "validation": 492, "ai_regulation": 1281, "compute_tools": 490},
    "Exscientia":  {"data": None, "validation": 443, "ai_regulation": 454, "compute_tools": None},
    "Schrodinger": {"data": None, "validation": None, "ai_regulation": None, "compute_tools": None},
    "Absci":       {"data": 420, "validation": 104, "ai_regulation": 591, "compute_tools": 571},
    "Evaxion":     {"data": None, "validation": 86, "ai_regulation": 148, "compute_tools": None},
    "Nurix":       {"data": 1158, "validation": 236, "ai_regulation": 1163, "compute_tools": 1158},
    "Compugen":    {"data": 657, "validation": 668, "ai_regulation": 658, "compute_tools": 665},
    "iBio":        {"data": 611, "validation": 321, "ai_regulation": 612, "compute_tools": 315},
    "Monte Rosa":  {"data": 1003, "validation": None, "ai_regulation": 995, "compute_tools": 1005},
    "Kymera":      {"data": 1058, "validation": None, "ai_regulation": 1048, "compute_tools": 1062},
    "Relay":       {"data": 855, "validation": None, "ai_regulation": 844, "compute_tools": 857},
    "Eikon":       {"data": 134, "validation": 133, "ai_regulation": 135, "compute_tools": None},
}
# Sentences outside the class regexes, read by hand (sensitivity only, not in the main counts).
SENSITIVITY = [("Exscientia", 447, "data", "says 'datasets', which the data pattern does not match"),
               ("Compugen", 324, "validation", "platform 'not yet fully proven clinically'; matched compute pattern only")]
CONTEXT = [("Schrodinger", 161, "competition from AI approaches; Schrödinger's only AI risk sentences concern competition"),
           ("Monte Rosa", 1002, "the one AI risk sentence that cites FDA's January 2025 draft guidance")]
# B2: stated runway, read from runway.csv; horizon = start of the named year or half-year, or the stated months.
RUNWAY = {
    "Recursion":   ("at least the next 12 months", 12, None),
    "Exscientia":  ("well into 2026", None, "2026-01-01"),
    "Schrodinger": ("through at least the next 24 months", 24, None),
    "Absci":       ("over at least the next 12 months", 12, None),
    "Evaxion":     ("into second half of 2027", None, "2027-07-01"),
    "Nurix":       ("through at least the next 12 months", 12, None),
    "Compugen":    ("into 2029", None, "2029-01-01"),
    "iBio":        ("for at least 12 months from the date of filing", 12, None),
    "Monte Rosa":  ("into 2029", None, "2029-01-01"),
    "Kymera":      ("into 2029", None, "2029-01-01"),
    "Relay":       ("into 2029", None, "2029-01-01"),
    "Eikon":       ("into the second half of 2027", None, "2027-07-01"),
}
# B4: the 8 discontinued candidates of the 32 cohort; reasons as recorded in an earlier step and 012.
STOPS = [
    ("EXS21546", "not sufficiently promising (company); therapeutic index (registry)", "efficacy or safety", "analysis/004/cohort_with_phase.csv"),
    ("DSP-1181", "not stated by the company", "not stated", "analysis/004/cohort_with_phase.csv"),
    ("REC-3964", "strategic / portfolio", "portfolio or strategic", "analysis/004/cohort_with_phase.csv"),
    ("BEN-2293", "efficacy", "efficacy or safety", "analysis/004/cohort_with_phase.csv"),
    ("ADG106", "not stated by the company (deprioritized)", "not stated", "analysis/012/new_rows_with_phase.csv"),
    ("bamlanivimab (LY-CoV555)", "authorization withdrawn: resistant variants; partner withdrew the product", "regulatory", "analysis/012/new_rows_with_phase.csv"),
    ("bebtelovimab (LY-CoV1404)", "authorization withdrawn at partner's request (lots expired; resistant variants)", "regulatory", "analysis/012/new_rows_with_phase.csv"),
    ("TAK-920/DNL919", "not stated by the company", "not stated", "analysis/012/new_rows_with_phase.csv"),
]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    texts = {n: norm(open(os.path.join(HERE, c["filing"]["text"])).read()) for n, c in IDX["companies"].items() if c["filing"]}
    coded, checks = [], []
    for co, cl in CODES.items():
        row = {"company": co, "form": IDX["companies"][co]["filing"]["form"], "filed": IDX["companies"][co]["filing"]["filed"]}
        for k in CLASSES:
            n = cl[k]
            row[k] = int(n is not None)
            row[k + "_quote"] = SENT[(co, n)] if n is not None else ""
            if n is not None:
                checks.append({"company": co, "class": k, "n": n, "found": norm(SENT[(co, n)]) in texts[co]})
        coded.append(row)
    for co, n, k, why in SENSITIVITY + [(a, b, "context", c) for a, b, c in CONTEXT]:
        checks.append({"company": co, "class": k, "n": n, "found": norm(SENT[(co, n)]) in texts[co]})
    with open(os.path.join(HERE, "coded.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(coded[0])); w.writeheader(); w.writerows(coded)
    # runway
    rrows = []
    rw = {r["company"]: r for r in csv.DictReader(open(os.path.join(HERE, "runway.csv")))}
    burn = {r["company"]: r for r in csv.DictReader(open(os.path.join(HERE, "burn.csv")))}
    for co, (phrase, months, end) in RUNWAY.items():
        filed = date.fromisoformat(rw[co]["filed"])
        yrs = months / 12 if months else (date.fromisoformat(end) - filed).days / 365.25
        found = norm(phrase).lower() in texts[co].lower()
        checks.append({"company": co, "class": "runway", "n": phrase, "found": found})
        b = burn.get(co, {})
        rrows.append({"company": co, "filed": rw[co]["filed"], "stated_horizon": phrase, "years_from_filing": round(yrs, 2),
                      "dated_horizon": int(end is not None),
                      "op_cash_flow": b.get("op_cash_flow", ""), "unit": b.get("unit", ""),
                      "going_concern_sentences": rw[co]["n_going_concern_sentences"]})
    with open(os.path.join(HERE, "runway_coded.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rrows[0])); w.writeheader(); w.writerows(rrows)
    with open(os.path.join(HERE, "stops.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["candidate", "recorded_reason", "class", "source_file"]); w.writerows(STOPS)
    json.dump(checks, open(os.path.join(HERE, "quote_check.json"), "w"), indent=1)
    n = len(coded)
    yrs_all = [r["years_from_filing"] for r in rrows]
    yrs_dated = [r["years_from_filing"] for r in rrows if r["dated_horizon"]]
    burns = {r["company"]: float(r["op_cash_flow"]) for r in rrows if r["op_cash_flow"] not in ("", "not tagged")}
    usd_users = sorted(-v / 1e6 for c, v in burns.items() if v < 0 and burn[c]["unit"] == "USD")
    summary = {
        "panel": len(IDX["companies"]), "with_annual_report": n,
        "no_annual_report": [c for c, v in IDX["companies"].items() if not v["filing"]],
        "companies_with_ai_sentence_in_risk_factors": len({c for c, _ in SENT}),
        "class_counts": {k: sum(r[k] for r in coded) for k in CLASSES},
        "class_counts_with_sensitivity": {k: sum(r[k] for r in coded) + sum(1 for c, _, kk, _ in SENSITIVITY if kk == k and not CODES[c][k]) for k in CLASSES},
        "companies_all_four": [r["company"] for r in coded if all(r[k] for k in CLASSES)],
        "companies_none": [r["company"] for r in coded if not any(r[k] for k in CLASSES)],
        "ai_sentences_total": len(SENT),
        "runway_years_median_all": round(statistics.median(yrs_all), 2), "runway_years_range_all": [min(yrs_all), max(yrs_all)],
        "runway_dated_n": len(yrs_dated), "runway_years_median_dated": round(statistics.median(yrs_dated), 2),
        "runway_12_month_only_n": sum(1 for r in rrows if not r["dated_horizon"] and r["years_from_filing"] <= 1),
        "op_cash_used_usd_millions_sorted": [round(x, 1) for x in usd_users],
        "op_cash_used_usd_median_millions": round(statistics.median(usd_users), 1),
        "op_cash_positive": [c for c, v in burns.items() if v > 0],
        "stops_by_class": {k: sum(1 for s in STOPS if s[2] == k) for k in ["efficacy or safety", "regulatory", "portfolio or strategic", "not stated"]},
        "quotes_checked": len(checks), "quotes_found": sum(1 for c in checks if c["found"]),
    }
    json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print([c for c in checks if not c["found"]])
    for r in rrows: print(r)


if __name__ == "__main__":
    main()
