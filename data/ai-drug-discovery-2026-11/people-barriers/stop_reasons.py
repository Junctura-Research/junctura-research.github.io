"""Cohort stop reasons, main reading and sensitivity lines.

Inputs: analysis/015/stops.csv (8 stops recorded through an earlier step plus NX-2127
(zelebrudomide), discontinued in August 2026 per Nurix's 10-Q for the quarter
ended 2026-08-31 (analysis/018/d2_stop_sentences.csv).

Main reading (rule set after the data were seen): ADG106's "deprioritized"
counts as portfolio; NX-2127 ("strategic prioritization of our wholly owned
oncology portfolio") counts as portfolio. Sensitivity: ADG106 as not stated.
Output: analysis/019/stop_reasons.json
"""
import csv, json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAP = {"efficacy or safety": "trial results", "portfolio or strategic": "portfolio",
       "regulatory": "other (regulatory)", "not stated": "not stated"}

rows = list(csv.DictReader(open(os.path.join(ROOT, "analysis/015/stops.csv"))))
stops = [{"candidate": r["candidate"], "recorded_reason": r["recorded_reason"],
          "class_015": MAP[r["class"]]} for r in rows]
nx_quote = ("In August 2026, as part of a strategic prioritization of our wholly owned "
            "oncology portfolio, we decided to discontinue further clinical development of zelebrudomide.")
d2 = open(os.path.join(ROOT, "analysis/018/d2_stop_sentences.csv")).read()
assert nx_quote in d2, "NX-2127 quote not found in analysis/018/d2_stop_sentences.csv"
stops.append({"candidate": "NX-2127 (zelebrudomide)", "recorded_reason": nx_quote,
              "class_015": "portfolio"})

def main_class(s):
    if s["candidate"].startswith("ADG106"):
        return "portfolio"
    return s["class_015"]

order = ["trial results", "portfolio", "other (regulatory)", "not stated"]
main = Counter(main_class(s) for s in stops)
sens = Counter(s["class_015"] for s in stops)
earlier8 = Counter(main_class(s) for s in stops[:8])
out = {
    "n_stops": len(stops),
    "main_reading_9": {k: main[k] for k in order},
    "sensitivity_ADG106_not_stated_9": {k: sens[k] for k in order},
    "main_reading_earlier_8": {k: earlier8[k] for k in order},
    "stops": [dict(s, class_main=main_class(s)) for s in stops],
}
json.dump(out, open(os.path.join(HERE, "stop_reasons.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in list(out)[:4]}, indent=1))
