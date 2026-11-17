# Data appendix: AI in Drug Discovery: The Intersection Ecosystem – November 2026

Frozen code and derived tables behind every computed number in the report. Third-party documents (filings, papers, releases) are linked from the report's footnotes, not copied here. Scripts were run in a research folder layout in which each step had its own folder; the 'step' column gives that folder, so relative input paths such as ../013/ refer to step 013.

| File | Step |
| --- | --- |
| ecosystem/abcellera_10k.py | 020 |
| ecosystem/abcellera_royalty_lines.json | 020 |
| ecosystem/build_summary_009.py | 009 |
| ecosystem/build_table_008.py | 008 |
| ecosystem/build_update_013.py | 013 |
| ecosystem/coverage_summary_013.json | 013 |
| ecosystem/d4_incumbents.py | 018 |
| ecosystem/d4_run.log | 018 |
| ecosystem/d5_xbrl.json | 018 |
| ecosystem/d5_xbrl.py | 018 |
| ecosystem/deals_nonsec_008.csv | 008 |
| ecosystem/deals_summary_008.json | 008 |
| ecosystem/deals_update.json | 019 |
| ecosystem/deals_update.py | 019 |
| ecosystem/deals_with_nurix_roche.csv | 019 |
| ecosystem/deals_with_source_007.csv | 007 |
| ecosystem/deals_without_terms.csv | 010 |
| ecosystem/deferred_summary.json | 010 |
| ecosystem/deferred_tables.py | 010 |
| ecosystem/ecosystem_multinationals_019.csv | 019 |
| ecosystem/emerging_013.csv | 013 |
| ecosystem/emerging_log_013.csv | 013 |
| ecosystem/g3_own_reading.csv | 010 |
| ecosystem/grants_nsf.py | 001 |
| ecosystem/nsf_grants.json | raw |
| ecosystem/revenue_by_type.csv | 009 |
| ecosystem/revenue_summary_009.json | 009 |
| ecosystem/significant_013.csv | 013 |
| ecosystem/term_trend.csv | 010 |
| ecosystem/term_trend.py | 010 |
| ecosystem/top20_share.csv | 009 |
| people-barriers/barriers.py | 015 |
| people-barriers/burn.csv | 015 |
| people-barriers/coded.csv | 015 |
| people-barriers/corresp.json | 017 |
| people-barriers/corresp.py | 017 |
| people-barriers/d2_stop_sentences.csv | 018 |
| people-barriers/deals_combined.csv | 008 |
| people-barriers/ema_retry.py | 017 |
| people-barriers/panel16.json | 017 |
| people-barriers/people_rev.csv | 017 |
| people-barriers/people_rev.json | 017 |
| people-barriers/people_rev.py | 017 |
| people-barriers/pool.csv | 016 |
| people-barriers/prospectus_coded.csv | 017 |
| people-barriers/ranked_rev.csv | 017 |
| people-barriers/runway_coded.csv | 015 |
| people-barriers/stop_reasons.json | 019 |
| people-barriers/stop_reasons.py | 019 |
| people-barriers/stops.csv | 015 |
| people-barriers/summary.json | 015 |
| people-barriers/summary.py | 015 |
| people-barriers/v_coded.csv | 018 |
| people-barriers/v_main.csv | 018 |
| people-barriers/v_main.json | 018 |
| people-barriers/v_validation_lit.py | 018 |
| people-barriers/xbrl_burn.py | 015 |
| pipeline/accutar_trials.json | 020 |
| pipeline/build_signposts.py | 017 |
| pipeline/build_summary.py | 010 |
| pipeline/cohort_32.csv | 014 |
| pipeline/cohort_32_020.csv | 020 |
| pipeline/cohort_32_final.csv | 019 |
| pipeline/cohort_recompute.py | 020 |
| pipeline/combine.py | 001 |
| pipeline/ctgov_durations.py | 014 |
| pipeline/d1_fda.py | 018 |
| pipeline/d1_fda_hits.csv | 018 |
| pipeline/d1_summary.json | 018 |
| pipeline/d3_phase3.py | 018 |
| pipeline/d3_phase3_trials.csv | 018 |
| pipeline/d6_matched_baseline.py | 018 |
| pipeline/d6_summary.json | 018 |
| pipeline/deals_build_table.py | 008 |
| pipeline/deals_summary.json | 008 |
| pipeline/discovery_times.csv | 014 |
| pipeline/durations.json | 014 |
| pipeline/durations_posthoc.json | 014 |
| pipeline/durations_posthoc.py | 014 |
| pipeline/fetch_020.py | 020 |
| pipeline/formd_test.py | 001 |
| pipeline/g3_own_reading.csv | 010 |
| pipeline/grants_nsf.py | 001 |
| pipeline/pairings.csv | 001 |
| pipeline/patents_uspto.py | 001 |
| pipeline/phase_transition.json | 014 |
| pipeline/phase_transition.py | 014 |
| pipeline/pipeline_figures.py | 019 |
| pipeline/pipeline_summary.json | 019 |
| pipeline/precision.csv | 002 |
| pipeline/precision.py | 002 |
| pipeline/pubs_openalex.py | 001 |
| pipeline/realms.py | 001 |
| pipeline/recompute.py | 018 |
| pipeline/recompute_summary.json | 018 |
| pipeline/signposts.csv | 023 (same as c023_signposts.csv: 40 open trials, with XL309's NCT05932862 added; column confidence_written_rule keeps the written-rule rating) |
| pipeline/signposts.py | 017 |
| pipeline/summary.json | 020 |
| pipeline/term_trend.csv | 010 |
| pipeline/term_trend.py | 010 |
| pipeline/trials_open.csv | 017 |
| pipeline/vintage_summary.json | 010 |
| pipeline/vintage_with_outcome.csv | 010 |
| pipeline/c021_recompute.py, c021_summary.json, c021_cohort_main.csv, c021_cohort_all_tiers.csv, c021_evidence.json | 021 (main cohort of 29 under the tier rule plus Recursion's three; rule-reading grid) |
| pipeline/c021_signposts.py, c021_signposts_summary.json | 021 |
| pipeline/schroedinger.py, schroedinger.json | 021 (time to candidate with SGR-1505; deal wording and revenue shares with Schrödinger as platform-named) |
| pipeline/raw_021/ | 021 (ClinicalTrials.gov and Europe PMC records) |
| people-barriers/c021_people.py, c021_people_021.csv, c021_ranked_021.csv, c021_people_021.json | 021 (Feng Ren C1 from the rentosertib design paper) |
| pipeline/signposts_020.csv | 018/020 (frozen input of c021_signposts.py) |
| pipeline/c022_recompute.py, c022_summary.json, c022_cohort_main.csv, c022_cohort_all_tiers.csv | 022 (main cohort of 30 with ISM5411; TAK-920/DNL919 as portfolio; Adagene and Drug Farm labeled borderline in the all-tiers file; percentages rounded half up) |
| pipeline/c022_fda_names.py, c022_fda_names.json | 022 (Drugs@FDA check by molecule and code name, 109 names, 25,670 original approvals; lirafugratinib found) |
| pipeline/c023_recompute.py, c023_summary.json, c023_cohort_main.csv, c023_cohort_all_tiers.csv, c023_evidence.json | 023 (main cohort of 32 with Insilico's ISM3312 and ISM3091/XL309; rule-reading grid; Phase 1 → 2; stop reasons; sensitivities) |
| pipeline/c023_fda_check.py, c023_fda_check.json | 023 (Drugs@FDA check for ISM3312, ISM3091, XL309 and ISM8207; no record) |
| pipeline/c023_signposts.py, c023_signposts.csv, c023_signposts_summary.json | 023 (open trials with NCT05932862 added; 40 trials, 19 candidates) |
| ecosystem/emerging_rules.md | 011 (Emerging Companies rules, copied from the research notebook) |
| people-barriers/c016_papers.py, c016_papers.json | 016 (author search for candidate and tool papers, including RoseTTAFold, RFdiffusion and ESM-2) |
