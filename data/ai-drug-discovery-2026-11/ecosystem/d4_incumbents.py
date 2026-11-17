"""D4: SEC full-text search, 2019-01-01 to 2026-11-17, for each drugmaker that misses the strict inclusion rule,
together with an AI term and "upfront" (all terms required), first 25 hits per query. Filings by the drugmaker
itself are dropped. Passages with the drugmaker name within 400 characters of an AI term and a deal word are
written to d4_passages.csv for hand reading."""
import sys, re, csv, json
sys.path.insert(0, 'analysis/018'); import edgar_fts as E
DM = {'Amgen': 'Amgen', 'Teva': 'Teva Pharmaceutical', 'CSL': 'CSL Behring', 'Regeneron': 'Regeneron'}
AI = ['"artificial intelligence"', '"machine learning"']
AIR = re.compile(r'artificial intelligence|machine learning|\bAI\b|deep learning', re.I)
DEAL = re.compile(r'collaborat|licens|agreement', re.I); MONEY = re.compile(r'upfront|up-front|milestone|\$\s?\d', re.I)
rows, summ = [], {}
for key, name in DM.items():
    hits = {}
    for a in AI:
        for h in E.search(f'"{name}" {a} "upfront"', '2019-01-01', '2026-11-17', max_hits=25): hits[h['url']] = h
    own = [u for u, h in hits.items() if key.lower() in h['filer'].lower()]
    n = 0
    for url, h in hits.items():
        if url in own or url.endswith('.xml'): continue
        t = E.text(url)
        for m in re.finditer(re.escape(name), t):
            w = t[max(0, m.start() - 400): m.end() + 400]
            if AIR.search(w) and DEAL.search(w) and MONEY.search(w):
                n += 1; rows.append({'drugmaker': key, 'filer': h['filer'][:60], 'form': h['form'], 'date': h['date'], 'url': url, 'passage': w})
    summ[key] = {'filings': len(hits), 'own_filings_dropped': len(own), 'passages': n,
                 'filers': sorted({h['filer'][:60] for u, h in hits.items() if u not in own})}
    print(key, summ[key]['filings'], n, flush=True)
w = csv.DictWriter(open('analysis/018/d4_passages.csv', 'w'), fieldnames=['drugmaker', 'filer', 'form', 'date', 'url', 'passage']); w.writeheader(); w.writerows(rows)
json.dump(summ, open('analysis/018/d4_summary.json', 'w'), indent=1)
