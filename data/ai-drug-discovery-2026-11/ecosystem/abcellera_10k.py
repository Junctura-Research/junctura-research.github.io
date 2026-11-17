"""Read AbCellera's 10-K filings (FY2021, FY2022, FY2025) from SEC EDGAR and extract sentences/rows mentioning royalt.
Usage (repo root): python3 -I analysis/020/abcellera_10k.py -> analysis/020/abcellera_royalty_lines.json"""
import json, re, requests, time
from bs4 import BeautifulSoup
UA = {'User-Agent': 'Junctura Research juncturaresearch@gmail.com'}
sub = requests.get('https://data.sec.gov/submissions/CIK0001703057.json', headers=UA, timeout=60).json()['filings']['recent']
tenk = [(sub['filingDate'][i], sub['accessionNumber'][i], sub['primaryDocument'][i], sub['reportDate'][i]) for i in range(len(sub['form'])) if sub['form'][i] == '10-K']
out = {}
for fd, acc, doc, rd in tenk:
    if rd[:4] not in ('2021', '2022', '2025'): continue
    url = f'https://www.sec.gov/Archives/edgar/data/1703057/{acc.replace("-", "")}/{doc}'
    time.sleep(0.3)
    t = BeautifulSoup(requests.get(url, headers=UA, timeout=120).text, 'lxml').get_text(' ')
    t = re.sub(r'\s+', ' ', t)
    hits = [t[max(0, m.start() - 250): m.end() + 250] for m in re.finditer(r'[Rr]oyalty revenue', t)]
    out[rd] = {'filed': fd, 'url': url, 'n_royalty_revenue': len(hits), 'snippets': hits[:8]}
json.dump(out, open('analysis/020/abcellera_royalty_lines.json', 'w'), indent=1)
for k, v in out.items(): print(k, v['filed'], v['url'], v['n_royalty_revenue']); [print('  >', s) for s in v['snippets'][:4]]
