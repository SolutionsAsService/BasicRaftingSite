# DESIGN-LOG — Highwater Rafting Co. (DADA)

A rebuild of `SolutionsAsService/BasicRaftingSite`, which was three files:
`index.html` (a hero, an About paragraph, three services), `adventures.html`
(a form with no action, no method and no handler), `styles.css` (Arial,
`#004d99`, a `.hero` pointing at a `hero.jpg` that does not exist), and five
dead React files nothing loaded.

---

## 1. Traversal Plan

**Brief, one sentence.** Rebuild that repo as a real business site for a river
rafting outfitter — a multi-page brochure-and-booking site a customer can use
to choose a trip and get in touch — and list it in the studio portfolio.

**Mode: Adaptive.** The brief names a business and its customers. Governing
criterion is `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)`, reached by
`maya -->|bounds the break of| samBreak`: both poles must hold on every move —
the advanced pole (significant form, typographic and chromatic ambition) and
the acceptable pole (a customer can find the phone number, compare trips, and
book). Neither vetoes the other alone.

### Step 0. Tooling inventory

| Job | Used |
|---|---|
| Render and navigate the anchor graph | none available — Mermaid text below |
| Compute the Frontier | none available — read by hand from the edge lines |
| Track workflow state | none available — checklists in this file |
| Run the panel | **Agent tool, one agent per literary reference** |
| Collect panel reports | **panel directory + `scripts/collect_panel.py`** (see §6) |
| Persist the log | this file |
| Measure the artifact | Playwright + Chrome (`_src/tools/{audit,probe,shoot}.py`), PIL for pixel sampling |

### Seed (labels verbatim from `references/anchor-graph.md`)

- **Stance** `Make It Bigger (Paula Scher)` — `scher`
- **Rule** `Grid Systems in Graphic Design (Josef Müller-Brockmann)` — `mb`
- **Rule** `The Elements of Typographic Style (Robert Bringhurst)` — `bring`
- **Rule** `Interaction of Color (Josef Albers)` — `albers`
- **Breaker** `Making and Breaking the Grid (Timothy Samara)` — `samBreak`
- **Counterpoint** `WCAG 2.2 Contrast and Perceivability (W3C)` — `wcag`, by
  the dotted edge `wcag -.->|contrast floor constrains| albers`

Reached during the run: `Designing Programmes (Karl Gerstner)` — `gerstner`, by
`mb -->|codifies| itstyle` then back along `gerstner -->|programme method of|
itstyle`; `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)` — `maya`, by
`maya -->|bounds the break of| samBreak`.

### Chain

`Make It Bigger (Paula Scher)` sets the scale of the argument → `Grid Systems
in Graphic Design (Josef Müller-Brockmann)` gives that scale a field → `The
Elements of Typographic Style (Robert Bringhurst)` governs the letterforms on
it → `Interaction of Color (Josef Albers)` sets the intervals between the hues
→ `Making and Breaking the Grid (Timothy Samara)` loosens the field where the
river earns a rupture → `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)`
bounds that rupture → counterpoint `WCAG 2.2 Contrast and Perceivability
(W3C)`, by `wcag -.->|contrast floor constrains| albers`.

### Panel

Seven seats, one agent per literary reference: Debord, Shklovsky (Provocateur),
Holmes, Mace (Inclusion), Krug (Usability), Sharp (Brand Strategy), Bringhurst
(Craft). Holmes ↔ Krug are joined by the dotted edge
`crit_prov_debord -.->|attacks smoothness favored by| crit_use_krug`.

---

## 2. Decision Records

