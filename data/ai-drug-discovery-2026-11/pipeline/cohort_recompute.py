"""an earlier step: apply a review ruling rulings to the cohort of 32.
Reworded working rule (the review, a review ruling; revised after the data were seen): conflicting evidence is resolved by the
precedence order (regulator action > company or partner stop statement > registry status > pipeline listing); a candidate
is 'unknown' only when evidence of equal rank conflicts, or there is no evidence.
Inputs: analysis/019/cohort_32_final.csv, analysis/014/cohort_trials.csv, analysis/019/stop_reasons.json,
analysis/014/phase_transition.json (BIO baselines), analysis/020/accutar_trials.json, analysis/020/abcellera_royalty_lines.json.
Outputs: analysis/020/cohort_32_020.csv, analysis/020/summary.json. Run from the repository root."""
import csv, json, math
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)]
rows = list(csv.DictReader(open('analysis/019/cohort_32_final.csv')))
trials = list(csv.DictReader(open('analysis/014/cohort_trials.csv')))
acc = json.load(open('analysis/020/accutar_trials.json'))
n = len(rows); assert n == 32
# 1. Re-check every candidate: registry statuses of its trials vs its recorded outcome.
recheck = []
for r in rows:
    st = sorted({t['status'] for t in trials if r['candidate'].split(' ')[0] in t['candidates'].split('; ') or t['candidates'] == r['candidate']})
    all_stopped = bool(st) and all(s in ('TERMINATED', 'WITHDRAWN') for s in st)
    recheck.append({'candidate': r['candidate'], 'outcome_019': r['outcome'], 'registry_statuses': st, 'all_registry_trials_terminated_or_withdrawn': all_stopped})
# 2. Apply the precedence rule to Accutar's AC0682 and AC176 (registry: all trials terminated > undated pipeline listing).
for r in rows:
    if r['candidate'] in ('AC0682', 'AC176'):
        assert r['outcome'] == 'unknown'
        r['outcome'] = 'discontinued'
        r['outcome_note'] = 'All registered trials terminated (ClinicalTrials.gov); registry status outranks the undated pipeline listing (precedence rule; a review ruling)'
for x in recheck:
    x['outcome_020'] = next(r['outcome'] for r in rows if r['candidate'] == x['candidate'])
    x['changed'] = x['outcome_019'] != x['outcome_020']
