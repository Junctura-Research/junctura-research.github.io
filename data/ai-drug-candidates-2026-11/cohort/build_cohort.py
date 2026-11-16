"""Cohort: hand-built cohort table -> cohort.csv.

Each row: one candidate that was in a clinical trial by 2023-12-31, with the dated document that ties it
to AI (entry_source, published 2019-01-01..2024-04-30), and its status as of 2026-11-16 (outcome_source).
Quotes are copied from the source. Tiers and outcome classes are defined in ../README.md.
"""
import csv

EX22 = "https://www.sec.gov/Archives/edgar/data/1865408/000186540823000011/exai-20221231.htm"
EX23 = "https://www.sec.gov/Archives/edgar/data/1865408/000186540824000018/exai-20231231.htm"
EXF1 = "https://www.sec.gov/Archives/edgar/data/1865408/000110465921114491/tm2119783-5_f1.htm"
SUMI21 = "https://www.sumitomo-pharma.com/ir/library/financial_results_summary/assets/pdf/ebr20210128.2.pdf"
SUMI22 = "https://www.sumitomo-pharma.com/ir/library/financial_results_summary/assets/pdf/ebr20220131.2.pdf"
SUMI23 = "https://www.sumitomo-pharma.com/ir/library/financial_results_summary/assets/pdf/ebr20231031.2.pdf"
SUMI26 = "https://d145j8vag8dpyh.cloudfront.net/rd/pipeline_new-medicine/pipeline_profile.html"
RX22 = "https://www.sec.gov/Archives/edgar/data/1601830/000160183023000010/rxrx-20221231.htm"
RX25 = "https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm"
SD23 = "https://www.sec.gov/Archives/edgar/data/1490978/000149097824000018/sdgr-20231231.htm"
SD25 = "https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm"
MR21 = "https://www.sec.gov/Archives/edgar/data/1826457/000119312521182268/d47776ds1.htm"
MR25 = "https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm"
NX20 = "https://www.sec.gov/Archives/edgar/data/1549595/000156459021006071/nrix-10k_20201130.htm"
NX25 = "https://www.sec.gov/Archives/edgar/data/1549595/000154959526000016/nrix-20251130.htm"
EV23 = "https://www.sec.gov/Archives/edgar/data/1828253/000110465924039004/evax-20231231x20f.htm"
EV25 = "https://www.sec.gov/Archives/edgar/data/1828253/000117184326001346/evax20251231_20f.htm"
CG22 = "https://www.sec.gov/Archives/edgar/data/1119774/000117891323000772/zk2329266.htm"
CG25 = "https://www.sec.gov/Archives/edgar/data/1119774/000117891326000663/zk2634416.htm"
INS21 = "https://www.hkstp.org/park-life/news-and-events/news/insilico-medicine-initiates-first-in-human-study-of-ism001-055-a-novel-drug-discovered-using-insi"
INSP3 = "https://clinicaltrials.gov/study/NCT07687459"
BEN23 = "https://cdn.financialreports.eu/financialreports/media/filings/9192/2023/ISS/9192_iss_2023-04-05_9e70dda6-693a-4dfa-83d9-a4b8a4b48421.pdf"
BEN24 = "https://www.dutchnews.nl/businesswire/benevolentai-unaudited-preliminary-results-for-the-year-ended-31-december-2023/"
GEN24 = "https://generatebiomedicines.com/news/generatebiomedicines-fortifies-leadership-in-generative-ai"
GEN26 = "https://www.sec.gov/Archives/edgar/data/2100782/000119312526062362/ck0002100782-20260223.htm"
PB26 = "https://www.sec.gov/Archives/edgar/data/1657677/000119312526262880/ck0001657677-20260609.htm"

COLS = ["candidate", "company", "tier", "claim", "ai_step", "entry_source", "entry_quote", "outcome",
        "outcome_reason", "outcome_date", "outcome_source", "outcome_quote", "ctgov_terms", "note"]
