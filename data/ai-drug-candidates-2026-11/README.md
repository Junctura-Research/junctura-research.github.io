# Data appendix: Status of AI-Linked Drug Candidates – November 2026

This folder contains the code and data behind every number computed in the Research Note "Status of AI-Linked Drug Candidates – November 2026" (Junctura Research, first published as of 2026-11-16, updated as of 2026-11-17). It is frozen: `current-list/`, `cohort/` and `checks/` are as they stood on 2026-11-16, except for the dated correction listed under "Notes and corrections". The Report Update of 2026-11-17 adds `update-2026-11/` and changes nothing in the other folders.

The sources themselves (SEC filings, company releases and pipeline tables, trial registrations) are not copied here. Third-party documents are linked, not rehosted; the URL of every source is in the tables and scripts.

## Folders

| Folder | Contents | Main outputs |
| --- | --- | --- |
| `current-list/` | The list of 37 drug candidates that companies tie to AI, found in filings dated 2024-01-01 to 2026-11-15, with each candidate's highest trial phase | `candidates.csv`, `candidates_with_phase.csv`, `summary.json` |
| `cohort/` | The dated cohort: candidates tied to AI in documents of 2019–2023 and in trials by 2023-12-31, with their status on 2026-11-16 | `cohort.csv`, `cohort_with_phase.csv`, `summary.json` |
| `checks/` | The Note's headline counts and intervals, and rechecks of present-day facts made on 2026-11-16 | `headline.json`, `raw/status_check.json`, `raw/generic_name_check.json`, `raw/sponsor_phase3_check.json` |
| `update-2026-11/` | Report Update of 2026-11-17 (files prefixed `c021_` and `c022_` hold earlier readings; files prefixed `c023_` hold the final cohort of 32 and its figures; see "Notes and corrections"): the cohort enlarged to 32 candidates, outcomes as of 2026-11-17, the Drugs@FDA approvals check, SEC stop statements and Phase 3 trials by sponsor | `cohort_32_final.csv`, `summary.json`, `note_variants.json`, `stop_reasons.json` |

Each folder has a `raw/` subfolder with the extracts returned by public interfaces: the ClinicalTrials.gov API version 2, the SEC EDGAR full-text search and submissions interfaces, openFDA (Drugs@FDA) and Europe PMC.

## Running the code

Python 3 with `requests`, `beautifulsoup4` and `lxml`. Run each script from its own folder. Scripts that query live services write to `raw/` and will return different results on a later date; the extracts here are the record as of the Note. SEC scripts send a `User-Agent` header with a contact address, as the SEC requires; replace it with your own. Filings downloaded by the SEC scripts are cached in `raw/filings/`, which is not included (about 1.6 GB).

The tables and counts can be rebuilt offline from the files here:

```
cd current-list && python summarize.py      # -> candidates_with_phase.csv, summary.json
cd ../cohort && python build_cohort.py      # -> cohort.csv
python summarize.py                         # -> cohort_with_phase.csv, summary.json
cd ../checks && python headline.py          # -> headline.json
```

### current-list/, in run order

| Step | Script | What it does | Output |
| --- | --- | --- | --- |
| 1 | `edgar_fts.py raw` | SEC EDGAR full-text search: 7 fixed queries, forms 10-K, 20-F, S-1, F-1, filed 2024-01-01 to 2026-11-15; filers kept if their industry code (SIC) is 2834, 2835, 2836 or 8731 | `raw/edgar_fts.json` |
| 2 | `edgar_sentences.py raw` | Downloads each kept filer's latest matching filing and pulls sentences joining an AI term with a candidate code or "product candidate" | `raw/edgar_sentences.json` |
| 3 | `edgar_windows.py raw` | Candidate codes within 300 characters of an AI term and a discovery verb. A review queue only; it over-matches | `raw/edgar_windows.json` |
| 4 | `seed_channel_b.py raw` | Counts how many of those filings name each of 35 AI drug-discovery companies. Companies named there, including private and non-US ones ("Channel B"), were added to the filers found in step 1 ("Channel A") | `raw/channel_b_seed.json` |
| 5 | `ctgov.py sponsors raw` | ClinicalTrials.gov: trials by sponsor for the Channel B companies | `raw/ctgov_sponsors.json` |
| 6 | `build_candidates.py` | Hand-built list: one row per candidate, with source URL, quoted claim and labels | `candidates.csv` |
| 7 | `ctgov.py candidates raw` | ClinicalTrials.gov: intervention search for each term in `candidates.csv` | `raw/ctgov_candidates.json` |
| 8 | `summarize.py` | Joins 6 and 7; highest phase per candidate; counts | `candidates_with_phase.csv`, `summary.json` |
| 9 | `fda_check.py raw` | openFDA Drugs@FDA, for candidates at Phase 3 or later | `raw/fda_check.json` |

