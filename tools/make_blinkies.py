#!/usr/bin/env python3
"""Animate the wall stamps with a continuous cathode-ray scan.

The bar advances four pixels per frame over a stamp fifty-six pixels
tall, so fourteen frames return it to its start and the loop repeats
without a seam. The contact stamps stay still, because they address a
reader who wants an address rather than a decoration.
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


import os

from PIL import Image

SRC = str(REPO / "assets" / "stamps")
W, H = 99, 56
FRAMES = 14
STEP = H // FRAMES        # Four pixels; fourteen frames close the cycle.
BAR = 10
SCAN = 0.68               # How much a scanline row keeps of its brightness.
LIFT = 1.55               # How much the bar raises the rows it covers.

STILL = {"email", "x", "linkedin", "liberapay"}


def crt(base, offset):
    """Apply the scanlines and the travelling bar for one frame."""
    px, out = base.load(), Image.new("RGB", (W, H))
    op = out.load()
    for y in range(H):
        d = (y - offset) % H
        scale = SCAN if y % 2 else 1.0
        if d < BAR:
            scale *= LIFT - (LIFT - 1.0) * (d / BAR)
        for x in range(W):
            r, g, b = px[x, y][:3]
            op[x, y] = (min(255, int(r * scale)), min(255, int(g * scale)),
                        min(255, int(b * scale)))
    return out


total = 0
for name in sorted(os.listdir(SRC)):
    if not name.endswith(".png"):
        continue
    stem = name[:-4]
    if stem in STILL:
        continue
    base = Image.open(f"{SRC}/{name}").convert("RGB")
    frames = [crt(base, (i * STEP) % H) for i in range(FRAMES)]
    frames = [f.quantize(colors=64, method=Image.MEDIANCUT,
                         dither=Image.NONE) for f in frames]
    out = f"{SRC}/{stem}.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=80, loop=0, optimize=True, disposal=1)
    total += os.path.getsize(out)
    print(f"  {stem:22s} {os.path.getsize(out):>6,} B")

print(f"\n{total:,} bytes animated; {len(STILL)} stamps stay still")
