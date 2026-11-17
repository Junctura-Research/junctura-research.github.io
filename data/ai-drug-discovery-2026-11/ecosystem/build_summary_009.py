"""an earlier step: merge the coded fragments, check every quote against its saved source text, and compute
the cycle's numbers into summary.json.

Inputs: frags/*_type.csv, frags/*_partner.csv (coded per AGENT_BRIEF.md), source texts in raw/text/,
raw/hk/ and analysis/008/raw/sources/. Outputs: revenue_by_type.csv, revenue_by_partner.csv,
quote_check.json, top20_share.csv, summary.json.
Definitions are those fixed in the research record section 2.
"""
import glob, json, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(HERE)

TOP20 = ['Eli Lilly', 'Merck & Co.', 'Pfizer', 'AbbVie', 'Johnson & Johnson', 'AstraZeneca', 'Roche', 'Novartis',
         'Sanofi', 'Bristol Myers Squibb', 'Novo Nordisk', 'GSK', 'Amgen', 'Boehringer Ingelheim', 'Takeda', 'Gilead',
         'Bayer', 'Teva', 'CSL', 'Regeneron']
# Partner name (as written in the filing) -> top-20 drugmaker. Genentech and Genzyme are subsidiaries.
ALIAS = [(r"Bristol", "Bristol Myers Squibb"), (r"Novartis", "Novartis"), (r"Sanofi|Genzyme", "Sanofi"),
         (r"^Gilead", "Gilead"), (r"^Pfizer", "Pfizer"), (r"^Roche|Genentech", "Roche"), (r"^Amgen", "Amgen"),
         (r"^Bayer", "Bayer")]
SHORT = {"Schrödinger": "Schrodinger", "Nurix Therapeutics": "Nurix", "Monte Rosa Therapeutics": "Monte Rosa",
         "Generate Biomedicines": "Generate", "Iambic Therapeutics": "Iambic"}

def top20(name):
    for pat, canon in ALIAS:
        if re.search(pat, str(name)):
            return canon
    return ""

norm = lambda s: re.sub(r"\s+", " ", str(s)).strip()

def load(kind):
    df = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(glob.glob(f"frags/*_{kind}.csv"))], ignore_index=True)
    df["company"] = df["company"].replace(SHORT)
    df["fy"] = df["fy"].astype(int)
    return df

typ, par = load("type"), load("partner")
typ["usd_m"] = typ["usd_m"].astype(float)

# Quote check: each quote must be an exact substring of its source text after collapsing whitespace.
cache, results = {}, []
for kind, df in (("type", typ), ("partner", par)):
    for i, r in df.iterrows():
        path = os.path.join(ROOT, r["source_file"]) if not os.path.isabs(r["source_file"]) else r["source_file"]
        if path not in cache:
            cache[path] = norm(open(path, errors="ignore").read()) if os.path.exists(path) else None
        ok = cache[path] is not None and norm(r["quote"]) in cache[path]
        results.append({"table": kind, "row": int(i), "company": r["company"], "fy": int(r["fy"]), "found": ok})
qc = {"quotes": len(results), "found": sum(r["found"] for r in results),
      "missing": [r for r in results if not r["found"]]}
json.dump(qc, open("quote_check.json", "w"), indent=1)

# Nurix FY2023 (year to 2023-11-30): the agreement partner was Seagen; Pfizer completed its acquisition of
# Seagen on 2023-12-14, after the fiscal year end, so FY2023 revenue is attributed to Seagen (not top 20).
par["top20"] = par["partner"].map(top20)
par.loc[(par.company == "Nurix") & (par.fy == 2023) & (par.partner.str.startswith("Pfizer")), "top20"] = ""
par.loc[(par.company == "Nurix") & (par.fy == 2023) & (par.partner.str.startswith("Pfizer")), "note"] = \
    "FY2023 counterparty was Seagen (acquired by Pfizer 2023-12-14, after Nurix's fiscal year end)"
typ.to_csv("revenue_by_type.csv", index=False)
par.to_csv("revenue_by_partner.csv", index=False)