### cohort/, in run order

| Step | Script | What it does | Output |
| --- | --- | --- | --- |
| 1 | `list_filings.py raw` | SEC EDGAR submissions: 10-K, 20-F, S-1 and F-1 filed 2020-01-01 to 2024-04-30 by the SEC filers with an AI candidate in the current list | `raw/filings_index.json` |
| 2 | `edgar_cohort.py raw` | Extracts candidate codes in clinical-stage sentences, and AI or machine-learning sentences, from those filings. A review queue only | `raw/edgar_cohort.json` |
| 3 | `latest_filings.py raw` | Each SEC filer's latest annual or IPO filing, for current status | `raw/latest_index.json` |
| 4 | `ctgov_cohort.py sponsors raw` | ClinicalTrials.gov: trials led by each current-list company with a start date on or before 2023-12-31 | `raw/ctgov_sponsors_2023.json` |
| 5 | `build_cohort.py` | Hand-built table: entry source and quote (2019–2023), outcome source and quote (to 2026-11-16) | `cohort.csv` |
| 6 | `ctgov_cohort.py candidates raw` | ClinicalTrials.gov: intervention search for each term in `cohort.csv` | `raw/ctgov_cohort.json` |
| 7 | `summarize.py` | Joins 5 and 6; highest phase; counts | `cohort_with_phase.csv`, `summary.json` |

### checks/

| Script | What it does | Output |
| --- | --- | --- |
| `headline.py` | Recomputes the cohort counts under the fixed cut-off: the 16-candidate headline, the 18-candidate variant, 95% Wilson score intervals, two label checks, and years of first trial | `headline.json` |
| `status_check.py raw` | Rechecks the Phase 3 trials of the three AI candidates and of the two borderline candidates in Phase 3, openFDA records for the three, and the dates of other sources the Note uses | `raw/status_check.json` |
| `generic_name_check.py raw` | For each current-list candidate, searches ClinicalTrials.gov again under other names listed with its code, to find late trials registered under a generic name | `raw/generic_name_check.json` |
| `sponsor_phase3_check.py raw` | Lists every Phase 3 trial led by the 17 current-list companies | `raw/sponsor_phase3_check.json` |

### update-2026-11/ (Report Update, 2026-11-17)

The cohort was enlarged after a coverage check of 2026-11-17 found AI drug-discovery companies outside the first search; the 16 added candidates entered after their outcomes were known. The entry rule is unchanged. Three rules were added or changed, all after the data were seen: an outcome precedence rule (regulator action, then a company or partner stop statement, then registry status, then a pipeline listing); a reworded "unknown" rule (a candidate is unknown only when evidence of equal rank conflicts, or there is no evidence); and "reached Phase 3 or later" counting only trials run by the sponsor or its development partner. Run every script from this folder. Scripts that read saved source texts (`build_rows.py`, `drug_farm.py`) check quotes against third-party documents, which are not included; their outputs are. Scripts that query live services (`ctgov_new.py`, `sec_stops.py`, `phase3_by_sponsor.py`, `ai_wording_checks.py`, `fda_approvals.py`) will return different results on a later date; `fda_approvals.py` takes the openFDA bulk file (`drug-drugsfda-0001-of-0001.json.zip`) as its argument.

