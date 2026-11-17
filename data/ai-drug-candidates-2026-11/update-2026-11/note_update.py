"""Numbers for the Report Update to the Research Note (as of 2026-11-17). No new data.

Usage (from this folder): python note_update.py
Inputs:
  cohort_32.csv          the 32-candidate dated cohort (16 original + 14 added at six companies + 2 Drug Farm)
  sec_stop_sentences.csv  Nurix 10-Q sentence: NX-2127 (zelebrudomide) discontinued in August 2026
  cohort_30_rules.json       Phase 3 tiers across all current candidates
  fda_summary.json        Drugs@FDA original approvals 2019-2026
  stop_reasons.json      stop reasons, main reading and sensitivity
Outputs: note_cohort_32.csv, note_update.json

Outcome precedence (rule set after the data were seen): regulator action > company or partner stop statement >
registry status > pipeline listing. Unknown and superseded count in the broad rate only.
"Reached Phase 3 or later" counts trials run by the sponsor or its development partner.
"""
import csv, json, math, datetime, os

ROOT = os.getcwd()
P = lambda p: os.path.join(ROOT, p)

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]
def line(k, n): return {"k": k, "n": n, "pct": round(100 * k / n, 1), "95ci": wilson(k, n)}

rows = list(csv.DictReader(open(P("cohort_32.csv"))))
assert len(rows) == 32
NX_QUOTE = ("In August 2026, as part of a strategic prioritization of our wholly owned oncology portfolio, "
            "we decided to discontinue further clinical development of zelebrudomide.")
assert NX_QUOTE in open(P("sec_stop_sentences.csv"), encoding="utf-8").read()
for r in rows:
    r["outcome_basis"] = ""
    if r["candidate"].startswith("NX-2127"):
        assert r["outcome"] == "active"
        r["outcome"] = "discontinued"
        r["outcome_basis"] = ("company stop statement (Nurix Form 10-Q for the quarter ended 2026-08-31, filed 2026-10-13); "
                              "registry trial NCT04830137 still listed as recruiting")
    if r["candidate"] in ("bamlanivimab (LY-CoV555)", "bebtelovimab (LY-CoV1404)"):
        r["outcome_basis"] = "regulator action: FDA emergency use authorization(s) revoked; never approved"
    if r["candidate"] in ("AC0682", "AC176"):
        r["outcome_basis"] = "all registered trials terminated; listed on an undated company pipeline page"

n = len(rows)
by = {o: [r["candidate"] for r in rows if r["outcome"] == o] for o in ("active", "discontinued", "unknown", "superseded")}
k = len(by["discontinued"]); kb = k + len(by["unknown"]) + len(by["superseded"])
P3 = ("Phase 3", "Phase 4")
p3_sponsor = [r["candidate"] for r in rows if r["highest_phase_sponsor"] in P3]
p3_any = [r["candidate"] for r in rows if r["highest_phase_registry"] in P3]
ORIG16 = rows[:16]
assert ORIG16[0]["candidate"] == "EXS21546" and ORIG16[15]["candidate"] == "BEN-2293"

# Follow-up since first trial (dated starts only) to 2026-11-17; and trials entered by end of 2022
AS_OF = datetime.date(2026, 11, 17)
fu, bound = {}, []
by2022 = 0
for r in rows:
    s = r["first_trial"]
    if s.startswith("by ") or "or earlier" in s[:20]:
        bound.append(r["candidate"])
        if "or earlier" in s[:20] and int(s[:4]) <= 2022:
            by2022 += 1
        continue
    d = s[:10] if s[7:8] == "-" and s[8:10].isdigit() else s[:7] + "-01"
    fu[r["candidate"]] = round((AS_OF - datetime.date.fromisoformat(d)).days / 365.25, 2)
    if int(s[:4]) <= 2022:
        by2022 += 1

def split(claim):
    rs = [r for r in rows if r["claim"] == claim]
    return {"n": len(rs), "discontinued": sum(r["outcome"] == "discontinued" for r in rs)}

# Variants carried over from the published Note, recomputed on 32
c004 = {r["candidate"]: r for r in csv.DictReader(open(P("../cohort/cohort_with_phase.csv")))}
gen = [c004["GB-0669"], c004["GB-0895"]]                     # 2024-01-04 Generate release (later cut-off)
assert gen[0]["outcome"] == "discontinued" and gen[1]["outcome"] == "active" and gen[1]["highest_phase"] == "Phase 3"
assert c004["BEN-8744"]["outcome"] == "unknown"              # AI-identified target only
sumi_unknown = kb + 2                                        # DSP-0038, DSP-2342 treated as unknown
rec = [r for r in rows if r["candidate"] == "REC-3964"][0]; assert rec["outcome"] == "discontinued"
variants = {
    "later_cutoff_with_Generate_34": {"strict": line(k + 1, n + 2), "broad": line(kb + 1, n + 2),
                                      "phase3_sponsor_or_partner": line(len(p3_sponsor) + 1, n + 2)},
    "with_BEN-8744_target_only_33": {"strict": line(k, n + 1), "broad": line(kb + 1, n + 1)},
    "without_REC-3964_31": {"strict": line(k - 1, n - 1)},
    "Sumitomo_DSP-0038_DSP-2342_unknown": {"broad": line(sumi_unknown, n)},
}

stops = {r["candidate"]: r["highest_phase_sponsor"] for r in rows if r["outcome"] == "discontinued"}
tiers = json.load(open(P("cohort_30_rules.json")))["phase3_tiers_all_current_candidates"]
out = {
    "as_of": "2026-11-17", "n": n,
    "added_candidates": [r["candidate"] for r in rows[16:]],
    "added_companies": sorted({r["company"] for r in rows[16:]}),
    "by_outcome": {o: len(v) for o, v in by.items()}, "members": by,
    "strict": line(k, n), "broad": line(kb, n),
    "sensitivity": {
        "strict_without_precedence_rule (bamlanivimab, bebtelovimab active)": line(k - 2, n),
        "strict_AC0682_AC176_discontinued": line(k + 2, n),
        "strict_without_NX-2127_stop (as of 2026-11-16 record)": line(k - 1, n),
    },
    "phase3_or_later_sponsor_or_partner_trials": dict(line(len(p3_sponsor), n), candidates=p3_sponsor),
    "phase3_or_later_with_investigator_phase4": dict(line(len(p3_any), n), candidates=p3_any),
    "variants": variants,
    "stops_highest_sponsor_phase": stops,
    "claim_split": {"explicit": split("explicit"), "platform": split("platform")},
    "original_16_now": {"strict": line(sum(r["outcome"] == "discontinued" for r in ORIG16), 16),
                        "broad": line(sum(r["outcome"] != "active" for r in ORIG16), 16)},
    "followup_years_dated": {"min": min(fu.values()), "max": max(fu.values()),
                             "min_candidate": min(fu, key=fu.get), "max_candidate": max(fu, key=fu.get),
                             "start_bound_only": bound},
    "entered_trials_by_end_2022": by2022,
    "phase3_tiers_all_current_candidates": tiers,
    "drugsfda": json.load(open(P("fda_summary.json"))),
    "stop_reasons": json.load(open(P("stop_reasons.json")))["main_reading_9"],
    "published_2026_11_16": {"n": 16, "strict": "4/16 = 25.0% (95% interval 10.2-49.5%)", "broad": "6/16 = 37.5%",
                             "phase3": "2/16 = 12.5%", "tiers": "1/3/5"},
}
with open(P("note_cohort_32.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump(out, open(P("note_update.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "members"}, indent=1))
