"""an earlier step: apply an earlier step's fixed rules (Rules 0-2, gap tests M1-M5) to the evidence from the three unfinished
coverage searches, and merge with an earlier step's results.

Usage (from the repo root): python analysis/013/build_update.py
Inputs: analysis/011/companies.csv an earlier step decisions, unchanged), analysis/013/frags/*.jsonl (evidence collected by
three fresh agents from analysis/013/AGENT_BRIEF.md; quotes checked by check_quotes.py).
Outputs (analysis/013/): companies_013.csv (every company decided or changed this cycle, with evidence), significant_013.csv,
emerging_013.csv, emerging_log_013.csv, m2_013.csv, summary.json.

As in an earlier step, the criteria each company meets were judged by hand from the evidence lines and are written out below
(DEC), so every call is visible. The evidence for each call is looked up from the frags by company and criterion.
"""
import csv, json, glob, os, collections

D = "analysis/013"
ALIAS = {"VantAI (now Proxima)": "VantAI", "Proxima": "VantAI", "Parabilis Medicines": "Parabilis",
         "Tangram Therapeutics (formerly e-therapeutics plc)": "Tangram Therapeutics",
         "Chipscreen Biosciences (微芯生物)": "Chipscreen", "Nxera Pharma (formerly Sosei)": "Nxera Pharma",
         "Oncodesign Precision Medicine (OPM)": "Oncodesign Precision Medicine", "LifeMine Therapeutics": "LifeMine",
         "HitGen (成都先导)": "HitGen", "Superluminal": "Superluminal Medicines"}
ev = collections.defaultdict(list)
for p in sorted(glob.glob(f"{D}/frags/*.jsonl")):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        r["frag"] = os.path.basename(p)
        ev[(ALIAS.get(r["company"], r["company"]), r["criterion"])].append(r)

old = {r["company"]: r for r in csv.DictReader(open("analysis/011/companies.csv"))}

