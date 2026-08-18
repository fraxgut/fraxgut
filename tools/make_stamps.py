#!/usr/bin/env python3
"""Generate the 99x56 stamps and colour the wall like a graph.

Each stamp carries a canton on the left holding the original logotype,
a rule, and the caption on the right.

The canton ground comes from the logotype itself: the script averages
the mark's own colour and darkens it to a ground, so a stamp is
recognisable from across the page. A mark that is pale or monochrome
averages to grey, so those stamps name their ground by hand in FIXED.

The wall is a three by seven grid, and two stamps that touch — including
on the diagonal — take different border colours, and different canton
grounds. That is the eight-neighbour colouring of a king graph, which
needs four colours at minimum. The script verifies the result and stops
rather than writing a clash.

Colours come from Phosphor Base24 (github.com/fraxgut/phosphor).
"""

import colorsys
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

# Paths resolve from this file, so the scripts run from anywhere.
REPO = pathlib.Path(__file__).resolve().parent.parent
LOGOS = REPO / "assets" / "logos"
OUT = REPO / "assets" / "stamps"
OUT.mkdir(parents=True, exist_ok=True)


def terminus(size):
    """Return a Terminus face, unpacking the console font on demand."""
    name = {12: "ter-x12b", 16: "ter-x16b"}[size]
    out = pathlib.Path(tempfile.gettempdir()) / f"{name}.pcf"
    if not out.exists():
        with open(out, "wb") as fh:
            subprocess.run(["gzip", "-dc",
                            f"/usr/share/fonts/terminus/{name}.pcf.gz"],
                           stdout=fh, check=True)
    return ImageFont.truetype(str(out), size)


W, H = 99, 56
CANTON = 28               # One width for every stamp.
CELL = 6                  # Terminus 12 advances six pixels.
BOX = 20                  # The mark never reaches the border.
GROUND_LEVEL = 0.30       # How far the logotype colour drops to a ground.

# --- PHOSPHOR BASE24 --------------------------------------------------
BLACK = "#000000"
BONE = "#FFFAEB"          # base07
MUTED = "#96948B"         # base05; never repeats a border colour.

# The bright chromatic slots, which carry the borders.
BORDERS = {
    "red": "#FF4C49", "orange": "#E7A739", "yellow": "#C98A04",
    "lime": "#9DDB3C", "green": "#44E084", "blue": "#3EA4F8",
    "violet": "#A573FF", "magenta": "#D5268A",
}

# Grounds named by hand, for marks whose own colour says the wrong thing:
# a white star averages to grey, and a lifted monochrome mark to bone.
FIXED = {
    "chile": "#4a0a12",         # The star is white; take the flag's red.
    "latine": "#3b1030",        # Tyrian purple, for the eagle.
    "santiago": "#2e2a26",      # The cross is red on white.
    "shell": "#0b2418",         # A drawn chevron on phosphor green.
    "foss": "#2b2016",          # The mark was lifted to bone.
    "instituto-nacional": "#101f42",
    "lazio": "#0d2b46",         # The club plays in sky blue.
    "futbol": "#0f2a14",        # Grass.
    "linkinpark": "#2a0d14",
    "clang": "#1a2c5c",         # The C logo is blue.
    "gentoo": "#2a1f3d",        # Gentoo purple.
}

font = terminus(12)

# --- THE WALL ---------------------------------------------------------
# Each cell: name, caption, sub, logo, preferred borders. The solver
# takes the first preference no neighbour holds.
WALL = [
    [("instituto-nacional", "INSTITUTO", "NACIONAL", "instituto-nacional.png",
      ["violet", "magenta"]),
     ("uchile", "UNIVERSIDAD", "DE CHILE", "uchile.png", ["blue", "violet"]),
     ("fcfm", "FCFM", "UCHILE", "fcfm.png", ["red", "magenta"]),
     ("dcc", "DCC", "UCHILE", "dcc.png", ["magenta", "red"]),
     ("gnu-linux", "GNU/LINUX", None, "tux.png", ["yellow", "orange"]),
     ("openbsd", "OPENBSD", None, "openbsd.png", ["orange", "yellow"]),
     ("gentoo", "GENTOO", None, "gentoo.png", ["violet", "magenta"])],

    [("shell", "SHELL", None, "shell.png", ["green", "lime"]),
     ("neovim", "NEOVIM", None, "neovim.png", ["lime", "green"]),
     ("clang", "C", None, "clang.png", ["blue", "violet"]),
     ("foss", "FREE", "SOFTWARE", "fsf.png", ["green", "lime"]),
     ("monero", "MONERO", None, "monero.png", ["orange", "yellow"]),
     ("minecraft", "MINECRAFT", None, "minecraft.png", ["lime", "green"]),
     ("dragonball", "DRAGON", "BALL", "dragonball.png", ["yellow", "orange"])],

    [("latine", "LINGVA", "LATINA", "aquila.png", ["violet", "magenta"]),
     ("santiago", "SANTIAGO", None, "santiago.png", ["red", "magenta"]),
     ("chile", "CHILE", None, "gunelve.png", ["blue", "green"]),
     ("laroja", "LA ROJA", None, "laroja.png", ["red", "orange"]),
     ("lazio", "SS LAZIO", None, "lazio.png", ["blue", "green"]),
     ("futbol", "FOOTBALL", None, "futbol.png", ["green", "yellow"]),
     ("linkinpark", "LINKIN", "PARK", "linkinpark.png", ["magenta", "violet"])],
]

ROWS, COLS = len(WALL), len(WALL[0])


def neighbours(r, c):
    """The eight cells that touch this one."""
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    yield nr, nc


