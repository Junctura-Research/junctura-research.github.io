"""an earlier step recomputation: (a) cohort attrition and Phase 1 -> 2 with NX-2127 (zelebrudomide) discontinued
(Nurix 10-Q filed 2026-10-13, d2_stop_sentences.csv); (b) a review ruling rulings on signposts: the three
'within 12 months, enrollment closed' dates to low, NX-2127's trial removed, FDA-action floors at 6/12/18 months
of filing preparation; (c) validation-literature counts from v_coded.csv."""
import csv, json, math
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)
n = 32; strict = 9
out = {'attrition': {'strict': f'{strict}/{n}', 'strict_pct': round(strict / n * 100, 1), 'strict_95ci': wilson(strict, n),
       'broad': f'{strict + 4}/{n}', 'broad_pct': round((strict + 4) / n * 100, 1),
       'sens_without_precedence_rule': round((strict - 2) / n * 100, 1), 'sens_accutar_stops': round((strict + 2) / n * 100, 1),
       'previous': {'strict_pct': 25.0, 'broad_pct': 37.5}}}
# Phase 1 -> 2: NX-2127 moves from unresolved to failed (stopped after Phase 1; oncology)
from itertools import product
adv, fail = 9, 6
cls_rates = [0.488] * 7 + [0.578] * 3 + [0.52] * 5   # 6 oncology + NX-2127, 3 infectious, 5 other
dist = [1.0]
for p in cls_rates:
    new = [0.0] * (len(dist) + 1)
    for k, v in enumerate(dist): new[k] += v * (1 - p); new[k + 1] += v * p
    dist = new
out['phase1_to_2'] = {'advanced': adv, 'resolved': adv + fail, 'pct': round(adv / (adv + fail) * 100, 1), 'ci95': wilson(adv, adv + fail),
                      'matched_expected': round(sum(cls_rates), 2), 'p_ge_observed_matched': round(sum(dist[adv:]), 3),
                      'previous': '9/14 = 64.3%'}
sp = list(csv.DictReader(open('analysis/017/signposts.csv')))
kept = [r for r in sp if 'NX-2127' not in r['candidates']]
conf = {'medium': 0, 'low': 0}
for r in kept:
    c = 'low' if r['reason'].startswith('within 12 months, enrollment closed') else r['confidence']
    conf[c] = conf.get(c, 0) + 1
cands = {r['candidates'] for r in kept}
out['signposts'] = {'open_trials': len(kept), 'removed': [r['nct'] for r in sp if r not in kept], 'candidates': len(cands), 'confidence': conf}
def add(ym, months):
    y, m = map(int, ym[:7].split('-')); m += months; y += (m - 1) // 12; m = (m - 1) % 12 + 1; return f'{y}-{m:02d}'
floors = {}
for name, pc in {'zovegalisib (borderline, Phase 3)': '2028-04', 'GB-0895 (platform, Phase 3)': '2028-12',
                 'bexobrutideg (platform, Phase 2 accelerated-approval route NCT07221500)': '2028-01',
                 'NX-5948 Phase 3 / rentosertib (explicit) Phase 3': '2029-10'}.items():
    floors[name] = {f'prep_{k}m': add(pc, k + 12) for k in (6, 12, 18)}
out['fda_action_floor'] = floors
v = [r for r in csv.DictReader(open('analysis/018/v_coded.csv')) if r['on_topic'] == 'yes']
out['validation_lit'] = {'on_topic': len(v), **{k: sum(int(r[k]) for r in v) for k in ['data', 'validation', 'clinical_evidence', 'regulation', 'compute_tools']},
                         'no_barrier_named': sum(1 for r in v if not any(int(r[k]) for k in ['data', 'validation', 'clinical_evidence', 'regulation', 'compute_tools']) and not r['other'])}
json.dump(out, open('analysis/018/summary.json', 'w'), indent=1); print(json.dumps(out, indent=1))
