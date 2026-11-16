"""Current list: writes candidates.csv, the hand-built candidate list.

Each row was set by reading the cited source (SEC filing on EDGAR, peer-reviewed paper, or company
press release). Labels (fixed before the search):
  explicit     = the source names this candidate as discovered/designed/optimized with AI or ML
  platform     = candidate came from a platform the company describes as AI-based; source does not
                 tie this candidate to the AI step
  computational= computational design not stated as AI (excluded from the AI count)
  indication   = AI picked a new use for an existing molecule (excluded: the molecule was not found by AI)
  borderline   = filing names ML only as one ingredient of a broader platform (excluded; listed for review)
ai_step: molecule (design/optimization), target, antigen (vaccine antigen selection), indication.
"""
import csv

E = "https://www.sec.gov/Archives/edgar/data/"
RX = E + "1601830/000160183026000039/rxrx-20251231.htm"
EX = E + "1865408/000186540824000018/exai-20231231.htm"
SD = E + "1490978/000149097826000010/sdgr-20251231.htm"
IA = E + "1997038/000119312526417416/iam-20261008.htm"
GE = E + "2100782/000119312526062362/ck0002100782-20260223.htm"
AB = E + "1672688/000167268826000068/absi-20251231.htm"
EV = E + "1828253/000117184326001346/evax20251231_20f.htm"
NX = E + "1549595/000154959526000016/nrix-20251130.htm"
CG = E + "1119774/000117891326000663/zk2634416.htm"
IB = E + "1420720/000142072026000020/ibio-20260731x10k.htm"
OD = E + "1882782/000119312526202398/odtx-20260504.htm"
EK = E + "1861123/000119312526130395/eikn_form_10-k_2025.htm"
MR = E + "1826457/000119312526109360/glue-20251231.htm"
PB = E + "1657677/000119312526262880/ck0001657677-20260609.htm"
BX = E + "1720893/000110465926036214/btai-20251231x10k.htm"
RL = E + "1812364/000119312526076739/rlay-20251231.htm"
ST = E + "1888886/000110465926020562/gpcr-20251231x10k.htm"
KY = E + "1815442/000119312526073395/kymr-20251231.htm"
KO = E + "1703647/000119312524138296/d820146ds1.htm"
NM = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12353801/"
NB = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11738990/"
EU = "https://www.eurekalert.org/news-releases/"

