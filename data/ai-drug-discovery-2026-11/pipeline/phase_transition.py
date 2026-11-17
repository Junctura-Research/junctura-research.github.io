"""an earlier step T1: phase-transition rates of the 32-candidate cohort, rules fixed in the research record section 2 before data.
Usage (from this folder): python phase_transition.py -> phase_transition.json
"""
import csv, json, math
def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]
rows = list(csv.DictReader(open("cohort_32.csv")))
COVID = {"bamlanivimab (LY-CoV555)", "bebtelovimab (LY-CoV1404)"}
RANK = {"Phase 1": 1, "Phase 1/2": 1.5, "Phase 2": 2, "Phase 2/3": 2.5, "Phase 3": 3, "Phase 4": 4}

def level(hp, p12_as_p2):
    r = RANK[hp]
    if r == 1.5: return 2 if p12_as_p2 else 1
    if r == 2.5: return 2
    return int(r)

def transition(phase, p12_as_p2=False, unknown_fail=False, drop=()):
    adv, fail, cens, excl = [], [], [], []
    for r in rows:
        if r["candidate"] in drop: continue
        lv = level(r["highest_phase_sponsor"], p12_as_p2)
        if lv < phase: continue
        if lv > phase: adv.append(r["candidate"]); continue
        o = r["outcome"]
        if o == "discontinued": fail.append(r["candidate"])
        elif o in ("unknown", "superseded"):
            (fail if unknown_fail else excl).append(r["candidate"])
        else: cens.append(r["candidate"])
    n = len(adv) + len(fail)
    res = {"advanced": adv, "failed": fail, "unresolved_active": cens, "excluded_unknown_superseded": excl,
           "resolved": n, "reportable (>=10 resolved)": n >= 10}
    if n:
        res["rate_pct"] = round(100 * len(adv) / n, 1); res["95ci"] = wilson(len(adv), n)
    return res

out = {"as_of": "2026-11-17", "n": len(rows),
       "baseline_BIO_2011_2020": {"phase1_to_2": 52.0, "phase2_to_3": 28.9, "oncology_phase1_to_2": 48.8,
                                   "oncology_phase2_to_3": 24.6, "infectious_phase1_to_2": 57.8, "infectious_phase2_to_3": 38.4,
                                   "source": "raw/sources/bio_2011_2020.txt lines 190-271"},
       "phase1_to_2": {"main": transition(1), "a_phase1_2_counts_as_phase2": transition(1, p12_as_p2=True),
                        "b_unknown_superseded_fail": transition(1, unknown_fail=True),
                        "c_without_covid_antibodies": transition(1, drop=COVID)},
       "phase2_to_3": {"main": transition(2), "a_phase1_2_counts_as_phase2": transition(2, p12_as_p2=True),
                        "b_unknown_superseded_fail": transition(2, unknown_fail=True),
                        "c_without_covid_antibodies": transition(2, drop=COVID)}}
json.dump(out, open("phase_transition.json", "w"), indent=1)
for ph in ("phase1_to_2", "phase2_to_3"):
    for k, v in out[ph].items():
        print(ph, k, len(v["advanced"]), "/", v["resolved"], v.get("rate_pct"), v.get("95ci"), "censored", len(v["unresolved_active"]))
