"""The Note's variant lines on the final cohort of 32 (Accutar's AC0682 and AC176 discontinued under the
precedence rule). Same variants as note_update.py, recomputed.
Inputs: cohort_32_final.csv; ../cohort/cohort_with_phase.csv (Generate's GB-0669, GB-0895 and
BenevolentAI's BEN-8744, outside the headline cohort).
Usage (from this folder): python note_variants.py -> note_variants.json"""
import csv, json, math
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)]
def line(k, n): return {"k": k, "n": n, "pct": round(k / n * 100, 1), "95ci": wilson(k, n)}
rows = list(csv.DictReader(open("cohort_32_final.csv", encoding="utf-8")))
n = len(rows); assert n == 32
k = sum(r["outcome"] == "discontinued" for r in rows)
kb = sum(r["outcome"] in ("discontinued", "unknown", "superseded") for r in rows)
RANK = {"Phase 1": 1, "Phase 1/2": 1, "Phase 2": 2, "Phase 2/3": 2, "Phase 3": 3, "Phase 4": 4}
p3 = [r["candidate"] for r in rows if RANK[r["highest_phase_sponsor"]] >= 3]
c004 = {r["candidate"]: r for r in csv.DictReader(open("../cohort/cohort_with_phase.csv", encoding="utf-8"))}
assert c004["GB-0669"]["outcome"] == "discontinued" and c004["GB-0895"]["outcome"] == "active"
assert c004["BEN-8744"]["outcome"] == "unknown"
dsp = [r for r in rows if r["candidate"] in ("DSP-0038", "DSP-2342")]; assert all(r["outcome"] == "active" for r in dsp)
ADDED = ("MindRank", "Accutar", "Aulos", "Adagene", "AbCellera", "Pharos", "Drug Farm")
orig = [r for r in rows if not any(a in r["company"] for a in ADDED)]; assert len(orig) == 16
stops = [r for r in rows if r["outcome"] == "discontinued"]
out = {
    "strict": line(k, n), "broad": line(kb, n),
    "phase3_or_later_sponsor_or_partner": dict(line(len(p3), n), candidates=p3),
    "later_cutoff_with_Generate_34": {"strict": line(k + 1, n + 2), "broad": line(kb + 1, n + 2), "phase3": line(len(p3) + 1, n + 2)},
    "with_BEN-8744_target_only_33": {"strict": line(k, n + 1), "broad": line(kb + 1, n + 1)},
    "without_REC-3964_31": {"strict": line(k - 1, n - 1)},
    "Sumitomo_DSP-0038_DSP-2342_unknown": {"broad": line(kb + 2, n)},
    "original_16_discontinued_now": sum(r["outcome"] == "discontinued" for r in orig),
    "stops_at_phase2_or_earlier_excluding_revoked_authorizations": sum(RANK[r["highest_phase_sponsor"]] <= 2 for r in stops if not r["candidate"].startswith(("bamlanivimab", "bebtelovimab"))),
}
json.dump(out, open("note_variants.json", "w"), indent=1); print(json.dumps(out, indent=1))
