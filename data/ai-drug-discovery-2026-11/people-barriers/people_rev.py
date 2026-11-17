"""an earlier step A: re-apply an earlier step's People rule with C1 and C2 limited to first, last or corresponding authors
(the review, a review ruling; a rule revised after the data were seen). Corresponding authors from Europe PMC full-text XML
(corresp.json, and AlphaFold 2 in raw/fulltext/AlphaFold2.xml: Jumper, Hassabis). The NX-5948 preprint has no open
full text, so only its first and last authors count. C3 already allowed corresponding authors; AlphaFold 3's
corresponding authors (Jaderberg, Hassabis, Jumper) are now applied to C3 too an earlier step checked first and last only).
Ranking code is an earlier step's, unchanged. Usage (repo root): python3 analysis/017/people_rev.py → people_rev.csv, ranked_rev.csv, people_rev.json"""
import json, pandas as pd
D16, D = 'analysis/016/', 'analysis/017/'
df = pd.read_csv(D16 + 'people.csv').fillna('')
AF3 = '10.1038/s41586-024-07487-w'
ALLOWED = {  # (criterion, outcome substring) -> persons allowed an earlier step person labels)
    ('C1', 'rentosertib'): {'Xu Z [10.1038/s41591-025-03743-2]', 'Alex Zhavoronkov'},          # first+corresp; last+corresp
    ('C1', 'NX-5948'): {'Noviski M [10.64898/2026.08.01.740538]', 'Cohen F [10.64898/2026.08.01.740538]'},  # first; last
    ('C1', 'bamlanivimab'): {'Jones BE [10.1126/scitranslmed.abf1906]', 'Ester Falconer'},    # first+corresp; last+corresp
    ('C2', 'Isomorphic'): {'Josh Abramson', 'John Jumper', 'Demis Hassabis', f'Jaderberg M [{AF3}]'},  # first; last+corresp; corresp; corresp
}
keep = []
for _, r in df.iterrows():
    k = next((k for k in ALLOWED if r.criterion == k[0] and k[1] in r.outcome and 'doi.org' in r.url), None)
    keep.append(k is None or r.person in ALLOWED[k])
rev = df[keep].copy()
rev = pd.concat([rev, pd.DataFrame([dict(person=f'Jaderberg M [{AF3}]', criterion='C3', outcome='AlphaFold (used in Isomorphic deals with Lilly and Novartis; Insilico CDK20 hit)',
      evidence=f'corresponding author, {AF3}', strength=3, url='https://doi.org/' + AF3, quote='', file='', note='added an earlier step')])])
rev['person'] = rev.person.replace({f'Jaderberg M [{AF3}]': 'Max Jaderberg', 'Xu Z [10.1038/s41591-025-03743-2]': 'Zuojun Xu',
                                     'Jones BE [10.1126/scitranslmed.abf1906]': 'Bryan E. Jones'})
rev.to_csv(D + 'people_rev.csv', index=False)
pool = pd.read_csv(D16 + 'pool.csv'); pm = pool[pool.reading == 'main']
CO_ALIAS = {'Atomwise (Numerion Labs)': 'Atomwise'}
def outcomes(g):  # an earlier step's function, unchanged
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
rk.to_csv(D + 'ranked_rev.csv', index=False)
top = rk[rk['rank'] <= 10]
out = dict(qualifying_people=len(rk), by_n_criteria=rk.n_criteria.value_counts().sort_index().to_dict(), top10=top.to_dict('records'),
           tied_at_cut=int((rk['rank'] == top['rank'].max()).sum()), cut_rank=int(top['rank'].max()),
           sensitivity_all_coauthors=json.load(open(D16 + 'summary.json'))['qualifying_people'])
json.dump(out, open(D + 'people_rev.json', 'w'), indent=1, default=str)
print(rk.head(16).to_string()); print({k: v for k, v in out.items() if k != 'top10'})
