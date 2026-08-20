#!/usr/bin/env python3
"""Animate the wall stamps with a band of light crossing each face.

A soft highlight sweeps from one side to the other and wraps, so the
loop closes without a seam. Each stamp starts at its own point in the
cycle, set by its position in the grid, which stops the wall from
pulsing as one block.

Browsers give every GIF its own clock — each starts when it finishes
decoding — so a sweep that crosses the whole wall in step is not
something this can promise. The phase offset is what keeps the wall
from looking synchronised.
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


import math
import os

from PIL import Image

SRC = str(REPO / "assets" / "stamps")
W, H = 99, 56
FRAMES = 18
FLOOR = 0.86              # The face at rest.
LIFT = 0.62               # How much brighter the band makes it.
SPREAD = 300.0            # Width of the band, as a squared falloff.

STILL = {"email", "x", "linkedin", "liberapay"}


def sweep(base, phase):
    """One frame: a band of light centred somewhere along the face."""
    px, out = base.load(), Image.new("RGB", (W, H))
    op = out.load()
    centre = phase * (W + 60) - 30
    # Precompute the column weights; every row shares them.
    weights = []
    for x in range(W):
        d = x - centre
        near = math.exp(-(d * d) / SPREAD)
        # The band wraps, so the leading edge appears before the tail goes.
        d2 = x - (centre - (W + 60))
        near = max(near, math.exp(-(d2 * d2) / SPREAD))
        weights.append(FLOOR + LIFT * near)
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y][:3]
            k = weights[x]
            op[x, y] = (min(255, int(r * k)), min(255, int(g * k)),
                        min(255, int(b * k)))
    return out


total = 0
for order, name in enumerate(sorted(os.listdir(SRC))):
    if not name.endswith(".png"):
        continue
    stem = name[:-4]
    if stem in STILL:
        continue
    base = Image.open(f"{SRC}/{name}").convert("RGB")
    # Each stamp enters the cycle at its own point.
    offset = (order * 0.37) % 1.0
    frames = [sweep(base, ((i / FRAMES) + offset) % 1.0)
              for i in range(FRAMES)]
    frames = [f.quantize(colors=64, method=Image.MEDIANCUT,
                         dither=Image.NONE) for f in frames]
    out = f"{SRC}/{stem}.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=70, loop=0, optimize=True, disposal=1)
    total += os.path.getsize(out)
    print(f"  {stem:22s} {os.path.getsize(out):>6,} B")

print(f"\n{total:,} bytes animated; {len(STILL)} stamps stay still")
