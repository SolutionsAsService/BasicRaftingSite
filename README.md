# Highwater Rafting Co.

Concept site for a river-rafting outfitter on the Arkansas River out of Salida,
Colorado. Seven static pages, generated from `_src/data/`. Deploys on Vercel
with clean URLs.

The site's one device is a **river gauge**: a 0–6,000 cfs axis. Every trip
carries the flow window it can be guided in, and the reading decides which
trips are open. The gauge can be moved by hand — drag it, or use `?cfs=1200` —
and every trip state on the page follows.

## Pages

| File | What it is |
|---|---|
| `index` | The river, the gauge, and what it would take today |
| `trips` | Six trips: class, duration, miles, minimum age, season, price, flow window |
| `guides` | Four guides, their seasons, certifications and favourite water |
| `safety` | Certifications, gear, what to bring, the safety talk, what to tell us first |
| `book` | Adds a trip up on the page; catches out-of-season dates and oversized parties |
| `visit` | Basecamp address, hours, directions, what is on site |
| `404` | Off the water |

## Replace these placeholders before going live

The business is fictional and every one of these is invented:

- **Phone** `(719) 555-0148` / `+17195550148` — a fictional 555-01xx number.
- **Email** `trips@highwaterrafting.example` — `.example` is reserved and cannot be owned.
- **Address and hours** — `_src/data/outfitter.json` (`basecamp`, `hours`).
- **Trips, prices, minimum ages, seasons and flow windows** — `_src/data/trips.json`.
- **Guides** — `_src/data/guides.json`.
- **The gauge reading** — `_src/data/outfitter.json` → `gauge.reading`, currently a
  **sample** (`"status": "sample"`) dated 11 Jun 2026. Wire it to the real source
  named in `gauge.source` (USGS 07091200) before going live. Until then the site
  prints every state in the conditional — "would run", not "running" — whenever
  today falls outside the season in `season.from` / `season.to`.
- **Booking** — there is no back end. The form adds the trip up on the page and
  says so. To take real bookings, set an endpoint in `js/site.js`.

## Editing

The root `*.html` files are generated. Edit `_src/data/*.json`,
`_src/layout.html` and `_src/pages/*.html`, then:

```bash
python _src/build.py
```

The build refuses to emit a page whose internal links point at a file it did
not write, so a dead link fails here rather than in a browser.

## Measuring

```bash
python _src/tools/audit.py     # overflow, contrast, target size, alt — 1280/390/320
python _src/tools/probe.py     # computed type, measure, link inventory, keyboard booking
python _src/tools/shoot.py     # screenshots per page per width into E:/raft-shots
python _src/tools/ogcard.py    # regenerate the 1200x630 social card
```

Design decisions, the critic rounds and the measurements are in `DESIGN-LOG.md`.
Facts about this medium that cost a measurement to learn are in
`CARRY-FORWARD.md` — read it before touching the CSS.
