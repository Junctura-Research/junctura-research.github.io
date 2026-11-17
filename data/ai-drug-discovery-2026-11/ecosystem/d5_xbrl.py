"""D5: SEC XBRL company facts (data.sec.gov) for the eight SEC filers of an earlier step. Lists every concept whose
name contains 'Royalt' or 'Software' with a nonzero USD value for a period ending 2021-01-01 to 2026-11-17.
Company facts carry no dimensions, so segment members (for example a software member of the revenue axis) are not
seen here; an earlier step read them from the XBRL instances."""
import sys, json
sys.path.insert(0, 'analysis/018'); import edgar_fts as E
CIK = {'Schrodinger': 1490978, 'Recursion': 1601830, 'Nurix': 1549595, 'Monte Rosa': 1826457, 'Kymera': 1815442,
       'Absci': 1672688, 'Generate': 2100782, 'Iambic': 1997038}
out = {}
for c, cik in CIK.items():
    try: d = json.loads(E._get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'))
    except Exception as e: out[c] = f'error {e}'; continue
    found = []
    for tax, concepts in d.get('facts', {}).items():
        for name, v in concepts.items():
            if 'royalt' in name.lower() or 'software' in name.lower():
                for unit, facts in v.get('units', {}).items():
                    nz = [f for f in facts if f.get('val') and '2021-01-01' <= f.get('end', '') <= '2026-11-17']
                    if nz: found.append({'concept': f'{tax}:{name}', 'unit': unit, 'n_facts': len(nz),
                                         'latest': max(nz, key=lambda f: f['end'])})
    out[c] = {'entity': d.get('entityName'), 'concepts': found}
    print(c, d.get('entityName'), [(f['concept'], f['latest']['end'], f['latest']['val'], f['latest'].get('form')) for f in found])
json.dump(out, open('analysis/018/d5_xbrl.json', 'w'), indent=1)
