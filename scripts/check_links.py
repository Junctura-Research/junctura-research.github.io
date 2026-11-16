"""Check that every internal link in the rendered site resolves to a file.

Internal means a relative link, a root-relative link, or an absolute link to
https://juncturaresearch.com. External links are not checked here (the research
agent checks those before a document is approved). Exits non-zero on any
broken link, so the deploy stops.

Usage: python3 scripts/check_links.py [_site]
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

SITE_HOSTS = {"juncturaresearch.com", "www.juncturaresearch.com"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)


def resolve(site: Path, page: Path, link: str):
    u = urlparse(link)
    if u.scheme in ("mailto", "tel", "javascript", "data"):
        return None
    if u.scheme in ("http", "https"):
        if u.netloc not in SITE_HOSTS:
            return None
        target = site / unquote(u.path).lstrip("/")
    elif not u.path:
        return None  # same-page anchor
    elif u.path.startswith("/"):
        target = site / unquote(u.path).lstrip("/")
    else:
        target = page.parent / unquote(u.path)
    if link.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def main(site: Path) -> int:
    broken, checked = [], 0
    for page in sorted(site.rglob("*.html")):
        p = Links()
        p.feed(page.read_text(encoding="utf-8", errors="ignore"))
        for link in p.links:
            target = resolve(site, page, link)
            if target is None:
                continue
            checked += 1
            if not target.resolve().is_file():
                broken.append(f"{page.relative_to(site)} -> {link}")
    for b in broken:
        print("BROKEN:", b)
    print(f"check_links: {checked} internal links checked, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "_site")))