# Revenue by type per company-year (sub-items excluded from sums).
main = typ[~typ.line_label.str.startswith("sub-item")]
piv = main[main.type != "total"].pivot_table(index=["company", "fy"], columns="type", values="usd_m", aggfunc="sum").fillna(0)
tot = main[main.type == "total"].groupby(["company", "fy"]).usd_m.sum()
piv["total"] = tot
piv["sum_check"] = (piv.drop(columns=["total"]).sum(axis=1) - piv["total"]).round(3)
for c in ["software", "collaboration", "grant", "other", "milestones", "royalties", "product"]:
    if c not in piv:
        piv[c] = 0.0
# Collaboration revenue (definition): all revenue that is not software, product or grant.
piv["collab_all"] = piv["collaboration"] + piv["other"] + piv["milestones"] + piv["royalties"]
piv["software_share"] = (piv["software"] / piv["total"]).where(piv["total"] > 0)
ms = typ[typ.line_label.str.startswith("sub-item of collaboration")].groupby(["company", "fy"]).usd_m.sum()
piv["itemized_milestones"] = ms
piv["milestone_share_of_collab"] = (piv["itemized_milestones"] / piv["collab_all"])

# Top-20 share, assessed only where named-partner dollar amounts cover >= 80% of collaboration revenue.
amt = par[pd.to_numeric(par.usd_m, errors="coerce").notna()].copy()
amt["v"] = amt.usd_m.astype(float)
# Exclusions: Kymera Note 5 duplicates (use MD&A amounts); Schrödinger contribution (grant) and software rows;
# cohort and percentage rows are non-numeric and already dropped; XtalPi amounts are customer totals across all
# revenue in RMB and their coverage is below 80% (top five 33-62%), so XtalPi is not assessed.
amt = amt[~((amt.company == "Kymera") & amt.basis.str.contains("Note 5"))]
amt = amt[~((amt.company == "Schrodinger") & amt.basis.str.contains(r"^software contribution|^drug discovery contribution|^related-party note: software|^software revenue from cohort", regex=True))]
amt = amt[~amt.partner.str.contains("unnamed|Customer [A-F]|Exscientia operations|National Institutes", regex=True)]
amt = amt[amt.company != "XtalPi"]
amt = amt[~amt.basis.str.contains("cumulative revenue recognized to date")]  # Monte Rosa 2025 Novartis 2025 agreement: cumulative, not annual
rows = []
for (co, fy), r in piv.iterrows():
    if r["collab_all"] <= 0:
        continue
    g = amt[(amt.company == co) & (amt.fy == fy)]
    named, t20 = g.v.sum(), g[g.top20 != ""].v.sum()
    cov = named / r["collab_all"]
    rows.append({"company": co, "fy": fy, "collab_revenue": round(r["collab_all"], 3), "named_partner_revenue": round(named, 3),
                 "coverage": round(cov, 3), "top20_revenue": round(t20, 3),
                 "top20_share": round(min(t20 / r["collab_all"], 1.0), 3) if cov >= 0.8 else None,  # MD&A rounding can exceed 100%; capped
                 "assessed": bool(cov >= 0.8),
                 "top20_partners": "; ".join(sorted(set(g[g.top20 != ""].top20))),
                 "other_partners": "; ".join(sorted(set(g[g.top20 == ""].partner)))})
t20 = pd.DataFrame(rows)
t20.to_csv("top20_share.csv", index=False)

# "Rising" test: companies with data for every year 2021-2025, USD reporters.
six = ["Schrodinger", "Recursion", "Nurix", "Kymera", "Absci", "Monte Rosa"]
c = piv.reset_index().pivot(index="company", columns="fy", values="collab_all").loc[six, [2021, 2022, 2023, 2024, 2025]]
comb = c.sum()
peak = {co: int(c.loc[co].idxmax()) for co in six}
dips = {co: [int(y) for y in range(2022, 2026) if c.loc[co, y] < c.loc[co, :y - 1].max()] for co in six}
rising = {
    "companies": six,
    "combined_by_year_usd_m": {int(k): round(v, 3) for k, v in comb.items()},
    "ratio_2025_to_2021": round(comb[2025] / comb[2021], 2),
    "avg_2024_25_vs_avg_2021_22": round(((comb[2024] + comb[2025]) / 2) / ((comb[2021] + comb[2022]) / 2), 2),
    "combined_without_monte_rosa": {int(k): round(v, 3) for k, v in c.drop("Monte Rosa").sum().items()},
    "peak_year": peak,
    "peak_in_2024_or_2025": sum(1 for v in peak.values() if v >= 2024),
    "years_below_an_earlier_high": dips,
    "companies_with_a_dip": sum(1 for v in dips.values() if v),
}

