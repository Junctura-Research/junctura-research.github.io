"""Cycle 021: apply the reviewer's PR #34 answers to the cohort, by script.
1. Tier rule as written: Adagene's four and Drug Farm's two candidates are borderline and leave the main cohort.
3. Recursion's REC-994, REC-2282, REC-4881 re-tested against the cycle 004 entry rule (the repurposing exclusion
   applies to approved drugs only): each is tied to the Recursion OS in Recursion's FY2022 10-K (filed 2023-02-27) and
   was in a Phase 2 or Phase 2/3 trial in 2022 (10-K; ClinicalTrials.gov). Platform tier, like REC-3964 from the same
   filing. Outcomes: REC-994 and REC-2282 discontinued (FY2025 10-K stop statement; registry COMPLETED / TERMINATED,
   no conflict), REC-4881 active (10-Q filed 2026-11-02: "ongoing TUPELO trial").
6. ADG206 stays active (Adagene FY2025 20-F: only an investigator study "deprioritized and terminated").
Rule-reading grid fixed in the cycle 021 plan before computing: cohorts {original16, tier26, main, all_tiers} x
outcome rules {precedence, accutar_unknown, no_precedence}; the range is min-max strict attrition over the grid.
Inputs: analysis/020/cohort_32_020.csv, analysis/004/cohort.csv, analysis/014/phase_transition.json,
analysis/020/summary.json, analysis/021/raw/rec_trials.json. Outputs: analysis/021/cohort_main.csv,
analysis/021/cohort_all_tiers.csv, analysis/021/summary.json. Usage (repo root): python3 analysis/021/recompute.py"""
import csv, json, math
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)]
pct = lambda k, n: round(k / n * 100, 1)
rows32 = list(csv.DictReader(open('analysis/020/cohort_32_020.csv')))
BORDER = ['ADG126 (muzastotug)', 'ADG106', 'ADG116', 'ADG206', 'DF-003', 'DF-006']
assert set(BORDER) <= {r['candidate'] for r in rows32}
ctg = json.load(open('analysis/021/raw/rec_trials.json'))
def first(q): return min(t['start'] for t in ctg[q])
NEW = [dict(candidate='REC-994', company='Recursion', tier='platform', outcome='discontinued', highest_phase_sponsor='Phase 2',
            highest_phase_registry='Phase 2', first_trial=f"{first('REC-994')} (NCT05085561, Phase 2; Recursion ran earlier Phase 1 trials)",
            outcome_note='Recursion FY2025 10-K: discontinued and/or partnering pursued (2025); registry COMPLETED. Added cycle 021 (PR #34).'),
       dict(candidate='REC-2282', company='Recursion', tier='platform', outcome='discontinued', highest_phase_sponsor='Phase 2/3',
            highest_phase_registry='Phase 2/3', first_trial=f"{first('REC-2282')} (NCT05130866, Phase 2/3)",
            outcome_note='Recursion FY2025 10-K: discontinued and/or partnering pursued (2025); registry TERMINATED (sponsor decision). Added cycle 021 (PR #34).'),
       dict(candidate='REC-4881', company='Recursion', tier='platform', outcome='active', highest_phase_sponsor='Phase 2',
            highest_phase_registry='Phase 2', first_trial='2022 (FY2022 10-K: Phase 1 healthy-volunteer trial initiated; Phase 2 underway); registry NCT05552755 start 2023-07-10',
            outcome_note='Recursion 10-Q filed 2026-11-02: ongoing TUPELO trial. Added cycle 021 (PR #34).')]
# cross-check against cycle 004 records of the same three
c4 = {r['candidate']: r for r in csv.DictReader(open('analysis/004/cohort.csv'))}
for x in NEW: assert c4[x['candidate']]['outcome' if 'outcome' in c4[x['candidate']] else list(c4[x['candidate']])[7]] == x['outcome'], x['candidate']
main = [r for r in rows32 if r['candidate'] not in BORDER] + NEW
alltiers = rows32 + NEW
ORIG16 = ['EXS21546', 'DSP-1181', 'DSP-0038', 'DSP-2342', 'EXS4318', 'GTAEXS617 (REC-617)', 'REC-3964', 'SGR-1505', 'MRT-2359',
          'NX-2127 (zelebrudomide)', 'NX-1607', 'NX-5948 (bexobrutideg)', 'EVX-01', 'EVX-02', 'ISM001-055 (rentosertib)', 'BEN-2293']
