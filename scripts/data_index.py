"""Post-render step: write a plain index.html into every folder under _site/data/.

GitHub Pages does not list folder contents, so without these pages a link to a
data folder (e.g. /data/<slug>/cohort/) would return 404. The data files
themselves are copied untouched by Quarto (resources: data/**); this script only
adds index pages to the output folder and never changes the source data.
"""

import html
import os
import sys
from pathlib import Path

DIRECTION = (
    "A human reviewer chooses the research topics and approves the direction of "
    "each investigation."
)


def human_size(n: int) -> str:
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def page(title: str, crumbs: str, intro: str, rows: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} – Junctura Research</title>
<meta name="description" content="{html.escape(title)}: files in a Junctura Research data appendix.">
<style>
body {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; max-width: 52rem; margin: 2rem auto; padding: 0 1rem; color: #222; line-height: 1.5; }}
a {{ color: #1a5fb4; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ text-align: left; padding: .3rem .6rem; border-bottom: 1px solid #ddd; font-size: .95rem; }}
td.size {{ text-align: right; white-space: nowrap; color: #555; }}
.crumbs {{ font-size: .9rem; color: #555; }}
footer {{ margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: .8rem; color: #555; }}
</style>
</head>
<body>
<p class="crumbs"><a href="/">Junctura Research</a> / {crumbs}</p>
<h1>{html.escape(title)}</h1>
{intro}
<table>
<thead><tr><th>Name</th><th style="text-align:right">Size</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
<footer>
<p><a href="/disclaimer.html">Disclaimer: research, not investment advice</a> · {DIRECTION} · <a href="/about.html">About</a> · <a href="/corrections.html">Corrections</a></p>
</footer>
</body>
</html>
"""


def build(site: Path) -> int:
    data_root = site / "data"
    if not data_root.is_dir():
        return 0
    count = 0
    for folder, dirnames, filenames in os.walk(data_root):
        folder = Path(folder)
        dirnames.sort()
        rel = folder.relative_to(site)  # e.g. data/ai-drug-candidates-2026-11/cohort
        parts = rel.parts

        # Breadcrumbs: each ancestor links to its own index.
        crumb_links = []
        for i in range(len(parts)):
            href = "/" + "/".join(parts[: i + 1]) + "/"
            label = html.escape(parts[i])
            crumb_links.append(label if i == len(parts) - 1 else f'<a href="{href}">{label}</a>')
        crumbs = " / ".join(crumb_links)

        intro = ""
        if len(parts) == 1:
            title = "Data appendices"
            intro = "<p>Each published document has a frozen data appendix with the code and data behind its computed numbers.</p>"
        else:
            slug = parts[1]
            title = "Data appendix: " + slug if len(parts) == 2 else "/".join(parts[1:])
            doc = site / "research" / f"{slug}.html"
            doc_link = (
                f'<p>Data appendix for <a href="/research/{slug}.html">the document published at /research/{slug}.html</a>'
                f' (<a href="/research/{slug}.pdf">PDF</a>). Files are frozen as of the document\'s as-of date and served as plain files.</p>'
                if doc.exists() else
                "<p>Files are frozen as of the document's as-of date and served as plain files.</p>"
            )
            readme = folder / "README.md"
            readme_note = (
                '<p>Start with <a href="README.md">README.md</a>, which describes every file.</p>'
                if readme.exists() else ""
            )
            intro = doc_link + readme_note

        rows = []
        if len(parts) > 1:
            rows.append('<tr><td><a href="../">../</a></td><td class="size"></td></tr>')
        for d in dirnames:
            rows.append(f'<tr><td><a href="{html.escape(d)}/">{html.escape(d)}/</a></td><td class="size"></td></tr>')
        for f in sorted(filenames):
            if f == "index.html":
                continue
            size = human_size((folder / f).stat().st_size)
            rows.append(f'<tr><td><a href="{html.escape(f)}">{html.escape(f)}</a></td><td class="size">{size}</td></tr>')

        out = folder / "index.html"
        if (Path(rel) / "index.html").exists():  # the source data has its own index
            print(f"data_index: {rel}/index.html exists in the data; not overwritten", file=sys.stderr)
            continue
        out.write_text(page(title, crumbs, intro, "\n".join(rows)), encoding="utf-8")
        count += 1
    return count


if __name__ == "__main__":
    site = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
    n = build(site)
    print(f"data_index: wrote {n} folder index pages under {site / 'data'}")
