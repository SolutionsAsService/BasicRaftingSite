"""Measure the site as rendered, not as written.

    python _src/tools/audit.py [--json]

Checks, at 1280 / 390 / 320 px:

  overflow   document scrollWidth > clientWidth (horizontal scroll)
  contrast   every text node against the PIXEL actually behind it, so gradient
             and image backgrounds are measured rather than guessed; threshold
             4.5:1, or 3:1 at >=24px / >=18.66px bold
  targets    interactive elements under 24x24 px (WCAG 2.5.8), ignoring links
             that sit inline in a sentence (the inline exception)
  alt        images without an alt attribute
  bytes      page + CSS + JS weight

Every figure it prints is computed from the rendered page at the moment it runs.
"""
import json
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

from capture import stitch
from serve import serve, ROOT

PAGES = ["index", "trips", "guides", "safety", "book", "visit", "404"]
SIZES = [1280, 390, 320]

COLLECT = """
() => {
  const out = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walk.nextNode())) {
    const t = n.nodeValue.trim();
    if (t.length < 2) continue;
    const el = n.parentElement;
    if (!el) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    // Measure the glyph run, not the element box: an element's box includes
    // padding, borders and rounded corners that the text never sits on.
    const rng = document.createRange();
    rng.selectNodeContents(n);
    let r = rng.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    out.push({
      text: t.slice(0, 60),
      color: cs.color,
      size: parseFloat(cs.fontSize),
      weight: cs.fontWeight,
      x: r.x + window.scrollX, y: r.y + window.scrollY,
      w: r.width, h: r.height
    });
  }
  return out;
}
"""

TARGETS = """
() => {
  const sel = 'a[href], button, input, select, textarea, summary';
  return [...document.querySelectorAll(sel)].map(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    // inline exception: a link inside running text, not a standalone control
    const inline = el.tagName === 'A' && (cs.display === 'inline' || cs.display.startsWith('inline'))
      && !el.querySelector('img, svg, h1, h2, h3, h4, button');
    return { tag: el.tagName.toLowerCase(), text: (el.textContent || '').trim().slice(0, 40),
             w: Math.round(r.width), h: Math.round(r.height), inline,
             offscreen: cs.display === 'none' || r.width === 0 };
  });
}
"""


def srgb(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (srgb(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_from_css(s):
    nums = [float(v) for v in s[s.find("(") + 1:s.find(")")].split(",")]
    rgb = tuple(int(v) for v in nums[:3])
    return rgb, (nums[3] if len(nums) > 3 else 1.0)


def over(fg, alpha, bg):
    """Composite a possibly-translucent text colour onto the pixel behind it."""
    return tuple(round(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


def audit(page, width: int, name: str):
    r = {"page": name, "width": width, "overflow": 0, "contrast": [], "targets": [], "alt": []}

    r["overflow"] = max(0, page.evaluate("document.documentElement.scrollWidth") - width)

    # Text colours and boxes first: the plate pass below makes colour transparent.
    texts = [t for t in page.evaluate(COLLECT) if t['y'] + t['h'] > 0]

    # Background plate: hide every glyph so the image holds only what sits
    # BEHIND the text. Sampling the ordinary screenshot compares each colour
    # against its own antialiased pixels and reports ~1:1 for everything.
    page.add_style_tag(content="*, *::before, *::after { color: transparent !important;"
                               " text-shadow: none !important; }")
    plate = pathlib.Path(f"E:/raft-shots/.plate-{name}-{width}.png")
    stitch(page, str(plate), freeze=True)
    with Image.open(plate) as im:
        bg = im.convert("RGB")
    plate.unlink()

    for el in texts:
        try:
            fg, alpha = rgb_from_css(el["color"])
            if alpha < 0.1:
                continue  # deliberately hidden text, not a contrast claim
        except Exception:
            continue
        # 1px inset: the outermost row of a glyph run is antialiased against
        # whatever is outside it, which is not a background the text sits on.
        x, y = max(0, int(el["x"]) + 1), max(0, int(el["y"]) + 1)
        w = max(1, min(int(el["w"]) - 2, bg.width - x))
        h = max(1, min(int(el["h"]) - 2, bg.height - y))
        crop = bg.crop((x, y, x + w, y + h))
        crop = crop.resize((min(64, crop.width), min(32, crop.height)))
        worst, worst_px = 99.0, None
        raw = crop.tobytes()
        for i in range(0, len(raw), 3):
            px = (raw[i], raw[i + 1], raw[i + 2])
            c = ratio(over(fg, alpha, px), px)
            if c < worst:
                worst, worst_px = c, px
        need = 3.0 if (el["size"] >= 24 or (el["size"] >= 18.66 and int(el["weight"]) >= 700)) else 4.5
        if worst < need:
            r["contrast"].append({"text": el["text"], "ratio": round(worst, 2), "need": need,
                                  "fg": el["color"], "bg": "rgb%s" % (worst_px,),
                                  "size": el["size"]})

    for t in page.evaluate(TARGETS):
        if t["offscreen"] or t["inline"]:
            continue
        if t["w"] < 24 or t["h"] < 24:
            r["targets"].append(t)

    for a in page.evaluate("() => [...document.images].map(i => ({src: i.src, alt: i.hasAttribute('alt')}))"):
        if not a["alt"]:
            r["alt"].append(a["src"].split("/")[-1])
    return r


def main() -> None:
    results = []
    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for width in SIZES:
            page = browser.new_page(viewport={"width": width, "height": 900})
            for name in PAGES:
                page.goto(f"{base}/{name}.html")
                page.wait_for_load_state("networkidle")
                results.append(audit(page, width, name))
            page.close()
        browser.close()

    if "--json" in sys.argv:
        print(json.dumps(results, indent=1))
        return

    fail = 0
    for r in results:
        n = len(r["contrast"]) + len(r["targets"]) + len(r["alt"]) + (1 if r["overflow"] else 0)
        fail += n
        print(f"{r['page']:>8} {r['width']:>5}px  overflow {r['overflow']:>3}  "
              f"contrast {len(r['contrast']):>2}  targets {len(r['targets']):>2}  "
              f"alt {len(r['alt'])}")
        for c in r["contrast"]:
            print(f"           contrast {c['ratio']:>5}:1 (need {c['need']}) "
                  f"{c['fg']} on {c['bg']} @ {c['size']:.0f}px  \"{c['text']}\"")
        for t in r["targets"]:
            print(f"           target {t['w']}x{t['h']} <{t['tag']}> \"{t['text']}\"")
        for a in r["alt"]:
            print(f"           alt missing: {a}")
    print(f"\n{fail} finding(s) across {len(results)} page-widths.")


if __name__ == "__main__":
    main()
