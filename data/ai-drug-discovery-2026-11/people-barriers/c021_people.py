"""Cycle 021: re-code Feng Ren's C1 from the 2024 rentosertib design paper (PR #34 point 4).
Ren F is first author of "A small-molecule TNIK inhibitor targets fibrosis in preclinical and clinical models"
(Nature Biotechnology, doi 10.1038/s41587-024-02143-0; Europe PMC record saved in analysis/021/raw/ren_paper.json),
which describes rentosertib's design. Under the PR #30 rule (first, last or corresponding author) he meets C1.
Ranking: cycle 016/017 code, unchanged (imported from analysis/017/people_rev.py logic, re-run on the revised table).
Usage (repo root): python3 analysis/021/people.py -> analysis/021/people_021.csv, ranked_021.csv, people_021.json"""
import json, pandas as pd
paper = json.load(open('analysis/021/raw/ren_paper.json'))
assert paper['authors'][0] == 'Ren F' and paper['authors'][-1] == 'Zhavoronkov A'
rev = pd.read_csv('analysis/017/people_rev.csv').fillna('')
assert not ((rev.person == 'Feng Ren') & (rev.criterion == 'C1')).any()
add = dict(person='Feng Ren', criterion='C1', outcome='rentosertib (ISM001-055) design paper',
           evidence='first author, 10.1038/s41587-024-02143-0', strength=3, url='https://doi.org/10.1038/s41587-024-02143-0',
           quote='', file='analysis/021/raw/ren_paper.json', note='added cycle 021 (PR #34)')
# Zhavoronkov is last author of the same paper; his C1 already stands (Phase 2a paper), so no change in his criteria count.
rev = pd.concat([rev, pd.DataFrame([add])], ignore_index=True)
rev.to_csv('analysis/021/people_021.csv', index=False)
D16 = 'analysis/016/'
pool = pd.read_csv(D16 + 'pool.csv'); pm = pool[pool.reading == 'main']
CO_ALIAS = {'Atomwise (Numerion Labs)': 'Atomwise'}
def outcomes(g):  # cycle 016's function, unchanged
    cos = {CO_ALIAS.get(c, c) for c in g[g.criterion == 'C4'].outcome}
    items = set(pm[pm.company.isin(cos)].item)
    for o in g[g.criterion.isin(['C1', 'C2', 'C3'])].outcome:
        if 'rentosertib' in o: items |= set(pm[pm.company == 'Insilico Medicine'].item) & {i for i in pm.item if 'rentosertib' in i}
        if 'NX-5948' in o: items |= {i for i in pm.item if 'NX-5948' in i}
        if 'bamlanivimab' in o: items |= {i for i in pm.item if 'bamlanivimab' in i}
        if 'Isomorphic' in o or 'AlphaFold' in o: items |= set(pm[pm.company == 'Isomorphic Labs'].item)
        if 'Dyno' in o: items |= set(pm[pm.company == 'Dyno Therapeutics'].item)
    return len(items)
rk = (rev.groupby('person').apply(lambda g: pd.Series(dict(criteria=','.join(sorted(set(g.criterion))), n_criteria=g.criterion.nunique(),
      strength=g.strength.max(), outcomes=outcomes(g)))).reset_index().sort_values(['n_criteria', 'strength', 'outcomes'], ascending=False))
rk['rank'] = rk[['n_criteria', 'strength', 'outcomes']].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)
rk.to_csv('analysis/021/ranked_021.csv', index=False)
two = rk[rk.n_criteria >= 2]
out = dict(qualifying_people=len(rk), by_n_criteria=rk.n_criteria.value_counts().sort_index().to_dict(),
           two_or_more=two[['person', 'criteria', 'n_criteria', 'rank']].to_dict('records'), single_criterion=int((rk.n_criteria == 1).sum()))
json.dump(out, open('analysis/021/people_021.json', 'w'), indent=1, default=int); print(json.dumps(out, indent=1, default=int))
