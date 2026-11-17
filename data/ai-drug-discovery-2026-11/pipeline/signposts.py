"""an earlier step S: open ClinicalTrials.gov trials for active AI-linked candidates and the Phase 3 tiers.
Rules fixed in the research record Usage (repo root): python3 analysis/017/signposts.py
Writes raw/ctgov_<term>.json, raw/ctgov_nct.json, trials_open.csv."""
import json, os, re, time, requests, pandas as pd
D = 'analysis/017/'
API = 'https://clinicaltrials.gov/api/v2/studies'
OPEN = {'RECRUITING', 'ACTIVE_NOT_RECRUITING', 'NOT_YET_RECRUITING', 'ENROLLING_BY_INVITATION'}
c = pd.read_csv('analysis/014/cohort_32.csv')
act = c[c.outcome == 'active']
# search terms per candidate: code names and generic names (from cohort labels), plus Phase 3 tier candidates outside the cohort
TERMS = {}
for cand in act.candidate:
    names = re.findall(r'[A-Za-z0-9\-]+', cand.replace('(', ' ').replace(')', ' '))
    TERMS[cand] = [n for n in names if n.lower() not in ('rec', 'now')]
TERMS['GTAEXS617 (REC-617)'] = ['GTAEXS617', 'GTAEXS-617', 'REC-617']
TERMS['ISM001-055 (rentosertib)'] = ['ISM001-055', 'rentosertib']
TERMS['GB-0895 (Generate; Phase 3 tier, not in cohort)'] = ['GB-0895']
TERMS['zovegalisib / RLY-2608 (Relay; borderline tier)'] = ['RLY-2608', 'zovegalisib']
TERMS['aleniglipron / GSBR-1290 (Structure; borderline tier)'] = ['aleniglipron', 'GSBR-1290']
studies = {}
for cand, terms in TERMS.items():
    for t in terms:
        js = requests.get(API, params={'query.intr': t, 'pageSize': 100}, timeout=60).json()
        # fallback (fixed before data was re-read): free-text query when the intervention field gives nothing
        jt = requests.get(API, params={'query.term': t, 'pageSize': 100}, timeout=60).json()
        json.dump({'intr': js, 'term': jt}, open(D + f'raw/ctgov_{re.sub(r"[^A-Za-z0-9]", "_", t)}.json', 'w'))
        for s in js.get('studies', []) + jt.get('studies', []):
            ps = s['protocolSection']; nct = ps['identificationModule']['nctId']
            ivs = ps.get('armsInterventionsModule', {}).get('interventions', [])
            names = ' '.join([i.get('name', '') + ' ' + ' '.join(i.get('otherNames', [])) for i in ivs])
            text = names + ' ' + (ps['identificationModule'].get('briefTitle') or '') + ' ' + (ps['identificationModule'].get('officialTitle') or '')
            if t.lower() not in text.lower():  # keep only trials naming the term in an intervention or title
                continue
            st = ps['statusModule']
            studies.setdefault(nct, dict(nct=nct, candidates=set(), title=ps['identificationModule'].get('briefTitle'),
                status=st.get('overallStatus'), phase='/'.join(ps.get('designModule', {}).get('phases', []) or []),
                sponsor=ps['sponsorCollaboratorsModule']['leadSponsor']['name'], start=st.get('startDateStruct', {}).get('date'),
                primary_completion=st.get('primaryCompletionDateStruct', {}).get('date'), pc_type=st.get('primaryCompletionDateStruct', {}).get('type'),
                completion=st.get('completionDateStruct', {}).get('date'), c_type=st.get('completionDateStruct', {}).get('type')))['candidates'].add(cand)
        time.sleep(0.3)
rows = [dict(v, candidates='; '.join(sorted(v['candidates']))) for v in studies.values()]
df = pd.DataFrame(rows).sort_values(['candidates', 'primary_completion'])
df.to_csv(D + 'trials_all.csv', index=False)
df[df.status.isin(OPEN)].to_csv(D + 'trials_open.csv', index=False)
print(len(df), 'trials naming a candidate;', df.status.isin(OPEN).sum(), 'open')
