"""Follow-up of D1 (Denali tividenofusp alfa) and D3 (Eikon EIK1001): every SEC filing naming the molecule,
2024-01-01 to 2026-11-17, first 40 hits per query; sentences that name it within the same sentence as an AI term, plus origin sentences."""
import sys, re, json
sys.path.insert(0, '.'); import edgar_fts as E
AI = re.compile(r'artificial intelligence|machine learning|\bAI\b|deep learning|neural network|\bgenerative\b', re.I)
ORIG = re.compile(r'acquir|in-licens|licensed|originat|discover', re.I)
out = {}
for mol, qs in {'EIK1001': ['"EIK1001"', '"EIK-1001"'], 'tividenofusp alfa / DNL310': ['"tividenofusp"', '"DNL310"']}.items():
    hits = {}
    for q in qs:
        for h in E.search(q, '2024-01-01', '2026-11-17', max_hits=40): hits[h['url']] = h
    pat = re.compile('|'.join(re.escape(q.strip('"')) for q in qs), re.I)
    ai_s, orig_s = [], []
    for url, h in hits.items():
        if url.endswith('.xml'): continue
        for s in E.sentences(E.text(url)):
            if pat.search(s) and len(s) < 1200:
                if AI.search(s): ai_s.append((h['date'], h['form'], h['filer'][:30], url, s))
                elif ORIG.search(s): orig_s.append((h['date'], h['form'], h['filer'][:30], url, s))
    out[mol] = {'filings': len(hits), 'filers': sorted({h['filer'] for h in hits.values()}),
                'ai_sentences': ai_s[:20], 'n_ai_sentences': len(ai_s), 'origin_sentences': list({s[4][:300]: s for s in orig_s}.values())[:8]}
json.dump(out, open('ai_wording_checks.json', 'w'), indent=1)
for m, v in out.items():
    print(m, v['filings'], v['filers'], 'AI sentences:', v['n_ai_sentences'])
    for s in v['ai_sentences'][:6]: print('  AI>', s[0], s[1], s[4][:300])
    for s in v['origin_sentences'][:5]: print('  OR>', s[0], s[1], s[4][:300])