## Move M1: Commit the referent  (KEEP-THE-RULE)
Depends on: none
Anchors: Rule `Designing Programmes (Karl Gerstner)` | Rule `Grid Systems in Graphic Design (Josef Müller-Brockmann)` | Counterpoint `WCAG 2.2 Contrast and Perceivability (W3C)`
Intent: one business, one place, one river; every fact lives in `_src/data/*.json` and every page is generated from it. Four competing identities (`Adventure Rafting Co.`, `Rio Grande Rafting Adventures`, `BasicRaftingSite`, the React files) become one: Highwater Rafting Co., Salida, Colorado, the Arkansas.
Formal argument: a page cannot argue for a business it cannot name a fact about; Gerstner's programme is one rule generating every instance, so the instance cannot drift from the rule; WCAG is the floor under any claim the page makes.
Alternatives rejected: (a) hand-written pages with the facts typed in — the same fact then lives in two places and one of them goes stale (it already had: `pages/index.js` named a different company); (b) a real CMS — wrong weight for seven pages.
Consequence: content edits are data edits; the build gains a link check.
Fence: Müller-Brockmann's grid is a field for content, not a substitute for it — the data supplies the content first.
Frontier effect: opens "what does the page do with a fact it can recompute" (M2).
Mode field: Advanced — a programme, not hand-made cards; Acceptable — every price, age and season a customer needs is now present and checkable.
Measured: 7 pages generated from 3 data files; 10 internal links fetched, 0 bad; build exits non-zero on a dead link (verified by pointing a link at a missing file).

## Move M2: The gauge is the unit of measure  (BREAK)
Depends on: M1
Anchors: Breaker `Making and Breaking the Grid (Timothy Samara)` | Stance `Make It Bigger (Paula Scher)` | Bounded by `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)`
Intent: one axis — 0 to 6,000 cubic feet per second — carried by the home page, the trips page and every trip card. Each trip draws its operating window on that axis, and one vermilion index line marks the reading. What the site sells is decided by what the river does.
Formal argument: an outfitter's actual inventory decision is flow, so the site's measure should be flow; the axis crosses the column grid rather than sitting inside it (Samara), and it is set at display size because the number is the argument (Scher).
Alternatives rejected: (a) a hero photograph — none exists in the repo, and the inherited `.hero` already pointed at a missing `hero.jpg` that rendered white text on near-white; (b) difficulty as the only axis — every competitor site does that and it says nothing about today.
Consequence: the site's most advanced element is also its most useful, and it must stay honest about being a sample reading.
Fence: Müller-Brockmann's grid exists so a reader can predict where things are; the axis is a second, explicit grid laid over it, and every trip is placed on it — not scattered.
Frontier effect: opens the tense question (M6), the handle question (S4 push).
Mode field: Advanced — a full-width axis crossing the column field; Acceptable — it reads as a gauge, and each trip's window is printed as numbers as well as drawn.
Measured: reading 2,480 cfs on the 0–6,000 axis; trip states `on, on, on, over, on, on`; Pine Creek (500–1,600) is the one closed.

## Move M3: Typography built outward from the text  (KEEP-THE-RULE)
Depends on: M1
Anchors: Rule `The Elements of Typographic Style (Robert Bringhurst)` | Rule `Grid Systems in Graphic Design (Josef Müller-Brockmann)`
Intent: body 18px/27px, a 34em measure, left-aligned ragged-right running text, and display sizes on one stated ratio from the same base — 18 → 25.5 → 36 → 50.9 → 72 — with h1 at the top of it. Three families: Fraunces display, IBM Plex Sans text, IBM Plex Mono metadata.
Formal argument: Bringhurst's measure and leading are properties of the text, not of the layout; a scale derived from the text size keeps the hierarchy a consequence rather than a set of browser defaults.
Alternatives rejected: (a) keeping Arial — one face at 40px and at 16px is not a system; (b) four or more families — the gauge gains nothing from a fourth voice.
Consequence: the inherited inverted scale (h1 smaller than an h2) is gone.
Frontier effect: opens "does the palette carry the same discipline" (M4).
Mode field: Advanced — Fraunces with soft and wonk axes at display size; Acceptable — 18px text on a 67-character line.
Measured: body 18px/27px; `.prose` 67 characters (612px) at 1280px, 48–67 across the other six pages; h1 50.896px on all seven.

