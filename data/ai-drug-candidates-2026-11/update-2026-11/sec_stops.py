"""D2: SEC full-text search (filings dated 2025-11-17 to 2026-11-17) for each cohort candidate not recorded
as discontinued, plus the Phase 3 tier candidates outside the cohort. Sentences naming the candidate and a
stop word are written to d2_stop_sentences.csv for hand reading."""
import csv, json, re, sys
sys.path.insert(0, '.'); import edgar_fts as E
C = {'DSP-0038': ['"DSP-0038"'], 'DSP-2342': ['"DSP-2342"'], 'EXS4318': ['"EXS4318"', '"EXS-4318"'],
     'GTAEXS617 (REC-617)': ['"REC-617"', '"GTAEXS617"', '"GTAEXS-617"'], 'SGR-1505': ['"SGR-1505"'],
     'MRT-2359': ['"MRT-2359"'], 'NX-2127 (zelebrudomide)': ['"NX-2127"', '"zelebrudomide"'], 'NX-1607': ['"NX-1607"'],
     'NX-5948 (bexobrutideg)': ['"NX-5948"', '"bexobrutideg"'], 'EVX-01': ['"EVX-01"'], 'EVX-02': ['"EVX-02"'],
     'ISM001-055 (rentosertib)': ['"rentosertib"', '"ISM001-055"'], 'MDR-001': ['"MDR-001"'], 'AC0682': ['"AC0682"'],
     'AC176': ['"AC176"'], 'AC699': ['"AC699"'], 'AC676': ['"AC676"'], 'AU-007 (imneskibart)': ['"AU-007"', '"imneskibart"'],
     'ADG126 (muzastotug)': ['"ADG126"', '"muzastotug"'], 'ADG116': ['"ADG116"'], 'ADG206': ['"ADG206"'],
     'PHI-101 (lasmotinib)': ['"PHI-101"', '"lasmotinib"'], 'DF-003': ['"DF-003"'], 'DF-006': ['"DF-006"'],
     'GB-0895 (tier)': ['"GB-0895"'], 'zovegalisib / RLY-2608 (tier)': ['"zovegalisib"', '"RLY-2608"'],
     'aleniglipron / GSBR-1290 (tier)': ['"aleniglipron"', '"GSBR-1290"']}
STOP = re.compile(r'discontinu|deprioriti|terminat|\bpaus|\bhalt|no longer|wind(?:ing)? down|ceas|clinical hold|out-licens|seek(?:ing)? a partner', re.I)
summ, rows = {}, []
for cand, qs in C.items():
    hits = {}
    for q in qs:
        for h in E.search(q, '2025-11-17', '2026-11-17'): hits[h['url']] = h
    terms = [q.strip('"') for q in qs]
    pat = re.compile('|'.join(re.escape(t) for t in terms), re.I)
    n_sent = 0
    for url, h in hits.items():
        if url.lower().endswith('.xml'): continue  # XBRL instances duplicate the HTML text
        try: t = E.text(url)
        except Exception as e: rows.append({'candidate': cand, **h, 'sentence': f'FETCH ERROR {e}'}); continue
        for s in E.sentences(t):
            if pat.search(s) and STOP.search(s) and len(s) < 1500:
                n_sent += 1; rows.append({'candidate': cand, **h, 'sentence': s.strip()})
    summ[cand] = {'filings': len(hits), 'filers': sorted({h['filer'] for h in hits.values()}), 'stop_sentences': n_sent}
    print(cand, len(hits), n_sent, flush=True)
fields = ['candidate', 'adsh', 'file', 'form', 'date', 'filer', 'cik', 'url', 'sentence']
w = csv.DictWriter(open('sec_stop_sentences.csv', 'w'), fieldnames=fields); w.writeheader(); w.writerows(rows)
json.dump(summ, open('sec_stop_search.json', 'w'), indent=1)
