"""Cycle 023 (PR #36, facts only under the rule freeze): Insilico's other programs tested against the cycle 004 entry rule.
- ISM3312 (3CL protease) enters, explicit: Insilico release 2023-02-23 ("generated and designed with the support of Insilico's
  proprietary generative chemistry platform Chemistry42"); release 2023-05-25 lists it "in Phase I trials". Not on ClinicalTrials.gov.
  Outcome by the cycle 004/012 written rule: absent from the pipeline chart of Insilico's latest annual filing (2025 annual report,
  HKEX 2026-04-28) with no stated partner or successor -> discontinued at Phase 1, reason not stated. Flag: insilico.com
  pipeline page still shows "Phase I Completed" (sensitivity: unknown).
- ISM3091 / XL309 (USP1) enters, explicit: Insilico release 2023-05-25 ("designed and optimized using Insilico's proprietary AI
  platform, Chemistry42"); Exelixis FY2023 10-K (filed 2024-02-06): transfer of "the ongoing phase 1 clinical trial" completed in Q4
  2023. Flag: NCT05932862 actual start 2024-04-03 (sensitivity: excluded). Active (Exelixis 10-Q filed 2026-10-29: enrollment ongoing).
- ISM8207 (QPCTL) does not enter: first patient dosed per Insilico release 2024-05-15; NCT06445517 start 2024-04-25.
Grid definitions unchanged (cycle 021); both join every grid cohort except the original 16.
Inputs: analysis/022/cohort_main.csv, analysis/022/cohort_all_tiers.csv, analysis/022/summary.json, analysis/014/phase_transition.json.
Outputs: analysis/023/cohort_main.csv, analysis/023/cohort_all_tiers.csv, analysis/023/summary.json.
Usage (repo root): python3 analysis/023/recompute.py"""
import csv, json, math
from decimal import Decimal, ROUND_HALF_UP
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)]
pct = lambda k, n: float((Decimal(k) * 100 / Decimal(n)).quantize(Decimal("0.1"), ROUND_HALF_UP))
main22 = list(csv.DictReader(open('analysis/022/cohort_main.csv')))
all22 = list(csv.DictReader(open('analysis/022/cohort_all_tiers.csv')))
s22 = json.load(open('analysis/022/summary.json'))
NEW = [dict(candidate='ISM3312', company='Insilico Medicine', tier='explicit', outcome='discontinued', highest_phase_sponsor='Phase 1',
            highest_phase_registry='none (not on ClinicalTrials.gov)', first_trial='2023 (Insilico release 2023-05-25: "in Phase I trials"; company page: Phase I initiated in China March 2023)',
            outcome_note='Absent from the pipeline chart of Insilico 2025 annual report (latest annual filing) and 2025 prospectus; no partner or successor stated -> discontinued (cycle 004 rule), reason not stated. Flag: insilico.com page shows "Phase I Completed". Added cycle 023 (PR #36).'),
       dict(candidate='ISM3091 (XL309)', company='Insilico Medicine (licensed to Exelixis)', tier='explicit', outcome='active', highest_phase_sponsor='Phase 1',
            highest_phase_registry='Phase 1', first_trial='2023 (Exelixis FY2023 10-K: ongoing phase 1 trial transferred Q4 2023); registry NCT05932862 actual start 2024-04-03',
            outcome_note='Exelixis 10-Q filed 2026-10-29: Phase 1, enrollment ongoing; registry ACTIVE_NOT_RECRUITING. Flag: registry start after 2023-12-31. Added cycle 023 (PR #36).')]