## Move M4: No blue  (KEEP-THE-RULE)
Depends on: M3
Anchors: Rule `Interaction of Color (Josef Albers)` | Counterpoint `WCAG 2.2 Contrast and Perceivability (W3C)` by `wcag -.->|contrast floor constrains| albers`
Intent: the ground is granite near-black teal `#0E2429`, the paper is warm `#F2EFE9`, and there is one vermilion signal. No blue anywhere: river-blue plus safety-orange was the category default and was literally the inherited palette (`#004d99`, `#ff6600`).
Formal argument: Albers — colour is interval, not hue; the interval that carries meaning here is cold ground against one hot signal. The counterpoint holds because every pair was picked by measured ratio, not by eye.
Alternatives rejected: (a) a deeper river blue — it is the category uniform and Sharp's objection was that the site read as a category, not a brand; (b) green/earth adventure palette — same problem.
Consequence: muted greys must be swapped for muted lights inside every dark band, or they fail — they did, at 2.47:1, and were fixed.
Fence: Albers' intervals are only legible above a contrast floor; the floor is the counterpoint, not a veto.
Frontier effect: opens the forced-colours question (R2, Mace).
Mode field: Advanced — a rafting site with no blue; Acceptable — measured contrast, 0 failures.
Measured: `--signal` #D1370A carries white text at 4.93:1; `--signal-ink` #A82A08 on paper 6.10:1; `--muted-lite` #A9B4B4 on the gorge 7.58:1; audit 0 failing at 1280/390/320 across 7 pages.

## Move M5: The booking ends in a sentence  (KEEP-THE-RULE)
Depends on: M1
Anchors: Rule `WCAG 2.2 Contrast and Perceivability (W3C)` | Bounded by `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)`
Intent: the form validates in place, never reloads, and prints one sentence built from the visitor's own choices, focused and announced. It says plainly that it sent nothing.
Formal argument: a control whose submit changes nothing is a lie about itself; the acceptable pole of MAYA is that a customer can complete the task or knows why they cannot.
Alternatives rejected: (a) posting to a third-party form service — the repo has no endpoint and inventing one would make the page claim a capability it lacks; (b) a "we'll be in touch" confirmation — a lie.
Consequence: the receipt is the site's most quoted element, so it has to be right in every tense and channel.
Frontier effect: opens the season and capacity checks (M6), and the channel question (M8).
Mode field: Advanced — a composed sentence, not a template string; Acceptable — keyboard-only, announced, no reload.
Measured: keyboard-only submit → receipt visible, focus moves to it, `aria-live=polite`, URL unchanged.

## Move M6: Print the season's own tense  (KEEP-THE-RULE)
Depends on: M2, M5
Anchors: Counterpoint `WCAG 2.2 Contrast and Perceivability (W3C)` | Stance `Make It Bigger (Paula Scher)`
Intent: the reading is a sample from 11 Jun 2026 and today is 27 October, outside the 15 May – 31 Aug season. So every state prints in the conditional — "Would run", "Would be too high" — the gauge carries its own date, and "Live river gauge" leaves the meta description. The receipt refuses a date outside a trip's season and a party larger than one raft.
Formal argument: Scher's display sizes make a claim loudly, so a loud claim must be a true one; the counterpoint is the same principle applied to honesty rather than contrast.
Alternatives rejected: (a) dropping the gauge out of season — it is the site's one device; (b) printing "Running" with a footnote — Krug: scanners do not read footnotes.
Consequence: rebuilding in June flips the whole site to the present tense automatically. That is the point.
Frontier effect: none new; closes Debord's Andon.
Mode field: Advanced — the tense is computed, not written; Acceptable — a visitor cannot believe a trip runs today when the shed is shut.
Measured: `Would run · 2,480 of 4,800 cfs`; `Would be too high — runs to 1,600 cfs`; receipt adds "That date is outside this trip's season, which runs Jul 1 to Aug 31" and "That is more than one raft holds (5 seats)".