out = {
    "quote_check": {k: qc[k] for k in ("quotes", "found")},
    "sum_check_max_abs_diff": float(piv["sum_check"].abs().max()),
    "by_company_year": {f"{co} {fy}": {k: (None if pd.isna(v) else round(float(v), 3)) for k, v in r.items()}
                        for (co, fy), r in piv.iterrows()},
    "rising": rising,
    "top20_share_assessed": t20[t20.assessed][["company", "fy", "top20_share"]].to_dict("records"),
    "top20_not_assessed": t20[~t20.assessed][["company", "fy", "coverage"]].to_dict("records"),
}
json.dump(out, open("summary.json", "w"), indent=1, default=float)
print(json.dumps({"quote_check": out["quote_check"], "sum_check": out["sum_check_max_abs_diff"], "rising": rising}, indent=1, default=float))
print(piv[["total", "software", "collab_all", "grant", "software_share", "itemized_milestones", "milestone_share_of_collab"]].round(3).to_string())
print(t20.to_string())

# Stated top-20 partner revenue in 2024 and 2025, by how an earlier step worded the matching deal
# (analysis/008/deals_combined.csv). Hand map: (company, drugmaker, fy) -> wording of the deal that the filing
# says produced the revenue. Monte Rosa 2024 Novartis revenue is the 2024 license ("none"); 2025 split not stated.
WORDING = {("Kymera", "Sanofi"): "none", ("Kymera", "Gilead"): "none",
           ("Nurix", "Gilead"): "explicit", ("Nurix", "Sanofi"): "explicit", ("Nurix", "Pfizer"): "explicit",
           ("Monte Rosa", "Roche"): "platform-named", ("Monte Rosa", "Novartis"): "none",
           ("Generate", "Amgen"): "platform-named", ("Generate", "Novartis"): "platform-named",
           ("Schrodinger", "Bristol Myers Squibb"): "computational", ("Schrodinger", "Novartis"): "computational",
           ("Insilico Medicine", "Sanofi"): "explicit"}
w = amt[(amt.top20 != "") & amt.fy.isin([2024, 2025])].copy()
w = w[~((w.company == "Monte Rosa") & (w.fy == 2025))]  # 1.8 of 123.7 stated; year not assessed
w["wording"] = [WORDING.get((c, t), "unmapped") for c, t in zip(w.company, w.top20)]
by_w = w.groupby(["fy", "wording"]).v.sum().round(3)
out["top20_revenue_by_deal_wording"] = {f"{fy} {wd}": float(v) for (fy, wd), v in by_w.items()}
out["top20_revenue_by_deal_wording_rows"] = w[["company", "fy", "partner", "top20", "v", "wording"]].to_dict("records")
json.dump(out, open("summary.json", "w"), indent=1, default=float)
print(by_w.to_string())

# Cross-check: undimensioned XBRL total revenue facts against the coded totals.
x = pd.read_csv("xbrl_revenue_facts.csv")
x = x[x.dims.isna() & x.concept.str.match(r"Revenue(s$|FromContractWithCustomer(Ex|In)cludingAssessedTax$)")]
x = x.groupby(["company", "fy"]).usd_m.max()
rt = typ[typ.type == "total"].groupby(["company", "fy"]).usd_m.sum()
j = pd.concat([x, rt], axis=1, keys=["xbrl", "coded"]).dropna()
out["xbrl_total_check"] = {"company_years": int(len(j)), "mismatches": int(((j.xbrl - j.coded).abs() > 0.001).sum())}
out["top20_company_years"] = {"with_revenue": int(len(t20)), "not_assessed": int((~t20.assessed).sum())}
json.dump(out, open("summary.json", "w"), indent=1, default=float)
print(out["xbrl_total_check"], out["top20_company_years"])
