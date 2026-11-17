"""D1: does any original NDA/BLA approval (2019-01-01 to 2026-11-17) belong to a
significant AI drug-discovery company or name a cohort / Phase 3 tier molecule?
Input: openFDA Drugs@FDA bulk file (https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip,
last_updated 2026-11-16), passed as argv[1] (not committed, 9.4 MB).
Output: d1_fda_approvals.csv (all original approvals in window), d1_fda_hits.csv, d1_summary.json"""
import sys, json, zipfile, csv, re
z = zipfile.ZipFile(sys.argv[1]); d = json.load(z.open(z.namelist()[0]))
sig = [r['company'] for r in csv.DictReader(open('analysis/013/significant_013.csv'))]
extra = ['Outpace', 'Relay', 'Structure Therap', 'Schrodinger', 'Schrödinger', 'Exscientia', 'Biolojic', 'Aulos',
         'Accutar', 'Drug Farm', 'Pharos', 'Denali', 'Nimbus', 'GT Apeiron', 'Insilico', 'Benevolent']
names = sig + extra
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
sponsor_keys = {n: norm(n.split('(')[0])[:10] for n in names}
molecules = ['rentosertib', 'bexobrutideg', 'zovegalisib', 'aleniglipron', 'bamlanivimab', 'bebtelovimab', 'etesevimab',
             'zelebrudomide', 'imneskibart', 'muzastotug', 'lasmotinib', 'zasocitinib', 'GB-0895', 'GB0895', 'ISM001',
             'NX-5948', 'NX-2127', 'NX-1607', 'MRT-2359', 'SGR-1505', 'REC-617', 'EXS', 'DSP-0038', 'DSP-2342', 'DSP-1181',
             'EVX-0', 'MDR-001', 'AC0682', 'AC176', 'AC699', 'AC676', 'AU-007', 'ADG1', 'ADG2', 'PHI-101', 'DF-003', 'DF-006',
             'BEN-2293', 'REC-3964', 'RLY-2608', 'GSBR-1290', 'TAK-279', 'DNL919', 'TAK-920']
rows = []
for r in d['results']:
    for s in r.get('submissions', []):
        if s.get('submission_type') == 'ORIG' and s.get('submission_status') == 'AP' and '20190101' <= s.get('submission_status_date', '') <= '20261117':
            gen = sorted({ai.get('name', '') for p in r.get('products', []) for ai in p.get('active_ingredients', [])})
            brand = sorted({p.get('brand_name', '') for p in r.get('products', [])})
            rows.append({'application': r['application_number'], 'sponsor': r.get('sponsor_name', ''),
                         'date': s['submission_status_date'], 'class': s.get('submission_class_code', ''),
                         'active_ingredients': '; '.join(gen), 'brands': '; '.join(brand)})
w = csv.DictWriter(open('analysis/018/d1_fda_approvals.csv', 'w'), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
hits = []
for row in rows:
    sp = norm(row['sponsor'])
    for n, k in sponsor_keys.items():
        if len(k) >= 4 and sp.startswith(k[:min(len(k), 8)]):
            hits.append({**row, 'match': 'sponsor:' + n})
    text = (row['active_ingredients'] + ' ' + row['brands']).lower()
    for m in molecules:
        if re.search(r'\b' + re.escape(m.lower()), text):
            hits.append({**row, 'match': 'molecule:' + m})
w = csv.DictWriter(open('analysis/018/d1_fda_hits.csv', 'w'), fieldnames=list(rows[0]) + ['match']); w.writeheader(); w.writerows(hits)
nme = [r for r in rows if r['class'] == 'TYPE 1' or r['application'].startswith('BLA')]
summ = {'source_last_updated': d['meta']['last_updated'], 'original_approvals_2019_2026': len(rows),
        'nda_type1_or_bla': len(nme), 'hits': len(hits), 'latest_approval_date': max(r['date'] for r in rows)}
json.dump(summ, open('analysis/018/d1_summary.json', 'w'), indent=1); print(summ)
for h in hits: print(h)
