"""Capture a page as one image, tile by tile, in the viewport.

Playwright's full_page=True capture is offset against the DOM: at 320px on
index.html a button whose getBoundingClientRect says y=441 paints its amber at
y=448 in the full_page image, so anything measured against it is measuring the
wrong seven pixels. A viewport capture is exact (the same button samples
rgb(242, 182, 107) at the centre). So scroll, shoot the viewport, and stitch.

The sticky header is pinned to the top of every tile; making it static is
layout-neutral and keeps it from repeating down the stitched image.
"""
import pathlib

from PIL import Image

QUIET = ("html { scroll-behavior: auto !important; }"
         ".masthead, .site-header { position: static !important; }")


def unpin(page):
    """Make sticky elements static for the duration of a capture.

    A sticky element is painted at its viewport position, not its document
    position, so in a stitched image its text and its background land in
    different rows and the contrast figure is nonsense. Sticky elements keep
    their place in normal flow, so this is layout-neutral.
    """
    page.evaluate("""() => document.querySelectorAll('*').forEach(el => {
        if (getComputedStyle(el).position === 'sticky') el.style.position = 'static';
    })""")


def stitch(page, path, tile=760, freeze=False):
    """Screenshot `page` in viewport-height tiles and write one PNG to `path`."""
    page.add_style_tag(content=QUIET)
    unpin(page)
    if freeze:
        page.add_style_tag(content="*, *::before, *::after { animation: none !important;"
                                   " transition: none !important; }")
    height = page.viewport_size["height"]
    width = page.viewport_size["width"]
    doc = page.evaluate("document.documentElement.scrollHeight")
    step = max(1, tile - 40)
    canvas = Image.new("RGB", (width, doc), (255, 255, 255))

    for y in range(0, doc, step):
        page.evaluate("window.scrollTo(0, %d)" % y)
        page.wait_for_timeout(60)
        # scrollTo clamps at the bottom, so paste where the page actually landed
        # rather than where it was asked to go, or the last tile shifts upward.
        top = page.evaluate("window.scrollY")
        shot = pathlib.Path(path).with_suffix(".tile.png")
        page.screenshot(path=str(shot))
        with Image.open(shot) as im:
            canvas.paste(im.convert("RGB"), (0, top))
        shot.unlink()
        if top >= doc - height:
            break

    canvas.save(path)
    page.evaluate("window.scrollTo(0, 0)")
    return path