with open('analysis/020/cohort_32_020.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
oc = {}
for r in rows: oc[r['outcome']] = oc.get(r['outcome'], 0) + 1
strict = oc['discontinued']; broad = strict + oc.get('unknown', 0) + oc.get('superseded', 0)
# Stops decided by the precedence rule (evidence of different ranks conflicts):
PREC = {'bamlanivimab (LY-CoV555)': 'regulator revocation vs registry Phase 4 listings',
        'bebtelovimab (LY-CoV1404)': 'regulator revocation vs registry Phase 4 listing',
        'ADG106': 'company "deprioritized" vs investigator-led trials recruiting', 'NX-2127 (zelebrudomide)': 'company 10-Q vs registry recruiting',
        'AC0682': 'registry terminated vs undated pipeline listing', 'AC176': 'registry terminated vs undated pipeline listing'}
assert all(any(r['candidate'] == c and r['outcome'] == 'discontinued' for r in rows) for c in PREC)
def pct(k): return round(k / n * 100, 1)
sens = {'accutar_unknown_PR25_reading': {'k': strict - 2, 'pct': pct(strict - 2)},
        'revoked_antibodies_reverted_only': {'k': strict - 2, 'pct': pct(strict - 2)},
        'no_precedence_rule_all_six_reverted': {'k': strict - len(PREC), 'pct': pct(strict - len(PREC)), 'reverted': list(PREC)}}
# 3. Phase 1 -> 2 an earlier step rules): candidates whose highest sponsor phase is Phase 1 and that are discontinued fail;
# Phase 1/2 counts as Phase 1; Phase 2 or later advanced.
RANK = {'Phase 1': 1, 'Phase 1/2': 1, 'Phase 2': 2, 'Phase 2/3': 2, 'Phase 3': 3, 'Phase 4': 4}
adv = [r['candidate'] for r in rows if RANK[r['highest_phase_sponsor']] >= 2]
fail = [r['candidate'] for r in rows if RANK[r['highest_phase_sponsor']] == 1 and r['outcome'] == 'discontinued']
pt = json.load(open('analysis/014/phase_transition.json'))['baseline_BIO_2011_2020']
cls = {'REC-3964': 'infectious', 'MRT-2359': 'oncology', 'NX-5948 (bexobrutideg)': 'oncology', 'EVX-01': 'oncology',
       'ISM001-055 (rentosertib)': 'other', 'MDR-001': 'other', 'ADG126 (muzastotug)': 'oncology',
       'bamlanivimab (LY-CoV555)': 'infectious', 'bebtelovimab (LY-CoV1404)': 'infectious',
       'EXS21546': 'oncology', 'DSP-1181': 'other', 'BEN-2293': 'other', 'ADG106': 'oncology', 'TAK-920/DNL919': 'other',
       'NX-2127 (zelebrudomide)': 'oncology', 'AC0682': 'oncology', 'AC176': 'oncology'}
assert set(adv + fail) == set(cls), set(adv + fail) ^ set(cls)
rate = {'oncology': pt['oncology_phase1_to_2'] / 100, 'infectious': pt['infectious_phase1_to_2'] / 100, 'other': pt['phase1_to_2'] / 100}
dist = [1.0]
for c in adv + fail:
    p = rate[cls[c]]; new = [0.0] * (len(dist) + 1)
    for k, v in enumerate(dist): new[k] += v * (1 - p); new[k + 1] += v * p
    dist = new
k, m = len(adv), len(adv) + len(fail)
p1 = {'advanced': k, 'resolved': m, 'pct': round(k / m * 100, 1), 'ci95': wilson(k, m), 'failed': fail,
      'matched_expected_advanced': round(sum(rate[cls[c]] for c in adv + fail), 2),
      'p_one_sided_ge_observed_matched': round(sum(dist[k:]), 3),
      'p_unmatched_baseline_52': round(sum(math.comb(m, i) * .52 ** i * .48 ** (m - i) for i in range(k, m + 1)), 3),
      'accutar_unknown_sensitivity': {'advanced': k, 'resolved': m - 2, 'pct': round(k / (m - 2) * 100, 1)},
      'previous_019': '9/15 = 60.0%'}
# 4. Stop reasons on 11: Accutar registry why-stopped texts.
sr = json.load(open('analysis/019/stop_reasons.json'))
acc_class = {'AC0682': ('portfolio', acc['NCT05080842']['whyStopped']), 'AC176': ('trial results', acc['NCT05241613']['whyStopped'])}
main = dict(sr['main']) if 'main' in sr else None
out = {'as_of': '2026-11-17', 'n': n, 'outcomes': oc, 'strict': f'{strict}/{n}', 'strict_pct': pct(strict), 'strict_95ci': wilson(strict, n),
       'broad': f'{broad}/{n}', 'broad_pct': pct(broad), 'broad_95ci': wilson(broad, n), 'sensitivity': sens,
       'by_tier': {t: {'n': sum(1 for r in rows if r['tier'] == t), 'discontinued': sum(1 for r in rows if r['tier'] == t and r['outcome'] == 'discontinued')} for t in ('explicit', 'platform')},
       'recheck_changed': [x for x in recheck if x['changed']],
       'recheck_flags_active_but_all_trials_stopped': [x for x in recheck if x['all_registry_trials_terminated_or_withdrawn'] and x['outcome_020'] not in ('discontinued',)],
       'unknown_after_rule': [r['candidate'] for r in rows if r['outcome'] == 'unknown'],
       'phase1_to_2': p1, 'stop_reasons_019': sr, 'accutar_stop_class_registry': acc_class}
json.dump({'recheck': recheck}, open('analysis/020/recheck.json', 'w'), indent=1)
json.dump(out, open('analysis/020/summary.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'stop_reasons_019'}, indent=1)); print(json.dumps(sr, indent=1)[:1500])
# Stop reasons on 11 stops: an earlier step classes applied to the registry's why-stopped text (AC0682: "development strategy
# was adjusted" -> portfolio or strategic; AC176: "benefit-risk ratio changes" -> efficacy or safety = trial results).
main11 = dict(sr['main_reading_9']); sens11 = dict(sr['sensitivity_ADG106_not_stated_9'])
for c, (cl, _) in acc_class.items(): main11[cl] += 1; sens11[cl] += 1
out['stop_reasons_11'] = {'main': main11, 'sensitivity_ADG106_not_stated': sens11,
                          'accutar_unknown_reading_9': sr['main_reading_9']}
json.dump(out, open('analysis/020/summary.json', 'w'), indent=1); print(out['stop_reasons_11'])
