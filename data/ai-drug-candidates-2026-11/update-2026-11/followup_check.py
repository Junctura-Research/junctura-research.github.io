"""Coverage audit, correction step: recount trial-entry years and follow-up after the first-trial date fix.

Usage (from this folder): python followup_check.py -> followup_check.json
Input: ../checks/headline.json (16-candidate headline).
Follow-up = years from the first trial date (first 7 or 10 characters) to the Note's as-of date, 2026-11-16.
Rows whose start reads "YYYY or earlier" are reported separately (bound only).
"""
import json, datetime
H = json.load(open("../checks/headline.json"))["headline_16"]
AS_OF = datetime.date(2026, 11, 16)
rows, bounds = {}, {}
for c, s in H["first_trial_by_candidate"].items():
    if "or earlier" in s[:20]:
        bounds[c] = s
        continue
    d = s[:10] if s[7:8] == "-" else s[:7] + "-01"
    y = (AS_OF - datetime.date.fromisoformat(d)).days / 365.25
    rows[c] = round(y, 2)
by_end_2022 = sum(v for k, v in H["first_trial_year"].items() if int(k[:4]) <= 2022)
out = {"entered_trials_by_end_2022": by_end_2022, "first_trial_year": H["first_trial_year"],
       "followup_years_dated": dict(sorted(rows.items(), key=lambda kv: kv[1])),
       "followup_min_max_dated": [min(rows.values()), max(rows.values())], "start_is_bound_only": bounds}
json.dump(out, open("followup_check.json", "w"), indent=1)
print(json.dumps(out, indent=1))
