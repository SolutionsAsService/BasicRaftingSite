"""Build the root *.html files from _src/layout.html, _src/pages/*.html and _src/data/*.json.

    python _src/build.py

Every fact the site prints — trips, prices, ages, the gauge reading, the phone
number — comes from _src/data/. Nothing is typed twice. The build also refuses
to emit a page whose internal links point at a file it did not write, so a
"Contact" that resolves to a 404 fails here rather than in a browser.
"""
import datetime
import html
import json
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
DATA = SRC / "data"
PAGES = SRC / "pages"

e = html.escape

outfitter = json.loads((DATA / "outfitter.json").read_text(encoding="utf-8"))
trips = json.loads((DATA / "trips.json").read_text(encoding="utf-8"))
guides = json.loads((DATA / "guides.json").read_text(encoding="utf-8"))

NAV = [
    ("/trips", "Trips"),
    ("/guides", "Guides"),
    ("/safety", "Safety"),
    ("/visit", "Basecamp"),
]
SCALE_MAX = outfitter["gauge"]["scaleMax"]

TODAY = datetime.date.today()


def md(year, stamp):
    """'05-15' -> a date in `year`."""
    return datetime.date(year, int(stamp[:2]), int(stamp[3:]))


def open_on(stamp_from, stamp_to, day=None):
    """Is `day` inside a season given as 'MM-DD' bounds?"""
    day = day or TODAY
    return md(day.year, stamp_from) <= day <= md(day.year, stamp_to)


# The whole site's tense depends on this: a gauge reading from June printed in
# October must not say "right now".
SEASON_OPEN = open_on(outfitter["season"]["from"], outfitter["season"]["to"])
RUNNING_WORD = "Running" if SEASON_OPEN else "Would run"
CLOSED_WORD = "Too high" if SEASON_OPEN else "Would be too high"
LOW_WORD = "Too low" if SEASON_OPEN else "Would be too low"


def pct(v):
    """Position of a flow value on the gauge axis, 0-100."""
    return round(v / SCALE_MAX * 100, 2)


def money(n):
    return f"${n:,}"


def gauge_block():
    """The river gauge: one axis, a reading, and what that reading closes."""
    g = outfitter["gauge"]
    now = g["reading"]
    # A tick at every flow where a trip stops being guidable, so the hand
    # meets the boundary instead of gliding through it.
    stops = "".join(
        f'<option value="{hi}"></option>'
        for hi in sorted({t["gauge"][1] for t in trips}))
    bands = "".join(
        f'<span class="g-band g-band--{b["label"]}" style="--from:{pct(0)}%;--to:{pct(b["to"])}%"></span>'
        for b in g["bands"]
    )
    # The slider is hidden until the script takes it: a control that does
    # nothing without JS is worse than no control.
    return f"""<div class="gauge" data-reading="{now}" data-season="{1 if SEASON_OPEN else 0}">
      <p class="gauge__eyebrow">{e(g["name"])}</p>
      <p class="gauge__read"><b>{now:,}</b><span>{e(g["unit"])}</span></p>
      <div class="gauge__scale" aria-hidden="true">
        {bands}
        <span class="g-now" style="--at:{pct(now)}%"></span>
      </div>
      <div class="gauge__axis" aria-hidden="true">
        <span>0</span><span>{SCALE_MAX // 3:,}</span><span>{SCALE_MAX * 2 // 3:,}</span><span>{SCALE_MAX:,}</span>
      </div>
      <div class="gauge__ctl" hidden>
        <label for="cfs">Move the gauge</label>
        <input type="range" id="cfs" min="0" max="{SCALE_MAX}" step="20" value="{now}"
               list="cfs-stops" aria-describedby="cfs-out"
               aria-valuetext="{now:,} cubic feet per second">
        <datalist id="cfs-stops">{stops}</datalist>
        <output id="cfs-out" for="cfs">{now:,} cfs</output>
      </div>
      <p class="gauge__foot"><span class="tag tag--sample">Sample reading</span>
        {e(g["observed"])} · {e(g["source"])}</p>
    </div>"""


def runs_now(trip, reading=None):
    """What a given flow means for one trip, in the season's own tense."""
    lo, hi = trip["gauge"]
    now = reading if reading is not None else outfitter["gauge"]["reading"]
    if now < lo:
        return ("low", f"{LOW_WORD} — needs {lo:,} cfs")
    if now > hi:
        return ("over", f"{CLOSED_WORD} — runs to {hi:,} cfs")
    return ("on", f"{RUNNING_WORD} · {now:,} of {hi:,} cfs")