def ground_for(name, logo):
    """The canton ground: the logotype's own colour, dropped to a field."""
    if name in FIXED:
        return FIXED[name]
    im = Image.open(LOGOS / logo).convert("RGBA")
    im.thumbnail((48, 48))
    px = im.load()
    tot, n = [0, 0, 0], 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            # Skip the transparent parts and the near-black outlines.
            if a > 120 and max(r, g, b) > 60:
                tot[0] += r
                tot[1] += g
                tot[2] += b
                n += 1
    if not n:
        return "#141a1e"
    r, g, b = (c / n for c in tot)
    return "#%02x%02x%02x" % (int(r * GROUND_LEVEL), int(g * GROUND_LEVEL),
                              int(b * GROUND_LEVEL))


def solve_borders():
    """Give each cell a border no neighbour holds, by preference."""
    chosen = {}
    for r in range(ROWS):
        for c in range(COLS):
            taken = {chosen[n] for n in neighbours(r, c) if n in chosen}
            for want in WALL[r][c][4]:
                if want not in taken:
                    chosen[(r, c)] = want
                    break
            else:
                spare = [k for k in BORDERS if k not in taken]
                if not spare:
                    raise SystemExit(f"no colour left for {WALL[r][c][0]}")
                chosen[(r, c)] = spare[0]
    return chosen


def shade(hex_colour, step):
    """Lift or deepen a ground, holding the hue the logotype gave it.

    Separating by weight rather than by hue is what keeps Monero orange
    and Tux blue-grey: a neighbour moves in lightness, not in colour.
    """
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, sat, v = colorsys.rgb_to_hsv(r, g, b)
    v = max(0.05, min(0.42, v + 0.055 * step))
    sat = min(1.0, sat + 0.05 * abs(step))
    r, g, b = colorsys.hsv_to_rgb(h, sat, v)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def far_enough(a, b, limit=34):
    """Two grounds differ if their channels are far enough apart."""
    ai = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    bi = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return sum(abs(x - y) for x, y in zip(ai, bi)) >= limit


def separate(grounds):
    """Push a ground around the hue circle until its neighbours differ.

    A stamp named in FIXED keeps its ground; the others move, which is
    what stops two monochrome marks from sitting on the same grey.
    """
    moved = 0
    for r in range(ROWS):
        for c in range(COLS):
            name = WALL[r][c][0]
            if name in FIXED:
                continue
            for turn in range(1, 8):
                clash = [n for n in neighbours(r, c)
                         if not far_enough(grounds[(r, c)], grounds[n])]
                if not clash:
                    break
                # Alternate down and up, so the wall keeps both weights.
                grounds[(r, c)] = shade(grounds[(r, c)],
                                        -turn if (r + c) % 2 else turn)
                if turn == 1:
                    moved += 1
    if moved:
        print(f"  grounds: {moved} moved off a neighbour's hue")
    return grounds


def check(borders, grounds):
    """Touching stamps must differ in border, and in ground."""
    left = []
    for r in range(ROWS):
        for c in range(COLS):
            for n in neighbours(r, c):
                if borders[(r, c)] == borders[n]:
                    raise SystemExit(
                        f"border clash: {WALL[r][c][0]} touches "
                        f"{WALL[n[0]][n[1]][0]}")
                if not far_enough(grounds[(r, c)], grounds[n]):
                    left.append((WALL[r][c][0], WALL[n[0]][n[1]][0]))
    print(f"  borders: {len(set(borders.values()))} colours, no touching pair "
          f"shares one")
    if left:
        print(f"  grounds: {len(left) // 2} pairs still sit close; name one "
              f"of each in FIXED")
        for a, b in left[:4]:
            print(f"      {a} / {b}")
    else:
        print("  grounds: every touching pair separated")


def stamp(name, caption, sub, logo, accent, ground):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, CANTON, H - 1], fill=ground)
    mark = Image.open(LOGOS / logo).convert("RGBA")
    ratio = min(BOX / mark.width, BOX / mark.height)
    mark = mark.resize((max(1, int(mark.width * ratio)),
                        max(1, int(mark.height * ratio))), Image.LANCZOS)
    img.paste(mark, ((CANTON - mark.width) // 2 + 1,
                     (H - mark.height) // 2), mark)
    d.line([CANTON, 2, CANTON, H - 3], fill=accent)

    # Terminus leaves a pixel of air beside each glyph; dropping it lets a
    # long caption keep clear of the border without changing the face.
    def line(text, y, colour):
        cell = 5 if len(text) > 9 else CELL
        x = CANTON + (W - CANTON - len(text) * cell) // 2
        for ch in text:
            d.text((x, y), ch, font=font, fill=colour)
            x += cell

    if sub:
        line(caption, 15, BONE)
        line(sub, 29, MUTED)
    else:
        line(caption, 22, BONE)

    d.rectangle([0, 0, W - 1, H - 1], outline=accent)
    img.save(OUT / f"{name}.png")


borders = solve_borders()
grounds = {(r, c): ground_for(WALL[r][c][0], WALL[r][c][3])
           for r in range(ROWS) for c in range(COLS)}
grounds = separate(grounds)
check(borders, grounds)

for r in range(ROWS):
    for c in range(COLS):
        name, caption, sub, logo, _ = WALL[r][c]
        stamp(name, caption, sub, logo, BORDERS[borders[(r, c)]],
              grounds[(r, c)])

print(f"\n{ROWS * COLS} wall stamps -> {OUT}\n")
for r in range(ROWS):
    print("  " + " ".join(
        f"{WALL[r][c][0][:9]:>9s} {borders[(r, c)][:4]}{grounds[(r, c)]}"
        for c in range(COLS)))
