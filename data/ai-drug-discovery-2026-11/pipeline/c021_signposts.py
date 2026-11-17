"""Cycle 021: regenerate signposts.csv so the published file matches the text (PR #34).
Starts from the cycle 018/020 file (written-rule ratings), then:
 - removes NX-2127's trial (development stopped, Nurix 10-Q; cycle 018 ruling);
 - applies the reviewer-accepted overrides: the three enrollment-closed trials within 12 months -> low (PR #31,
   set after the data were seen); GB-0895's two Phase 3 trials -> low (cycle 020, set after the data were seen);
 - relabels Adagene and Drug Farm trials 'borderline' (PR #34 tier ruling);
 - adds REC-4881's open trial NCT05552755 (Recursion; enters the cohort, PR #34), rated by the written rule.
Keeps the written-rule rating in a column 'confidence_written_rule' and the reason for any override.
Usage (repo root): python3 analysis/021/signposts.py"""
import json, pandas as pd
d = pd.read_csv('analysis/021/signposts_020_input.csv', dtype=str)  # frozen cycle 018/020 file (appendix copy: pipeline/signposts_020.csv)
d = d[d.nct != 'NCT04830137'].copy()
d['confidence_written_rule'] = d.confidence; d['override'] = ''
OV = {'NCT04524871': 'enrollment closed, date within 12 months: low (PR #31; set after the data were seen)',
      'NCT07116889': 'enrollment closed, date within 12 months: low (PR #31; set after the data were seen)',
      'NCT05546268': 'enrollment closed, date within 12 months: low (PR #31; set after the data were seen)',
      'NCT07276724': 'GB-0895 full enrollment expected 1H 2028 plus 52-week endpoint: low (cycle 020; set after the data were seen)',
      'NCT07359846': 'GB-0895 full enrollment expected 1H 2028 plus 52-week endpoint: low (cycle 020; set after the data were seen)'}
for n, why in OV.items():
    i = d.index[d.nct == n]; assert len(i) == 1, n
    d.loc[i, 'confidence'] = 'low'; d.loc[i, 'override'] = why
bl = d.candidates.str.startswith(('ADG', 'DF-'))
d.loc[bl, 'tier'] = 'borderline (Adagene, Drug Farm; PR #34)'
t = json.load(open('analysis/021/raw/rec4881_tupelo.json')); s = t['statusModule']
pc = s['primaryCompletionDateStruct']['date']
assert s['overallStatus'] == 'RECRUITING' and pc < '2027-11-17'  # within 12 months and recruiting -> low (written rule)
new = dict(nct='NCT05552755', candidates='REC-4881', title=t['title'], status=s['overallStatus'], phase='PHASE1/PHASE2',
           sponsor=t['sponsor'], start=s['startDateStruct']['date'], primary_completion=pc, pc_type=s['primaryCompletionDateStruct']['type'],
           completion=s['completionDateStruct']['date'], c_type=s['completionDateStruct']['type'], confidence='low',
           reason='within 12 months, still recruiting', tier='cohort (Phase 1-2)',
           signpost='primary completion (main readout) of Phase 1/2 NCT05552755', confidence_written_rule='low', override='')
d = pd.concat([d, pd.DataFrame([new])], ignore_index=True)
d.to_csv('analysis/021/signposts.csv', index=False)
out = {'open_trials': len(d), 'candidates': d.candidates.nunique(), 'confidence': d.confidence.value_counts().to_dict(),
       'written_rule': d.confidence_written_rule.value_counts().to_dict(),
       'passed_before_2026_11_17': int((d.primary_completion < '2026-11-17').sum()),
       'dates_2025_2026': int(d.primary_completion.str[:4].isin(['2025', '2026']).sum())}
json.dump(out, open('analysis/021/signposts_summary.json', 'w'), indent=1); print(out)