# Hand decisions ------------------------------------------------------------------------------------------------------
# company: (R0 class, R0 basis, Rule 1 criteria met, Rule 2 criteria met, emerging eligibility True/False/None, note)
# Emerging eligibility = founded on or after 2021-11-17 OR first disclosed financing on or after that date
# (None = cannot be assessed). Only R0 'in' companies count in the significant and Emerging lists.
A = "agent R0 quote (company's own text)"
DEC = {
 # --- newly significant (R0 in) ---
 "Syntekabio": ("in", A + "; was 'unverified' in an earlier step", "S4", "", False, "KOSDAQ 2019-12-17; no trial found"),
 "Veritas In Silico": ("in", A + " (wording from a 2026 platform rename; earlier text not opened)", "S4", "E1", False,
                       "TSE Growth 130A, 2024-02; Takeda research agreement 2023-06 (terms not disclosed; ended 2026-04 per agent)"),
 "Rakovina Therapeutics": ("in", A, "S4", "", False, "TSX Venture RKV, 2021-04-01; preclinical"),
 "Cellarity": ("in", "an earlier step R0", "S3", "E2 E3", False, "S3 274 as of 2022-10-04 (company); founded 2017; CLY-124 Phase 1 2025"),
 "NewLimit": ("in", A, "S3", "E3", True, "S3 682.2 from dated rounds (seed not found); founded 2021 (month not given); first Form D sale 2023-05-08"),
 "Seismic Therapeutic": ("in", A, "S3", "E2 E3", True, "S3 222 as of 2023-12-04 (company); launch financing 2022-02-09"),
 "Basecamp Research": ("in", A, "S3", "E3", None, "S3 220 = sum of Series A 20, B 60, C 140 (seed not found)"),
 # --- in, not significant ---
 "Outpace Bio": ("in", A, "", "E2 E3", None, "S3 'approximately $200 million' (company): at the threshold, not counted; sensitivity"),
 "Orbis Medicines": ("in", A, "", "E3", True, "EUR 26m seed in 2024 is the first disclosed financing; Series A EUR 90m 2025-01-06; S3 EUR 116m"),
 "BioGeometry": ("in", A + " (Chinese release)", "", "", None, "Series A and A+ together over USD 100m; single round not stated"),
 "StoneWise": ("in", A + "; was 'unverified'", "", "E2", False, "founded 2018 (news); Series B and B+ together USD 100m (2021-04, split not stated)"),
 "Deep Apple Therapeutics": ("in", A + "; was 'unverified'", "", "E1", True, "incorporated 2021; first Form D sale 2021-12-06; Novo Nordisk collaboration 2025-06-11"),
 "Drug Farm": ("in", A + " (undated current site); was 'unverified'", "", "E2", None, "DF-003 Phase 1 2023-09-15 and DF-006 Phase 1 by 2023-09-26 enter the cohort (2023 releases tie the platform to AI)"),
 "Fauna Bio": ("in", A + "; was 'unverified'", "", "E1", False, "USD 9m seed 2021-09-21 opened (earlier seed in search results only); Lilly up to USD 494m"),
 "Genetic Leap": ("in", A + "; was 'unverified'", "", "E1", None, "founding date not verified; Lilly up to USD 409m"),
 "Helixon": ("in", "news wording (company site unreachable); was 'unverified'", "", "E3", None,
             "founded 2021-06 (news); Series A about CNY 500m 2022-06; the report names earlier angel investors, date unknown"),
 "Orakl Oncology": ("in", A + "; was 'unverified'", "", "", True, "registered 2023-01-25; EUR 3m seed"),
 "Receptor.AI": ("in", A + "; was 'unverified'", "", "", None, ""),
 "VantAI": ("in", A + "; was 'unverified'", "", "E3", None, "now Proxima; incorporated over five years before 2026; USD 80m seed 2026"),
 # --- founding dates resolved for an earlier step 'in' companies ---
 "AI Proteins": ("in", "an earlier step R0", "", "E1", True, "Form D: incorporated 2021, first sale 2022-01-11; BMS deal 2024-12-03"),
 "Variational AI": ("in", "an earlier step R0", "", "E1", True, "incorporated 2019-08-29 (BC registry); first disclosed financing announced 2021-11-17, the cut-off day itself; Merck deal 2025-09-23"),
 "Accutar Biotechnology": ("in", "an earlier step R0", "", "E2", False, "Form D: incorporated 2015"),
 "Inceptive": ("in", "an earlier step R0", "", "E3", None, "Form D: incorporated 2021 (month not given); 2021 financing implied by news"),
 "Terray Therapeutics": ("in", "an earlier step R0", "", "E1 E3", None, "founded 2018 (news); seed undated"),
 "Elsie Biotechnologies": ("in", "an earlier step R0", "", "E1", None, "founding date not found in an allowed source"),
 # --- other classes (out of headline counts; criteria shown for sensitivity) ---
 "AstralBio": ("borderline", A, "", "", True, "incorporated 2023"),
 "Sail Biomedicines": ("borderline", "news paraphrase only; was 'unverified'", "S1", "", None, "J&J upfront 785 an earlier step"),
 "Rgenta Therapeutics": ("out", "no AI wording on own pages; was 'unverified'", "", "", False, ""),
 "Matchpoint Therapeutics": ("borderline", A, "S1 S3", "", None, "Novartis upfront 60; 70 + 150"),
 "Dewpoint Therapeutics": ("borderline", A, "S3", "E1", False, "Form D sum 304.3"),
 "Treeline Biosciences": ("borderline", A, "S3", "", None, "Form D sum 1,094.8"),
 "TRIANA Biomedicines": ("borderline", A, "S3", "", None, "230"),
 "Neumora": ("borderline", A, "S3 S4", "", False, "listed NMRA"),
 "LifeMine": ("borderline", A, "", "E3", None, "75 + 188; company total not opened"),
 "MoleculeMind": ("borderline", A, "", "", None, "over 100 cumulative"),
 "Ventus Therapeutics": ("computational", A, "S3", "", None, "Series B 100, Series C 140"),
 "Tangram Therapeutics": ("borderline", "filing says 'computational power'; site heading 'AI drug discovery'", "S4", "", False, "AIM ETX until 2024-05-09; first trial 2026-03-03"),
 "Chipscreen": ("borderline", "news only", "S4", "", False, "STAR listing date not checked against an exchange source"),
 "Nxera Pharma": ("borderline", A, "S4", "", False, "TSE Prime 4565"),
 "PRISM BioLab": ("borderline", A, "S4", "", False, "TSE Growth 206A"),
 "Oncodesign Precision Medicine": ("borderline", A, "S4", "", False, "Euronext Access+ 2022-09-26"),
 "Poolbeg Pharma": ("borderline", A, "S4", "", False, "AIM POLB; listing date not confirmed"),
 "Pharnext": ("indication", A, "S2 S4", "", False, "PXT3003 (combination of existing drugs) Phase 3 NCT04762758; not a new molecule"),
 "Zymeworks": ("computational", A, "S4", "", False, "TSX until 2019-10-01"),
 "BioAge Labs": ("out", "prospectus has no AI or ML wording", "", "", False, ""),
 "DP Technology": ("out", "general AI-for-science supplier", "", "", False, ""),
 "Zephyr AI": ("out", A, "", "", False, ""),
 "HitGen": ("out", "contract research", "", "", False, ""),
 "FRONTEO": ("out", "general AI software", "", "", False, ""),
 "Redwood AI Corp.": ("out", "AI chemistry software", "", "", False, ""),
 "Evotec": ("out", "contract research", "", "", False, ""),
 "Orbital Therapeutics": ("borderline", "an earlier step R0", "S3", "E3", True, "acquired by BMS for USD 1.5bn (announced 2025-10-10); acquisition is not counted as an S1 deal"),
 "Lila Sciences": ("borderline", "an earlier step R0", "S3", "E3", True, "S3 550 as of 2025-10-15"),
}

