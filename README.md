# junctura-research.github.io

Source of [juncturaresearch.com](https://juncturaresearch.com), the public site of Junctura Research. It is a [Quarto](https://quarto.org) website, built and published to GitHub Pages by GitHub Actions on every push to `main`.

Drafts are written and validated in the private research repository. Only documents the reviewer has approved are copied here.

## Layout

| Path | What it is |
| --- | --- |
| `index.qmd` | Home page and the list of publications (built automatically from `research/`) |
| `about.qmd` | How the research is produced and directed |
| `corrections.qmd` | Every published error, the date found, and the fix |
| `research/<slug>.qmd` | One published document. Renders to `/research/<slug>.html` and `/research/<slug>.pdf` |
| `research/_metadata.yml` | Settings for every document: HTML and PDF output, the type and as-of line |
| `data/<slug>/` | The document's frozen data appendix, served as plain files at `/data/<slug>/` |
| `filters/doc-meta.lua` | Adds "Research Note · Evidence as of …" and the PDF link to each document; adds the Google Scholar PDF tag |
| `scripts/data_index.py` | Runs after each render; writes a file-listing page into every folder under `_site/data/` so folder links work |
| `scripts/check_links.py` | Fails the build if any internal link (including `https://juncturaresearch.com/...` links) points to a missing file |
| `_quarto.yml` | Site settings: navigation, footer disclaimer, search, sitemap |
| `.github/workflows/publish.yml` | Build on every pull request; build and publish on `main` |

## Publishing an approved document

1. Copy the approved `.qmd` from the research repository to `research/<slug>.qmd`, using the folder name as the slug (e.g. `papers/ai-drug-candidates-2026-11/note.qmd` becomes `research/ai-drug-candidates-2026-11.qmd`).
2. Copy its `data/` folder to `data/<slug>/`. Do not add or rename files inside it; it is frozen.
3. Check the front matter: `title`, `subtitle`, `description`, `date`, `as-of`, `document-type` (`research-note`, `intersection-report` or `report-update`), `google-scholar: true`.
4. Open a pull request. The build renders the site, writes the data folder indexes and checks every internal link. Download the `site-preview` artifact from the run to look at it.
5. Merge. The site updates within a few minutes.

A Report Update edits the report's own file in place: new `as-of` date and a dated changelog entry in the report. A correction also gets a row on `corrections.qmd`.

## Building locally

Install Quarto 1.8, then `quarto preview` (live) or `quarto render` followed by `python3 scripts/check_links.py _site`. The PDF uses Typst, which ships with Quarto; the first render downloads one Typst package.

## One-time settings

- Settings → Pages → Build and deployment → Source: **GitHub Actions**.
- Settings → Pages → Custom domain: `juncturaresearch.com`; tick **Enforce HTTPS** once the certificate is issued.
