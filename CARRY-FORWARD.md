# Carry-Forward Ledger (facts about this medium, measured in this run)

Read this before Step 1 of any later run on this site, or on the studio's other
static sites.

- **An element parked off-canvas still has a rect.** A skip link at
  `left: -999px` reported 1.03:1 in the contrast pass, because the sampler clamps
  a negative x to 0 and reads the page corner instead of the link's own
  background. Park it with `transform: translateY(-150%)` instead: the rect goes
  negative, the filter `y + h > 0` drops it, and it slides in on focus.
- **A contrast auditor samples the pixel behind the glyph run.** It hides every
  glyph and screenshots, so anything painted by `background` is visible to it and
  anything painted by `color` is not. A bullet drawn with
  `background: var(--signal)` passes while it exists and vanishes under
  `forced-colors: active`; a bullet drawn with `content: "\25A0"` and `color`
  inherits `CanvasText` and survives.
- **A local static server is not Vercel.** `cleanUrls: true` makes `/trips` a
  200 in production and a 404 on `SimpleHTTPRequestHandler`, so a link checker
  that tries one path reports ten dead links that are alive. Try `raw`, then
  `raw + ".html"`.
- **`page.click()` on a submit button did not fire the handler; Enter from a
  field did.** Use the keyboard path when a test needs a submit — it is also the
  path the accessibility acceptance test is written against.
- **A gradient or `color-mix` background is measured, not guessed, by the
  plate pass** — but `forced-color-adjust: none` is needed per element or the
  forced-colours pass repaints it. Exempt every band *and* the index needle;
  missing the needle is the easy one to miss.
- **`aria-live` on a summary plus `aria-valuetext` on the slider that drives it
  makes a screen reader say the same change twice.** Pick one. The slider's
  `valuetext` carries the reading and the count, which is the richer
  announcement; the summary then needs no live region.
- **A function declaration placed by an edit can land outside the block it was
  meant to close**, leaving a stray `}` and a whole file that silently does
  nothing. `node --check js/site.js` after every structural edit to that file.
- **Rotated 12px caps cost a row its height below 900px.** Gate
  `writing-mode: vertical-rl` behind a `min-width` query rather than shipping it
  at every width.
- **`min-height: 24px` passes WCAG 2.5.8 and fails the spirit of a slider** —
  the one control that demands fine motor control should get the 44px the
  buttons get.
- **Panel seats die in transport, not in argument.** Launch at most three at a
  time, keep the prompt under ~350 words, and make each seat file its verdict to
  `panel/R<n>/<seat>.md` as its last action; then collect from the directory. A
  seat that never files is recorded as NOT REPORTED, never reconstructed.
- See also `PersonalPortfolio/CARRY-FORWARD.md` and `hot-tub-site/CARRY-FORWARD.md`
  (smooth-scroll capture artefacts, `display: grid` splitting loose text from an
  inline `<code>`, `1fr` refusing to shrink below a nowrap child).