main = main22 + NEW; alltiers = all22 + NEW
for name, rs in (('main', main), ('all_tiers', alltiers)):
    with open(f'analysis/023/cohort_{name}.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(main22[0].keys())); w.writeheader(); w.writerows(rs)
BORDER = ['ADG126 (muzastotug)', 'ADG106', 'ADG116', 'ADG206', 'DF-003', 'DF-006']
REC3 = ['REC-994', 'REC-2282', 'REC-4881']
ORIG16 = ['EXS21546', 'DSP-1181', 'DSP-0038', 'DSP-2342', 'EXS4318', 'GTAEXS617 (REC-617)', 'REC-3964', 'SGR-1505', 'MRT-2359',
          'NX-2127 (zelebrudomide)', 'NX-1607', 'NX-5948 (bexobrutideg)', 'EVX-01', 'EVX-02', 'ISM001-055 (rentosertib)', 'BEN-2293']
orig = [r for r in main if r['candidate'] in ORIG16]; assert len(orig) == 16
tier = [r for r in main if r['candidate'] not in REC3]; assert len(tier) == 29
assert len(main) == 32 and len(alltiers) == 38
PREC = ['bamlanivimab (LY-CoV555)', 'bebtelovimab (LY-CoV1404)', 'ADG106', 'NX-2127 (zelebrudomide)', 'AC0682', 'AC176']
ACC = ['AC0682', 'AC176']
def strict(rs, rule, override=None):
    k = 0
    for r in rs:
        o = (override or {}).get(r['candidate'], r['outcome'])
        if rule == 'accutar_unknown' and r['candidate'] in ACC: o = 'unknown'
        if rule == 'no_precedence' and r['candidate'] in PREC: o = 'active_or_unknown'
        k += o == 'discontinued'
    return k
COH = {'original16': orig, 'tier29': tier, 'main': main, 'all_tiers': alltiers}
grid = {c: {u: {'k': strict(rs, u), 'n': len(rs), 'pct': pct(strict(rs, u), len(rs))} for u in ('precedence', 'accutar_unknown', 'no_precedence')} for c, rs in COH.items()}
vals = [(v['pct'], c, u) for c, d in grid.items() for u, v in d.items()]
n = len(main); k = strict(main, 'precedence')
oc = {}
for r in main: oc[r['outcome']] = oc.get(r['outcome'], 0) + 1
broad = sum(r['outcome'] in ('discontinued', 'unknown', 'superseded') for r in main)
RANK = {'Phase 1': 1, 'Phase 1/2': 1, 'Phase 2': 2, 'Phase 2/3': 2, 'Phase 3': 3, 'Phase 4': 4}
p3 = [r['candidate'] for r in main if RANK[r['highest_phase_sponsor']] >= 3]
pt = json.load(open('analysis/014/phase_transition.json'))['baseline_BIO_2011_2020']
cls = {'REC-3964': 'infectious', 'MRT-2359': 'oncology', 'NX-5948 (bexobrutideg)': 'oncology', 'EVX-01': 'oncology',
       'ISM001-055 (rentosertib)': 'other', 'MDR-001': 'other', 'ADG126 (muzastotug)': 'oncology',
       'bamlanivimab (LY-CoV555)': 'infectious', 'bebtelovimab (LY-CoV1404)': 'infectious', 'EXS21546': 'oncology',
       'DSP-1181': 'other', 'BEN-2293': 'other', 'ADG106': 'oncology', 'TAK-920/DNL919': 'other',
       'NX-2127 (zelebrudomide)': 'oncology', 'AC0682': 'oncology', 'AC176': 'oncology',
       'REC-994': 'other', 'ISM5411': 'other', 'REC-2282': 'oncology', 'REC-4881': 'oncology',
       'ISM3312': 'infectious', 'ISM3091 (XL309)': 'oncology'}  # cycle 022 classes plus ISM3312 (COVID-19 antiviral)
rate = {'oncology': pt['oncology_phase1_to_2'] / 100, 'infectious': pt['infectious_phase1_to_2'] / 100, 'other': pt['phase1_to_2'] / 100}
def p12(rs, exclude=()):
    adv = [r['candidate'] for r in rs if RANK[r['highest_phase_sponsor']] >= 2 and r['candidate'] not in exclude]
    fail = [r['candidate'] for r in rs if RANK[r['highest_phase_sponsor']] == 1 and r['outcome'] == 'discontinued' and r['candidate'] not in exclude]
    dist = [1.0]
    for c in adv + fail:
        p = rate[cls[c]]; new = [0.0] * (len(dist) + 1)
        for i, v in enumerate(dist): new[i] += v * (1 - p); new[i + 1] += v * p
        dist = new
    a, m = len(adv), len(adv) + len(fail)
    return {'advanced': a, 'resolved': m, 'pct': pct(a, m), 'ci95': wilson(a, m), 'failed': fail,
            'matched_expected': round(sum(rate[cls[c]] for c in adv + fail), 2), 'p_one_sided_matched': round(sum(dist[a:]), 3)}
sr = dict(s22['stop_reasons_main']); sr['not stated'] += 1  # ISM3312: no stated reason
assert sum(sr.values()) == k
sens = {'ISM3312_unknown': {'strict': f"{strict(main, 'precedence', {'ISM3312': 'unknown'})}/{n}", 'pct': pct(strict(main, 'precedence', {'ISM3312': 'unknown'}), n)},
        'without_ISM3091': {'strict': f"{k}/{n - 1}", 'pct': pct(k, n - 1)},
        'without_both_new': {'strict': f"{k - 1}/{n - 2}", 'pct': pct(k - 1, n - 2)}}
out = {'as_of': '2026-11-17', 'cycle': '023', 'main_n': n, 'main_outcomes': oc, 'strict': f'{k}/{n}', 'strict_pct': pct(k, n), 'strict_95ci': wilson(k, n),
       'broad': f'{broad}/{n}', 'broad_pct': pct(broad, n), 'broad_95ci': wilson(broad, n),
       'by_tier': {t: {'n': sum(r['tier'] == t for r in main), 'discontinued': sum(r['tier'] == t and r['outcome'] == 'discontinued' for r in main)} for t in ('explicit', 'platform')},
       'phase3_or_later_sponsor': {'k': len(p3), 'pct': pct(len(p3), n), 'candidates': p3},
       'rule_grid': grid, 'range': {'min': min(vals), 'max': max(vals)},
       'no_precedence_main': grid['main']['no_precedence'],
       'stops_beyond_original16': [r['candidate'] for r in main if r['outcome'] == 'discontinued' and r['candidate'] not in ORIG16],
       'phase1_to_2': p12(main), 'phase1_to_2_without_recursion_additions': p12(main, REC3), 'phase1_to_2_all_tiers': p12(alltiers),
       'stop_reasons_main': sr, 'sensitivity_023': sens, 'added': ['ISM3312', 'ISM3091 (XL309)'],
       'not_entered': {'ISM8207': 'first patient dosed per Insilico release 2024-05-15; NCT06445517 start 2024-04-25'}}
json.dump(out, open('analysis/023/summary.json', 'w'), indent=1)
print(json.dumps({x: out[x] for x in ('main_n', 'strict', 'strict_pct', 'strict_95ci', 'broad', 'broad_pct', 'by_tier', 'phase3_or_later_sponsor', 'range', 'no_precedence_main', 'stop_reasons_main', 'sensitivity_023')}, indent=1))
print({c: {u: v['pct'] for u, v in d.items()} for c, d in grid.items()})
print(out['phase1_to_2'], out['phase1_to_2_without_recursion_additions'])
