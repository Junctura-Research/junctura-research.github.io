"""an earlier step: all computed numbers into summary.json.
Usage: python3 build_summary.py   (after term_trend.py, check_quotes.py, deferred_tables.py; precision_sample.csv judged)
Inputs: vintage.csv, g3_own_reading.csv, ../004/cohort_with_phase.csv, term_counts.csv, precision_sample.csv, deferred_summary.json
Cohort: the 16 headline candidates (the review cut-off, a review ruling) = the first 16 headline rows of an earlier step's cohort;
GB-0669 and GB-0895 form the 18-candidate variant.
Sensitivities (boundary cases found during coding, not foreseen in the plan):
  S1: evolutionary algorithms not counted as generative: EXS21546 -> not stated; DSP-1181, DSP-0038 -> G1
      (their dated sources name evolutionary design, plus prioritisation for DSP-1181/0038, and no other generative method).
  S2: Nurix platform text taken from the S-1 closest to the design date (names no AI method): NX-2127, NX-1607, NX-5948 -> not stated.
"""
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *f: os.path.join(HERE, *f)
ORDER = ["G1", "G2", "G3", "G4", "computational", "not stated"]
S1 = {"EXS21546": "not stated", "DSP-1181": "G1", "DSP-0038": "G1"}
S2 = {"NX-2127": "not stated", "NX-1607": "not stated", "NX-5948": "not stated"}
GEN_RANK = {"G1": 1, "G2": 2, "G3": 3, "G4": 4}


def counts(s):
    return {k: int((s == k).sum()) for k in ORDER}


def highest(gens):
    g = [x for x in str(gens).split(";") if x in GEN_RANK]
    return max(g, key=GEN_RANK.get) if g else None


def main():
    v = pd.read_csv(P("vintage.csv"))
    coh = pd.read_csv(P("..", "004", "cohort_with_phase.csv"))
    coh = coh[coh.tier == "headline"].reset_index(drop=True)
    coh["key"] = coh.candidate.str.split(" ").str[0]
    v["key"] = v.candidate.str.split(" ").str[0]
    m = coh[["key", "outcome", "highest_phase"]].merge(v, on="key", how="left")
    m["cohort16"] = ~m.key.isin(["GB-0669", "GB-0895"])
    m["vintage_S1"] = m.apply(lambda r: S1.get(r.key, r.vintage), axis=1)
    m["vintage_S2"] = m.apply(lambda r: S2.get(r.key, r.vintage), axis=1)
    m["vintage_S1S2"] = m.apply(lambda r: S1.get(r.key, S2.get(r.key, r.vintage)), axis=1)
    m["later_highest"] = m.later_generations_named.map(highest)
    m["retro_attribution"] = m.apply(lambda r: bool(r.later_highest) and GEN_RANK.get(r.later_highest, 0) > GEN_RANK.get(r.vintage, 0), axis=1)
    m["design_year"] = m.design_date.astype(str).str[:4].astype(int)
    m.drop(columns="key").to_csv(P("vintage_with_outcome.csv"), index=False)
    c16, c18 = m[m.cohort16], m
    outc = lambda d, col: {k: d[d[col] == k].outcome.value_counts().to_dict() for k in ORDER if (d[col] == k).any()}
    s = {"part_A": {
        "n16": int(len(c16)), "n18": int(len(c18)),
        "vintage16": counts(c16.vintage), "vintage18": counts(c18.vintage),
        "vintage16_S1_evolutionary_not_generative": counts(c16.vintage_S1),
        "vintage16_S2_nurix_from_S1_filing": counts(c16.vintage_S2),
        "vintage16_S1_and_S2": counts(c16.vintage_S1S2),
        "level16": c16.level.value_counts().to_dict(), "level18": c18.level.value_counts().to_dict(),
        "outcome_by_vintage16": outc(c16, "vintage"),
        "outcome_by_vintage18": outc(c18, "vintage"),
        "g2_or_g4_named_in_window_any": int(c18.generations_named.str.contains("G2|G4").sum()),
        "anachronism_flags": 0,
        "retro_attribution": m[m.retro_attribution].candidate.tolist(),
        "later_sources_found18": int(m.later_source_date.notna().sum()),
        "design_year_range18": [int(m.design_year.min()), int(m.design_year.max())],
        "design_year_counts18": m.design_year.value_counts().sort_index().to_dict(),
        "g3_candidates18": m[m.vintage == "G3"].candidate.tolist(),
    }}
    # Part B
    tc = pd.read_csv(P("term_counts.csv"))
    gens = ["G1_ml_prediction", "G2_structure_prediction", "G3_generative", "G4_foundation_language", "computational"]
    panel_years = list(range(2021, 2026))
    have = tc[tc.fiscal_year.isin(panel_years)].groupby("company").fiscal_year.nunique()
    panel = sorted(have[have == len(panel_years)].index)
    bp = tc[tc.company.isin(panel) & tc.fiscal_year.isin(panel_years)]
    s["part_B"] = {
        "filings": int(len(tc)), "companies": int(tc.company.nunique()),
        "balanced_panel_2021_2025": panel,
        "panel_companies_mentioning": {g: {int(fy): int((grp[g + "_sentences"] > 0).sum()) for fy, grp in bp.groupby("fiscal_year")} for g in gens},
        "all_filers_by_year": pd.read_csv(P("term_trend.csv")).set_index("fiscal_year")[[g + "_companies" for g in gens] + ["companies"]].to_dict("index"),
        "g4_sentences_by_company": tc.groupby("company").G4_foundation_language_sentences.sum().loc[lambda x: x > 0].to_dict(),
        "g2_sentences_by_company": tc.groupby("company").G2_structure_prediction_sentences.sum().loc[lambda x: x > 0].to_dict(),
    }
    ps = pd.read_csv(P("precision_sample.csv"))
    s["part_B"]["precision_sample"] = {g: {"yes": int((grp.own_tool == "yes").sum()), "n": int(len(grp)), "pool": int(grp["pool"].iloc[0]),
                                           "share": round(float((grp.own_tool == "yes").mean()), 2)} for g, grp in ps.groupby("generation")}
    g3r = pd.read_csv(P("g3_own_reading.csv"))
    s["part_B"]["g3_own_tool_panel_hand_read"] = {int(k): int(v) for k, v in g3r[g3r.own_tool == "yes"].groupby("fiscal_year").company.count().items()}
    s["part_B"]["g3_not_own_tool"] = g3r[g3r.own_tool == "no"][["company", "fiscal_year"]].to_dict("records")
    s["part_C"] = json.load(open(P("deferred_summary.json")))
    json.dump(s, open(P("summary.json"), "w"), indent=1, default=str)
    print(json.dumps(s, indent=1, default=str))


if __name__ == "__main__":
    main()
