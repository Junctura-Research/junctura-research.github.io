"""an earlier step S: apply the fixed confidence rule (the research record) to open trials, and derive the earliest
FDA-decision arithmetic. As of 2026-11-17. Usage (repo root): python3 analysis/017/build_signposts.py
→ signposts.csv, summary.json. Company date statements checked in filings (fetch_filings.py; Insilico's 2025 annual
report saved in an earlier step: none states a readout date, so no registry date is confirmed (no 'high')."""
import json, pandas as pd
D = 'analysis/017/'
ASOF, PLUS12 = '2026-11-17', '2027-11-17'
t = pd.read_csv(D + 'trials_open.csv')
TIER = {'ISM001-055 (rentosertib)': 'main (explicit)', 'NX-5948 (bexobrutideg)': 'main (platform)', 'GB-0895 (Generate; Phase 3 tier, not in cohort)': 'main (platform)',
        'zovegalisib / RLY-2608 (Relay; borderline tier)': 'borderline', 'aleniglipron / GSBR-1290 (Structure; borderline tier)': 'borderline'}
def pc(d):  # month-only dates compared at the end of the month's first day (conservative ordering is not affected at this resolution)
    return d if len(d) == 10 else d + '-01'
def conf(r):
    d = pc(r.primary_completion)
    if r.status == 'NOT_YET_RECRUITING': return 'low', 'not yet recruiting'
    if d < ASOF: return 'low', 'estimated date already passed'
    if d < PLUS12 and r.status in ('RECRUITING', 'ENROLLING_BY_INVITATION'): return 'low', 'within 12 months, still recruiting'
    if d < PLUS12: return 'medium', 'within 12 months, enrollment closed (case not named in the rule; assigned medium, disclosed)'
    return 'medium', 'registry estimate 12+ months out; no filed company date'
t[['confidence', 'reason']] = t.apply(lambda r: pd.Series(conf(r)), axis=1)
t['tier'] = t.candidates.map(TIER).fillna('cohort (Phase 1-2)')
t['signpost'] = 'primary completion (main readout) of ' + t.phase.str.replace('PHASE', 'Phase ').str.replace('/', '/') + ' ' + t.nct
t.to_csv(D + 'signposts.csv', index=False)
p3 = t[t.phase == 'PHASE3'].sort_values('primary_completion')
add = lambda ym, m: str(pd.Period(ym[:7], 'M') + m)
derived = {r.nct: dict(candidate=r.candidates, tier=r.tier, primary_completion=r.primary_completion,
                       earliest_fda_action=add(r.primary_completion, 24)) for _, r in p3.iterrows()}
# Nurix: Phase 2 DAYBreak (NCT07221500) "designed to support accelerated approval" (10-K filed 2026-01-28)
nx = t[t.nct == 'NCT07221500'].iloc[0]
derived['NCT07221500 (accelerated-approval route, company design claim)'] = dict(candidate=nx.candidates, tier='main (platform)', primary_completion=nx.primary_completion, earliest_fda_action=add(nx.primary_completion, 24))
summ = dict(as_of=ASOF, open_trials=len(t), candidates_with_open_trials=t.candidates.nunique(), confidence=t.confidence.value_counts().to_dict(),
            reasons=t.reason.value_counts().to_dict(), passed_estimated=int((t.reason == 'estimated date already passed').sum()),
            phase3_open=p3[['nct', 'candidates', 'tier', 'status', 'start', 'primary_completion', 'confidence']].to_dict('records'),
            derived_rule='primary completion + 12 months filing preparation (assumption) + 12 months (60-day filing + 10-month standard NME review, PDUFA VII)',
            derived=derived, by_year=t.primary_completion.str[:4].value_counts().sort_index().to_dict(),
            active_cohort_without_open_trial=sorted(set(pd.read_csv('analysis/014/cohort_32.csv').query("outcome=='active'").candidate) - set(t.candidates)))
json.dump(summ, open(D + 'summary.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k != 'phase3_open'}, indent=1, default=str))
print(t[['nct', 'candidates', 'phase', 'status', 'primary_completion', 'confidence']].to_string())