H = ["candidate", "company", "company_type", "channel", "claim", "ai_step", "source", "source_quote", "ctgov_terms", "note"]
R = [
 # Channel A: SEC filers
 ["REC-617 (GTAEXS617)", "Recursion (from Exscientia)", "US-listed", "A", "explicit", "molecule", RX, "This program utilized our generative AI and active learning platform to optimize molecule design", "REC-617; GTAEXS617; GTAEXS-617", ""],
 ["REC-3565", "Recursion", "US-listed", "A", "explicit", "molecule", RX, "Leveraging our AI-driven, multi-parameter optimization approach, we focused on an allosteric mechanism ... for REC-3565", "REC-3565", ""],
 ["REC-4539 (EXS74539)", "Recursion (from Exscientia)", "US-listed", "A", "explicit", "molecule", EX, "We used machine learning models to optimise multiple parameters including CNS penetrance, potency and ADMET properties", "REC-4539; EXS74539", "Phase 1 (ENLYGHT) expected to start 1H 2026 per Recursion 10-K"],
 ["REC-1245", "Recursion", "US-listed", "A", "platform", "target", RX, "pipeline described as AI-native; RBM39 degrader from the Recursion OS", "REC-1245", ""],
 ["REC-4881", "Recursion", "US-listed", "A", "indication", "indication", RX, "a novel, platform-derived biological insight — identifying MEK1/2 inhibition as a therapeutic entry point", "REC-4881", "existing MEK1/2 inhibitor; AI step was the indication"],
 ["EXS4318", "Exscientia / Bristol Myers Squibb", "US-listed (partner: multinational)", "A", "platform", "molecule", EX, "a compound precision designed by us and in-licensed by Bristol Myers Squibb", "EXS4318; EXS-4318", ""],
 ["DSP-0038", "Exscientia / Sumitomo Pharma", "US-listed (partner: non-US multinational)", "A", "platform", "molecule", EX, "Using the first generation of our design platform we also developed additional drug candidates ... including DSP-0038", "DSP-0038", ""],
 ["SGR-1505", "Schrodinger", "US-listed", "A", "explicit", "molecule", SD, "Combining multi-parameter optimization, FEP+, and machine learning ... enabling us to select SGR-1505", "SGR-1505", ""],
 ["SGR-2921", "Schrodinger", "US-listed", "A", "computational", "molecule", SD, "computational platform; no ML statement for this candidate", "SGR-2921", "discontinued Aug 2025 per 10-K"],
 ["SGR-3515", "Schrodinger", "US-listed", "A", "computational", "molecule", SD, "computational platform; no ML statement for this candidate", "SGR-3515", ""],
 ["IAM1363", "Iambic Therapeutics", "US IPO filer (S-1, 2026)", "A", "explicit", "molecule", IA, "HER2 pan-mutant inhibitor: discovery driven by ML coupled with microscale HTE", "IAM1363", ""],
 ["GB-0895", "Generate Biomedicines", "US IPO filer (S-1, 2026)", "A", "platform", "molecule", GE, "GB-0895, utilizes our binding affinity and developability optimization modules; platform uses proprietary AI and ML", "GB-0895", ""],
 ["GB-4362", "Generate Biomedicines", "US IPO filer (S-1, 2026)", "A", "platform", "molecule", GE, "We used binding affinity and developability optimization modules ... to engineer ... GB-4362", "GB-4362", ""],
 ["GB-5267", "Generate Biomedicines", "US IPO filer (S-1, 2026)", "A", "platform", "molecule", GE, "We used binding affinity and developability optimization modules ... to engineer ... GB-5267", "GB-5267", ""],
 ["ABS-101", "Absci", "US-listed", "A", "platform", "molecule", AB, "portfolio of AI-designed antibody therapeutics", "ABS-101", "company will seek a partner rather than advance it (10-K)"],
 ["ABS-201", "Absci", "US-listed", "A", "platform", "molecule", AB, "portfolio of AI-designed antibody therapeutics", "ABS-201", ""],
 ["EVX-01", "Evaxion", "US-listed (Danish)", "A", "explicit", "antigen", EV, "EVX-01's vaccine targets are neoantigens identified by AI-Immunology", "EVX-01", ""],
 ["bexobrutideg (NX-5948)", "Nurix", "US-listed", "A", "platform", "molecule", NX, "Both our wholly owned and partnered pipelines are driven by our DEL-AI discovery engine", "NX-5948; bexobrutideg", ""],
 ["zelebrudomide (NX-2127)", "Nurix", "US-listed", "A", "platform", "molecule", NX, "pipelines are driven by our DEL-AI discovery engine", "NX-2127; zelebrudomide", ""],
 ["NX-1607", "Nurix", "US-listed", "A", "platform", "molecule", NX, "pipelines are driven by our DEL-AI discovery engine", "NX-1607", ""],
 ["COM701", "Compugen", "US-listed (Israeli)", "A", "platform", "target", CG, "utilizing Unigen, our AI/ML powered computational discovery platform, to identify novel drug targets", "COM701", ""],
 ["COM902", "Compugen", "US-listed (Israeli)", "A", "platform", "target", CG, "utilizing Unigen ... to identify novel drug targets", "COM902", ""],
 ["rilvegostomig", "Compugen / AstraZeneca", "US-listed (partner: multinational)", "A", "computational", "target", CG, "We discovered TIGIT in 2009 with our immune checkpoint computational discovery capabilities (no AI/ML statement tied to TIGIT)", "rilvegostomig; AZD2936", "developed by AstraZeneca; TIGIT component derived from COM902. Relabeled from platform to computational after a citation check"],
 ["GS-0321 (COM503)", "Compugen / Gilead", "US-listed (partner: multinational)", "A", "platform", "target", CG, "clinical-stage programs: ... GS-0321 (previously COM503)", "GS-0321; COM503", ""],
 ["IBIO-600", "iBio", "US-listed", "A", "explicit", "molecule", IB, "the first molecule generated using our AI Drug Discovery Platform", "IBIO-600", "Phase 1 in Australia; first participant dosed June 2026 (10-K)"],
 ["OD-001", "Odyssey Therapeutics", "US IPO filer (S-1, 2026)", "A", "platform", "molecule", OD, "Our AI/ML platform is designed to support small-molecule drug discovery", "OD-001", ""],
 ["EIK1006", "Eikon Therapeutics", "US-listed", "A", "explicit", "molecule", EK, "apply ML and computational chemistry to develop novel molecules that target ... AR; EIK1006 is our second internally derived clinical candidate", "EIK1006", ""],
 ["MRT-2359", "Monte Rosa", "US-listed", "A", "platform", "molecule", MR, "QuEEN discovery engine; geometric deep learning to identify reprogrammable ligases", "MRT-2359", ""],
 ["MRT-6160", "Monte Rosa", "US-listed", "A", "platform", "molecule", MR, "QuEEN discovery engine", "MRT-6160", ""],
 ["MRT-8102", "Monte Rosa", "US-listed", "A", "platform", "molecule", MR, "QuEEN discovery engine", "MRT-8102", ""],
 ["zolucatetide (FOG-001)", "Parabilis Medicines", "US IPO filer (S-1, 2026)", "A", "platform", "molecule", PB, "Helicon discovery platform integrates advanced AI- and physics-based computational modeling", "FOG-001; zolucatetide", "Phase 3 planned 1H 2027 (S-1)"],
 ["BXCL501 (dexmedetomidine)", "BioXcel", "US-listed", "A", "indication", "indication", BX, "Our drug identification platform led to the identification of dexmedetomidine ... approval by the FDA as IGALMI", "BXCL501", "approved 2022 as IGALMI; existing molecule"],
 ["BXCL502 (latrepirdine)", "BioXcel", "US-listed", "A", "indication", "indication", BX, "We identified ... BXCL502 − Latrepirdine (Dimebon) − through our AI-based platform", "BXCL502; latrepirdine", "existing molecule"],
 ["RLY-2608", "Relay Therapeutics", "US-listed", "A", "borderline", "molecule", RL, "machine learning named as one part of the Dynamo platform", "RLY-2608", ""],
 ["aleniglipron (GSBR-1290)", "Structure Therapeutics", "US-listed", "A", "borderline", "molecule", ST, "integrating ... computational chemistry ... and machine learning", "GSBR-1290; aleniglipron", ""],
 ["KT-621", "Kymera", "US-listed", "A", "borderline", "molecule", KY, "we have integrated artificial intelligence (AI) and machine learning into virtual screening, hit validation and optimization", "KT-621", ""],
 ["KRRO-110", "Korro Bio", "US-listed", "A", "borderline", "molecule", KO, "Machine learning optimization of oligonucleotides", "KRRO-110", ""],
 # Channel B: private / non-US-listed
 ["rentosertib (ISM001-055)", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "explicit", "target+molecule", NM, "a first-in-class AI-generated small-molecule inhibitor of TNIK, a first-in-class target in IPF discovered using generative AI", "INS018_055; ISM001-055; rentosertib", "peer-reviewed (Nature Medicine 2025; Nature Biotechnology 2024)"],
 ["ISM6331", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "explicit", "molecule", EU + "1137916", "discovered and designed using Insilico Medicine's proprietary generative AI-powered drug discovery platform, Chemistry42", "ISM6331", "company claim; unverified by the independent citation check (EurekAlert! returned HTTP 403 to it)"],
 ["ISM3412", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "explicit", "molecule", EU + "1087962", "ISM3412 was designed using ligand-based AI-enabled drug design by ... Chemistry42", "ISM3412", "company claim; unverified by the independent citation check (EurekAlert! returned HTTP 403 to it)"],
 ["ISM5411", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "explicit", "molecule", EU + "1067877", "Generative chemistry enables Insilico to develop gut-restricted PHD inhibitors", "ISM5411", "company claim summarizing a Nature Biotechnology paper; unverified by the independent citation check (EurekAlert! returned HTTP 403 to it)"],
 ["ISM8207", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "platform", "molecule", EU + "1071279", "Insilico's wholly owned AI-driven drug discovery pipelines", "ISM8207", "company claim"],
 ["ISM5939", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "platform", "molecule", EU + "1071279", "Insilico's wholly owned AI-driven drug discovery pipelines", "ISM5939", "company claim"],
 ["ISM9528", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "platform", "molecule", EU + "1071279", "Insilico's wholly owned AI-driven drug discovery pipelines", "ISM9528", "company claim"],
 ["ISM8969", "Insilico Medicine", "listed outside the US / not an SEC filer", "B", "platform", "molecule", EU + "1071279", "Insilico's wholly owned AI-driven drug discovery pipelines", "ISM8969", "company claim"],
 ["BEN-8744", "BenevolentAI", "private (delisted)", "B", "platform", "target", "https://pharmatimes.com/news/benevolentai_doses_participants_in_ben-8744_study_1497005/", "Our AI powered drug-discovery platform identified PDE10 as a novel target for UC (company statement reported by PharmaTimes, 31 Aug 2023)", "BEN8744; BEN-8744", "company claim"],
 ["ENV-294", "Enveda", "private", "B", "platform", "molecule", "https://www.biospace.com/press-releases/enveda-initiates-phase-2-clinical-trials-of-env-294-a-first-in-class-oral-therapy-in-atopic-dermatitis-and-asthma", "ENV-294 is a novel, first-in-class, small molecule discovered using Enveda's proprietary platform; Enveda uses AI-powered tools to identify and characterize ... molecules", "ENV-294", "company claim"],
]
with open("candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(H)
    w.writerows(R)
print(len(R), "rows")
