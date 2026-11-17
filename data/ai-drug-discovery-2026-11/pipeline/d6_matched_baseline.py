"""D6: Phase 1 -> 2 advancement in the cohort (9 of 14 resolved, analysis/014/phase_transition.json)
against an indication-matched BIO 2011-2020 baseline. Indication classes assigned by hand from the
cohort records an earlier step, 012, 013); fixed in the an earlier step plan before computing."""
import json
pt = json.load(open('analysis/014/phase_transition.json'))
b = pt['baseline_BIO_2011_2020']
cls = {'REC-3964': 'infectious', 'MRT-2359': 'oncology', 'NX-5948 (bexobrutideg)': 'oncology', 'EVX-01': 'oncology',
       'ISM001-055 (rentosertib)': 'other', 'MDR-001': 'other', 'ADG126 (muzastotug)': 'oncology',
       'bamlanivimab (LY-CoV555)': 'infectious', 'bebtelovimab (LY-CoV1404)': 'infectious',
       'EXS21546': 'oncology', 'DSP-1181': 'other', 'BEN-2293': 'other', 'ADG106': 'oncology', 'TAK-920/DNL919': 'other'}
rate = {'oncology': b['oncology_phase1_to_2'] / 100, 'infectious': b['infectious_phase1_to_2'] / 100, 'other': b['phase1_to_2'] / 100}
adv, fail = pt['phase1_to_2']['main']['advanced'], pt['phase1_to_2']['main']['failed']
assert set(adv + fail) == set(cls), set(adv + fail) ^ set(cls)
ps = [rate[cls[c]] for c in adv + fail]
dist = [1.0]
for p in ps:
    new = [0.0] * (len(dist) + 1)
    for k, v in enumerate(dist):
        new[k] += v * (1 - p); new[k + 1] += v * p
    dist = new
obs = len(adv)
out = {'n_resolved': len(ps), 'observed_advanced': obs, 'observed_rate': round(obs / len(ps) * 100, 1),
       'class_counts': {k: sum(1 for c in cls.values() if c == k) for k in rate},
       'expected_advanced': round(sum(ps), 2), 'expected_rate': round(sum(ps) / len(ps) * 100, 1),
       'p_one_sided_ge_observed': round(sum(dist[obs:]), 3),
       'p_unmatched_baseline_52': round(sum(__import__('math').comb(14, k) * .52 ** k * .48 ** (14 - k) for k in range(obs, 15)), 3)}
json.dump(out, open('analysis/018/d6_summary.json', 'w'), indent=1); print(out)
