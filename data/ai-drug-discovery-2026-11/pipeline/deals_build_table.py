"""an earlier step: recompute the an earlier step inclusion counts with deals from private and non-US AI partners.

Usage: python3 build_table.py
Inputs:  ../007/annual_class.csv, ../007/deals.csv an earlier step, unchanged)
         annual_overrides.csv  (the review answer 2 on a review ruling for AstraZeneca; Bayer and CSL from nonsec_reports.json)
         deals_nonsec.csv      (hand-coded deals from company releases and exchange filings, with quotes)
Outputs: ecosystem_multinationals.csv, deals_combined.csv, summary.json
Definitions are those of an earlier step (analysis/007/README.md). "AI-adjacent" = a deal whose source has no AI wording.
"""
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *f: os.path.join(HERE, *f)
CORE = ["discovery collaboration", "asset license", "license and collaboration"]


def stats(deals):
    core = deals[deals.deal_type.isin(CORE)]
    up = core.upfront_usd_m.dropna()
    both = core.dropna(subset=["upfront_usd_m", "potential_milestones_usd_m"])
    u, m = float(both.upfront_usd_m.sum()), float(both.potential_milestones_usd_m.sum())
    return core, {
        "core_deals": int(len(core)),
        "by_type": core.deal_type.value_counts().to_dict(),
        "by_ai_wording": core.ai_wording.value_counts().to_dict(),
        "upfront_n": int(len(up)),
        "upfront_median_usd_m": round(float(up.median()), 2) if len(up) else None,
        "upfront_min_usd_m": float(up.min()) if len(up) else None,
        "upfront_max_usd_m": float(up.max()) if len(up) else None,
        "upfront_sum_usd_m": round(float(up.sum()), 1),
        "upfront_share": {"n_deals": int(len(both)), "upfront_sum": round(u, 1), "milestones_sum": round(m, 1),
                          "share": round(u / (u + m), 3) if len(both) else None,
                          "median_deal_share": round(float((both.upfront_usd_m / (both.upfront_usd_m + both.potential_milestones_usd_m)).median()), 3) if len(both) else None},
    }


def company_table(cls, core):
    rows = []
    for _, c in cls.iterrows():
        n = c.company
        d = core[core.drugmaker == n]
        d_ai = d[d.ai_wording == "explicit"]
        unit, acq = c.unit_or_investment, c.acquisition
        assessed = c.ties_ai_to_rd != ""
        broad = len(d) > 0 or unit == "yes" or acq == "yes"
        strict = len(d_ai) > 0 or unit == "yes" or acq == "yes"
        na = (not assessed) and len(d) == 0
        rows.append({"rank": int(c["rank"]), "company": n, "annual_source": c.annual_source,
                     "A_ties_ai_to_rd": c.ties_ai_to_rd, "B_unit_or_investment": unit, "D_acquisition": acq,
                     "C_deals_with_terms": len(d), "C_deals_explicit_ai": len(d_ai),
                     "C_partners": "; ".join(f"{r.ai_company} ({r.deal_type}, {r.ai_wording}, {r.channel})" for r in d.itertuples()),
                     "meets_broad": "yes" if broad else ("not assessed" if na else "no"),
                     "meets_strict": "yes" if strict else ("not assessed" if na else "no")})
    return pd.DataFrame(rows).sort_values("rank")


def lists(t):
    return {"strict_met": t[t.meets_strict == "yes"].company.tolist(),
            "strict_not_met": t[t.meets_strict == "no"].company.tolist(),
            "broad_met": t[t.meets_broad == "yes"].company.tolist(),
            "broad_not_met": t[t.meets_broad == "no"].company.tolist(),
            "not_assessed": t[t.meets_broad == "not assessed"].company.tolist()}