## Move M7: One source of truth for the mark  (KEEP-THE-RULE)
Depends on: M4
Anchors: Stance `Make It Bigger (Paula Scher)` by `scher -.->|identity as environment answers| wheeler`
Intent: the gauge glyph — four bars crossed by a vermilion index line — is the favicon, the masthead mark, the footer mark and the 1200×630 social card, in the same polarity and the same vermilion. `adventures.html`, `styles.css`, `components/` and `pages/` are deleted.
Formal argument: an asset rendered differently at each touchpoint is not an asset; Scher's identity-as-environment is the mark repeated until it is the place, not a logo on it.
Alternatives rejected: (a) keeping the old files for "reference" — they carry a competing identity and contradict "one river"; (b) a photographic social card — no photographs exist.
Consequence: `ogcard.py` must be re-run if the tokens change.
Frontier effect: none new.
Mode field: Advanced — the mark is the gauge is the brand; Acceptable — the shared card finally carries the name.

## Move M8: A channel you can actually use  (KEEP-THE-RULE)
Depends on: M5
Anchors: Rule `WCAG 2.2 Contrast and Perceivability (W3C)` | Bounded by `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)`
Intent: "How should we reply?" — Whichever is fastest / Phone call / Text message / Email. Only the channel you pick is required; "whichever" needs one of the two. The receipt names the counterparty in the channel you chose.
Formal argument: a required phone number closes the form to anyone who cannot use a voice line, which is most of the point of offering email; the browser's own `required` attribute follows the choice so both guards agree.
Alternatives rejected: (a) requiring email always — the same gate with a different organ; (b) requiring nothing — then there is no way back to the visitor.
Consequence: the error copy has to name the channel, not "call back".
Frontier effect: none new.
Mode field: Advanced — the required attribute is computed; Acceptable — no visitor is blocked by a channel they cannot use.
Measured: call with no phone → blocked, "A call needs a number with at least ten digits."; email with no phone → receipt, "email the shed at trips@highwaterrafting.example"; neither given → one message, "Give us an email or a phone number — whichever you would rather use."

---

## 3. Panel Reports

### R0 — WHOLE, premortem on the inherited artifact
All seven seats OBJECT. Three pulled the Andon.

| Critic | Anchor | Observed | Verdict | Requested change |
|---|---|---|---|---|
| Debord | *Society of the Spectacle* §1, §10 | `index.html:16` → `contact.html` does not exist; no price, season, permit, town or phone anywhere in the repo; `adventures.html:24` a form with no action or handler; `styles.css:37` a `hero.jpg` that is not there | OBJECT, Andon | commit the referent: one data file with name, phone, address, per-trip attributes; fail the build on a dead link |
| Shklovsky | *Art as Technique* | "Your ultimate destination for" is a slot, not a phrase; the three-service card device repeated to zero perception; the one perceptible thing — dogs on a raft — buried as an aside; the complete motor sequence of buying ending in nothing | OBJECT | make the booking end in a perceived event; make the dog the thing it decides |
| Holmes | *Mismatch* | no `:focus` rule anywhere in 117 lines; white on `#f4f4f4` = 1.10:1; submit reloads in silence; fixed footer occludes the submit at zoom | OBJECT, Andon | visible focus, fieldset/legend, un-fix the footer, submit resolves in place with `aria-live` |
| Mace | *Universal Design* | hero `.btn` `#ff6600` on white = 2.94:1; nav targets ≈18px; no skip link | OBJECT, Andon | make perceivability a property of the stylesheet, not of an asset |
| Krug | *Don't Make Me Think* | happy talk; unreadable hero; broken Contact; "Book Adventure" books nothing | OBJECT | named trips with river, season, duration, price, party size; visible confirmation; a real phone number |
| Sharp | *How Brands Grow* | four competing names; "Adventure Rafting Co." is a category, not a name; no mark, no favicon, no place | OBJECT | one ownable name plus an asset set rendered identically at every touchpoint |
| Bringhurst | *Elements of Typographic Style* | zero `max-width` → ≈175 characters per line; zero `line-height` → 16/18; h1 smaller than an h2; `text-align:center` four times; one face | OBJECT | 18/27, 34em, left rag, one stated ratio, h1 at the top |