| Step | Script | What it does | Output |
| --- | --- | --- | --- |
| 1 | `ctgov_new.py` | ClinicalTrials.gov: sponsor and intervention searches for the candidates at the six added companies; Phase 3 trials by sponsor | `raw/ctgov_candidates.json`, `raw/ctgov_sponsors_2023.json`, `raw/ctgov_phase3.json` |
| 2 | `build_rows.py` | Hand-built rows for the 14 candidates tested at MindRank, Accutar, Aulos Bioscience (Biolojic Design), Adagene, AbCellera and Pharos iBio, with entry and outcome sources and quotes | `new_rows.csv` |
| 3 | `repair_recompute.py` | Joins those rows with registry phases; counts on 30 candidates before the added rules | `new_rows_with_phase.csv`, `repair_summary.json` |
| 4 | `apply_rules.py` | Applies the outcome precedence rule, the sponsor-or-partner Phase 3 rule, and "unknown" for AC0682 and AC176; Phase 3 tiers across current candidates | `cohort_30_rules.json` |
| 5 | `drug_farm.py` | Adds Drug Farm's DF-003 and DF-006 (ClinicalTrials.gov extract in `raw/ctgov_drugfarm.json`) | `drug_farm_rows.csv`, `cohort_32_before_recheck.json` |
| 6 | `cohort_32.py` | Assembles the 32-candidate table from `../cohort/cohort_with_phase.csv` (16 original candidates), `new_rows_with_phase.csv` and `drug_farm_rows.csv` | `cohort_32.csv` |
| 7 | `sec_stops.py` (uses `edgar_fts.py`) | SEC full-text search, 2025-11-17 to 2026-11-17, for stop statements about candidates not recorded as discontinued; read by hand. Found Nurix's statement on NX-2127 | `sec_stop_sentences.csv`, `sec_stop_search.json` |
| 8 | `fda_approvals.py` | Every original NDA and BLA approval in Drugs@FDA dated 2019-01-01 to 2026-11-13 (latest approval in the bulk file of 2026-11-16), matched against the companies in `significant_companies.csv` and the candidate names | `fda_approvals.csv`, `fda_hits.csv`, `fda_summary.json` |
| 9 | `phase3_by_sponsor.py` | ClinicalTrials.gov Phase 3 trials (start 2015 or later) with any of the 53 companies in `significant_companies.csv` as sponsor or collaborator | `phase3_by_sponsor.csv`, `phase3_by_sponsor_summary.json` |
| 10 | `ai_wording_checks.py` | SEC filings naming the two molecules found in steps 8 and 9 (Denali's tividenofusp alfa, Eikon's EIK1001), checked for sentences that tie them to AI | `ai_wording_checks.json` |
| 11 | `stop_reasons.py` | Stop reasons of the nine discontinued candidates, from `stops.csv` plus NX-2127 | `stop_reasons.json` |
| 12 | `followup_check.py` | Years of follow-up and trial-entry years of the 16 original candidates after the first-trial date correction | `followup_check.json` |
| 13 | `note_update.py` | The Update's first figures: NX-2127 set to discontinued (company stop statement); strict and broad stop rates with 95% Wilson intervals, sensitivity lines, Phase 3 or later, follow-up and trial-entry years on 32, the later-cut-off and target-only variants. Superseded for the stop rates by steps 14–16; still the source of the follow-up and trial-entry years | `note_cohort_32.csv`, `note_update.json` |
| 14 | `fetch_accutar.py` | ClinicalTrials.gov records (status, why stopped) of Accutar's four AC0682 and AC176 trials. Also fetches AbCellera's XBRL revenue facts from SEC EDGAR, which the Note does not use (not included) | `accutar_trials.json` |
| 15 | `recompute.py` | Applies the precedence rule to AC0682 and AC176 (all trials terminated outranks the undated pipeline listing) on `cohort_32_input.csv`, and rechecks every candidate's registry statuses (`cohort_trials.csv`) under the reworded "unknown" rule; final stop rates, sensitivity lines (Accutar as unknown; no precedence rule), tiers, Phase 1 to Phase 2 against `phase_transition.json`, stop reasons on 11 stops | `cohort_32_final.csv`, `summary.json`, `recheck.json` |
| 16 | `note_variants.py` | The variant lines on the final cohort: later cut-off, BEN-8744 included, without REC-3964, Sumitomo's two as unknown | `note_variants.json` |
| 17 | `note_table.py` | Prints the Note's 32-row table from `cohort_32_final.csv` | (printed) |

`cohort_32_final.csv` is the cohort as published: one row per candidate with tier, outcome, both highest phases and first trial. In it and in `note_cohort_32.csv`, `highest_phase_registry` is the highest ClinicalTrials.gov label among started trials, and `highest_phase_sponsor` the highest among trials run by the sponsor or its development partner (they differ for bamlanivimab and bebtelovimab, whose Phase 4 labels come from investigator-led trials). `outcome_basis` names the evidence that decided the outcome where the precedence rule mattered.

## Definitions

**AI claim labels** (column `claim`), set before the search:

- `explicit`: the source names this candidate as discovered, designed or optimized with AI or machine learning. Where AI chose the target rather than the molecule, `ai_step` says so.
- `platform`: the candidate came from a platform the company describes as AI-based, but the source does not tie this candidate to the AI step.
- `borderline`: the filing names machine learning only as one ingredient of a broader platform. Kept out of the headline count.
- `computational`: computational design not described as AI. Excluded.
- `indication`: AI picked a new use for an existing molecule. Excluded, because the molecule was not found by AI.

