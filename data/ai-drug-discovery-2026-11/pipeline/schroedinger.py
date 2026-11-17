"""Cycle 021: recompute what the earlier "computational, not AI" rulings on Schrodinger (PR #21, PR #27) affected (PR #34).
Schrodinger is now described in its own words (FY2025 10-K: "physics-based methods, combined with the rapid data processing
and scaling advantages of machine learning"). Applied consistently:
 (a) time to candidate: SGR-1505 joins the main reading (longest stated time per candidate, PR #27 rule);
 (b) clinic-share illustration recomputed with the new median;
 (c) deal wording: Schrodinger's three 'computational' deals become 'platform-named' (its platform text names machine learning);
 (d) top-20 partner revenue by deal wording, 2024 and 2025, with the same merge;
 (e) strict drugmaker inclusion: recomputed (strict counts explicit deals only, so (c) cannot change it; checked).
Inputs: analysis/014/discovery_times.csv, analysis/019/pipeline_summary.json, analysis/019/deals_with_nurix_roche.csv,
papers/ai-drug-discovery-2026-11/data/ecosystem/revenue_summary_009.json, analysis/019/deals_update.py.
Output: analysis/021/schroedinger.json. Usage (repo root): python3 analysis/021/schroedinger.py"""
import json, statistics, importlib.util, pandas as pd
dt = pd.read_csv('analysis/014/discovery_times.csv')
c = dt[dt.end_point_class == 'candidate']
longest = c.groupby('candidate').months.max().to_dict(); earliest = {}
import re
key = lambda x: re.search(r'(\d{4}-\d{2})', x).group(1)  # date inside text such as 'undated web page (PDF version uploaded 2023-10 ...)'
for k, g in c.groupby('candidate'): earliest[k] = g.assign(sd=g.source_date.map(key)).sort_values('sd').months.iloc[0]
ps = json.load(open('analysis/019/pipeline_summary.json'))
assert {k: v for k, v in longest.items() if k != 'SGR-1505'} == {k.replace(' (rentosertib)', ' (rentosertib)'): v for k, v in ps['discovery_times']['main_longest_without_SGR1505']['values'].items()}
med_l = statistics.median(longest.values()); med_e = statistics.median(earliest.values())
med_l_wo = statistics.median([v for k, v in longest.items() if k != 'SGR-1505'])
cs = ps['clinic_share_illustration']; clinic = 10.5  # cycle 014 T4 assumptions: preclinical 1 year, clinic 10.5 years unchanged
base_disc = 4.5
tot = cs['baseline_total_years'] - base_disc + med_l / 12
# deals
d = pd.read_csv('analysis/019/deals_with_nurix_roche.csv', dtype={'signed': str})
d2 = d.copy(); d2.loc[d2.ai_wording == 'computational', 'ai_wording'] = 'platform-named'
spec = importlib.util.spec_from_file_location('du', 'analysis/019/deals_update.py'); du = importlib.util.module_from_spec(spec); spec.loader.exec_module(du)
cls = du.classes()
_, before = du.block(d, cls); t2, after = du.block(d2, cls)
rv = json.load(open('papers/ai-drug-discovery-2026-11/data/ecosystem/revenue_summary_009.json'))['top20_revenue_by_deal_wording']
shares = {}
for y in ('2024', '2025'):
    v = {w: rv[f'{y} {w}'] for w in ('explicit', 'platform-named', 'computational', 'none')}
    tot_y = sum(v.values())
    shares[y] = {'total_usd_m': round(tot_y, 1),
                 'before': {w: round(x / tot_y * 100) for w, x in v.items()},
                 'after': {'explicit': round(v['explicit'] / tot_y * 100), 'platform-named (incl. Schrodinger)': round((v['platform-named'] + v['computational']) / tot_y * 100), 'none': round(v['none'] / tot_y * 100)}}
out = {'schrodinger_quote': 'We have built our platform on a foundation of rigorous, physics-based methods, combined with the rapid data processing and scaling advantages of machine learning, that together provide a significant advantage over traditional methods.',
       'time_to_candidate': {'main_longest_with_SGR1505': {'n': len(longest), 'median_months': med_l, 'values': longest},
                             'earliest_with_SGR1505': {'n': len(earliest), 'median_months': med_e, 'values': earliest},
                             'previous_main_without_SGR1505': med_l_wo},
       'clinic_share_illustration': {'baseline_total_years': cs['baseline_total_years'], 'baseline_clinic_share_pct': cs['baseline_clinic_share_pct'],
                                     'median_months': med_l, 'stated_total_years': round(tot, 2), 'stated_clinic_share_pct': round(clinic / tot * 100, 1)},
       'deal_wording_before': before['all_deals']['by_ai_wording'], 'deal_wording_after': after['all_deals']['by_ai_wording'],
       'strict_before': before['strict_count'], 'strict_after': after['strict_count'], 'broad_after': after['broad_count'],
       'strict_not_met_after': after['strict_not_met'],
       'top20_revenue_shares_by_wording': shares}
json.dump(out, open('analysis/021/schroedinger.json', 'w'), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