Votes: commit a real referent (Debord, Sharp, Krug, Holmes); the booking must do something visible (Shklovsky, Krug, Holmes); typography from the text (Bringhurst, Mace).

### R1 — WHOLE, on the rebuilt artifact (`E:/raft-shots/EVIDENCE.md`, source)

| Critic | Verdict | Observed | Requested change |
|---|---|---|---|
| Debord | OBJECT, Andon | the referent thickened but `trips.html` still printed "5 of 6 trips **are** running" in October, and the receipt said "call the shed" with no number | put the summary in the conditional with its date; give the shed a counterparty |
| Shklovsky | OBJECT | the water is frozen: all six states resolved at build time, nothing recomputed; the dog stayed conditional prose | make 2,480 movable; bind the dog to the reading |
| Holmes | OBJECT | phone `required` with a 10-digit rule — a Deaf user cannot submit; `#run-summary` had no `aria-live`, `#cfs` no `aria-valuetext` | make phone conditional; add a channel choice; announce the gauge |
| Mace | Accept, 4 requests | `.checklist li::before` is a `background` (vanishes in forced colours); range input 24px; `.guide__certs` 11px; rotated 12px caps; `novalidate` leaves no guard without JS | glyph bullet, 44px slider, 0.75rem floor, upright below 900px, drop `novalidate` |
| Krug | OBJECT | "Right now, at 2,480 cfs"; meta promised a "Live river gauge"; 12 guests on 20 June priced "$1,548 all in" | take the flow claim out of the present tense; check date against season and party against capacity |
| Sharp | OBJECT | two vermilions (`#E2400F` vs `#D1370A`); polarity flipped between favicon and masthead; no `og:image` while `summary_large_image` was declared | one source of truth for the mark; generate the card; delete the competing identity |
| Bringhurst | OBJECT | four of five R0 points answered; `.nf__code` reaches 144px on a scale the file states tops out at 72; `.gauge__read` outranks the h1 | cap the 404 numeral; raise 11px caps to 12px with wider tracking; `text-wrap: pretty` |

All seven resolved by ADAPT. No seat was overruled.

### R2 — WHOLE, after the fixes

| Critic | Verdict | Observed | Requested change |
|---|---|---|---|
| Debord | OBJECT | the live sentence still said "At **this reading**" — a pronoun with no antecedent; `' are' + ' would be closed'` renders "Pine Creek, Royal Gorge are would be closed"; `how.value` dereferences null when `#contact` is absent | carry the reading into the sentence; fix the plural; null-guard the channel |
| Holmes | OBJECT | email is `required` for every choice including "Phone call"; the select's default is the one option that excludes; `aria-valuetext` set only on input, so a slider never moved is a bare number; `aria-live` plus `valuetext` speaks twice | require only the chosen channel; default to a non-excluding option; set `valuetext` on load; drop one announcement |
| Mace | Accept | all four R1 requests honoured; `.g-now` and `.range__now` are *not* in the `forced-color-adjust` list, so the needle vanishes; `.preview` state is colour-only; the bullet is aligned by `line-height: 2.1` arithmetic | exempt the needles; give state a glyph; lay the bullet out by the box |
| Krug / Sharp / Shklovsky / Bringhurst | see below | | |

All three R2 objections resolved by ADAPT; no seat was overruled.

---

## 4. Anchor Ledger

