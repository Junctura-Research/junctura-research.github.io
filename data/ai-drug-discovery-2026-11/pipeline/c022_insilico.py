"""Cycle 022: ClinicalTrials.gov (API v2) records of trials sponsored by Insilico Medicine, with start dates, phases,
status and interventions; flags trials that started on or before 2023-12-31 (cohort entry rule, part a).
Usage (repo root): python3 analysis/022/insilico.py   Output: analysis/022/insilico_trials.json"""
import json, requests
url = 'https://clinicaltrials.gov/api/v2/studies'
rows, tok = [], None
while True:
    p = {'query.spons': 'Insilico Medicine', 'pageSize': 100, 'format': 'json'}
    if tok: p['pageToken'] = tok
    d = requests.get(url, params=p, timeout=60).json()
    for s in d['studies']:
        ps = s['protocolSection']
        rows.append({'nct': ps['identificationModule']['nctId'], 'title': ps['identificationModule'].get('briefTitle'),
                     'sponsor': ps['sponsorCollaboratorsModule']['leadSponsor']['name'],
                     'start': ps['statusModule'].get('startDateStruct', {}).get('date'),
                     'status': ps['statusModule'].get('overallStatus'),
                     'phases': ps.get('designModule', {}).get('phases'),
                     'interventions': [i.get('name') for i in ps.get('armsInterventionsModule', {}).get('interventions', [])]})
    tok = d.get('nextPageToken')
    if not tok: break
rows.sort(key=lambda r: r['start'] or '')
for r in rows: r['started_by_2023'] = bool(r['start']) and r['start'] <= '2023-12-31'
json.dump(rows, open('analysis/022/insilico_trials.json', 'w'), indent=1)
for r in rows: print(r['start'], r['nct'], r['status'], r['phases'], r['interventions'], '|', r['sponsor'])
