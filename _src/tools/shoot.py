"""Screenshot every page at desktop and phone widths.

    python _src/tools/shoot.py [out_dir]

Writes <out_dir>/<page>-<width>.png, stitched from viewport tiles (see
capture.py). Used to render the artifact for the design panel.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

from capture import stitch
from serve import serve

PAGES = ["index", "trips", "guides", "safety", "book", "visit", "404"]
SIZES = [(1280, 900), (390, 844), (320, 700)]


def main() -> None:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "E:/raft-shots")
    out.mkdir(parents=True, exist_ok=True)

    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height},
                                    device_scale_factor=1)
            for name in PAGES:
                page.goto(f"{base}/{name}.html")
                page.wait_for_load_state("networkidle")
                stitch(page, str(out / f"{name}-{width}.png"), tile=height)
            page.close()
        browser.close()

    for f in sorted(out.glob("*.png")):
        print(f"{f.name:22} {f.stat().st_size:>9,} bytes")


if __name__ == "__main__":
    main()