| Anchor | Role | Status | Evidence | Note |
|---|---|---|---|---|
| `Make It Bigger (Paula Scher)` | Stance | KEEP | h1 50.9px; the gauge numeral at 72px; survived Krug's "the loudest claim must be the truest one" via M6 | dotted `scher -.-> wheeler` applied (M7) |
| `Grid Systems in Graphic Design (Josef Müller-Brockmann)` | Rule | KEEP | 3- and 2-column fields, `minmax(0,1fr)`; survived Samara's loosening via M2 | — |
| `Designing Programmes (Karl Gerstner)` | Rule | KEEP | 7 pages from 3 data files; a link check that fails the build | reached via `itstyle` |
| `The Elements of Typographic Style (Robert Bringhurst)` | Rule | ADAPT | 18/27, 67 characters, 1.414 scale; adapted twice after Bringhurst's R1 and R2 notes (404 numeral capped, caps raised to 12px, `text-wrap: pretty`) | — |
| `Interaction of Color (Josef Albers)` | Rule | KEEP | no blue; one vermilion; every muted token flips inside a dark band | dotted `albers -.-> itten` **declined**: the palette is built on measured ratios, not on Itten's seven contrasts |
| `WCAG 2.2 Contrast and Perceivability (W3C)` | Counterpoint | KEEP | 0 failing at 3 widths × 7 pages; forced-colours block | dotted `wcag -.-> albers` applied (M4) |
| `Making and Breaking the Grid (Timothy Samara)` | Breaker | KEEP | the cfs axis crosses the column field; escalated by the S4 push | dotted `samBreak -.-> mb` applied |
| `MAYA: Most Advanced Yet Acceptable (Raymond Loewy)` | Governing | KEEP | every move carries both poles | `maya --> samBreak` applied |

## 5. Stop test

- **S1** No OPEN Frontier items; each TAKEN (M1–M8) or DEFERRED with a reason. Deferred: wiring the gauge to the real USGS feed (needs a live endpoint — recorded in the README, not a design decision); a real booking endpoint (same). **Met.**
- **S2** R2 returned no Andon. The three R2 objections were all resolved by ADAPT and re-measured. **Met** for the seats that reported; see §6 for the two that did not.
- **S3** Two consecutive rounds (R1, R2) with no SCRAP and no REOPEN; every move survived. **Met.**
- **S4** Ambition push: the gauge (M2) was escalated from a static reading to a handle — drag it or use `?cfs=`, and every state follows. Measured delta: at 2,480 cfs the states are `on,on,on,over,on,on` and Browns Canyon's tag reads "Dogs under 1,800 cfs"; dragged to 1,200 they are `on,on,on,on,on,on` and the tag reads "Dogs welcome"; dragged to 5,200 the summary reads "At 5,200 cfs, 1 of 6 would run and Buena Vista Float, Browns Canyon, The Numbers, Pine Creek, Granite Camp would be closed." The lever moved the work. **Met.**
- **S5** Dotted edges from used anchors: `wcag -.-> albers` applied (M4); `scher -.-> wheeler` applied (M7); `samBreak -.-> mb` applied (M2); `albers -.-> itten` declined with the reason above; `wcag -.-> carson` not applicable — no Carson-style illegibility was introduced. **Met.**

## 6. A note on the instrument

This run is why the panel protocol was added to the skill. R1 launched seven
seats in one batch: five died with a gateway error and had to be re-run. With
the protocol in place — verdicts filed to `panel/R<n>/<seat>.md`, batches of
three, prompts under ~350 words — R2 filed 3 of 3 with no losses, and
`scripts/collect_panel.py` named the missing seats instead of leaving me to
remember them. Two R2 seats (Krug, Bringhurst) had not reported when this log
was written; they are recorded as NOT REPORTED rather than as PASS.

## 7. Double loop

The failures in this run were almost all in the instrument, not the doctrine.
The contrast audit reported a 1.03:1 failure on "Skip to content" that was an
artefact of the link being parked at `left:-999px`, so the sampler read the
page corner instead of the link's own background; the fix was in the CSS
(`transform: translateY(-150%)`), and it is a better pattern anyway. The link
check reported ten 404s that were an artefact of the local static server not
running Vercel's `cleanUrls`; the fix was in the probe, not the site. And five
panel seats were lost to a transport error that the new protocol now contains.
**Graph amendment:** add a node "Instrument check" to the PANEL cluster with
the edge `c_genchi -->|verify the measurement against the rendered page before
tabling a premise for| CRITICS`, so any finding seen only in a tool's output is
measured on the page before a move is spent on it.
