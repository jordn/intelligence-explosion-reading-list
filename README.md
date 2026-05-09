# Intelligence Explosion Reading List

Essays on the intelligence explosion — scaling, takeoff dynamics, alignment, and the geopolitics of getting through it. Converted from the authors' freely-published web originals to EPUB for offline / Kindle / e-reader use.

> **Read these at the source.** The canonical home for each essay is on its author's own site, linked below. The EPUBs here are mirrors for convenience only — please go to the originals for the latest version, comments, footnotes, and to support the authors directly.

If you are an author of any work below and would prefer it removed, please open an issue and I'll take it down immediately.

---

## Essays

### Situational Awareness: The Decade Ahead
**Leopold Aschenbrenner** — June 2024
🔗 **Canonical source: <https://situational-awareness.ai/>**
📥 [Author's official PDF](https://situational-awareness.ai/wp-content/uploads/2024/06/situationalawareness.pdf)

A nine-part series arguing that AGI by roughly 2027 is plausible from straight-line extrapolation of compute, algorithmic efficiency, and "unhobbling" gains — plus the geopolitical and security implications.

📖 [`situational-awareness.epub`](./situational-awareness.epub) (27 MB, with all 43 figures)

---

### Machines of Loving Grace
**Dario Amodei** — October 2024
🔗 **Canonical source: <https://www.darioamodei.com/essay/machines-of-loving-grace>**

The optimistic case: what a post-AGI world looks like if it goes well — biology, neuroscience, economics, governance, work and meaning.

📖 [`machines-of-loving-grace.epub`](./machines-of-loving-grace.epub) (72 KB)

---

### The Adolescence of Technology
**Dario Amodei** — January 2026
🔗 **Canonical source: <https://www.darioamodei.com/essay/the-adolescence-of-technology>**

The companion to *Machines of Loving Grace*: the risk side. National security, economic disruption, threats to democracy, and how to defend against them.

📖 [`the-adolescence-of-technology.epub`](./the-adolescence-of-technology.epub) (85 KB)

---

### The Scaling Hypothesis
**Gwern Branwen** — 2020 (revised through 2022)
🔗 **Canonical source: <https://gwern.net/scaling-hypothesis>**

The pre-GPT-4 essay laying out why scale alone might be sufficient for general intelligence — Sutton's bitter lesson taken to its conclusion, with extensive historical context.

📖 [`the-scaling-hypothesis.epub`](./the-scaling-hypothesis.epub) (153 KB)

---

## How these were built

All EPUBs are produced from the authors' published HTML/PDF, converted with [Calibre](https://calibre-ebook.com/)'s `ebook-convert`. The Aschenbrenner one scrapes all nine chapter pages, downloads the 43 figures locally so they're embedded, and merges into a single HTML before conversion.

The build script for the multi-chapter Aschenbrenner EPUB is in [`scripts/build_situational_awareness.py`](./scripts/build_situational_awareness.py) and is regenerable from scratch — clone, run, and you'll have your own copy directly from the canonical source.

```bash
pip install beautifulsoup4
python3 scripts/build_situational_awareness.py
```

Calibre's `ebook-convert` is required (`brew install --cask calibre` on macOS).

## Sending to Kindle

Drop any of the `.epub` files on [Send to Kindle](https://www.amazon.com/sendtokindle), or email as an attachment to your `*@kindle.com` address. EPUB 3 (what these are) is preferred over EPUB 2 — the web uploader has been finicky about the latter.

## Attribution & licensing

All essays are © their respective authors. The EPUBs are provided here for convenient offline reading with prominent attribution and links to the canonical sources. The authors retain all rights; please respect their preferences if they ask for content to be removed.

The build scripts in this repo are MIT licensed.
