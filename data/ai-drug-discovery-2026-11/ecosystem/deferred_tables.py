"""an earlier step Part C (the review, a review ruling): deals without terms per drugmaker, and the strict-count sensitivity line.

Usage: python3 deferred_tables.py
Inputs:  ../008/deals_nonsec.csv an earlier step hand-coded deals, with quotes and sources),
         ../008/ecosystem_multinationals.csv an earlier step inclusion table)
Outputs: deals_without_terms.csv (per drugmaker), deferred_summary.json
No new searching. Definitions as in an earlier step: core = discovery collaboration, asset license, license and collaboration;
"without terms" = no upfront, equity, milestone or headline amount. an earlier step (SEC channel) rows all carry terms as counted then.
"""
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *f: os.path.join(HERE, *f)
CORE = ["discovery collaboration", "asset license", "license and collaboration"]
AMT = ["upfront_usd_m", "equity_usd_m", "potential_milestones_usd_m", "headline_usd_m"]


def main():
    d = pd.read_csv(P("..", "008", "deals_nonsec.csv"))
    eco = pd.read_csv(P("..", "008", "ecosystem_multinationals.csv"))
    noterms = d[d[AMT].isna().all(axis=1)]
    core_nt = noterms[noterms.deal_type.isin(CORE)]
    other_nt = noterms[noterms.deal_type == "other"]
    rows = []
    for _, e in eco.sort_values("rank").iterrows():
        n = e.company
        c = core_nt[core_nt.drugmaker == n]
        o = other_nt[other_nt.drugmaker == n]
        rows.append({"rank": e["rank"], "drugmaker": n,
                     "core_deals_with_terms": int(e.C_deals_with_terms),
                     "core_deals_without_terms": len(c),
                     "core_without_terms_explicit_ai": int((c.ai_wording == "explicit").sum()),
                     "core_without_terms_partners": "; ".join(f"{r.ai_company} ({r.deal_type}, {r.announced})" for r in c.itertuples()),
                     "other_deals_without_terms": len(o),
                     "other_without_terms_partners": "; ".join(f"{r.ai_company} ({r.announced})" for r in o.itertuples()),
                     "meets_strict_cycle008": e.meets_strict,
                     "meets_strict_if_no_terms_counted": "yes" if (e.meets_strict == "yes" or (c.ai_wording == "explicit").any()) else e.meets_strict})
    t = pd.DataFrame(rows)
    t.to_csv(P("deals_without_terms.csv"), index=False)
    s = {
        "core_deals_without_terms": int(len(core_nt)),
        "core_without_terms_by_ai_wording": core_nt.ai_wording.value_counts().to_dict(),
        "core_without_terms_by_type": core_nt.deal_type.value_counts().to_dict(),
        "drugmakers_with_core_deal_without_terms": int((t.core_deals_without_terms > 0).sum()),
        "other_deals_without_terms": int(len(other_nt)),
        "drugmakers_with_other_deal_without_terms": int((t.other_deals_without_terms > 0).sum()),
        "unclassified_rows_excluded": d[~d.deal_type.isin(CORE + ["other"]) | d.deal_type.isna()][["ai_company", "drugmaker", "deal_type"]].to_dict("records"),
        "strict_count_cycle008": int((t.meets_strict_cycle008 == "yes").sum()),
        "strict_count_if_explicit_no_terms_counted": int((t.meets_strict_if_no_terms_counted == "yes").sum()),
        "strict_added_by_sensitivity": t[(t.meets_strict_cycle008 != "yes") & (t.meets_strict_if_no_terms_counted == "yes")].drugmaker.tolist(),
        "strict_still_not_met": t[t.meets_strict_if_no_terms_counted != "yes"].drugmaker.tolist(),
    }
    json.dump(s, open(P("deferred_summary.json"), "w"), indent=1)
    print(json.dumps(s, indent=1))
    print(t[["rank", "drugmaker", "core_deals_with_terms", "core_deals_without_terms", "core_without_terms_explicit_ai", "other_deals_without_terms", "meets_strict_cycle008", "meets_strict_if_no_terms_counted"]].to_string(index=False))


if __name__ == "__main__":
    main()
