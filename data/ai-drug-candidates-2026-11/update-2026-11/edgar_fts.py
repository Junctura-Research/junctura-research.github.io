"""Shared helpers: SEC EDGAR full-text search and document text, cached under raw/ (cache not committed)."""
import json, os, re, time, hashlib, html, requests
from bs4 import BeautifulSoup
H = {'User-Agent': 'Junctura Research juncturaresearch@gmail.com'}
CACHE = 'raw/cache'; os.makedirs(CACHE, exist_ok=True)
_last = [0.0]
def _get(url, params=None):
    key = hashlib.sha1((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    p = os.path.join(CACHE, key)
    if os.path.exists(p): return open(p, encoding='utf-8').read()
    wait = 0.15 - (time.time() - _last[0])
    if wait > 0: time.sleep(wait)
    for i in range(3):
        r = requests.get(url, params=params, headers=H, timeout=60); _last[0] = time.time()
        if r.status_code == 200: break
        time.sleep(2)
    r.raise_for_status()
    open(p, 'w', encoding='utf-8').write(r.text); return r.text
def search(q, start, end, forms=None, max_hits=500):
    out, frm = [], 0
    while frm < max_hits:
        params = {'q': q, 'dateRange': 'custom', 'startdt': start, 'enddt': end, 'from': frm}
        if forms: params['forms'] = forms
        d = json.loads(_get('https://efts.sec.gov/LATEST/search-index', params))
        hits = d['hits']['hits']
        for h in hits:
            s = h['_source']; adsh, fn = h['_id'].split(':', 1)
            out.append({'adsh': adsh, 'file': fn, 'form': s.get('form'), 'date': s.get('file_date'),
                        'filer': '; '.join(s.get('display_names', [])), 'cik': s.get('ciks', [''])[0].lstrip('0'),
                        'url': f"https://www.sec.gov/Archives/edgar/data/{s.get('ciks', [''])[0].lstrip('0')}/{adsh.replace('-', '')}/{fn}"})
        frm += len(hits)
        if not hits or frm >= d['hits']['total']['value']: break
    return out[:max_hits]
def text(url):
    raw = _get(url)
    if url.lower().endswith(('.htm', '.html', '.xml')):
        raw = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
        raw = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
    return re.sub(r'\s+', ' ', raw)
def sentences(t):
    return re.split(r'(?<=[.;!?])\s+(?=[A-Z(“"])', t)
