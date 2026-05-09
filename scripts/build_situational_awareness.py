#!/usr/bin/env python3
"""
Build a single EPUB of Leopold Aschenbrenner's "Situational Awareness: The Decade Ahead"
by scraping the nine chapter pages from situational-awareness.ai, fetching all figures
locally so they embed correctly, and converting via Calibre's `ebook-convert`.

Cross-chapter links (e.g. the "Next:" navigation, in-text references to other chapters)
are rewritten to internal EPUB anchors so navigation stays inside the book on Kindle.

Canonical source: https://situational-awareness.ai/

Requires:
  - Python 3.9+
  - beautifulsoup4 (`pip install beautifulsoup4`)
  - Calibre's ebook-convert on PATH (`brew install --cask calibre`)

Usage: python3 scripts/build_situational_awareness.py
Output: ./situational-awareness.epub
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


BASE = "https://situational-awareness.ai"

# (path, title, anchor-id)
CHAPTERS = [
    ("/", "Introduction", "intro"),
    ("/from-gpt-4-to-agi/", "I. From GPT-4 to AGI: Counting the OOMs", "from-gpt-4-to-agi"),
    ("/from-agi-to-superintelligence/", "II. From AGI to Superintelligence: the Intelligence Explosion", "from-agi-to-superintelligence"),
    ("/racing-to-the-trillion-dollar-cluster/", "IIIa. Racing to the Trillion-Dollar Cluster", "racing-to-the-trillion-dollar-cluster"),
    ("/lock-down-the-labs/", "IIIb. Lock Down the Labs: Security for AGI", "lock-down-the-labs"),
    ("/superalignment/", "IIIc. Superalignment", "superalignment"),
    ("/the-free-world-must-prevail/", "IIId. The Free World Must Prevail", "the-free-world-must-prevail"),
    ("/the-project/", "IV. The Project", "the-project"),
    ("/parting-thoughts/", "V. Parting Thoughts", "parting-thoughts"),
]

# Map full canonical URLs (and a few common variants) to the in-book anchor id.
def _build_path_to_anchor():
    m = {}
    for path, _, anchor in CHAPTERS:
        for variant in {path, path.rstrip("/"), path.rstrip("/") + "/"}:
            m[variant] = anchor
    return m

PATH_TO_ANCHOR = _build_path_to_anchor()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-reading-list/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_image(url: str, img_dir: Path) -> str:
    """Fetch image, normalizing problematic formats (GIF→PNG first frame, WebP→PNG)
    so Kindle's e-ink renderer doesn't choke or crash. Animated GIFs in particular
    have caused 'page cannot be displayed' crashes mid-chapter."""
    parsed = urllib.parse.urlparse(url)
    name = os.path.basename(parsed.path) or "img"
    prefix = hashlib.md5(url.encode()).hexdigest()[:6]

    ext = os.path.splitext(name)[1].lower()
    if ext in (".gif", ".webp"):
        stem = os.path.splitext(name)[0]
        safe = f"{prefix}_{stem}.png"
    else:
        safe = f"{prefix}_{name}"

    local = img_dir / safe
    if not local.exists():
        try:
            data = fetch(url)
            if ext in (".gif", ".webp"):
                from io import BytesIO
                from PIL import Image
                im = Image.open(BytesIO(data))
                # First frame for animated formats
                if getattr(im, "is_animated", False):
                    im.seek(0)
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA")
                im.save(local, format="PNG", optimize=True)
                print(f"    converted {ext} → PNG: {name}")
            else:
                local.write_bytes(data)
        except Exception as e:
            print(f"  ! image failed {url}: {e}")
            return url
    return f"images/{safe}"


def rewrite_link(href: str, current_anchor: str) -> str:
    """Map a URL on situational-awareness.ai to an internal anchor if possible."""
    if not href:
        return href
    parsed = urllib.parse.urlparse(href)
    # Only rewrite same-domain or relative links
    same_site = parsed.netloc in ("", "situational-awareness.ai", "www.situational-awareness.ai")
    if not same_site:
        return href
    path = parsed.path or "/"
    if path in PATH_TO_ANCHOR:
        target = PATH_TO_ANCHOR[path]
        # If link is to the current chapter and there's a sub-anchor, keep it for now
        if target == current_anchor and parsed.fragment:
            return f"#{parsed.fragment}"
        return f"#{target}"
    return href


def clean_chapter(html: str, anchor: str, img_dir: Path) -> str:
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_="entry-content")
    if article is None:
        raise RuntimeError("no .entry-content found in page")

    # Strip elements Kindle's renderer chokes on or that are page chrome
    for tag in article.find_all(["script", "style", "noscript", "form", "iframe", "svg"]):
        tag.decompose()
    junk = re.compile(
        r"sharedaddy|jp-relatedposts|wp-block-buttons|nav-links|comments|widget|"
        r"ez-toc|wp-block-spacer|eztoc-hide",
        re.I,
    )
    for t in article.find_all(class_=junk):
        t.decompose()
    # Also kill the per-chapter <nav> ez-toc widgets entirely
    for n in article.find_all("nav"):
        n.decompose()

    for img in article.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src:
            img.decompose()
            continue
        if src.startswith("/"):
            src = BASE + src
        if src.startswith("http"):
            img["src"] = fetch_image(src, img_dir)
        for attr in list(img.attrs):
            if attr not in ("src", "alt", "width", "height"):
                del img[attr]

    # Rewrite internal cross-chapter links so navigation stays inside the EPUB
    for a in article.find_all("a", href=True):
        a["href"] = rewrite_link(a["href"], anchor)

    return str(article)


def main() -> None:
    out_epub = Path("situational-awareness.epub").resolve()
    workdir = Path(tempfile.mkdtemp(prefix="sa_build_"))
    img_dir = workdir / "images"
    img_dir.mkdir()

    print(f"working in {workdir}")

    parts = []
    for path, title, anchor in CHAPTERS:
        url = BASE + path
        print(f"  fetching {url}")
        html = fetch(url).decode("utf-8", errors="replace")
        body = clean_chapter(html, anchor, img_dir)
        parts.append(
            f'<h1 id="{anchor}" style="page-break-before: always">{title}</h1>\n{body}\n'
        )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><title>Situational Awareness: The Decade Ahead</title></head>
<body>
<h1>Situational Awareness</h1>
<h2>The Decade Ahead</h2>
<p><em>Leopold Aschenbrenner, June 2024</em></p>
<p>Source: <a href="{BASE}/">{BASE}/</a></p>
{''.join(parts)}
</body>
</html>
"""
    combined = workdir / "combined.html"
    combined.write_text(doc, encoding="utf-8")
    print(f"\nwrote {combined.name} ({len(doc):,} bytes), {len(list(img_dir.iterdir()))} images cached")

    if not shutil.which("ebook-convert"):
        sys.exit("ebook-convert not on PATH; install Calibre")

    cmd = [
        "ebook-convert", str(combined), str(out_epub),
        "--title", "Situational Awareness: The Decade Ahead",
        "--authors", "Leopold Aschenbrenner",
        "--pubdate", "2024-06",
        "--language", "en",
        "--epub-version", "3",
        "--chapter", "//h:h1",
        "--level1-toc", "//h:h1",
        "--level2-toc", "//h:h2",
        "--page-breaks-before", "//h:h1",
    ]
    print(f"\nrunning ebook-convert...")
    subprocess.run(cmd, check=True, cwd=workdir)
    print(f"\n→ {out_epub}")


if __name__ == "__main__":
    main()