def range_bar(trip):
    lo, hi = trip["gauge"]
    now = outfitter["gauge"]["reading"]
    return f"""<div class="range" aria-hidden="true">
        <span class="range__ok" style="--lo:{pct(lo)}%;--hi:{pct(hi)}%"></span>
        <span class="range__now" style="--at:{pct(now)}%"></span>
      </div>
      <p class="range__legend"><span>{lo:,}</span><span class="sr-only"> to </span><span>{hi:,} cfs</span></p>"""


def dog_tag(trip, reading):
    """The dog rule is a fact at low water and a condition above it."""
    if not trip["dogs"]:
        return '<span class="tag tag--no">No dogs</span>'
    low = trip.get("dogLow")
    if low and reading > low:
        return f'<span class="tag tag--dog">Dogs under {low:,} cfs</span>'
    return '<span class="tag tag--dog">Dogs welcome</span>'


def trip_card(t):
    now = outfitter["gauge"]["reading"]
    state, note = runs_now(t)
    rapids = "".join(f"<li>{e(r)}</li>" for r in t.get("rapids", []))
    return f"""<li class="trip" id="trip-{t['id']}" data-state="{state}"
        data-lo="{t['gauge'][0]}" data-hi="{t['gauge'][1]}" data-dog-low="{t.get('dogLow', 0)}"
        data-dogs="{1 if t['dogs'] else 0}" data-note="{e(t.get('dogNote', ''))}"
        data-age="{t['minAge']}" data-px="{t['price']}" data-seats="{t['seats']}"
        data-from="{t['seasonFrom']}" data-to="{t['seasonTo']}">
      <div class="trip__head">
        <p class="trip__class"><b>Class {e(t['klass'])}</b> {e(t['klassName'])}</p>
        <h3>{e(t['name'])}</h3>
        <p class="trip__section">{e(t['section'])}</p>
      </div>
      <dl class="trip__facts">
        <div><dt>Duration</dt><dd>{e(t['duration'])}</dd></div>
        <div><dt>Miles</dt><dd>{t['miles']}</dd></div>
        <div><dt>Minimum age</dt><dd>{t['minAge']}</dd></div>
        <div><dt>Season</dt><dd>{e(t['season'])}</dd></div>
        <div><dt>Price</dt><dd class="price">{money(t['price'])} <span>per person</span></dd></div>
      </dl>
      <p class="trip__blurb">{e(t['blurb'])}</p>
      {f'<ul class="trip__rapids">{rapids}</ul>' if rapids else ''}
      <div class="trip__gauge">
        <p class="trip__state" data-state="{state}">{e(note)}</p>
        {range_bar(t)}
      </div>
      <p class="trip__tags">{dog_tag(t, now)}</p>
      <a class="btn btn--solid" href="book?trip={t['id']}">Book {e(t['name'])}</a>
    </li>"""


def trip_preview(t):
    state, note = runs_now(t)
    return f"""<li class="preview" data-state="{state}"
        data-lo="{t['gauge'][0]}" data-hi="{t['gauge'][1]}">
      <a href="/trips#trip-{t['id']}">
        <span class="preview__class">Class {e(t['klass'])}</span>
        <span class="preview__name">{e(t['name'])}</span>
        <span class="preview__meta">{e(t['duration'])} · {money(t['price'])} · age {t['minAge']}+</span>
        <span class="preview__state">{e(note)}</span>
        <span class="preview__go" aria-hidden="true">&rarr;</span>
      </a>
    </li>"""


def guide_card(g):
    certs = "".join(f"<li>{e(c)}</li>" for c in g["certs"])
    return f"""<li class="guide">
      <h3>{e(g['name'])}</h3>
      <p class="guide__role">{e(g['role'])} · {g['years']} seasons</p>
      <p class="guide__fav">Favourite water: <b>{e(g['favourite'])}</b></p>
      <p class="guide__line">{e(g['line'])}</p>
      <ul class="guide__certs">{certs}</ul>
    </li>"""


def simple_token(key, value):
    return value


