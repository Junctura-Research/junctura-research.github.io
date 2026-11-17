"""an earlier step E: one scripted request for EMA's reflection paper on AI in the medicinal product lifecycle (a review ruling).
Usage (repo root): python3 analysis/017/ema_retry.py → raw/ema/result.json (+ PDF and text if it opens)"""
import json, subprocess, requests
D = 'analysis/017/raw/ema/'
URL = 'https://www.ema.europa.eu/en/documents/scientific-guideline/reflection-paper-use-artificial-intelligence-ai-medicinal-product-lifecycle_en.pdf'
r = requests.get(URL, headers={'User-Agent': 'Junctura Research juncturaresearch@gmail.com'}, timeout=120)
res = dict(url=URL, status=r.status_code, content_type=r.headers.get('content-type'), bytes=len(r.content), retrieved='2026-11-17')
if r.status_code == 200 and r.content[:4] == b'%PDF':
    open(D + 'reflection_paper.pdf', 'wb').write(r.content)
    subprocess.run(['pdftotext', '-layout', D + 'reflection_paper.pdf', D + 'reflection_paper.txt'])
json.dump(res, open(D + 'result.json', 'w'), indent=1); print(res)
