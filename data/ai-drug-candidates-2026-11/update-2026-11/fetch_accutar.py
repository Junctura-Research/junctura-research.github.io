"""Fetches: (1) ClinicalTrials.gov why-stopped text for Accutar's four terminated trials;
(2) AbCellera (CIK 1703057) XBRL company facts, revenue and royalty concepts, from SEC EDGAR.
Usage (from this folder): python3 fetch_accutar.py -> accutar_trials.json, abcellera_xbrl.json (the second file is not used by the Note)"""
import json, requests, time
UA = {'User-Agent': 'Junctura Research juncturaresearch@gmail.com'}
out = {}
for nct in ['NCT05080842', 'NCT05489679', 'NCT05241613', 'NCT05673109']:
    j = requests.get(f'https://clinicaltrials.gov/api/v2/studies/{nct}', timeout=30).json()
    s = j['protocolSection']['statusModule']
    out[nct] = {'title': j['protocolSection']['identificationModule'].get('briefTitle'), 'overallStatus': s.get('overallStatus'),
                'whyStopped': s.get('whyStopped'), 'lastUpdate': s.get('lastUpdatePostDateStruct', {}).get('date'),
                'conditions': j['protocolSection'].get('conditionsModule', {}).get('conditions')}
json.dump(out, open('accutar_trials.json', 'w'), indent=1); print(json.dumps(out, indent=1))
j = requests.get('https://data.sec.gov/api/xbrl/companyfacts/CIK0001703057.json', headers=UA, timeout=60).json()
res = {'entity': j.get('entityName'), 'concepts': {}}
for tax, facts in j['facts'].items():
    for k, v in facts.items():
        if 'oyalt' in k or k in ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'):
            for unit, arr in v['units'].items():
                fy = [a for a in arr if a.get('fp') == 'FY' and a.get('form') == '10-K' and a.get('frame', '').startswith('CY') and len(a['frame']) == 6]
                res['concepts'][f'{tax}:{k}'] = {a['frame']: a['val'] for a in fy}
json.dump(res, open('abcellera_xbrl.json', 'w'), indent=1); print(json.dumps(res, indent=1))
