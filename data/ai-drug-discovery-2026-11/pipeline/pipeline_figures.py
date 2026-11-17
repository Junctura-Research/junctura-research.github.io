"""Figures for the Intersection Report's 'intersection', 'state' and 'signposts' parts.
Inputs (all on record): analysis/014/cohort_32.csv (cohort of 32 as of an earlier step, a review ruling rulings),
analysis/018/summary.json (NX-2127 discontinued per Nurix 10-Q filed 2026-10-13), analysis/014/discovery_times.csv.
Outputs: analysis/019/cohort_32_final.csv, analysis/019/pipeline_summary.json. Run from the repository root."""
import csv, json, math, re, statistics

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)]

rows = list(csv.DictReader(open('analysis/014/cohort_32.csv')))
for r in rows:
    if r['candidate'].startswith('NX-2127'):
        r['outcome'] = 'discontinued'
        r['outcome_note'] = 'Nurix 10-Q for quarter ended 2026-08-31: development discontinued, decision August 2026'
    else:
        r['outcome_note'] = ''
    r['tier'] = r['claim']
with open('analysis/019/cohort_32_final.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['candidate', 'company', 'tier', 'outcome', 'highest_phase_sponsor', 'highest_phase_registry', 'first_trial', 'outcome_note'], extrasaction='ignore')
    w.writeheader(); w.writerows(rows)

n = len(rows)
oc = {}
for r in rows: oc[r['outcome']] = oc.get(r['outcome'], 0) + 1
strict = oc['discontinued']; broad = strict + oc.get('unknown', 0) + oc.get('superseded', 0)
p3 = [r['candidate'] for r in rows if r['highest_phase_sponsor'] in ('Phase 3', 'Phase 4')]
p3_reg = [r['candidate'] for r in rows if r['highest_phase_registry'] in ('Phase 3', 'Phase 4')]
tiers = {t: sum(1 for r in rows if r['tier'] == t) for t in ('explicit', 'platform')}
tier_disc = {t: sum(1 for r in rows if r['tier'] == t and r['outcome'] == 'discontinued') for t in tiers}

# Discovery times: longest stated time per candidate (main; rule set after the evidence came back),
# earliest-dated statement (sensitivity), SGR-1505 (computational) as a sensitivity line.
dt = [r for r in csv.DictReader(open('analysis/014/discovery_times.csv')) if r['end_point_class'] == 'candidate']
def ym(s):
    m = re.search(r'(\d{4})-(\d{2})', s); return m.group(0) if m else '9999-99'
longest, earliest = {}, {}
for r in dt:
    c, m = r['candidate'], float(r['months'])
    longest[c] = max(longest.get(c, 0), m)
    if c not in earliest or ym(r['source_date']) < earliest[c][0]: earliest[c] = (ym(r['source_date']), m)
earliest = {c: v[1] for c, v in earliest.items()}
main = {c: v for c, v in longest.items() if c != 'SGR-1505'}
disc = {'main_longest_without_SGR1505': {'n': len(main), 'median_months': statistics.median(main.values()), 'values': main},
        'earliest_statement_without_SGR1505': {'n': len(main), 'median_months': statistics.median(v for c, v in earliest.items() if c != 'SGR-1505'),
                                               'values': {c: v for c, v in earliest.items() if c != 'SGR-1505'}},
        'longest_with_SGR1505': {'n': len(longest), 'median_months': statistics.median(longest.values())},
        'earliest_with_SGR1505': {'n': len(earliest), 'median_months': statistics.median(earliest.values())}}
# Clinic-share illustration (BIO 2021: 10.5 years clinical and regulatory; Schuhmacher 2016: 4.5 + 1 years)
clin, pre = 10.5, 1.0
def share(disc_years): return round(clin / (disc_years + pre + clin) * 100, 1)
illus = {'baseline_total_years': 4.5 + pre + clin, 'baseline_clinic_share_pct': share(4.5),
         'main_median_months': disc['main_longest_without_SGR1505']['median_months'],
         'stated_total_years': round(disc['main_longest_without_SGR1505']['median_months'] / 12 + pre + clin, 2),
         'stated_clinic_share_pct': share(disc['main_longest_without_SGR1505']['median_months'] / 12)}
out = {'as_of': '2026-11-17', 'n': n, 'outcomes': oc, 'strict': f'{strict}/{n}', 'strict_pct': round(strict / n * 100, 1), 'strict_95ci': wilson(strict, n),
       'broad': f'{broad}/{n}', 'broad_pct': round(broad / n * 100, 1),
       'phase3_or_later_sponsor_or_partner': p3, 'phase3_or_later_registry_label': p3_reg,
       'tiers': tiers, 'discontinued_by_tier': tier_disc, 'discovery_times': disc, 'clinic_share_illustration': illus}
json.dump(out, open('analysis/019/pipeline_summary.json', 'w'), indent=1); print(json.dumps(out, indent=1))

# Signposts after the rulings applied in analysis/018/recompute.py: NX-2127's trial removed,
# 'within 12 months, enrollment closed' dates moved to low. Primary-completion years of the 38 open trials.
sp = [r for r in csv.DictReader(open('analysis/017/signposts.csv')) if 'NX-2127' not in r['candidates']]
years, conf = {}, {}
for r in sp:
    y = r['primary_completion'][:4]; years[y] = years.get(y, 0) + 1
    c = 'low' if r['reason'].startswith('within 12 months, enrollment closed') else r['confidence']
    conf[c] = conf.get(c, 0) + 1
out['signposts'] = {'open_trials': len(sp), 'candidates': len({r['candidates'] for r in sp}), 'confidence': conf,
                    'primary_completion_by_year': dict(sorted(years.items())),
                    'passed_before_2026_11_17': sum(1 for r in sp if r['primary_completion'] < '2026-11-17')}
json.dump(out, open('analysis/019/pipeline_summary.json', 'w'), indent=1); print(json.dumps(out['signposts'], indent=1))
