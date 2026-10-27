"""Render the 1200x630 social card from the same tokens as the site.

    python _src/tools/ogcard.py

A shared link is the touchpoint this outfitter reaches most and the one the
site itself never renders, so the card is generated rather than left to
whatever the crawler finds. It is drawn from the same mark, the same display
face and the same gauge axis as the pages.
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "_src" / "data"
OUT = ROOT / "assets" / "images" / "og-card.png"

o = json.loads((DATA / "outfitter.json").read_text(encoding="utf-8"))
MARK = (ROOT / "assets" / "images" / "favicon.svg").read_text(encoding="utf-8")

CARD = """<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,400..900,0..100,0..1&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  html,body{margin:0;height:630px;width:1200px;overflow:hidden}
  body{background:#0E2429;color:#F2EFE9;font-family:"IBM Plex Sans",system-ui,sans-serif;
       display:flex;flex-direction:column;justify-content:center;padding:0 88px}
  .row{display:flex;align-items:center;gap:26px}
  svg{width:96px;height:96px;flex:none}
  .word{font-family:Fraunces,Georgia,serif;font-weight:800;font-size:82px;letter-spacing:-.03em;
        font-variation-settings:"SOFT" 0,"WONK" 0,"opsz" 144;line-height:.95;color:#fff}
  .tag{font-family:Fraunces,Georgia,serif;font-style:italic;font-size:46px;margin:34px 0 0;
       color:#FF6A3D;font-variation-settings:"SOFT" 30,"WONK" 1,"opsz" 100}
  .meta{margin-top:30px;font-family:"IBM Plex Mono",ui-monospace,monospace;
        font-size:23px;letter-spacing:.06em;text-transform:uppercase;color:#A9B4B4}
  .axis{margin-top:38px;height:14px;background:#16333A;border-radius:2px;position:relative;width:680px}
  .axis i{position:absolute;top:0;bottom:0;background:#1B4A52}
  .axis b{position:absolute;top:-5px;bottom:-5px;width:5px;background:#D1370A}
</style>
<div class="row">__MARK__<div class="word">Highwater<span style="font-size:.42em;letter-spacing:.02em"> Rafting Co.</span></div></div>
<p class="tag">__TAGLINE__</p>
<p class="meta">__PLACE__ &middot; __RIVER__ &middot; __NTRIPS__ guided trips</p>
<div class="axis"><i style="left:0;right:88.3%"></i><i style="left:10%;right:20%"></i>
  <b style="left:__ATPCT__%"></b></div>
"""

scale = o["gauge"]["scaleMax"]
at = round(o["gauge"]["reading"] / scale * 100, 2)


def main() -> None:
    html = (CARD
            .replace("__MARK__", MARK)
            .replace("__TAGLINE__", o["tagline"])
            .replace("__PLACE__", o["place"])
            .replace("__RIVER__", o["river"].replace("the ", "the ").title())
            .replace("__NTRIPS__", "6")
            .replace("__ATPCT__", str(at)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        page = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page.set_content(html)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(OUT))
        b.close()
    print(f"wrote {OUT.relative_to(ROOT)}  {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    sys.exit(main())
