"""Add Nurix-Roche (bexobrutideg, 2026) to the combined deal table and recompute the report's money statistics.

Usage: python3 deals_update.py
Inputs (unchanged): ../008/deals_combined.csv, ../007/annual_class.csv, ../008/annual_overrides.csv,
                    ../008/build_table.py (stats and company_table functions, an earlier step/008 rules)
Outputs: deals_with_nurix_roche.csv, deals_update.json, ecosystem_multinationals_019.csv (per-drugmaker table after the update)

New row, read from Nurix's Form 8-K filed 2026-06-08 (accession 0001549595-26-000030):
  Item 1.01: "Roche will make an upfront cash payment of $700.0 million to Nurix, and Nurix will be eligible to
  receive development, regulatory, and sales milestone payments, with total potential payments of up to
  $2.3 billion, including the upfront payment."
  Milestone ceiling = 2,300 - 700 = 1,600 ($ million). No equity stated. Deal type: license and collaboration
  (the 8-K's "License and Collaboration Agreement"; co-development and co-commercialization in the US).
  AI wording: none. Item 1.01 and the body of Exhibit 99.1 describe the deal with no AI words; the only AI words
  are in the press release's company boilerplate ("Powered by its proprietary AI-integrated DEL-AI discovery
  engine ..."), which does not describe this deal. Sensitivity: platform-named.
"""
import importlib.util, json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *f: os.path.join(HERE, *f)
spec = importlib.util.spec_from_file_location("bt8", P("..", "008", "build_table.py"))
bt8 = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt8)
AMT = ["upfront_usd_m", "equity_usd_m", "potential_milestones_usd_m", "headline_usd_m"]
URL = "https://www.sec.gov/Archives/edgar/data/1549595/000154959526000030/nrix-20260606.htm"

NEW = {"drugmaker": "Roche", "ai_company": "Nurix", "signed": "2026-06", "deal_type": "license and collaboration",
       "upfront_usd_m": 700.0, "equity_usd_m": float("nan"), "potential_milestones_usd_m": 1600.0,
       "headline_usd_m": 2300.0, "ai_wording": "none", "channel": "SEC filing an earlier step, Form 8-K)",
       "terms_quote": "Under the Collaboration Agreement, Roche will make an upfront cash payment of $700.0 million to Nurix, and Nurix will be eligible to receive development, regulatory, and sales milestone payments, with total potential payments of up to $2.3 billion, including the upfront payment.",
       "ai_quote": "", "source_url": URL, "group": ""}


def classes():
    cls = pd.read_csv(P("..", "007", "annual_class.csv"), dtype=str).fillna("")
    ov = pd.read_csv(P("..", "008", "annual_overrides.csv"), dtype=str).fillna("")
    for _, o in ov.iterrows():
        i = cls.index[cls.company == o.company][0]
        for col in ["annual_source", "ties_ai_to_rd", "unit_or_investment", "acquisition"]:
            if o[col] != "":
                cls.at[i, col] = o[col]
    return cls


def with_terms(d):
    is7 = d.channel.str.contains("007")
    return d[is7 | d[AMT].notna().any(axis=1)]


def block(d, cls):
    wt = with_terms(d)
    core, s = bt8.stats(wt)
    _, s_nocspc = bt8.stats(wt[wt.ai_company != "CSPC Pharmaceutical"])
    t = bt8.company_table(cls, core)
    t_alt = bt8.company_table(cls, core[core.ai_company != "Phenomic AI"])
    return t, {"all_deals": s, "without_cspc": s_nocspc,
            "strict_count": int((t.meets_strict == "yes").sum()),
            "broad_count": int((t.meets_broad == "yes").sum()),
            "strict_without_phenomic": int((t_alt.meets_strict == "yes").sum()),
            "strict_not_met": t[t.meets_strict == "no"].company.tolist()}


def main():
    before = pd.read_csv(P("..", "008", "deals_combined.csv"), dtype={"signed": str})
    after = pd.concat([before, pd.DataFrame([NEW])], ignore_index=True)
    after.to_csv(P("deals_with_nurix_roche.csv"), index=False)
    cls = classes()
    alt = after.copy(); alt.loc[alt.index[-1], "ai_wording"] = "platform-named"
    out = {"new_deal": {k: (None if (isinstance(v, float) and v != v) else v) for k, v in NEW.items()},
           "before": block(before, cls)[1], "after": block(after, cls)[1],
           "sensitivity_after_platform_named": {"by_ai_wording": bt8.stats(with_terms(alt))[1]["by_ai_wording"]}}
    block(after, cls)[0].to_csv(P("ecosystem_multinationals_019.csv"), index=False)
    json.dump(out, open(P("deals_update.json"), "w"), indent=1)
    for k in ["before", "after"]:
        b = out[k]
        for s in ["all_deals", "without_cspc"]:
            x = b[s]
            print(k, s, x["core_deals"], x["by_ai_wording"], "upfront n", x["upfront_n"], "median", x["upfront_median_usd_m"],
                  "range", x["upfront_min_usd_m"], x["upfront_max_usd_m"], "share", x["upfront_share"])
        print(k, "strict", b["strict_count"], "broad", b["broad_count"], "strict w/o phenomic", b["strict_without_phenomic"])


if __name__ == "__main__":
    main()
