# Intelligence Explosion Reading List

Essays on the intelligence explosion — scaling, takeoff dynamics, alignment, and the geopolitics of getting through it. Converted from the authors' freely-published web originals to EPUB for offline / Kindle / e-reader use.

> **Read these at the source.** The canonical home for each essay is on its author's own site, linked below. The EPUBs here are mirrors for convenience — please go to the originals for the latest version, footnotes, and to support the authors directly.
>
> If you are an author of any work below and would prefer it removed, please open an issue and I'll take it down immediately.

---

<table>
<tr>
<td width="200" valign="top">
  <a href="./Leopold%20Aschenbrenner%20-%20Situational%20Awareness.epub"><img src="covers/situational-awareness.jpg" width="180" alt="Situational Awareness cover" /></a>
</td>
<td valign="top">

### Situational Awareness: The Decade Ahead

**Leopold Aschenbrenner** · June 2024 · ~165 pages

Nine-part series arguing that AGI by roughly 2027 is plausible from straight-line extrapolation of compute, algorithmic efficiency, and "unhobbling" gains — followed by an intelligence explosion, a national-security race, and the geopolitical implications that follow.

📖 [`Leopold Aschenbrenner - Situational Awareness.epub`](./Leopold%20Aschenbrenner%20-%20Situational%20Awareness.epub) · 10 MB · all 43 figures, internal cross-chapter links<br>
🌐 Read online: [situational-awareness.ai](https://situational-awareness.ai/) · [Official PDF](https://situational-awareness.ai/wp-content/uploads/2024/06/situationalawareness.pdf)

</td>
</tr>
</table>

---

<table>
<tr>
<td width="200" valign="top">
  <a href="./Dario%20Amodei%20-%20Machines%20of%20Loving%20Grace.epub"><img src="covers/machines-of-loving-grace.jpg" width="180" alt="Machines of Loving Grace cover" /></a>
</td>
<td valign="top">

### Machines of Loving Grace

**Dario Amodei** · October 2024 · ~50 pages

The optimistic case. What a post-AGI world looks like if it goes well — biology, neuroscience, economic development, governance, work and meaning. Counterweight to the doom literature.

📖 [`Dario Amodei - Machines of Loving Grace.epub`](./Dario%20Amodei%20-%20Machines%20of%20Loving%20Grace.epub) · 81 KB<br>
🌐 Read online: [darioamodei.com/essay/machines-of-loving-grace](https://www.darioamodei.com/essay/machines-of-loving-grace)

</td>
</tr>
</table>

---

<table>
<tr>
<td width="200" valign="top">
  <a href="./Dario%20Amodei%20-%20The%20Adolescence%20of%20Technology.epub"><img src="covers/the-adolescence-of-technology.jpg" width="180" alt="The Adolescence of Technology cover" /></a>
</td>
<td valign="top">

### The Adolescence of Technology

**Dario Amodei** · January 2026 · ~70 pages

The companion piece to *Machines of Loving Grace*. The risks side: national security, economic disruption, threats to democracy, and how civilizations defend against the failure modes of powerful AI.

📖 [`Dario Amodei - The Adolescence of Technology.epub`](./Dario%20Amodei%20-%20The%20Adolescence%20of%20Technology.epub) · 99 KB<br>
🌐 Read online: [darioamodei.com/essay/the-adolescence-of-technology](https://www.darioamodei.com/essay/the-adolescence-of-technology)

</td>
</tr>
</table>

---

<table>
<tr>
<td width="200" valign="top">
  <a href="./Gwern%20Branwen%20-%20The%20Scaling%20Hypothesis.epub"><img src="covers/the-scaling-hypothesis.png" width="180" alt="The Scaling Hypothesis cover" /></a>
</td>
<td valign="top">

### The Scaling Hypothesis

**Gwern Branwen** · 2020 (revised through 2022) · ~120 pages

Pre-GPT-4 essay arguing that scale alone might be sufficient for general intelligence — Sutton's bitter lesson taken to its conclusion, with extensive historical context and a tour through what we already knew when we should have known better.

📖 [`Gwern Branwen - The Scaling Hypothesis.epub`](./Gwern%20Branwen%20-%20The%20Scaling%20Hypothesis.epub) · 1.9 MB<br>
🌐 Read online: [gwern.net/scaling-hypothesis](https://gwern.net/scaling-hypothesis)

</td>
</tr>
</table>

---

## How these were built

All EPUBs are produced by scraping just the article content from each author's canonical page (with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)), caching figures locally (re-encoding GIFs and WebP to static PNGs that Kindle can render), repairing invalid block-inside-inline HTML left by WordPress / Webflow plugins, and converting via [Calibre](https://calibre-ebook.com/)'s `ebook-convert` to EPUB 3.

All four EPUBs validate clean against [`epubcheck`](https://www.w3.org/publishing/epubcheck/) (0 errors, 0 warnings).

```bash
pip install beautifulsoup4 Pillow
brew install --cask calibre        # macOS, or install Calibre from elsewhere
brew install epubcheck             # optional, for validation

python3 scripts/build_situational_awareness.py
python3 scripts/build_dario_essays.py
python3 scripts/build_gwern_essay.py
```

## Sending to Kindle

Drop any of the `.epub` files on [Send to Kindle](https://www.amazon.com/sendtokindle), or email as an attachment to your `*@kindle.com` address. The Send-to-Kindle web uploader has historically been finicky about EPUB 2 and about pages with embedded SVG / animated GIFs / extensionless image refs — every fix here is informed by an `epubcheck` run.

## Attribution & licensing

All essays are © their respective authors (Leopold Aschenbrenner, Dario Amodei, Gwern Branwen). Cover images are from each author's own website. The EPUBs are mirrored here for offline reading convenience with prominent attribution and links to the canonical sources. The authors retain all rights; please respect their preferences if they ask for content to be removed.

The build scripts in this repository are MIT-licensed (see [`LICENSE`](./LICENSE)).