`ai_step` records what the AI did: `molecule` (design or optimization), `target`, `antigen` (vaccine antigen selection) or `indication`.

**Cohort tiers** (column `tier` in `cohort/`):

- `headline`: a document of the time ties the candidate to AI, explicitly or through a platform it calls AI-based, and AI acted on the molecule (including choosing a vaccine's antigens), or the step is not stated.
- `AI-identified target`: AI picked the target only. Kept out of the headline count.
- `borderline (target)`: machine learning is one named ingredient of a target-discovery platform.
- `retro-AI`: in trials by 2023, but the AI tie appears only in documents dated after 2023.
- `indication`, `computational`: as above.
- `no 2019-2023 source opened`: in trials by 2023, but no document of that period was opened. Left out of the denominator.

**Entry cut-off.** SEC filings filed by 2024-04-30 (annual reports for fiscal 2023), and other company documents dated 2019–2023. The table in `cohort/` marks Generate Biomedicines' two candidates (GB-0669, GB-0895) as `headline`, because a 2024-04-30 cut-off was applied to them. Their only document of the time that was opened is a company release dated 2024-01-04. `checks/headline.py` removes them from the 16-candidate headline and keeps them in the 18-candidate variant.

**Outcome classes** (column `outcome`), fixed before the outcomes were collected, except `superseded`:

- `discontinued`: the company announced discontinuation, deprioritization, a pause or a halt; or the candidate left the company's pipeline with no partner or successor.
- `active`: in the latest pipeline of the company or its partner, or a trial is recruiting or active.
- `unknown`: neither can be shown from public sources. Reworded on 2026-11-17, after the data were seen: conflicting evidence is resolved by the precedence order (see `update-2026-11/`); a candidate is unknown only when evidence of equal rank conflicts, or there is no evidence.
- `superseded`: the company replaced the candidate with a successor (EVX-02 by EVX-03). Counted in the broad stop rate, not the strict one.

**Highest phase.** The ClinicalTrials.gov phase label among matching trials that have started (not "not yet recruiting" or "withdrawn"). A trial matches a candidate only if the candidate's code or name appears in its intervention list, punctuation ignored. Where no started trial is registered, the phase stated by the company is used (`DOC_PHASE` in `cohort/summarize.py`).

## Notes and corrections

- **RLY-2608.** `current-list/candidates_with_phase.csv` records Relay's RLY-2608 (borderline) at Phase 2. A Phase 3 trial, NCT06982521, has recruited since 2025-08-26 and names the drug only as "zovegalisib". The Note uses the corrected phase. RLY-2608 is outside the AI count, so no headline figure changes. `checks/generic_name_check.py` and `checks/sponsor_phase3_check.py` found no other candidate in an unrecorded Phase 3 trial. In `raw/generic_name_check.json`, `current_list_top` is each candidate's highest phase from the current-list search. Its one "Phase 2" hit for NX-1607 comes from the generic term "Cbl-b Inhibitor", which matches other companies' drugs, and is a false positive.
- **Label differences between the two tables.** DSP-0038 is `platform` in `current-list/` and `explicit` in `cohort/`; REC-617 is the reverse. Cohort labels come only from documents dated by 2024-04-30, and the current list used current documents. If DSP-0038 were labeled platform-only, the cohort split would be 7 explicit and 9 platform-only.
- **Correction, 2026-11-17 (found 2026-11-16).** Two first-trial dates in `cohort/cohort_with_phase.csv` (column `first_trial_start`) were later than the candidates' first trials shown in company documents and the trial registry. The intervention searches had missed each candidate's first trial. EVX-01: 2022-09-19 corrected to 2019-01-28 (trial NCT03715985, registered under the name "EVAX-01-CAF09b", start 2019-01-28; Evaxion's Form F-1 of 2021-01-08 says the trial "commenced in January 2019"). Rentosertib (ISM001-055): 2022-02-21 corrected to 2021-12 (Insilico release of 2021-12-01 announcing the first volunteer dosed in an Australian microdose trial). The fix is the `DATE_FIX` table in `cohort/summarize.py`; `cohort/cohort_with_phase.csv` and `checks/headline.json` were rebuilt. No cohort membership, outcome, phase or headline count changed. The number of candidates in trials by the end of 2022 stays at 11. The longest dated follow-up since first trial rises from under 7 years to 7.8 years (EVX-01), so the Note's range now reads "about 3 to 8 years".
- **EXS21546.** The outcome reason combines the company's words ("not sufficiently promising") and the trial registry's stated reason ("challenge to reach suitable therapeutic index").
- **Unregistered trials.** REC-3964's Phase 1 is not on ClinicalTrials.gov; Recursion's 10-K filed 2023-02-27 says "A Phase 1 study in healthy volunteers is underway." Trials registered only outside ClinicalTrials.gov are missed.
- **Refused scripted access.** Business Wire and the Euronext company-news pages did not return content to scripted requests. The FogPharma release of June 2023 could not be read.
- **Update of 2026-11-17.** Outcomes in `cohort/` are as of 2026-11-16 and are kept as published. `update-2026-11/cohort_32_final.csv` holds the outcomes as of 2026-11-17; for the original 16 it differs only for NX-2127 (discontinued; Nurix, Form 10-Q filed 2026-10-13). `note_cohort_32.csv` is the earlier reading of the same day, with Accutar's AC0682 and AC176 as unknown; `cohort_32_final.csv` records them as discontinued under the precedence rule.
- **Rules applied in cycle 021 (reviewer ruling, 2026-11-17).** `update-2026-11/c021_cohort_main.csv` is the main cohort of 29: Adagene's four and Drug Farm's two candidates leave it as borderline under the written tier rule, and Recursion's REC-994, REC-2282 and REC-4881 enter under the entry rule (the repurposing exclusion applies to approved drugs only). `c021_cohort_all_tiers.csv` (35) keeps all of them. `c021_summary.json` gives every figure and the grid of rule readings; `c021_recompute.py` produces both; `c021_evidence.json` holds the quotes the changes rest on.
- **Cycle 022 (2026-11-17, rules unchanged).** `update-2026-11/c022_cohort_main.csv` is the main cohort of 30: Insilico's ISM5411 enters as explicit (Insilico release of 2023-12-05, copy on Kyodo News PR Wire: "Designed by AI from scratch"; Phase 1 trial NCT06012578 from 2023-11-08), and TAK-920/DNL919's stop reason is recorded as portfolio (Denali, Form 10-K for 2023). `c022_cohort_all_tiers.csv` (36) adds the six borderline candidates. `c022_summary.json` gives every figure and the grid of rule readings; `c022_recompute.py` produces all three. `c022_fda_names.py` searches every original approval in the openFDA Drugs@FDA bulk file (meta last_updated 2026-11-16; path as its argument) for 109 molecule names and code names from all tiers; `c022_fda_names.json` holds the result (25,670 approvals scanned; the only new-molecule match is lirafugratinib, NDA 220425, Elevar, approved 2026-09-23, a borderline-tier molecule; the other matches are dexmedetomidine and its generics). Both c022 scripts were run from the root of the Junctura Research working repository and read earlier-cycle inputs by repository path (as in `c021_recompute.py`); their outputs here are the record. The c021 files are kept as published.
- **Cycle 023 (2026-11-17, rules unchanged).** `update-2026-11/c023_cohort_main.csv` is the main cohort of 32: Insilico's ISM3312 (3CL protease inhibitor; Insilico release of 2023-02-23, EurekAlert! copy; discontinued at Phase 1 under the written outcome rule, being absent from the pipeline chart of Insilico's 2025 annual report and its 2025 prospectus; reason not stated) and ISM3091 (XL309, licensed to Exelixis; Insilico release of 2023-05-25, EurekAlert! copy; Phase 1 trial transferred to Exelixis in the fourth quarter of 2023; active) enter as explicit. ISM8207 does not enter (first patient dosed in 2024). `c023_cohort_all_tiers.csv` (38) adds the six borderline candidates. `c023_summary.json` gives every figure, the grid of rule readings and three sensitivity lines (ISM3312 as unknown; without ISM3091, whose registry start is 2024-04-03; without both); `c023_recompute.py` produces all three. `c023_fda_check.py` queries openFDA Drugs@FDA for ISM3312, ISM3091, XL309 and ISM8207; `c023_fda_check.json` records no match. `c023_evidence.json` holds the quotes and URLs the additions rest on. `c023_recompute.py` was run from the root of the Junctura Research working repository and reads cycle 022 inputs by repository path; its outputs here are the record. The c021 and c022 files are kept as published.
- **Not included here:** the downloaded filings and third-party documents (linked by URL instead), and an internal script that checks the Note's wording against a list of investment terms.
