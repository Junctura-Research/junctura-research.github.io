"""Cycle 023: openFDA Drugs@FDA search for the new candidates' names (cycle 022 name-based method).
Usage (repo root): python3 analysis/023/fda_check.py -> analysis/023/fda_check.json"""
import json, requests
out = {}
for nm in ['ISM3312', 'ISM3091', 'XL309', 'ISM8207']:
    q = f'openfda.generic_name:"{nm}"+openfda.brand_name:"{nm}"+products.active_ingredients.name:"{nm}"'
    r = requests.get(f'https://api.fda.gov/drug/drugsfda.json?search={q}&limit=5', timeout=60)
    out[nm] = {'http': r.status_code, 'matches': r.json().get('meta', {}).get('results', {}).get('total', 0) if r.status_code == 200 else 0}
json.dump(out, open('analysis/023/fda_check.json', 'w'), indent=1); print(out)
