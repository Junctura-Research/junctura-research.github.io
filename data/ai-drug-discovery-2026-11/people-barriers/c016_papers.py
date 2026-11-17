"""Cycle 016: authors of candidate discovery papers and tool papers, from Europe PMC."""
import requests, json, time
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
H = {'User-Agent': 'Junctura Research research script (juncturaresearch@gmail.com)'}
Q = {
 'rentosertib': '(rentosertib OR "ISM001-055" OR (TNIK AND inhibitor AND fibrosis AND generative))',
 'NX-5948': '(bexobrutideg OR "NX-5948")',
 'GB-0895': '("GB-0895" OR GB0895)',
 'bamlanivimab': '("LY-CoV555" AND (discovery OR isolated OR neutralizing) AND AbCellera)',
 'bebtelovimab': '("LY-CoV1404")',
 'zovegalisib': '(zovegalisib OR "RLY-2608")',
 'aleniglipron': '(aleniglipron OR "GSBR-1290")',
 'AlphaFold2': 'DOI:"10.1038/s41586-021-03819-2"',
 'AlphaFold3': 'DOI:"10.1038/s41586-024-07487-w"',
 'RoseTTAFold': 'DOI:"10.1126/science.abj8754"',
 'RFdiffusion': 'DOI:"10.1038/s41586-023-06415-8"',
 'ESM-2': 'DOI:"10.1126/science.ade2574"',
}
out = {}
for k, q in Q.items():
    r = requests.get(API, params=dict(query=q, format='json', resultType='core', pageSize=25), headers=H, timeout=60)
    res = r.json().get('resultList', {}).get('result', [])
    out[k] = [dict(title=x.get('title'), journal=(x.get('journalInfo') or {}).get('journal', {}).get('title'),
                   year=x.get('pubYear'), doi=x.get('doi'), pmid=x.get('pmid'), source=x.get('source'),
                   pubtype=(x.get('pubTypeList') or {}).get('pubType'),
                   authors=[a.get('fullName') for a in (x.get('authorList') or {}).get('author', [])],
                   affiliations=sorted({aff.get('affiliation','') for a in (x.get('authorList') or {}).get('author', [])
                                        for aff in (a.get('authorAffiliationDetailsList') or {}).get('authorAffiliation', [])})[:15])
              for x in res]
    print(k, r.status_code, len(res))
    time.sleep(0.5)
json.dump(out, open('analysis/016/papers.json', 'w'), indent=1, ensure_ascii=False)
