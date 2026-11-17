"""V: Europe PMC title-and-abstract query on validation barriers (a review ruling), query fixed in the an earlier step plan.
argv[1] = 'main' or 'refined' (refined drops the validation/prospective clause; allowed once)."""
import sys, json, csv, requests
base = ('(TITLE:"artificial intelligence" OR TITLE:"machine learning" OR TITLE:"deep learning") AND TITLE:"drug discovery"'
        ' AND {val}(ABSTRACT:challenge* OR ABSTRACT:barrier* OR ABSTRACT:limitation*) AND PUB_TYPE:"review" AND PUB_YEAR:[2023 TO 2026]')
val = '(ABSTRACT:"validation" OR ABSTRACT:"prospective") AND ' if sys.argv[1] == 'main' else ''
q = base.format(val=val)
r = requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
                 params={'query': q, 'format': 'json', 'resultType': 'core', 'pageSize': 10, 'sort': 'CITED desc'}, timeout=60)
d = r.json()
rows = [{'rank': i + 1, 'id': x.get('id'), 'source': x.get('source'), 'doi': x.get('doi', ''), 'year': x.get('pubYear'),
         'cited': x.get('citedByCount'), 'journal': x.get('journalInfo', {}).get('journal', {}).get('title', ''),
         'title': x.get('title'), 'abstract': x.get('abstractText', '')} for i, x in enumerate(d['resultList']['result'])]
w = csv.DictWriter(open(f'analysis/018/v_{sys.argv[1]}.csv', 'w'), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump({'query': q, 'hitCount': d['hitCount'], 'http': r.status_code}, open(f'analysis/018/v_{sys.argv[1]}.json', 'w'), indent=1)
print(d['hitCount'])
for x in rows: print(x['rank'], x['year'], x['cited'], x['doi'], '|', x['title'])
