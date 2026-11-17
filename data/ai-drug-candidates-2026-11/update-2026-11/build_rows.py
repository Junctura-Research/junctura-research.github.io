"""Cohort repair: hand-built rows for the candidates tested this cycle (the original cohort columns plus quote files).

Usage: python build_rows.py -> new_rows.csv
Every quote is checked verbatim (after collapsing whitespace) against the saved text named in *_file by
check_quotes.py. Paths are relative to this folder; the saved source texts are not included. Rules: fixed before outcomes were traced (see ../README.md).
"""
import csv

S11 = "sources/"
S12 = "raw/sources/"
ABCL_S1 = "https://www.sec.gov/Archives/edgar/data/1703057/000119312520302988/d29983ds1a.htm"
ABCL_10K21 = "https://www.sec.gov/Archives/edgar/data/1703057/000156459022007077/abcl-10k_20211231.htm"
ABCL_10K22 = "https://www.sec.gov/Archives/edgar/data/1703057/000156459023002128/abcl-10k_20221231.htm"
ABCL_10K25 = "https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm"
ADAG_20F22 = "https://www.sec.gov/Archives/edgar/data/1818838/000110465923052043/adag-20221231x20f.htm"
ADAG_20F25 = "https://www.sec.gov/Archives/edgar/data/1818838/000110465926038612/adag-20251231x20f.htm"
ADAG_20F24 = "https://www.sec.gov/Archives/edgar/data/1818838/000141057825000419/adag-20241231x20f.htm"
FDA_ARCH = "https://www.fda.gov/emergency-preparedness-and-response/mcm-legal-regulatory-and-policy-framework/emergency-use-authorization-archived-information"
MR23 = "https://www.biospace.com/mindrank-announces-first-in-human-phase-1-study-of-mdr-001-in-china"
ACC21 = ("https://www.biospace.com/accutar-biotechnology-announces-first-patient-dosed-with-ac0682-in-phase-1-study-in-patients-"
         "with-er-positive-her2-negative-locally-advanced-or-metastatic-breast-cancer")
ACC_PIPE = "https://www.accutarbio.com/workflow"
AUL23 = ("https://www.biospace.com/aulos-bioscience-advances-au-007-to-phase-2-portion-of-phase-1-2-study-evaluating-"
         "computationally-designed-il-2-antibody-for-treatment-of-solid-tumors")
AUL_PIPE = "https://aulosbio.com/our-pipeline/"
MR_PIPE = "https://www.mindrank.ai/en/pipeline"
PH21 = "https://www.newswire.co.kr/newsRead.php?no=921524"
PH_IR26 = "https://file.irgo.co.kr/data/BOARD/ATTACH_PDF/UURVMU45Q6JKQCH8B37ZXG9ARQUVC2RX2026414141647.pdf"

ADAG_AI = "We are combining computational biology and artificial intelligence to design novel antibodies"
ADAG_PLAT = "Our DPL platform is empowered by our computational platform, artificial intelligence and three innovative technologies: NEObody, SAFEbody, and POWERbody."