# --------------------------------------------------------------------------
# token expansion
# --------------------------------------------------------------------------
def tokens():
    o = outfitter
    running = [t for t in trips if runs_now(t)[0] == "on"]
    closed = [t for t in trips if runs_now(t)[0] != "on"]
    season_str = f'{o["season"]["start"]} – {o["season"]["end"]}'
    now_reading = o["gauge"]["reading"]
    observed = o["gauge"]["observed"]
    n_run, n_all = len(running), len(trips)
    closed_names = ", ".join(t["name"] for t in closed) or "none"
    # The summary has to carry the reading's own tense and date: "5 of 6 are
    # running" printed in October is a number pretending to be a river.
    # Two readings worth trying, computed from the trips rather than picked:
    # the highest flow every trip can still be guided at, and one near the top
    # of the axis where only the Gorge survives.
    try_low = max(t["gauge"][0] for t in trips)
    try_high = max(t["gauge"][1] for t in trips) - 300
    summary = (
        f'At the sample reading of {now_reading:,} cfs ({observed}), {n_run} of '
        f'{n_all} trips would run and {closed_names} would be closed: it needs '
        f'the river to drop before it can be guided.'
        if not SEASON_OPEN else
        f'At {now_reading:,} cfs, {n_run} of {n_all} trips are running and '
        f'{closed_names} is closed: it needs the river to drop before it can be '
        f'guided.')
    return {
        "{{name}}": e(o["name"]),
        "{{shortName}}": e(o["shortName"]),
        "{{tagline}}": e(o["tagline"]),
        "{{place}}": e(o["place"]),
        "{{river}}": e(o["river"]),
        "{{phone}}": e(o["phone"]),
        "{{phoneHref}}": e(o["phoneHref"]),
        "{{email}}": e(o["email"]),
        "{{founded}}": str(o["founded"]),
        "{{season}}": f'{e(o["season"]["start"])} – {e(o["season"]["end"])}',
        "{{peak}}": e(o["season"]["peak"]),
        "{{peakNote}}": e(o["season"]["peakNote"]),
        "{{runSummary}}": e(summary),
        "{{tryLow}}": f'{try_low:,}',
        "{{tryHigh}}": f'{try_high:,}',
        "{{tryLowN}}": str(len([t for t in trips if runs_now(t, try_low)[0] == "on"])),
        "{{tryHighN}}": str(len([t for t in trips if runs_now(t, try_high)[0] == "on"])),
        "{{gaugeNow}}": f'{o["gauge"]["reading"]:,}',
        "{{gaugeDate}}": e(o["gauge"]["observed"]),
        "{{seasonState}}": "in season" if SEASON_OPEN else "out of season today",
        "{{seasonLine}}": (
            f'Trips run {season_str}. The gauge below is a sample reading from '
            f'{e(o["gauge"]["observed"])}, so every state on this page is what '
            f'that flow would do — not what the river is doing now.'
            if not SEASON_OPEN else
            f'Trips run {season_str}, and the shed is open today.'),
        "{{gauge}}": gauge_block(),
        "{{trips}}": "".join(trip_card(t) for t in trips),
        "{{previews}}": "".join(trip_preview(t) for t in trips),
        "{{featured}}": "".join(trip_preview(t) for t in trips if t.get("featured")),
        "{{guides}}": "".join(guide_card(g) for g in guides),
        "{{nTrips}}": str(len(trips)),
        "{{nGuides}}": str(len(guides)),
        "{{nRunning}}": str(len(running)),
        "{{nClosed}}": str(len(closed)),
        "{{closedNames}}": ", ".join(t["name"] for t in closed) or "none",
        "{{tripOptions}}": "".join(
            f'<option value="{t["id"]}" data-price="{t["price"]}" data-min-age="{t["minAge"]}" '
            f'data-dogs="{1 if t["dogs"] else 0}" data-klass="{e(t["klass"])}" '
            f'data-miles="{t["miles"]}" data-duration="{e(t["duration"])}" '
            f'data-section="{e(t["section"])}" data-note="{e(t.get("dogNote", ""))}" '
            f'data-from="{t["seasonFrom"]}" data-to="{t["seasonTo"]}" '
            f'data-seats="{t["seats"]}" data-dog-low="{t.get("dogLow", 0)}">'
            f'{e(t["name"])} — Class {e(t["klass"])}, {e(t["duration"])}, '
            f'{money(t["price"])} per person</option>' for t in trips),
        "{{creds}}": "".join(f"<li>{e(c)}</li>" for c in o["creds"]),
        "{{hours}}": "".join(
            f'<div><dt>{e(h["days"])}</dt><dd>{e(h["time"])}</dd></div>' for h in o["hours"]),
        "{{address}}": f'{e(o["basecamp"]["line1"])}<br>{e(o["basecamp"]["line2"])}',
        "{{basecampNote}}": e(o["basecamp"]["note"]),
        "{{seasonNote}}": e(o["seasonNote"]),
        "{{statusNote}}": e(o["statusNote"]),
        "{{promise}}": "".join(
            f'<div class="stat"><b>{e(p["n"])}</b><span>{e(p["label"])}</span></div>'
            for p in o["promise"]),
        "{{year}}": "2026",
    }


