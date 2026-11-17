"""Precision of an earlier step's OpenAlex pairing counts, from hand labels.
Usage: python -I precision.py <labels.csv> <an earlier step openalex_pubs.json> <out.csv>
Labels: R relevant, P peripheral, W wrong sense, U cannot judge (no abstract returned)."""
import csv, json, math, sys
from collections import Counter, defaultdict

labels, pubs, out = sys.argv[1:4]
counts = {k: sum(v["by_year"].values()) for k, v in json.load(open(pubs))["pairs"].items()}
lab = defaultdict(Counter)
datause = Counter()
for r in csv.DictReader(open(labels)):
    lab[r["pairing"]][r["label"]] += 1
    if r["label"] == "P" and "(data use)" in r["reason"]:
        datause[r["pairing"]] += 1


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0, c - h), min(1, c + h)


rows = []
for p, c in lab.items():
    n = sum(c.values())
    lo, hi = wilson(c["R"], n)
    rows.append({"pairing": p, "openalex_count_2019_2025": counts[p], "n": n,
                 "relevant": c["R"], "peripheral": c["P"], "wrong_sense": c["W"], "cannot_judge": c["U"],
                 "peripheral_data_use": datause[p],
                 "strict_precision": round(c["R"] / n, 3), "strict_ci95_low": round(lo, 3), "strict_ci95_high": round(hi, 3),
                 "lenient_precision": round((c["R"] + c["P"]) / n, 3),
                 "strict_excl_cannot_judge": round(c["R"] / (n - c["U"]), 3),
                 "strict_with_data_use": round((c["R"] + datause[p]) / n, 3),
                 "adjusted_count_strict": round(counts[p] * c["R"] / n),
                 "adjusted_count_strict_ci_low": round(counts[p] * lo),
                 "adjusted_count_strict_ci_high": round(counts[p] * hi),
                 "adjusted_count_lenient": round(counts[p] * (c["R"] + c["P"]) / n)})
for key, col in [("openalex_count_2019_2025", "rank_raw"), ("adjusted_count_strict", "rank_strict"),
                 ("adjusted_count_lenient", "rank_lenient")]:
    for i, r in enumerate(sorted(rows, key=lambda r: -r[key]), 1):
        r[col] = i
rows.sort(key=lambda r: r["rank_raw"])
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
tot = Counter()
for c in lab.values(): tot.update(c)
print("all 300:", dict(tot))
for r in rows:
    print(r)
