#!/usr/bin/env python3
"""Check the profile documents: box alignment, links and asset paths."""

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
import re
import unicodedata

ROOT = str(REPO)
import glob
DOCS = ["README.md", "LICENCE.md"] + sorted(glob.glob("i18n/*/README.md"))

BOX_START = ("┌", "╔")
BOX_CHARS = set("┌┐└┘├┤─│╔╗╚╝║═┬┴┼")


def width(s):
    """Terminal cell width of a string, counting wide glyphs as two."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1
               for c in s)


problems = []

for doc in DOCS:
    path = os.path.join(ROOT, doc)
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")

    # --- BOX ALIGNMENT ---
    inside, block, start = False, [], 0
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if inside:
                widths = {width(b) for b in block
                          if b and b[0] in BOX_CHARS}
                if len(widths) > 1:
                    problems.append(
                        f"{doc}:{start} box lines differ in width: "
                        f"{sorted(widths)}")
                    for bn, b in enumerate(block, start + 1):
                        if b and b[0] in BOX_CHARS and width(b) != max(widths):
                            problems.append(
                                f"    line {bn}: width {width(b)} — {b!r}")
                inside, block = False, []
            else:
                inside, start = True, n
            continue
        if inside:
            block.append(line)

    # --- RELATIVE LINKS AND IMAGES ---
    base = os.path.dirname(path)
    targets = re.findall(r'\]\(([^)#]+?)\)', text) + \
        re.findall(r'src="([^"]+)"', text)
    for t in targets:
        if t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        resolved = os.path.normpath(os.path.join(base, t))
        if not os.path.exists(resolved):
            problems.append(f"{doc}: missing target {t} -> {resolved}")

    # --- ACCESSIBILITY: every img needs alt ---
    for img in re.findall(r'<img\b[^>]*>', text, re.S):
        if 'alt=' not in img:
            problems.append(f"{doc}: img without alt: {img[:70]}")

if problems:
    print(f"{len(problems)} problems\n")
    for p in problems:
        print(" ", p)
else:
    print("All boxes aligned, all links resolve, every image has alt text.")
