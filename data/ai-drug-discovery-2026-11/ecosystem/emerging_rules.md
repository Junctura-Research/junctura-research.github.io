# Emerging Companies rules

Copied word for word from the research notebook: the entry rule fixed in cycle 011 (notebook/011-coverage-audit.md, "Rule 2"), and the reviewer's direction on Variational AI (pull request #26, notebook/STATE.md). The rule refers to the significant-company rule (Rule 1) and the company definition (Rule 0) of the same entry. The dated log cited as analysis/011/emerging_log.csv is published, as updated in cycle 013, as emerging_log_013.csv in this folder.

## Rule 2 — Emerging Companies entry rule (reviewer, PR #21 addendum)

An AI drug-discovery company (Rule 0) that is **not** significant under Rule 1, and was founded on or after 2021-11-17 or made its first disclosed financing on or after that date, enters if it meets at least one of:

- **E1:** a disclosed deal of any size with one of the 20 largest drugmakers;
- **E2:** a first candidate entering a clinical trial (registry entry or company statement);
- **E3:** a disclosed single financing round of at least $50 million;
- **E4:** a peer-reviewed paper (not a preprint), with company authors, stating that its platform produced a molecule;
- **E5:** a non-dilutive grant or award of at least $5 million from a government body (for example NIH, ARPA-H, BARDA, DOE, EU Horizon or EIC) or a major charitable funder (for example Wellcome, Gates Foundation, CEPI).

**Content:** one line per company: what it claims (labeled as a company claim), the qualifying evidence with a source, and the date. No assessment of team, prospects or value; none of the wording "to watch", "promising" or "opportunity".
**Size:** at most 15. If more qualify, rank by the number of criteria met, then by the date of the most recent qualifying evidence (newest first), then alphabetically. Those ranked 16 and below are listed as "qualified, not listed" in the analysis data, not in public text.
**Moves:** a company moves to the significant list when it meets Rule 1. It is removed after three years with no new qualifying evidence. Every addition, move and removal is logged with its date in `analysis/011/emerging_log.csv`. All entries this cycle are dated 2026-11-17.

## Reviewer direction on PR #26 (Variational AI)

Variational AI stays on the Emerging list, flagged (earliest financing announced exactly five years before the as-of date; it leaves at the first update unless new evidence appears).