H, T, R, I, C, N = "headline", "AI-identified target", "retro-AI", "indication", "computational", "no 2019-2023 source opened"
B = "borderline (target)"
ROWS = [
    ["EXS21546", "Exscientia (now Recursion)", H, "explicit", "molecule", EXF1,
     "We originated the first three AI-designed precision drug candidates to enter human clinical trials. Our most advanced internally developed drug candidate, EXS21546, is one of these",
     "discontinued", "not sufficiently promising (company); therapeutic index (registry)", "2023", EX23,
     "we stopped the Phase 1/2 clinical trial of EXS21546 after receiving information demonstrating that the drug candidate was not sufficiently promising to justify further clinical development",
     "EXS21546; EXS-21546", "ClinicalTrials.gov NCT05920408 why_stopped: challenge to reach suitable therapeutic index"],
    ["DSP-1181", "Sumitomo Pharma (designed with Exscientia)", H, "explicit", "molecule", SUMI21,
     "DSP-1181 is a novel compound created by Sumitomo Dainippon Pharma using Exscientia's AI technologies",
     "discontinued", "not stated by the company", "2022-01", SUMI22,
     "Listed under 'Main revisions since the announcement of October 2021' and absent from the pipeline table as of January 31, 2022",
     "DSP-1181", "Phase 1 in Japan (Sumitomo, as of 2021-01-28). Exscientia's F-1 counts it among 'the first three AI-designed precision drug candidates' but does not name it"],
    ["DSP-0038", "Sumitomo Pharma (designed with Exscientia)", H, "explicit", "molecule", SUMI22,
     "DSP-0038 is a novel compound discovered at Sumitomo Dainippon Pharma using Exscientia's AI technologies",
     "active", "", "2026-10-30", SUMI26, "Listed with planned indication Alzheimer's disease psychosis (page as of October 30, 2026; no phase stated)",
     "DSP-0038", "Sumitomo pipeline PDF as of July 31, 2025 lists DSP-0038 at Phase 1 in the U.S.: https://d145j8vag8dpyh.cloudfront.net/rd/pipeline_new-medicine/assets/pdf/epip.pdf"],
    ["DSP-2342", "Sumitomo Pharma (designed with Exscientia)", H, "explicit", "molecule", SUMI23,
     "DSP-2342 is a novel compound discovered at Sumitomo Pharma using Exscientia's AI technologies",
     "active", "", "2026-10-30", SUMI26, "Listed with planned indication TBD (page as of October 30, 2026; no phase stated)",
     "DSP-2342", "Phase 1 in the U.S. in Sumitomo's pipeline as of 2023-10-31 and as of July 31, 2025 (epip.pdf). A Phase 2 brain-imaging study (NCT07850102) is not yet recruiting"],
    ["EXS4318", "Bristol Myers Squibb (designed by Exscientia)", H, "platform", "molecule", EX22,
     "both BMS and Sanofi have in-licenced molecules we designed through our collaborations and the first molecule in-licensed from BMS is now in the clinic",
     "unknown", "", "", RX25, "Not mentioned in Recursion's 10-K for 2025; no BMS source found",
     "EXS4318; EXS-4318", "Exscientia's 10-K for 2023 lists 'BMY-licensed EXS4318' as in clinical trials"],
    ["GTAEXS617 (REC-617)", "Exscientia / GT Apeiron (now Recursion)", H, "platform", "molecule", EX22,
     "We originated the first ever AI-designed precision drug candidates to enter human clinical trials ... Two programmes, EXS21546 and GTAEXS617, are both in Phase 1/2 clinical studies",
     "active", "", "2026-02-25", RX25, "such as REC-4881 in FAP and REC-617 in advanced solid tumors", "GTAEXS617; REC-617", ""],
    ["REC-3964", "Recursion", H, "platform", "molecule", RX22,
     "REC-3964 is a new chemical entity that was identified with our brute-force approach which utilized phenomics ... Structure-activity-relationship (SAR) was driven through the Recursion OS",
     "discontinued", "strategic / portfolio", "2025-05", RX25,
     "the clinical programs REC-2282 for NF2, REC-994 for CCM, and REC-3964 for C. difficile were discontinued and/or partnering opportunities are being pursued",
     "REC-3964", "The same 10-K describes the Recursion OS in machine learning and AI terms"],
    ["SGR-1505", "Schrodinger", H, "explicit", "molecule", SD23,
     "Combining multi-parameter optimization, FEP+, and machine learning, we were able to prioritize tight-binding compounds ... enabling us to select SGR-1505 as our development candidate",
     "active", "", "2026-02-25", SD25, "We plan to progress the development of our proprietary drug discovery programs, including SGR-1505 and SGR-3515",
     "SGR-1505", ""],
    ["MRT-2359", "Monte Rosa", H, "platform", "molecule", MR21,
     "In silico ternary complex modeling and screening : A suite of proprietary AI-driven algorithms, called Rhapsody, to rapidly identify and prioritize MGDs",
     "active", "", "2026-03-17", MR25, "our clinical trials for our GSPT1-directed MGD MRT-2359", "MRT-2359", ""],
    ["NX-2127 (zelebrudomide)", "Nurix", H, "platform", "molecule", NX20,
     "We have built a suite of custom analytical tools including machine learning for interpretation and prioritization of our DEL binder outputs",
     "active", "", "2026-01-28", NX25, "Continue development of zelebrudomide through dose escalation", "NX-2127; zelebrudomide",
     "Machine learning is one named tool for hit-finding on the DEL platform (10-K filed 2021-02-16); the filing does not tie it to this candidate"],
    ["NX-1607", "Nurix", H, "platform", "molecule", NX20,
     "We have built a suite of custom analytical tools including machine learning for interpretation and prioritization of our DEL binder outputs",
     "active", "", "2026-01-28", NX25, "Listed as a clinical-stage candidate in the 10-K for fiscal 2025 (the current list)", "NX-1607",
     "As NX-2127"],
    ["NX-5948 (bexobrutideg)", "Nurix", H, "platform", "molecule", NX20,
     "We have built a suite of custom analytical tools including machine learning for interpretation and prioritization of our DEL binder outputs",
     "active", "", "2026-08-03", "https://clinicaltrials.gov/study/NCT07516093", "Study of NX-5948 Versus Pirtobrutinib in R/R CLL/SLL: Phase 3, recruiting", "NX-5948; bexobrutideg",
     "As NX-2127"],
    ["EVX-01", "Evaxion", H, "explicit", "antigen", EV23,
     "Figure 1: Our AI models and vaccine pipeline. EVX-01 EVX-01 is a novel liposomal, peptide-based cancer vaccine",
     "active", "", "2026-03-05", EV25, "EVX-01 Three-year phase 2 clinical efficacy data H2", "EVX-01",
     "AI selected the vaccine antigens; counted as in the current list"],
    ["EVX-02", "Evaxion", H, "explicit", "antigen", EV23,
     "Our additional two personalized cancer vaccines, EVX-02 and EVX-03, developed based on our PIONEER AI model, are in early clinical and late pre-clinical development",
     "superseded", "successor candidate", "2024-03-26", EV23,
     "the promising clinical, immune and safety data from the EVX-02 Phase 1/2a clinical trial together with the superior EVX-03 pre- clinical data, support moving EVX-03 into clinical development",
     "EVX-02", "Not in the 2026 milestone list of the 20-F for 2025; named there only under patents"],
    ["ISM001-055 (rentosertib)", "Insilico Medicine", H, "explicit", "target+molecule", INS21,
     "We have leveraged our end-to-end AI-powered drug discovery platform, including the usage of generative biology and generative chemistry, to discover novel biological targets and generate novel molecules with drug-like properties. ISM001-055 is the first such compound to enter the clinic",
     "active", "", "2026-11-15", INSP3, "Phase 3 trial recruiting (the current list)", "INS018_055; ISM001-055; rentosertib", ""],
    ["BEN-2293", "BenevolentAI", H, "platform", "not stated", BEN23,
     "BenevolentAI (AMS: BAI) is a leading, clinical-stage AI-enabled drug discovery and",
     "discontinued", "efficacy", "2023-05", BEN24,
     "the Company confirmed there will be no further investment in BEN-2293 following its Phase IIa study results in AD earlier in the year, where the safety and tolerability primary endpoints were successfully met but the efficacy secondary endpoints were not",
     "BEN2293; BEN-2293", "The release ties the company's platform to AI but does not say which step AI performed for this candidate"],
    ["GB-0669", "Generate Biomedicines", H, "platform", "molecule", GEN24,
     "announced key advancements across its clinical pipeline and generative AI platform, including its first patient dosed in GB-0895, progress in the phase 1 study for GB-0669",
     "discontinued", "strategic / commercial", "2026-02-23", GEN26,
     "Development of GB-0669 was subsequently paused due to changes in the commercial landscape related to PrEP agents for COVID-19",
     "GB-0669", "Entry source dated 2024-01-04 (see README: late cut-off)"],
    ["GB-0895", "Generate Biomedicines", H, "platform", "molecule", GEN24,
     "announced key advancements across its clinical pipeline and generative AI platform, including its first patient dosed in GB-0895",
     "active", "", "2026-02-23", GEN26, "Two Phase 3 trials in severe asthma (the current list)", "GB-0895",
     "Entry source dated 2024-01-04 (see README: late cut-off)"],
    ["BEN-8744", "BenevolentAI", T, "platform", "target", BEN24,
     "its discovery validates the ability of the Benevolent PlatformTM to identify novel targets for evaluation",
     "unknown", "", "2024-03-13", BEN24,
     "BEN-8744 progressed into a Phase Ia clinical study in August 2023 and top-line data is expected in Q1 2024 (no later status found in sources opened)",
     "BEN8744; BEN-8744", "Current-list source: PharmaTimes, 31 Aug 2023, 'Our AI powered drug-discovery platform identified PDE10 as a novel target for UC'"],
    ["COM701", "Compugen", B, "borderline", "target", CG22,
     "Our broadly applicable predictive drug target discovery capabilities employ a suite of cloud-based computational solutions and purpose-built algorithms to sort through both public and proprietary datasets encompassing genomics, single cell and spatial transcriptomics, proteomics and machine learning based analysis of IHC images",
     "active", "", "2026-03-02", CG25, "Listed among clinical-stage programs (the current list)", "COM701",
     "Machine learning is one ingredient of the target-discovery platform (20-F filed 2023-02-28); the 20-F filed 2020-02-24 describes the platform as computational without AI. Target-only and borderline"],
    ["COM902", "Compugen", B, "borderline", "target", CG22,
     "Our broadly applicable predictive drug target discovery capabilities employ a suite of cloud-based computational solutions and purpose-built algorithms to sort through both public and proprietary datasets encompassing genomics, single cell and spatial transcriptomics, proteomics and machine learning based analysis of IHC images",
     "active", "", "2026-03-02", CG25, "Listed among clinical-stage programs (the current list)", "COM902", "As COM701"],
    ["FOG-001 (zolucatetide)", "Parabilis Medicines (formerly FogPharma)", R, "AI claim only after 2023", "molecule", PB26,
     "Our Helicon discovery platform integrates advanced artificial intelligence (\"AI\")- and physics-based computational modeling",
     "active", "", "2026-06-09", PB26, "Phase 1/2 recruiting (the current list)", "FOG-001; zolucatetide",
     "The June 2023 first-patient release (Business Wire) returned HTTP 403 and was not read; search snippets describe Helicon peptides without AI. Labeled retro-AI pending a readable 2023 source"],
    ["REC-994", "Recursion", I, "platform", "indication", RX22, "", "discontinued", "strategic / portfolio", "2025-05", RX25,
     "the clinical programs REC-2282 for NF2, REC-994 for CCM, and REC-3964 for C. difficile were discontinued", "REC-994", "Existing molecule (tempol)"],
    ["REC-2282", "Recursion", I, "platform", "indication", RX22, "", "discontinued", "strategic / portfolio", "2025-05", RX25,
     "the clinical programs REC-2282 for NF2, REC-994 for CCM, and REC-3964 for C. difficile were discontinued", "REC-2282", "Existing molecule (AR-42)"],
    ["REC-4881", "Recursion", I, "platform", "indication", RX22, "", "active", "", "2026-02-25", RX25,
     "such as REC-4881 in FAP and REC-617 in advanced solid tumors", "REC-4881", "Existing molecule (TAK-733)"],
    ["SGR-2921", "Schrodinger", C, "computational", "molecule", SD23, "", "discontinued", "company decision", "2025-08",
     "https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm", "Discontinued (the current list)", "SGR-2921", ""],
    ["ISM5411", "Insilico Medicine", N, "", "", "", "", "active", "", "", "", "Phase 2 (the current list)", "ISM5411",
     "Phase 1 began 2023-11; no 2019-2023 Insilico document naming it was opened"],
]


def main():
    w = csv.writer(open("cohort.csv", "w", newline=""))
    w.writerow(COLS)
    for r in ROWS:
        assert len(r) == len(COLS), r[0]
        w.writerow(r)


if __name__ == "__main__":
    main()
