#!/usr/bin/env python3
"""
Build clean EPUBs of Dario Amodei's essays from darioamodei.com by extracting
just the article body + footnotes from each Webflow page, downloading images
locally, and converting via Calibre.

Webflow's raw HTML has a lot of unrelated chrome (header/footer/scripts) that
seems to confuse Send-to-Kindle's web uploader — extracting just the essay
content produces a renderer-friendly EPUB that uploads cleanly.

Canonical sources:
  - https://www.darioamodei.com/essay/machines-of-loving-grace
  - https://www.darioamodei.com/essay/the-adolescence-of-technology

Requires:
  - Python 3.9+
  - beautifulsoup4
  - Calibre's ebook-convert on PATH

Usage: python3 scripts/build_dario_essays.py
Outputs: ./Dario Amodei - Machines of Loving Grace.epub, ./Dario Amodei - The Adolescence of Technology.epub
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("install beautifulsoup4: pip install beautifulsoup4")


ESSAYS = [
    {
        "url": "https://www.darioamodei.com/essay/machines-of-loving-grace",
        "title": "Machines of Loving Grace",
        "subtitle": "How AI Could Transform the World for the Better",
        "pubdate": "2024-10",
        "outfile": "Dario Amodei - Machines of Loving Grace.epub",
    },
    {
        "url": "https://www.darioamodei.com/essay/the-adolescence-of-technology",
        "title": "The Adolescence of Technology",
        "subtitle": "Confronting and Overcoming the Risks of Powerful AI",
        "pubdate": "2026-01",
        "outfile": "Dario Amodei - The Adolescence of Technology.epub",
    },
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-reading-list/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_image(url: str, img_dir: Path) -> str:
    parsed = urllib.parse.urlparse(url)
    name = os.path.basename(parsed.path) or "img"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:80]
    prefix = hashlib.md5(url.encode()).hexdigest()[:6]
    safe = f"{prefix}_{name}"
    local = img_dir / safe
    if not local.exists():
        try:
            local.write_bytes(fetch(url))
        except Exception as e:
            print(f"    ! image failed {url}: {e}")
            return url
    return f"images/{safe}"


def extract(html: str, source_url: str, img_dir: Path) -> str:
    """Pull just the article body + footnotes from a darioamodei.com page."""
    soup = BeautifulSoup(html, "html.parser")

    # The Webflow page has two .rich-text blocks: the essay body and footnotes.
    body = soup.select_one("div.rich-text.w-richtext")
    foots = soup.select_one("div.rich-text.cc-footnotes.w-richtext")
    if body is None:
        raise RuntimeError(f"no article body in {source_url}")

    fragments = [body]
    if foots is not None and foots is not body:
        fragments.append(foots)

    # Strip elements that confuse Kindle / Send-to-Kindle
    for frag in fragments:
        for tag in frag.find_all(["script", "style", "noscript", "form", "iframe", "svg"]):
            tag.decompose()

        # Resolve image src to absolute then cache locally
        for img in frag.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if not src:
                img.decompose()
                continue
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urllib.parse.urljoin(source_url, src)
            if src.startswith("http"):
                img["src"] = fetch_image(src, img_dir)
            for attr in list(img.attrs):
                if attr not in ("src", "alt", "width", "height"):
                    del img[attr]

        # Resolve relative anchor links to absolute (footnote refs etc work in-doc)
        for a in frag.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/") and not href.startswith("//"):
                a["href"] = urllib.parse.urljoin(source_url, href)
            # Strip Webflow data-* attrs that aren't useful
            for attr in list(a.attrs):
                if attr.startswith("data-") or attr in ("class",):
                    del a[attr]

    parts = []
    parts.append(str(fragments[0]))
    if len(fragments) > 1:
        parts.append('<hr/><h2 id="footnotes">Footnotes</h2>')
        parts.append(str(fragments[1]))
    return "\n".join(parts)


def build_essay(essay: dict, out_dir: Path) -> None:
    print(f"\n=== {essay['title']} ===")
    print(f"  fetching {essay['url']}")
    html = fetch(essay["url"]).decode("utf-8", errors="replace")

    workdir = Path(tempfile.mkdtemp(prefix="dario_build_"))
    img_dir = workdir / "images"
    img_dir.mkdir()
    print(f"  workdir: {workdir}")

    body_html = extract(html, essay["url"], img_dir)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><title>{essay['title']}</title></head>
<body>
<h1>{essay['title']}</h1>
<h2>{essay['subtitle']}</h2>
<p><em>Dario Amodei, {essay['pubdate']}</em></p>
<p>Source: <a href="{essay['url']}">{essay['url']}</a></p>
<hr/>
{body_html}
</body>
</html>
"""
    combined = workdir / "combined.html"
    combined.write_text(doc, encoding="utf-8")
    n_images = len(list(img_dir.iterdir()))
    print(f"  wrote combined.html ({len(doc):,} bytes), {n_images} images")

    out_epub = out_dir / essay["outfile"]
    cmd = [
        "ebook-convert", str(combined), str(out_epub),
        "--title", essay["title"],
        "--authors", "Dario Amodei",
        "--pubdate", essay["pubdate"],
        "--language", "en",
        "--epub-version", "3",
        "--chapter", "//h:h1",
        "--level1-toc", "//h:h1",
        "--level2-toc", "//h:h2",
        "--page-breaks-before", "//h:h1",
    ]
    print(f"  running ebook-convert...")
    subprocess.run(cmd, check=True, cwd=workdir, stdout=subprocess.DEVNULL)
    print(f"  → {out_epub} ({out_epub.stat().st_size:,} bytes)")


def main() -> None:
    if not shutil.which("ebook-convert"):
        sys.exit("ebook-convert not on PATH; install Calibre")
    out_dir = Path.cwd()
    for essay in ESSAYS:
        build_essay(essay, out_dir)


if __name__ == "__main__":
    main()
