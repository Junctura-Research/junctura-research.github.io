"""an earlier step A: corresponding authors of the C1 and C2 papers from Europe PMC full-text XML (where open).
Usage (repo root): python3 analysis/017/corresp.py → raw/fulltext/<key>.xml, corresp.json"""
import json, re, requests
from bs4 import BeautifulSoup
D = 'analysis/017/'
P = {'rentosertib': '10.1038/s41591-025-03743-2', 'NX-5948': '10.64898/2026.08.01.740538',
     'bamlanivimab': '10.1126/scitranslmed.abf1906', 'AlphaFold2': '10.1038/s41586-021-03819-2', 'AlphaFold3': '10.1038/s41586-024-07487-w'}
E = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
out = {}
for k, doi in P.items():
    res = requests.get(E + 'search', params={'query': f'DOI:"{doi}"', 'format': 'json', 'resultType': 'core'}, timeout=60).json()['resultList']['result']
    pmcid = next((x.get('pmcid') for x in res if x.get('pmcid')), None)
    rec = dict(doi=doi, pmcid=pmcid, open_full_text=False, corresponding=[], method='')
    if pmcid:
        x = requests.get(E + f'{pmcid}/fullTextXML', timeout=120)
        if x.status_code == 200 and '<article' in x.text:
            open(D + f'raw/fulltext/{k}.xml', 'w').write(x.text); rec['open_full_text'] = True
            soup = BeautifulSoup(x.text, 'lxml-xml')
            ids = {c.get('id') for c in soup.find_all('corresp')}
            # some articles mark corresponding authors by an author-notes footnote reading "Corresponding author"
            ids |= {f.get('id') for f in soup.find_all('fn') if 'Corresponding author' in f.get_text()}
            # authors: contrib-type="author", or plain <contrib> inside an author contrib-group (AlphaFold 3 markup)
            authors = soup.find_all('contrib', {'contrib-type': 'author'}) or [c for g in soup.find_all('contrib-group', {'content-type': 'author'}) for c in g.find_all('contrib')]
            for c in authors:
                xr = [r.get('rid') for r in c.find_all('xref') if r.get('ref-type') in ('corresp', 'author-notes')]
                if c.get('corresp') == 'yes' or any(r in ids for r in xr) or c.find('xref', {'ref-type': 'corresp'}):
                    n = c.find('name')
                    if n: rec['corresponding'].append(((n.find('surname').text if n.find('surname') else '') + ' ' + (n.find('given-names').text if n.find('given-names') else '')).strip())
            rec['method'] = 'contrib corresp="yes", xref ref-type="corresp", or xref to a "Corresponding author" footnote'
            rec['corresp_text'] = [re.sub(r'\s+', ' ', c.get_text(' ')) for c in soup.find_all('corresp')][:5]
    out[k] = rec; print(k, pmcid, rec['open_full_text'], rec['corresponding'], rec.get('corresp_text'))
json.dump(out, open(D + 'corresp.json', 'w'), indent=1)
