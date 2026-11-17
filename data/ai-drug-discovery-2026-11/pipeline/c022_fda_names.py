"""Cycle 022 (PR #35): Drugs@FDA approvals check by molecule name and code name, all tiers, including licensed-out
molecules. Cycle 018's D1 matched sponsors and a short name list, and missed lirafugratinib (RLY-4008, approved to
Elevar Therapeutics). Here every candidate name of every tier is matched against every active-ingredient and brand
name of every original (ORIG) approval in the openFDA Drugs@FDA bulk file, regardless of sponsor.
Names: candidate and ctgov_terms columns of analysis/003/candidates.csv (47 candidates, all labels incl. borderline,
computational, indication), analysis/004/cohort.csv, analysis/021/cohort_all_tiers.csv, plus the generic (INN) names
on record in cycles 003-021 (list GENERIC below, each with its code name).
Input: https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip (path as argv[1]).
Usage (repo root): python3 analysis/022/fda_names.py /tmp/fda/dd.zip   Output: analysis/022/fda_names.json"""
import csv, json, re, sys, zipfile
GENERIC = {'zovegalisib': 'RLY-2608', 'lirafugratinib': 'RLY-4008', 'migoprotafib': 'RLY-1971 / GDC-1971',
           'aleniglipron': 'GSBR-1290', 'rentosertib': 'ISM001-055', 'bexobrutideg': 'NX-5948', 'zelebrudomide': 'NX-2127',
           'muzastotug': 'ADG126', 'bamlanivimab': 'LY-CoV555', 'bebtelovimab': 'LY-CoV1404', 'etesevimab': 'LY-CoV016',
           'zasocitinib': 'TAK-279', 'rilvegostomig': 'AZD2936', 'tempol': 'REC-994', 'mezigdomide': 'CC-92480 (control check)',
           'cendakimab': 'none (control check)'}
names = {}
def add(n, src):
    n = n.strip()
    if len(n) >= 4: names.setdefault(n, set()).add(src)
for f, cols in (('analysis/003/candidates.csv', ('candidate', 'ctgov_terms')), ('analysis/004/cohort.csv', ('candidate', 'ctgov_terms')),
                ('analysis/021/cohort_all_tiers.csv', ('candidate',))):
    for r in csv.DictReader(open(f)):
        for c in cols:
            for part in re.split(r'[;/()]|\bformerly\b', r.get(c) or ''):
                add(part, f)
for g, code in GENERIC.items(): add(g, 'GENERIC'); [add(x, 'GENERIC') for x in re.split(r'[/()]', code) if 'check' not in x and x.strip() != 'none']
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
z = zipfile.ZipFile(sys.argv[1]); d = json.load(z.open(z.namelist()[0]))
hits, n_orig = [], 0
for r in d['results']:
    for s in r.get('submissions', []):
        if s.get('submission_type') == 'ORIG' and s.get('submission_status') == 'AP':
            n_orig += 1
            fields = [ai.get('name', '') for p in r.get('products', []) for ai in p.get('active_ingredients', [])] + \
                     [p.get('brand_name', '') for p in r.get('products', [])] + (r.get('openfda', {}).get('generic_name') or [])
            blob = ' '.join(norm(x) for x in fields)
            for n in names:
                if norm(n) and norm(n) in blob:
                    hits.append({'name': n, 'sources': sorted(names[n]), 'application': r['application_number'], 'sponsor': r.get('sponsor_name'),
                                 'brand': sorted({p.get('brand_name', '') for p in r.get('products', [])}),
                                 'ingredients': sorted(set(fields[:len(fields)])), 'approval_date': s.get('submission_status_date')})
out = {'meta_last_updated': d.get('meta', {}).get('last_updated'), 'n_names': len(names), 'names': sorted(names),
       'n_orig_approvals_scanned': n_orig, 'hits': hits}
json.dump(out, open('analysis/022/fda_names.json', 'w'), indent=1)
print(out['meta_last_updated'], 'names', len(names), 'ORIG approvals', n_orig)
for h in hits: print(h['name'], h['application'], h['sponsor'], h['brand'], h['approval_date'])
