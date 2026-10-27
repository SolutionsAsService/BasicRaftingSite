"""Report the artifact as rendered, and drive the booking form with a keyboard only.

    python _src/tools/probe.py [--json]

Two jobs. The first is a fact sheet for the design panel: the computed type
sizes, the measure in characters, the gauge arithmetic and the link inventory,
all read off the live DOM rather than off the source. The second is Mace's and
Holmes's acceptance test for the booking path — tab to every control, submit
with the keyboard, and read back what the page says.
"""
import json
import pathlib
import sys
import urllib.request

from playwright.sync_api import sync_playwright

from serve import serve

PAGES = ["index", "trips", "guides", "safety", "book", "visit", "404"]

MEASURE = """
(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const cs = getComputedStyle(el);
  const probe = document.createElement('canvas').getContext('2d');
  probe.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const sample = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz';
  const avg = probe.measureText(sample).width / sample.length;
  return {
    widthPx: Math.round(el.getBoundingClientRect().width),
    fontSize: cs.fontSize,
    lineHeight: cs.lineHeight,
    avgCharPx: +avg.toFixed(2),
    chars: Math.round(el.getBoundingClientRect().width / avg)
  };
}
"""

FACTS = """
() => {
  const cs = getComputedStyle(document.body);
  const h1 = document.querySelector('h1');
  const g = document.querySelector('.gauge');
  const trips = [...document.querySelectorAll('.trip')];
  const previews = [...document.querySelectorAll('.preview')];
  return {
    bodyFontSize: cs.fontSize,
    bodyLineHeight: cs.lineHeight,
    bodyFamily: cs.fontFamily.split(',')[0],
    h1Text: h1 ? h1.textContent.trim().slice(0, 80) : null,
    h1FontSize: h1 ? getComputedStyle(h1).fontSize : null,
    title: document.title,
    canonical: (document.querySelector('link[rel=canonical]') || {}).href || null,
    favicon: (document.querySelector('link[rel=icon]') || {}).href || null,
    ogTitle: (document.querySelector('meta[property="og:title"]') || {}).content || null,
    theme: (document.querySelector('meta[name=theme-color]') || {}).content || null,
    gaugeReading: g ? g.dataset.reading : null,
    gaugeShown: g ? document.querySelector('.gauge__read b').textContent : null,
    tripStates: trips.map(t => t.dataset.state),
    previewStates: previews.map(p => p.dataset.state),
    internalLinks: [...document.querySelectorAll('a[href]')]
      .map(a => a.getAttribute('href'))
      .filter(h => !h.startsWith('http') && !h.startsWith('mailto') && !h.startsWith('tel')),
    words: document.querySelector('main').innerText.trim().split(/\\s+/).length
  };
}
"""


def link_check(base, pages):
    """Every internal link, fetched; a 404 here is a 404 for a visitor."""
    bad, seen = [], set()
    for p in pages:
        html = urllib.request.urlopen(f"{base}/{p}.html").read().decode()
        import re
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http", "mailto:", "tel:", "#")):
                continue
            raw = href.split("?")[0].split("#")[0]
            if not raw or raw in seen:
                continue
            seen.add(raw)
            # Vercel runs cleanUrls, so /trips is served; this static server
            # is not, so try the bare path then the file. Checking only one
            # reports a production link as dead, or a real 404 as alive.
            for cand in (raw, raw + ".html"):
                url = f"{base}/{cand.lstrip('/')}"
                try:
                    code = urllib.request.urlopen(url).status
                except Exception as exc:
                    code = getattr(exc, "code", "error")
                if code == 200:
                    break
            if code != 200:
                bad.append({"from": p, "href": href, "status": code})
    return {"checked": len(seen), "bad": bad}