orig = [r for r in rows32 if r['candidate'] in ORIG16]; assert len(orig) == 16
tier26 = [r for r in rows32 if r['candidate'] not in BORDER]; assert len(tier26) == 26
for name, rs in (('main', main), ('all_tiers', alltiers)):
    with open(f'analysis/021/cohort_{name}.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows32[0].keys())); w.writeheader(); w.writerows(rs)
PREC = ['bamlanivimab (LY-CoV555)', 'bebtelovimab (LY-CoV1404)', 'ADG106', 'NX-2127 (zelebrudomide)', 'AC0682', 'AC176']
ACC = ['AC0682', 'AC176']
def strict(rs, rule):
    k = 0
    for r in rs:
        o = r['outcome']
        if rule == 'accutar_unknown' and r['candidate'] in ACC: o = 'unknown'
        if rule == 'no_precedence' and r['candidate'] in PREC: o = 'active_or_unknown'
        k += o == 'discontinued'
    return k
COH = {'original16': orig, 'tier26': tier26, 'main': main, 'all_tiers': alltiers}
grid = {c: {u: {'k': strict(rs, u), 'n': len(rs), 'pct': pct(strict(rs, u), len(rs))} for u in ('precedence', 'accutar_unknown', 'no_precedence')} for c, rs in COH.items()}
vals = [(v['pct'], c, u) for c, d in grid.items() for u, v in d.items()]
n = len(main); k = strict(main, 'precedence')
oc = {}
for r in main: oc[r['outcome']] = oc.get(r['outcome'], 0) + 1
broad = sum(r['outcome'] in ('discontinued', 'unknown', 'superseded') for r in main)
RANK = {'Phase 1': 1, 'Phase 1/2': 1, 'Phase 2': 2, 'Phase 2/3': 2, 'Phase 3': 3, 'Phase 4': 4}
p3 = [r['candidate'] for r in main if RANK[r['highest_phase_sponsor']] >= 3]
# Phase 1 -> 2 (cycle 014 rule) with cycle 018 D6 indication-matched test
pt = json.load(open('analysis/014/phase_transition.json'))['baseline_BIO_2011_2020']
cls = {'REC-3964': 'infectious', 'MRT-2359': 'oncology', 'NX-5948 (bexobrutideg)': 'oncology', 'EVX-01': 'oncology',
       'ISM001-055 (rentosertib)': 'other', 'MDR-001': 'other', 'ADG126 (muzastotug)': 'oncology',
       'bamlanivimab (LY-CoV555)': 'infectious', 'bebtelovimab (LY-CoV1404)': 'infectious', 'EXS21546': 'oncology',
       'DSP-1181': 'other', 'BEN-2293': 'other', 'ADG106': 'oncology', 'TAK-920/DNL919': 'other',
       'NX-2127 (zelebrudomide)': 'oncology', 'AC0682': 'oncology', 'AC176': 'oncology',
       'REC-994': 'other', 'REC-2282': 'oncology', 'REC-4881': 'oncology'}  # CCM: neurology/vascular -> other; NF2 meningioma, FAP polyps -> oncology
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
REC3 = ['REC-994', 'REC-2282', 'REC-4881']
# stop reasons (cycle 015 classes; PR #29 main reading; cycle 020 Accutar classes); Recursion's two: strategic/portfolio (cycle 004)
s20 = json.load(open('analysis/020/summary.json'))['stop_reasons_11']['main']
sr = dict(s20); sr['portfolio'] -= 1  # ADG106 (deprioritized -> portfolio, PR #29) leaves with Adagene
sr['portfolio'] += 2                   # REC-994, REC-2282
assert sum(sr.values()) == k
out = {'as_of': '2026-11-17', 'main_n': n, 'main_outcomes': oc, 'strict': f'{k}/{n}', 'strict_pct': pct(k, n), 'strict_95ci': wilson(k, n),
       'broad': f'{broad}/{n}', 'broad_pct': pct(broad, n), 'broad_95ci': wilson(broad, n),
       'by_tier': {t: {'n': sum(r['tier'] == t for r in main), 'discontinued': sum(r['tier'] == t and r['outcome'] == 'discontinued' for r in main)} for t in ('explicit', 'platform')},
       'phase3_or_later_sponsor': {'k': len(p3), 'pct': pct(len(p3), n), 'candidates': p3},
       'rule_grid': grid, 'range': {'min': min(vals), 'max': max(vals)},
       'added_after_outcome_known': 'see stops_beyond_original16',
       'stops_beyond_original16': [r['candidate'] for r in main if r['outcome'] == 'discontinued' and r['candidate'] not in ORIG16],
       'phase1_to_2': p12(main), 'phase1_to_2_without_recursion_additions': p12(main, REC3), 'phase1_to_2_all_tiers': p12(alltiers),
       'stop_reasons_main': sr, 'removed_borderline': BORDER, 'added': REC3, 'ADG206': 'active (all-tiers reading only)'}
json.dump(out, open('analysis/021/summary.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
