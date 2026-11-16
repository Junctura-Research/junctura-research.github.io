# Data appendix: Status of AI-Linked Drug Candidates – November 2026

This folder contains the code and data behind every number computed in the Research Note "Status of AI-Linked Drug Candidates – November 2026" (Junctura Research, as of 2026-11-16). It is frozen: the files are as they stood on the Note's as-of date.

The sources themselves (SEC filings, company releases and pipeline tables, trial registrations) are not copied here. Third-party documents are linked, not rehosted; the URL of every source is in the tables and scripts.

## Folders

| Folder | Contents | Main outputs |
| --- | --- | --- |
| `current-list/` | The list of 37 drug candidates that companies tie to AI, found in filings dated 2024-01-01 to 2026-11-15, with each candidate's highest trial phase | `candidates.csv`, `candidates_with_phase.csv`, `summary.json` |
| `cohort/` | The dated cohort: candidates tied to AI in documents of 2019–2023 and in trials by 2023-12-31, with their status on 2026-11-16 | `cohort.csv`, `cohort_with_phase.csv`, `summary.json` |
| `checks/` | The Note's headline counts and intervals, and rechecks of present-day facts made on 2026-11-16 | `headline.json`, `raw/status_check.json`, `raw/generic_name_check.json`, `raw/sponsor_phase3_check.json` |

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
- `unknown`: neither can be shown from public sources.
- `superseded`: the company replaced the candidate with a successor (EVX-02 by EVX-03). Counted in the broad stop rate, not the strict one.

**Highest phase.** The ClinicalTrials.gov phase label among matching trials that have started (not "not yet recruiting" or "withdrawn"). A trial matches a candidate only if the candidate's code or name appears in its intervention list, punctuation ignored. Where no started trial is registered, the phase stated by the company is used (`DOC_PHASE` in `cohort/summarize.py`).

## Notes and corrections

- **RLY-2608.** `current-list/candidates_with_phase.csv` records Relay's RLY-2608 (borderline) at Phase 2. A Phase 3 trial, NCT06982521, has recruited since 2025-08-26 and names the drug only as "zovegalisib". The Note uses the corrected phase. RLY-2608 is outside the AI count, so no headline figure changes. `checks/generic_name_check.py` and `checks/sponsor_phase3_check.py` found no other candidate in an unrecorded Phase 3 trial. In `raw/generic_name_check.json`, `current_list_top` is each candidate's highest phase from the current-list search. Its one "Phase 2" hit for NX-1607 comes from the generic term "Cbl-b Inhibitor", which matches other companies' drugs, and is a false positive.
- **Label differences between the two tables.** DSP-0038 is `platform` in `current-list/` and `explicit` in `cohort/`; REC-617 is the reverse. Cohort labels come only from documents dated by 2024-04-30, and the current list used current documents. If DSP-0038 were labeled platform-only, the cohort split would be 7 explicit and 9 platform-only.
- **EXS21546.** The outcome reason combines the company's words ("not sufficiently promising") and the trial registry's stated reason ("challenge to reach suitable therapeutic index").
- **Unregistered trials.** REC-3964's Phase 1 is not on ClinicalTrials.gov; Recursion's 10-K filed 2023-02-27 says "A Phase 1 study in healthy volunteers is underway." Trials registered only outside ClinicalTrials.gov are missed.
- **Refused scripted access.** Business Wire and the Euronext company-news pages did not return content to scripted requests. The FogPharma release of June 2023 could not be read.
- **Not included here:** the downloaded filings and third-party documents (linked by URL instead), and an internal script that checks the Note's wording against a list of investment terms.