R = [
    # candidate, company, tier, claim, ai_step, origin (m2 = the coverage audit list; completeness = found this cycle)
    dict(candidate="MDR-001", company="MindRank AI", tier="headline", claim="explicit", ai_step="molecule", origin="m2",
         entry_source=MR23, entry_file=S11 + "clinical_mindrank_2023.txt", entry_date="2023-06-14",
         entry_quote="MDR-001 is a novel, β-arrestin 2 selective, orally bioavailable small-molecule GLP-1 RA discovered using MindRank's proprietary AI platform, Molecule Pro.",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=MR_PIPE, outcome_file=S12 + "mindrank_pipeline.txt",
         outcome_quote="Pipeline Powered by Molecule Pro ™ Program Target Indication Discovery Optimization IND-enabling Phase I Phase II Phase III Partner MDR-001 GLP-1RA Obesity",
         ctgov_terms="MDR-001; MDR001",
         note="Company says Phase 3 has started (home page: 'It has entered Phase III clinical trials'; release 2026-01-06). ClinicalTrials.gov NCT07274137 (Phase 3) is NOT_YET_RECRUITING with estimated start 2026-02; the latest started registered trial is Phase 2 NCT06606483 (start 2024-09-23). China's drug trial registry (chinadrugtrials.org.cn) returned a script challenge page (HTTP 202) with no registry content; recorded as unavailable."),
    dict(candidate="AC0682", company="Accutar Biotechnology", tier="headline", claim="explicit", ai_step="molecule", origin="m2",
         entry_source=ACC21, entry_file=S11 + "clinical_accutar_2021.txt", entry_date="2021-12-01",
         entry_quote="it marks the first program from our AI-enabled drug discovery platform and our chimeric degrader portfolio to enter the clinic",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ACC_PIPE, outcome_file=S12 + "accutar_pipeline_workflow.txt",
         outcome_quote="AC0682 ER Degrader Breast Cancer Potential best-in-class",
         ctgov_terms="AC0682; AC682",
         note="Both registered trials TERMINATED; why stopped: 'Voluntarily terminate the study since the sponsor's development strategy was adj[usted]'. The company's undated pipeline page still lists it, so the fixed rule gives 'active'. Sensitivity: discontinued."),
    dict(candidate="AC176", company="Accutar Biotechnology", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ACC21, entry_file=S11 + "clinical_accutar_2021.txt", entry_date="2021-12-01",
         entry_quote="Accutar is a clinical stage biotech company focused on AI-enabled drug discovery, and its application to the discovery and development of clinically differentiated medicines.",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ACC_PIPE, outcome_file=S12 + "accutar_pipeline_workflow.txt",
         outcome_quote="AC0176 AR Degrader Prostate Cancer",
         ctgov_terms="AC176; AC0176",
         note="Both registered trials TERMINATED; why stopped: 'Subject benefit-risk ratio changes, sponsor decides to voluntarily terminate stu[dy]'. Undated pipeline page still lists it ('active' under the fixed rule). Sensitivity: discontinued."),
    dict(candidate="AC699", company="Accutar Biotechnology", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ACC21, entry_file=S11 + "clinical_accutar_2021.txt", entry_date="2021-12-01",
         entry_quote="Accutar is a clinical stage biotech company focused on AI-enabled drug discovery, and its application to the discovery and development of clinically differentiated medicines.",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ACC_PIPE, outcome_file=S12 + "accutar_pipeline_workflow.txt",
         outcome_quote="AC0699 ER Degrader Breast Cancer", ctgov_terms="AC699; AC0699",
         note="Trial-entry evidence is the registry (NCT05654532, start 2022-12-29). AI tie is company-level."),
    dict(candidate="AC676", company="Accutar Biotechnology", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ACC21, entry_file=S11 + "clinical_accutar_2021.txt", entry_date="2021-12-01",
         entry_quote="Accutar is a clinical stage biotech company focused on AI-enabled drug discovery, and its application to the discovery and development of clinically differentiated medicines.",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ACC_PIPE, outcome_file=S12 + "accutar_pipeline_workflow.txt",
         outcome_quote="AC0676 BTK Degrader (WT & C481S)", ctgov_terms="AC676; AC0676",
         note="Trial-entry evidence is the registry (NCT05780034, start 2023-06-20). AI tie is company-level."),
    dict(candidate="AU-007 (imneskibart)", company="Aulos Bioscience (designed by Biolojic Design)", tier="headline", claim="explicit", ai_step="molecule", origin="m2",
         entry_source=AUL23, entry_file=S11 + "clinical_aulos_2023.txt", entry_date="2023-12-18",
         entry_quote="AU-007 is a human IgG1 monoclonal antibody designed using artificial intelligence",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=AUL_PIPE, outcome_file=S12 + "aulos_pipeline2.txt",
         outcome_quote="Our lead asset, imneskibart (AU-007)", ctgov_terms="AU-007; AU007",
         note="Registry: NCT05267626 Phase 1/2, RECRUITING."),
    dict(candidate="ADG126 (muzastotug)", company="Adagene", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote=ADAG_AI + " | " + ADAG_PLAT,
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="particularly our lead product candidate ADG126 (muzastotug), which is still in clinical stage",
         ctgov_terms="ADG126; muzastotug", note="ADG126 is a SAFEbody, one of the three technologies the 20-F says the AI-empowered DPL platform includes."),
    dict(candidate="ADG106", company="Adagene", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote=ADAG_AI + " | " + ADAG_PLAT,
         outcome="discontinued", outcome_reason="not stated by the company (deprioritized)", outcome_date="by 2025-03-24",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="ADG106 has been deprioritized.", ctgov_terms="ADG106",
         note="Wording first appears in the 20-F for 2024 (filed 2025-03-24), not in the one filed 2024-03-29. Investigator-led trials at National University Hospital Singapore are still listed RECRUITING / ACTIVE_NOT_RECRUITING; the company statement is given precedence (outcome precedence rule). Sensitivity: active."),
    dict(candidate="ADG116", company="Adagene", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote=ADAG_AI + " | " + ADAG_PLAT,
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="ADG116 is clinically active and ready to advance into further clinical development as resources allow.",
         ctgov_terms="ADG116", note="In the latest pipeline, but no trial of it is recruiting; 'as resources allow' wording. Weakest 'active' call."),
    dict(candidate="bamlanivimab (LY-CoV555)", company="AbCellera (developed by Eli Lilly)", tier="headline", claim="platform", ai_step="not stated", origin="m2",
         entry_source=ABCL_S1, entry_file=S11 + "clinical_abcellera_s1_2020.txt", entry_date="2020-11-24",
         entry_quote="The Company’s full-stack, AI-powered drug discovery platform searches and analyzes the database of natural immune systems to find antibodies that can be developed as drugs. | we applied our technology stack to co-develop LY-CoV555,",
         outcome="discontinued", outcome_reason="authorization withdrawn: resistant variants; partner withdrew the product", outcome_date="2023-12-14",
         outcome_source=FDA_ARCH + " ; " + ABCL_10K25, outcome_file=S12 + "fda_eua_archived.txt | " + S12 + "edgar_AbCellera_10-K_2026-02-24.txt",
         outcome_quote="Lilly does not intend to offer this product in the United States anymore | 2 Expect no further progress/no ultimate approval.",
         ctgov_terms="bamlanivimab; LY-CoV555; LY3819253",
         note="EUA for bamlanivimab alone issued 2020-11-09 and revoked 2021-04-16 for resistant variants (FDA release); EUA with etesevimab issued 2021-02-09, revoked 2023-12-14 at Lilly's request of 2023-10-23 (FDA). Never approved. AbCellera's FY2025 10-K table still reads 'Marketed, EUA', with footnote 2. Sensitivity: active (literal table entry)."),
    dict(candidate="bebtelovimab (LY-CoV1404)", company="AbCellera (developed by Eli Lilly)", tier="headline", claim="platform", ai_step="not stated", origin="completeness",
         entry_source=ABCL_10K21, entry_file=S12 + "edgar_AbCellera_10-K_2022-02-25.txt", entry_date="2022-02-25",
         entry_quote="Our full-stack, artificial intelligence-, or AI, powered antibody discovery platform | we deployed our platform to identify bebtelovimab (also known as LY-CoV1404)",
         outcome="discontinued", outcome_reason="authorization withdrawn at partner's request (lots expired; resistant variants)", outcome_date="2024-12-13",
         outcome_source=FDA_ARCH + " ; " + ABCL_10K25, outcome_file=S12 + "fda_eua_archived.txt | " + S12 + "edgar_AbCellera_10-K_2026-02-24.txt",
         outcome_quote="On December 5, 2024, Lilly requested that the U.S. Food and Drug Administration revoke the Emergency Use Authorization for bebtelovimab since all lots of bebtelovimab manufactured and labeled for use under EUA 111 have expired. | 2 Expect no further progress/no ultimate approval.",
         ctgov_terms="bebtelovimab; LY-CoV1404; LY3853113",
         note="EUA issued 2022-02-11, revoked 2024-12-13 (FDA). Lilly-run trials: Phase 2 (BLAZE-4) and the Phase 2/3 BLAZE-1 record. The highest label, Phase 4, comes from an investigator-led comparison of authorized antibodies (NCT04790786, UPMC, terminated). AbCellera's FY2021 10-K table gave 'Phase 2'."),
    dict(candidate="TAK-920/DNL919", company="AbCellera (developed by Denali Therapeutics with Takeda)", tier="headline", claim="platform", ai_step="not stated", origin="completeness",
         entry_source=ABCL_10K22, entry_file=S12 + "edgar_AbCellera_10-K_2023-02-21.txt", entry_date="2023-02-21",
         entry_quote="We currently use AI and machine learning methods extensively in our engine | TAK-920/DNL919 Phase 1 Denali Therapeutics Inc. Neurology - Alzheimer's Disease AbCellera Partner-initiated Discovery",
         outcome="discontinued", outcome_reason="not stated by the company", outcome_date="by 2026-02-24",
         outcome_source=ABCL_10K25, outcome_file=S12 + "edgar_AbCellera_10-K_2026-02-24.txt",
         outcome_quote="TAK-920/DNL919 Phase 1 2 Denali Therapeutics Inc. | 2 Expect no further progress/no ultimate approval.",
         ctgov_terms="DNL919; TAK-920",
         note="Partner-initiated program discovered with AbCellera's engine; Phase 1 NCT05450549 (Denali), start 2022-07-14, COMPLETED. Outcome rests on AbCellera's footnote; no Denali statement opened."),
    dict(candidate="ADG206", company="Adagene", tier="headline", claim="platform", ai_step="not stated", origin="completeness",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote=ADAG_AI + " | " + ADAG_PLAT + " | our two anti-CD137 antibodies, ADG106 and ADG206, which are in clinical development",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="Other than our wholly-owned product candidates (ADG126, ADG116, ADG206 and ADG106)",
         ctgov_terms="ADG206",
         note="Phase 1 NCT05614258 (Adagene), start 2023-02-13, ACTIVE_NOT_RECRUITING. A POWERbody. An investigator-initiated study in Singapore 'has been deprioritized and terminated' (FY2025 20-F); the candidate itself stays in the list of wholly owned candidates."),
    dict(candidate="PHI-101 (lasmotinib)", company="Pharos iBio", tier="headline", claim="explicit", ai_step="molecule", origin="m2 (provisional in the coverage audit)",
         entry_source=PH21, entry_file=S12 + "pharos_newswire_2021.txt", entry_date="2021-04-14",
         entry_quote="회사가 개발 중인 글로벌 혁신신약 PHI-101은 2016년 ‘케미버스’의 심장독성 예측 모델을 통한 후보물질 최적화 기술 기반으로 공동연구개발을 통해 발굴한 차세대 FLT3 돌연변이 표적항암제다. | AI 기반 신약개발 플랫폼 ‘케미버스(Chemiverse)’",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=PH_IR26, outcome_file=S12 + "pharos_ir_2026.txt",
         outcome_quote="라스모티닙(PHI-101) (급성 골수성 백혈병, 재발성 난소암)", ctgov_terms="PHI-101; PHI101",
         note="Company release in Korean (agent's translation: PHI-101 'was discovered in 2016 through joint research based on candidate optimization using Chemiverse's cardiotoxicity prediction model'; Chemiverse is 'an AI-based drug development platform'). The same release says the ovarian and breast cancer indications came from Chemiverse drug repurposing (indication-type use, not counted). 2026 IR deck: AML Phase 1 completed and CSR received. A 2022 peer-reviewed protocol funded by Pharos (no company authors) also says PHI-101 was 'identified by artificial intelligence'."),
    # Other tiers (outside the headline)
    dict(candidate="ADG104", company="Adagene (out-licensed to Sanjin, Greater China)", tier="borderline (company-level only)", claim="borderline", ai_step="not stated", origin="completeness",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote="out-licensed the Greater China rights of ADG104, an anti-PD-L1 mAb currently in Phase 2 clinical development, to Sanjin",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="This program is currently in Phase 2 clinical development.", ctgov_terms="ADG104",
         note="No 2019-2023 document names a platform technology (NEObody, SAFEbody, POWERbody) for it; licensed out in 2018. Kept out of the headline."),
    dict(candidate="ADG125", company="Adagene (out-licensed to Dragon Boat, Greater China)", tier="borderline (company-level only)", claim="borderline", ai_step="not stated", origin="completeness",
         entry_source=ADAG_20F22, entry_file=S12 + "edgar_Adagene_20-F_2023-04-28.txt", entry_date="2023-04-28",
         entry_quote="During 2021, Dragon Boat advanced this candidate, an anti-CSF-1R monoclonal antibody (ADG125/BC006) into phase 1 development.",
         outcome="active", outcome_reason="", outcome_date="",
         outcome_source=ADAG_20F25, outcome_file=S12 + "edgar_Adagene_20-F_2026-04-01.txt",
         outcome_quote="our outlicensed product candidates, ADG104 and ADG125", ctgov_terms="ADG125; BC006",
         note="As ADG104: no named platform technology. Kept out of the headline."),
]

# Company-stated phase where ClinicalTrials.gov has no started registration (the original cohort DOC_PHASE convention)
DOC_PHASE = {"ADG104": "Phase 2", "ADG125": "Phase 1"}

if __name__ == "__main__":
    cols = list(R[0].keys())
    for r in R:
        r.setdefault("doc_phase", DOC_PHASE.get(r["candidate"], ""))
    cols = list(R[0].keys())
    with open("new_rows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R)
    print(len(R), "rows")