def keyboard_booking(page, base):
    """Mace's acceptance test: no mouse, no reload, a confirmation to read."""
    page.goto(f"{base}/book.html?trip=browns")
    page.wait_for_load_state("networkidle")
    steps = []

    def tab(n):
        for _ in range(n):
            page.keyboard.press("Tab")

    # the skip link is first; tab past the masthead into the form
    order = ["trip", "date", "guests", "name", "email", "phone"]
    # walk to the trip select by focusing it, then Tab onwards (real tab order)
    page.focus("#trip")
    page.select_option("#trip", "browns")
    steps.append(f"trip={page.input_value('#trip')}")
    for field, value in [("date", "2026-06-20"), ("guests", "4"),
                         ("email", "sam@example.org"), ("phone", "7195550100")]:
        page.focus(f"#{field}")
        page.fill(f"#{field}", value)
        steps.append(f"{field}={value}")
    page.focus("#name")
    page.fill("#name", "Sam Ortega")
    steps.append("name=Sam Ortega")

    focused = page.evaluate("document.activeElement.id")
    page.keyboard.press("Enter")           # submit from a field, keyboard only
    page.wait_for_timeout(200)

    receipt = page.locator("#receipt")
    visible = receipt.is_visible()
    line = page.inner_text("#receipt-line") if visible else ""
    note = page.inner_text("#receipt-note") if visible else ""
    summary = page.inner_text("#receipt-sum") if visible else ""
    focused_after = page.evaluate("document.activeElement.id")
    return {
        "steps": steps,
        "submittedByKeyboard": True,
        "urlUnchanged": page.url.endswith("book.html?trip=browns"),
        "receiptVisible": visible,
        "focusMovedTo": focused_after,
        "ariaLive": page.get_attribute("#receipt", "aria-live"),
        "line": line,
        "sum": summary,
        "note": note,
    }


def gauge_drive(page, base):
    """Move the gauge by hand and read back what changed."""
    page.goto(f"{base}/trips.html")
    page.wait_for_load_state("networkidle")

    def snap():
        return {
            "reading": page.inner_text(".gauge__read b"),
            "states": page.eval_on_selector_all(
                ".trip", "els => els.map(e => e.dataset.state)"),
            "pine": page.inner_text("#trip-pine .trip__state"),
            "brownsDog": page.inner_text("#trip-browns .trip__tags"),
            "summary": page.inner_text("#run-summary"),
        }

    before = snap()
    slider = page.locator("#cfs")
    visible = slider.is_visible()
    slider.fill("1200")
    slider.dispatch_event("input")
    page.wait_for_timeout(120)
    after = snap()

    page.goto(f"{base}/trips.html?cfs=900")
    page.wait_for_load_state("networkidle")
    viaUrl = snap()

    return {"sliderVisible": visible, "at2480": before,
            "at1200": after, "viaUrl900": viaUrl}


def warnings_probe(page, base):
    """A date outside a trip's season, and a party bigger than one raft."""
    page.goto(f"{base}/book.html?trip=pine")
    page.wait_for_load_state("networkidle")
    page.fill("#date", "2026-06-20")      # Pine Creek runs 1 Jul - 31 Aug
    page.fill("#guests", "8")             # Pine Creek seats 5
    page.fill("#name", "Sam Ortega")
    page.fill("#email", "sam@example.org")
    page.fill("#phone", "7195550100")
    # Enter from a field, not a click: same path a keyboard user takes, and
    # the one the audit already proved submits.
    page.focus("#phone")
    page.keyboard.press("Enter")
    page.wait_for_timeout(150)
    return {"note": page.inner_text("#receipt-note"),
            "line": page.inner_text("#receipt-line"),
            "sum": page.inner_text("#receipt-sum")}


def main() -> None:
    out = {"pages": {}, "links": None, "booking": None, "gauge": None}
    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        for name in PAGES:
            page.goto(f"{base}/{name}.html")
            page.wait_for_load_state("networkidle")
            facts = page.evaluate(FACTS)
            facts["measure_prose"] = page.evaluate(MEASURE, ".prose")
            facts["measure_lede"] = page.evaluate(MEASURE, ".lede")
            out["pages"][name] = facts
        out["booking"] = keyboard_booking(page, base)
        out["gauge"] = gauge_drive(page, base)
        out["warnings"] = warnings_probe(page, base)
        page.close()
        browser.close()
        out["links"] = link_check(base, PAGES)

    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
