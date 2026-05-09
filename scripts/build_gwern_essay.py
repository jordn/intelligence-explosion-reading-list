#!/usr/bin/env python3
"""
Build a clean EPUB of Gwern's "The Scaling Hypothesis" by extracting just the
article body (#markdownBody) from gwern.net, downloading any referenced images
locally, and converting via Calibre.

Calibre's direct HTML→EPUB conversion of the gwern.net page leaks ~250 broken
references to the site's static JS/CSS/icon assets, which fails strict EPUB
validation. Extracting just the article content produces a clean, valid EPUB.

Canonical source: https://gwern.net/scaling-hypothesis

Requires:
  - Python 3.9+
  - beautifulsoup4
  - Pillow
  - Calibre's ebook-convert on PATH

Usage: python3 scripts/build_gwern_essay.py
Output: ./Gwern Branwen - The Scaling Hypothesis.epub
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
from io import BytesIO
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    from PIL import Image
except ImportError:
    sys.exit("install dependencies: pip install beautifulsoup4 Pillow")


SOURCE_URL = "https://gwern.net/scaling-hypothesis"
TITLE = "The Scaling Hypothesis"
AUTHOR = "Gwern Branwen"
PUBDATE = "2020"

_PIL_FMT_TO_EXT = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".png", "WEBP": ".png", "BMP": ".png"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-reading-list/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_image(url: str, img_dir: Path) -> str:
    parsed = urllib.parse.urlparse(url)
    raw = os.path.basename(parsed.path) or "img"
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", os.path.splitext(raw)[0])[:60] or "img"
    prefix = hashlib.md5(url.encode()).hexdigest()[:6]
    for existing in img_dir.glob(f"{prefix}_{stem}.*"):
        return f"images/{existing.name}"
    try:
        data = fetch(url)
        im = Image.open(BytesIO(data))
        if getattr(im, "is_animated", False):
            im.seek(0)
        fmt = (im.format or "PNG").upper()
        if fmt == "JPEG" and im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif fmt != "JPEG" and im.mode not in ("RGB", "RGBA", "L"):
            im = im.convert("RGBA")
        ext = _PIL_FMT_TO_EXT.get(fmt, ".png")
        out_fmt = "JPEG" if ext == ".jpg" else "PNG"
        safe = f"{prefix}_{stem}{ext}"
        save_kwargs = {"optimize": True}
        if out_fmt == "JPEG":
            save_kwargs["quality"] = 85
        im.save(img_dir / safe, format=out_fmt, **save_kwargs)
        return f"images/{safe}"
    except Exception as e:
        print(f"  ! image failed {url}: {e}")
        return url


def extract(html: str, img_dir: Path) -> str:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("#markdownBody") or soup.select_one("article") or soup.select_one("main")
    if body is None:
        raise RuntimeError("no article body found")

    # Strip page chrome / things that won't render usefully on Kindle
    for tag in body.find_all(["script", "style", "noscript", "form", "iframe", "svg"]):
        tag.decompose()
    junk = re.compile(
        r"backlinks-append|similars-append|link-bibliography-append|"
        r"footnote-back|sidenote|metadata-block|page-metadata|"
        r"link-icon|icon-special|link-modified|TOC|admonition-icon",
        re.I,
    )
    for t in body.find_all(class_=junk):
        t.decompose()
    for t in body.find_all(id=re.compile(r"backlinks|similars|link-bibliography|TOC", re.I)):
        t.decompose()

    # Resolve images and rewrite refs to local cache
    for img in body.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src:
            img.decompose()
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urllib.parse.urljoin(SOURCE_URL, src)
        if src.startswith("http"):
            img["src"] = fetch_image(src, img_dir)
        for attr in list(img.attrs):
            if attr not in ("src", "alt", "width", "height"):
                del img[attr]

    # Make all relative anchor URLs absolute (footnotes still work via #fragment)
    for a in body.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/") and not href.startswith("//"):
            a["href"] = urllib.parse.urljoin(SOURCE_URL, href)
        # Strip site-specific data-* attrs
        for attr in list(a.attrs):
            if attr.startswith("data-") or attr in ("class",):
                del a[attr]

    # Repair invalid block-inside-inline nesting
    inline_parents = ("p", "sup", "sub", "span", "em", "strong", "b", "i", "a")
    for _ in range(5):
        changed = False
        for div in list(body.find_all(["div", "section", "figure"])):
            parent = div.parent
            if parent is None or parent is body:
                continue
            if parent.name in inline_parents:
                parent.unwrap()
                changed = True
        if not changed:
            break

    return str(body)


def main() -> None:
    if not shutil.which("ebook-convert"):
        sys.exit("ebook-convert not on PATH; install Calibre")

    workdir = Path(tempfile.mkdtemp(prefix="gwern_build_"))
    img_dir = workdir / "images"
    img_dir.mkdir()
    print(f"workdir: {workdir}")
    print(f"fetching {SOURCE_URL}")
    html = fetch(SOURCE_URL).decode("utf-8", errors="replace")
    body_html = extract(html, img_dir)
    n_images = len(list(img_dir.iterdir()))
    print(f"  {n_images} images cached")

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><title>{TITLE}</title></head>
<body>
<h1>{TITLE}</h1>
<p><em>{AUTHOR}, {PUBDATE} (revised through 2022)</em></p>
<p>Source: <a href="{SOURCE_URL}">{SOURCE_URL}</a></p>
<hr/>
{body_html}
</body>
</html>
"""
    combined = workdir / "combined.html"
    combined.write_text(doc, encoding="utf-8")
    print(f"wrote combined.html ({len(doc):,} bytes)")

    out_epub = Path.cwd() / "Gwern Branwen - The Scaling Hypothesis.epub"
    cmd = [
        "ebook-convert", str(combined), str(out_epub),
        "--title", TITLE,
        "--authors", AUTHOR,
        "--pubdate", PUBDATE,
        "--language", "en",
        "--epub-version", "3",
        "--chapter", "//h:h1",
        "--level1-toc", "//h:h1",
        "--level2-toc", "//h:h2",
    ]
    print("running ebook-convert...")
    subprocess.run(cmd, check=True, cwd=workdir, stdout=subprocess.DEVNULL)
    print(f"→ {out_epub} ({out_epub.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