def main():
    cls7 = pd.read_csv(P("..", "007", "annual_class.csv"), dtype=str).fillna("")
    d7 = pd.read_csv(P("..", "007", "deals.csv"), dtype={"signed": str})
    d7["channel"] = "SEC filing an earlier step"
    d8 = pd.read_csv(P("deals_nonsec.csv"), dtype={"announced": str})
    d8["channel"] = "release or exchange filing an earlier step"
    d8 = d8.rename(columns={"announced": "signed"})
    d7["headline_usd_m"] = float("nan")
    cols = ["drugmaker", "ai_company", "signed", "deal_type", "upfront_usd_m", "equity_usd_m",
            "potential_milestones_usd_m", "headline_usd_m", "ai_wording", "channel"]
    AMT = ["upfront_usd_m", "equity_usd_m", "potential_milestones_usd_m", "headline_usd_m"]
    alld = pd.concat([d7[cols + ["quote"]].rename(columns={"quote": "terms_quote"}),
                      d8[cols + ["terms_quote", "ai_quote", "source_url", "group"]]], ignore_index=True)
    alld.to_csv(P("deals_combined.csv"), index=False)

    # an earlier step baseline, recomputed from its own inputs (reproduces analysis/007/summary.json)
    core7, s7 = stats(d7)
    t7 = company_table(cls7, core7)

    # an earlier step: annual-report overrides, then all deals with terms
    cls8 = cls7.copy()
    ov = pd.read_csv(P("annual_overrides.csv"), dtype=str).fillna("")
    for _, o in ov.iterrows():
        i = cls8.index[cls8.company == o.company][0]
        for col in ["annual_source", "ties_ai_to_rd", "unit_or_investment", "acquisition"]:
            if o[col] != "":
                cls8.at[i, col] = o[col]
    # an earlier step rows are kept as an earlier step counted them; an earlier step rows need at least one dollar amount
    is7 = alld.channel.str.contains("007")
    with_terms = alld[is7 | alld[AMT].notna().any(axis=1)]
    core8, s8 = stats(with_terms)
    t8 = company_table(cls8, core8)
    t8.to_csv(P("ecosystem_multinationals.csv"), index=False)
    new_core = core8[core8.channel.str.contains("008")]
    _, s_new = stats(new_core)

    no_terms = d8[d8.deal_type.isin(CORE) & d8[AMT].isna().all(axis=1)]
    assessed = cls8[cls8.ties_ai_to_rd != ""]
    l7, l8 = lists(t7), lists(t8)
    s = {
        "A_annual_reports_assessed": {"cycle007": int((cls7.ties_ai_to_rd != "").sum()), "cycle008": int(len(assessed))},
        "A_tie_ai_to_rd": {"cycle007": int((cls7.ties_ai_to_rd == "yes").sum()), "cycle008": int((assessed.ties_ai_to_rd == "yes").sum())},
        "A_not_assessed_cycle008": cls8[cls8.ties_ai_to_rd == ""].company.tolist(),
        "deals_cycle007": s7,
        "deals_new_cycle008_with_terms": s_new,
        "deals_combined": s8,
        "new_deals_terms_not_disclosed": {"n": int(len(no_terms)),
                                          "by_ai_wording": no_terms.ai_wording.value_counts().to_dict(),
                                          "drugmakers": sorted(no_terms.drugmaker.unique().tolist())},
        "inclusion_cycle007": {k: v for k, v in l7.items()},
        "inclusion_cycle008": {k: v for k, v in l8.items()},
        "change": {"strict_added": [c for c in l8["strict_met"] if c not in l7["strict_met"]],
                   "broad_added": [c for c in l8["broad_met"] if c not in l7["broad_met"]],
                   "newly_assessed": [c for c in l7["not_assessed"] if c not in l8["not_assessed"]]},
        "new_deals_by_group": new_core.group.value_counts().sort_index().to_dict() if len(new_core) else {},
        "new_deals_headline_only": int(new_core[new_core[["upfront_usd_m", "equity_usd_m", "potential_milestones_usd_m"]].isna().all(axis=1)].shape[0]),
        "drugmakers_with_explicit_ai_deal": {"cycle007": int((t7.C_deals_explicit_ai > 0).sum()), "cycle008": int((t8.C_deals_explicit_ai > 0).sum())},
    }
    s["new_deals_drugmakers"] = sorted(new_core.drugmaker.unique().tolist())
    # Sensitivity 1: without CSPC (a drugmaker with an AI platform, not a self-described AI company)
    _, s["sensitivity_new_without_cspc"] = stats(new_core[new_core.ai_company != "CSPC Pharmaceutical"])
    # Sensitivity 2: strict count without deals whose only source is a wire copy on a news site (Phenomic AI)
    t_alt = company_table(cls8, core8[core8.ai_company != "Phenomic AI"])
    s["sensitivity_strict_without_phenomic"] = int((t_alt.meets_strict == "yes").sum())
    s["strict_count"] = {"cycle007": len(l7["strict_met"]), "cycle008": len(l8["strict_met"])}
    s["broad_count"] = {"cycle007": len(l7["broad_met"]), "cycle008": len(l8["broad_met"])}
    json.dump(s, open(P("summary.json"), "w"), indent=1)
    print(json.dumps(s, indent=1))
    print(t8[["rank", "company", "A_ties_ai_to_rd", "C_deals_with_terms", "C_deals_explicit_ai", "meets_broad", "meets_strict"]].to_string(index=False))


if __name__ == "__main__":
    main()
