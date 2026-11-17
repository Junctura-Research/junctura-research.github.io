"""Cycle 023: add XL309/ISM3091's open trial NCT05932862 (Exelixis) to the cycle 021 signposts file. ISM3312 has no registry record.
Status ACTIVE_NOT_RECRUITING, primary completion 2027-04-30 (estimated): a date within 12 months with enrollment closed falls outside
the written rule (written-rule column: medium, as for the three such trials in cycle 017) and is rated low under the PR #31 override.
Usage (repo root): python3 analysis/023/signposts.py -> analysis/023/signposts.csv, analysis/023/signposts_summary.json"""
import json, pandas as pd
d = pd.read_csv('analysis/021/signposts.csv', dtype=str)
p = json.load(open('analysis/023/raw/ctgov_ISM3091.json'))['studies'][0]['protocolSection']; s = p['statusModule']
pc = s['primaryCompletionDateStruct']['date']
assert s['overallStatus'] == 'ACTIVE_NOT_RECRUITING' and '2026-11-17' < pc < '2027-11-17'
new = dict(nct='NCT05932862', candidates='XL309 (ISM3091)', title=p['identificationModule']['briefTitle'], status=s['overallStatus'], phase='PHASE1',
           sponsor=p['sponsorCollaboratorsModule']['leadSponsor']['name'], start=s['startDateStruct']['date'], primary_completion=pc,
           pc_type=s['primaryCompletionDateStruct']['type'], completion=s.get('completionDateStruct', {}).get('date'),
           c_type=s.get('completionDateStruct', {}).get('type'), confidence='low', reason='within 12 months, enrollment closed',
           tier='cohort (Phase 1)', signpost='primary completion (main readout) of Phase 1 NCT05932862', confidence_written_rule='medium',
           override='enrollment closed, date within 12 months: low (PR #31; set after the data were seen)')
d = pd.concat([d, pd.DataFrame([new])], ignore_index=True)
d.to_csv('analysis/023/signposts.csv', index=False)
out = {'open_trials': len(d), 'candidates': d.candidates.nunique(), 'confidence': d.confidence.value_counts().to_dict(),
       'written_rule': d.confidence_written_rule.value_counts().to_dict(),
       'passed_before_2026_11_17': int((d.primary_completion < '2026-11-17').sum()),
       'estimated_dates_passed': int(((d.primary_completion < '2026-11-17') & (d.pc_type == 'ESTIMATED')).sum()),
       'dates_2025_2026': int(d.primary_completion.str[:4].isin(['2025', '2026']).sum())}
json.dump(out, open('analysis/023/signposts_summary.json', 'w'), indent=1); print(out)