# an earlier step significant list ("in" + Rule 1) and emerging list
sig011 = {c for c, r in old.items() if r["r0"] == "in" and r["significant_criteria"]}
assert len(sig011) == 45, len(sig011)
em011 = {c for c, r in old.items() if r["r0"] == "in" and not r["significant_criteria"] and r["emerging_criteria"]
         and r["founded_or_first_funded_after_2021_11_17"] == "True"}
assert em011 == {"Charm Therapeutics", "Aureka Biotechnologies", "Noetik"}, em011


def evidence(c, crits):
    out = []
    for k in crits + ["R0", "FOUNDED", "FIRST_FUNDING"]:
        for e in ev.get((c, k), []):
            out.append(f'{k}: {e["value"]} | {e["source_url"]} | "{e["quote"][:200]}"')
    return " || ".join(out)


rows = []
for c, (r0, basis, s, e, elig, note) in DEC.items():
    rows.append(dict(company=c, new_in_013=c not in old, r0_011=old.get(c, {}).get("r0", ""), r0=r0, r0_basis=basis,
                     significant_criteria=s, emerging_criteria=e, founded_or_first_funded_after_2021_11_17=elig,
                     note=note, evidence=evidence(c, (s + " " + e).split())))
with open(f"{D}/companies_013.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

new_sig = sorted(c for c, d in DEC.items() if d[0] == "in" and d[2] and c not in sig011)
sig = sorted(sig011 | set(new_sig))
with open(f"{D}/significant_013.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["company", "criteria", "source"])
    for c in sig:
        w.writerow([c, DEC[c][2] if c in DEC else old[c]["significant_criteria"], "an earlier step" if c in new_sig else "an earlier step"])

# Emerging list: rank by number of criteria met, then latest qualifying evidence (newest first), then name.
LATEST = {"Charm Therapeutics": "2026-09-28", "Aureka Biotechnologies": "2026-08", "Noetik": "2026-01-08",
          "Deep Apple Therapeutics": "2025-06-11", "Variational AI": "2025-09-23", "AI Proteins": "2024-12-03",
          "Orbis Medicines": "2025-01-06"}
CRIT = {"Charm Therapeutics": "E2 E3", "Aureka Biotechnologies": "E3", "Noetik": "E1"}
new_em = sorted(c for c, d in DEC.items() if d[0] == "in" and not d[2] and d[3] and d[4] is True and c not in sig)
for c in new_em: CRIT[c] = DEC[c][3]
em = sorted(set(CRIT), key=lambda c: (-len(CRIT[c].split()), "".join(chr(255 - ord(x)) for x in LATEST[c]), c))
assert len(em) <= 15
with open(f"{D}/emerging_013.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["rank", "company", "criteria", "latest_evidence", "added"])
    for i, c in enumerate(em, 1):
        w.writerow([i, c, CRIT[c], LATEST[c], "2026-11-17 an earlier step" if c in em011 else "2026-11-17 an earlier step"])
with open(f"{D}/emerging_log_013.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "company", "action", "reason"])
    for c in new_em: w.writerow(["2026-11-17", c, "added an earlier step", CRIT[c]])
    for c in ("NewLimit", "Seismic Therapeutic"):
        w.writerow(["2026-11-17", c, "significant at entry (not listed as emerging)", DEC[c][2]])

# M2 (cohort entry) and M1 (Phase 3 / approved): one row per company checked this cycle.
m2 = [dict(company="Drug Farm", candidate="DF-003; DF-006", first_trial="2023-09-15 (NCT05997641); DF-006 Phase 1 Part 3 dosed by 2023-09-26 (ACTRN12621000592842)",
           ai_document_2019_2023="releases of 2023-09-19 and 2023-09-26: 'IDInVivo platform combines breakthrough technologies in genetics and AI'",
           enters_cohort=True, reason="platform tier; both active (see cohort_013.py). Corrected after the citation check: the agent had recorded no AI wording"),
      dict(company="Pharnext", candidate="PXT3003", first_trial="Phase 3 NCT04762758 started 2021-03-30",
           ai_document_2019_2023="", enters_cohort=False, reason="R0 'indication': combination of existing drugs; not a new molecule (M1 not met)")]
for c, d in DEC.items():
    if d[0] == "in" and c not in ("Drug Farm",):
        lines = ev.get((c, "M2"), []) + [e for e in ev.get((c, "NOTE"), []) if "M2" in e["value"]]
        if lines:
            m2.append(dict(company=c, candidate="", first_trial="", ai_document_2019_2023="", enters_cohort=False,
                           reason="; ".join(x["value"] for x in lines)[:200]))
with open(f"{D}/m2_013.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(m2[0])); w.writeheader(); w.writerows(m2)

S = {
    "as_of": "2026-11-17",
    "companies_decided_013": len(DEC), "new_companies_013": sum(c not in old for c in DEC),
    "by_r0_013": collections.Counter(d[0] for d in DEC.values()),
    "unverified_resolved": {c: DEC[c][0] for c in DEC if old.get(c, {}).get("r0") == "unverified"},
    "significant_011": len(sig011), "significant_new": new_sig, "significant_013": len(sig),
    "significant_by_criterion_new": collections.Counter(k for c in new_sig for k in DEC[c][2].split()),
    "significant_sensitivity": {"Outpace Bio at 'approximately $200 million' counted": len(sig) + 1},
    "significant_other_classes_new": {c: f"{d[0]}: {d[2]}" for c, d in DEC.items() if d[0] != "in" and d[2]},
    "emerging_013": em, "emerging_added": new_em,
    "emerging_cannot_be_assessed": sorted(c for c, d in DEC.items() if d[0] == "in" and not d[2] and d[3] and d[4] is None),
    "emerging_sensitivity": {"Helixon": "cannot be assessed: the 2022-06 Series A report names earlier angel investors (date unknown)",
                             "Variational AI if the cut-off day itself is excluded": "leaves"},
    "M1_new": 0, "M2_new_cohort_candidates": 2,
    "M2_note": "Drug Farm DF-003 and DF-006 enter (platform; 2023 releases tie the IDInVivo platform to AI); no other new 'in' company had a trial by 2023-12-31; cohort 30 -> 32 (cohort_013.json)",
    "M3_new": 0, "M3_note": "Parabilis-Regeneron (upfront 50) is already in analysis/008/deals_combined.csv as platform-named; no new explicit-AI deal with Amgen, Teva, CSL or Regeneron",
    "M4_new": "not assessed (Syntekabio, Veritas In Silico, Rakovina revenue not opened)",
}
json.dump(S, open(f"{D}/summary.json", "w"), indent=1, default=dict, ensure_ascii=False)
print(json.dumps(S, indent=1, default=dict, ensure_ascii=False))
print(open(f"{D}/emerging_013.csv").read())
