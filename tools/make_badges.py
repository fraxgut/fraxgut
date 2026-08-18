#!/usr/bin/env python3
"""Generate the social badges, each carrying its own logotype.

A badge is twenty-eight pixels tall: the mark on a field in the brand's
own colour, then the name. The mark travels inside the file as a data
URI, so the badge needs no other host.
"""

import pathlib
import subprocess
import tempfile

# Paths resolve from this file, so the scripts run from anywhere.
REPO = pathlib.Path(__file__).resolve().parent.parent


def terminus(size):
    """Return a Terminus face, unpacking the console font on demand.

    Terminus ships gzipped in /usr/share/fonts, and FreeType needs it
    unpacked. The copy lands in a temporary directory, never in the
    repository.
    """
    from PIL import ImageFont
    name = {12: "ter-x12b", 16: "ter-x16b"}[size]
    out = pathlib.Path(tempfile.gettempdir()) / f"{name}.pcf"
    if not out.exists():
        src = pathlib.Path("/usr/share/fonts/terminus") / f"{name}.pcf.gz"
        with open(out, "wb") as fh:
            subprocess.run(["gzip", "-dc", str(src)], stdout=fh, check=True)
    return ImageFont.truetype(str(out), size)


import base64
import os
import xml.sax.saxutils as x

from PIL import ImageFont

MARKS = str(REPO / "tools" / "marks")
OUT = str(REPO / "assets" / "badges")
os.makedirs(OUT, exist_ok=True)

FONT = "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(FONT, 12)

H = 28
MARK = 16                 # Height of the logotype inside the badge.
PAD = 9


def embed(name):
    blob = open(f"{MARKS}/{name}.png", "rb").read()
    return "data:image/png;base64," + base64.b64encode(blob).decode()


WIDTH = 0                 # Filled in below: the widest badge sets them all.


def measure(label, mark_ratio):
    return PAD + max(1, round(MARK * mark_ratio)) + 7 + \
        int(font.getlength(label)) + PAD


def badge(name, label, colour, mark, mark_ratio, text_colour="#ffffff"):
    """Compose one badge: field, mark, then the name, at the set width."""
    mark_w = max(1, round(MARK * mark_ratio))
    total = WIDTH

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<!--
assets/badges/{name}.svg
@fraxgut
CC-BY-SA-4.0
Social badge: {label}
-->
<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{H}"
     role="img" aria-label="{x.escape(label)}">
  <title>{x.escape(label)}</title>
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".12"/>
    <stop offset="1" stop-opacity=".12"/>
  </linearGradient>
  <rect width="{total}" height="{H}" rx="3" fill="{colour}"/>
  <rect width="{total}" height="{H}" rx="3" fill="url(#g)"/>
  <image x="{PAD}" y="{(H - MARK) / 2}" width="{mark_w}" height="{MARK}"
         href="{embed(mark)}"/>
  <text x="{PAD + mark_w + 7}" y="19" fill="{text_colour}" font-size="12"
        font-family="DejaVu Sans,Verdana,Geneva,sans-serif"
        font-weight="bold">{x.escape(label)}</text>
</svg>
'''
    open(f"{OUT}/{name}.svg", "w", encoding="utf-8").write(svg)
    print(f"  {name:16s} {total:>4d}x{H}  {label}")


SET = [
    ("email", "EMAIL", "#2f6f3a", "email", 44 / 30, "#ffffff"),
    ("linkedin", "IN/FRAXGUT", "#0a66c2", "linkedin", 160 / 158, "#ffffff"),
    ("x", "@FRAXGUT", "#1c1f24", "x", 160 / 145, "#ffffff"),
    ("liberapay", "LIBERAPAY", "#f6c915", "liberapay", 125 / 160, "#1a1a1a"),
    ("gpg", "464F905B27A2BA82", "#3a3f4b", "gpg", 40 / 44, "#ffffff"),
    ("email-es", "CORREO", "#2f6f3a", "email", 44 / 30, "#ffffff"),
    ("email-la", "EPISTULA", "#2f6f3a", "email", 44 / 30, "#ffffff"),
]
WIDTH = max(measure(lbl, ratio) for _, lbl, _, _, ratio, _ in SET)
print(f"  one width for all: {WIDTH}px")
for name, lbl, colour, mark, ratio, tc in SET:
    badge(name, lbl, colour, mark, ratio, tc)