def expand(text):
    for k, v in tokens().items():
        text = text.replace(k, v)
    return text


def token_hex(name):
    """Read a brand colour out of the stylesheet.

    The mark is rendered in three places — the favicon, the inline SVG in the
    layout, and the generated social card — and a colour typed in more than one
    of them will drift. The stylesheet is the one that says it; the favicon is
    written from it.
    """
    css = (ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
    m = re.search(rf"--{name}:\s*(#[0-9A-Fa-f]{{6}})\s*;", css)
    if not m:
        sys.exit(f"brand colour --{name} not found in assets/css/styles.css")
    return m.group(1)


def write_favicon():
    gorge, stone, signal = (token_hex(n) for n in ("gorge", "stone", "signal"))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="5" fill="{gorge}"/>
  <g fill="{stone}">
    <path d="M7 7h4v18H7z"/>
    <path d="M13 11h4v14h-4z"/>
    <path d="M19 15h4v10h-4z"/>
    <path d="M25 19h2v6h-2z"/>
  </g>
  <path d="M4 22.5h24" stroke="{signal}" stroke-width="2.5"/>
</svg>
"""
    (ROOT / "assets" / "images" / "favicon.svg").write_text(svg, encoding="utf-8")
    return gorge, stone, signal


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
layout = (SRC / "layout.html").read_text(encoding="utf-8")
built = {}

for page in sorted(PAGES.glob("*.html")):
    slug = page.stem
    body = page.read_text(encoding="utf-8")
    title = ""
    m = re.search(r"<!--\s*title:\s*(.+?)\s*-->", body)
    if m:
        title = m.group(1)
    desc = ""
    m = re.search(r"<!--\s*description:\s*(.+?)\s*-->", body)
    if m:
        desc = m.group(1)
    out = expand(layout)
    out = out.replace("{{slug}}", slug)
    out = out.replace("{{title}}", e(title or outfitter["name"]))
    out = out.replace("{{description}}", e(expand(desc)))
    out = out.replace("{{pageTitle}}", e(expand(title) if title else outfitter["tagline"]))
    out = out.replace("{{content}}", expand(body))
    nav = "".join(
        '<a href="{s}"{cur}>{n}</a>'.format(
            s=s, n=e(n), cur=' aria-current="page"' if s == slug else "")
        for s, n in NAV)
    out = out.replace("{{nav}}", nav)
    left = re.findall(r"\{\{.*?\}\}", out)
    if left:
        sys.exit(f"unfilled token(s) in {slug}: {sorted(set(left))}")
    built[slug] = out

# --- link check: an internal href that resolves to nothing fails the build ---
targets = {f"{s}.html" for s in built} | {s for s in built} | {""}
targets |= {"trips.html", "guides.html", "safety.html", "visit.html", "book.html", "index.html"}
bad = []
for slug, doc in built.items():
    for href in re.findall(r'href="([^"]+)"', doc):
        if href.startswith(("http", "mailto:", "tel:", "#", "?")):
            continue
        path = href.split("?")[0].split("#")[0].strip("/")
        if not path:
            continue
        # a generated page, or a file that really exists on disk
        if path in targets or (ROOT / path).is_file():
            continue
        bad.append(f"{slug}: {href}")
if bad:
    sys.exit("dead internal link(s):\n  " + "\n  ".join(bad))

for slug, doc in built.items():
    (ROOT / f"{slug}.html").write_text(doc, encoding="utf-8", newline="\n")

print("mark:", "favicon.svg written from --gorge/--stone/--signal", write_favicon())

print(f"built {len(built)} pages: {', '.join(sorted(built))}")
print(f"  {len(trips)} trips, {len(guides)} guides, gauge {outfitter['gauge']['reading']:,} cfs")
print(f"  running now: {tokens()['{{nRunning}}']} of {len(trips)} "
      f"(closed: {tokens()['{{closedNames}}']})")
