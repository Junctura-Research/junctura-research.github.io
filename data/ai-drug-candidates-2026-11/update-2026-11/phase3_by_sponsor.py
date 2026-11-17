"""D3: ClinicalTrials.gov API v2 Phase 3 trials (any status, start 2015 or later) with a significant company
(significant_companies.csv) as lead sponsor or collaborator (query.spons). Output: d3_phase3_trials.csv."""
import csv, json, requests, time
sig = [r['company'] for r in csv.DictReader(open('significant_companies.csv'))]
alias = {'Generate': 'Generate Biomedicines', 'Iambic': 'Iambic Therapeutics', 'Odyssey': 'Odyssey Therapeutics',
         'Parabilis': 'Parabilis Medicines', 'Nurix': 'Nurix Therapeutics', 'Kymera': 'Kymera Therapeutics',
         'Monte Rosa': 'Monte Rosa Therapeutics', 'Recursion': 'Recursion Pharmaceuticals', 'Valo Health': 'Valo Health',
         'Eikon Therapeutics': 'Eikon Therapeutics', 'Exscientia': 'Exscientia', 'Insilico Medicine': 'Insilico'}
rows, per = [], {}
for c in sig:
    q = alias.get(c, c)
    params = {'query.spons': f'"{q}"', 'filter.advanced': 'AREA[Phase]PHASE3 AND AREA[StartDate]RANGE[2015-01-01,MAX]',
              'pageSize': 200, 'fields': 'NCTId,BriefTitle,OverallStatus,Phase,StartDate,LeadSponsorName,CollaboratorName,InterventionName'}
    r = requests.get('https://clinicaltrials.gov/api/v2/studies', params=params, timeout=60); time.sleep(0.3)
    if r.status_code != 200: per[c] = f'HTTP {r.status_code}'; continue
    st = r.json().get('studies', []); per[c] = len(st)
    for s in st:
        p = s['protocolSection']; sc = p.get('sponsorCollaboratorsModule', {})
        rows.append({'company_query': q, 'nct': p['identificationModule']['nctId'], 'title': p['identificationModule'].get('briefTitle', ''),
                     'status': p.get('statusModule', {}).get('overallStatus', ''), 'phase': ';'.join(p.get('designModule', {}).get('phases', [])),
                     'start': p.get('statusModule', {}).get('startDateStruct', {}).get('date', ''),
                     'lead': sc.get('leadSponsor', {}).get('name', ''), 'collaborators': ';'.join(x['name'] for x in sc.get('collaborators', [])),
                     'interventions': ';'.join(i['name'] for i in p.get('armsInterventionsModule', {}).get('interventions', []))})
w = csv.DictWriter(open('phase3_by_sponsor.csv', 'w'), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump({'per_company': per, 'trials': len(rows), 'unique_nct': len({r['nct'] for r in rows})}, open('phase3_by_sponsor_summary.json', 'w'), indent=1)
print({k: v for k, v in per.items() if v}); print(len(rows))
for r in rows: print(r['company_query'], '|', r['nct'], r['status'], r['start'], '|', r['lead'][:30], '|', r['collaborators'][:40], '|', r['interventions'][:90])
