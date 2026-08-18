#!/usr/bin/env python3
"""Generate the 99x56 stamps and colour the wall like a graph.

Each stamp carries a canton on the left holding the original logotype,
a rule, and the caption on the right.

The wall is a three by seven grid, and two stamps that touch — including
on the diagonal — take different border colours, and different canton
grounds. That is the eight-neighbour colouring of a king graph, which
needs four colours at minimum; the palette here gives more, so the wall
reads as variety rather than as a pattern.

The order groups by subject: the four schools, then the tools, then
culture, with Lingua Latina beside Chile.
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

from PIL import Image, ImageDraw, ImageFont

LOGOS = str(REPO / "assets" / "logos")
OUT = str(REPO / "assets" / "stamps")
os.makedirs(OUT, exist_ok=True)

W, H = 99, 56
CANTON = 28               # One width for every stamp.
CELL = 6                  # Terminus 12 advances six pixels.
BOX = 20                  # The mark never reaches the border.

# --- FRANKIFUSCUS PALETTE ---------------------------------------------
# TODO(fraxgut): the scheme becomes Phosphor, and Base24 rather than
# Base16. Rename these constants, and the prose in the four pages that
# calls it a base16 scheme, when that lands.
BLACK = "#000000"
BONE = "#fffaeb"
MUTED = "#96948b"         # Caption tone; it never repeats a border colour.

BORDERS = {
    "red": "#d81323", "orange": "#d84413", "yellow": "#d89613",
    "lime": "#96d813", "green": "#13d876", "blue": "#1386d8",
    "violet": "#7513d8", "magenta": "#d81365",
}
GROUNDS = {
    "navy": "#0e1f3d", "maroon": "#2b0f12", "slate": "#141a1e",
    "olive": "#131a10", "tyrian": "#5b1836", "crimson": "#a8121f",
    "coal": "#17140f", "moss": "#0f1c17", "sky": "#0d2b46",
    "bone-field": "#241a1a",
}

font = terminus(12)

# --- THE WALL ---------------------------------------------------------
# Each cell: name, caption, sub, logo, preferred borders, preferred
# grounds. The solver takes the first preference no neighbour holds.
WALL = [
    # Schools, then the first tools.
    [("instituto-nacional", "INSTITUTO", "NACIONAL", "instituto-nacional.png",
      ["violet", "magenta"], ["navy", "slate"]),
     ("uchile", "UNIVERSIDAD", "DE CHILE", "uchile.png",
      ["blue", "violet"], ["slate", "navy"]),
     ("fcfm", "FCFM", "UCHILE", "fcfm.png",
      ["red", "magenta"], ["maroon", "coal"]),
     ("dcc", "DCC", "UCHILE", "dcc.png",
      ["magenta", "red"], ["coal", "maroon"]),
     ("gnu-linux", "GNU/LINUX", None, "tux.png",
      ["yellow", "orange"], ["slate", "coal"]),
     ("openbsd", "OPENBSD", None, "openbsd.png",
      ["orange", "yellow"], ["moss", "olive"]),
     ("gentoo", "GENTOO", None, "gentoo.png",
      ["violet", "magenta"], ["tyrian", "coal"])],

    # The rest of the tools, then what I watch and play.
    [("shell", "SHELL", None, "shell.png",
      ["green", "lime"], ["olive", "moss"]),
     ("neovim", "NEOVIM", None, "neovim.png",
      ["lime", "green"], ["moss", "slate"]),
     ("foss", "FREE", "SOFTWARE", "fsf.png",
      ["green", "lime"], ["olive", "coal"]),
     ("monero", "MONERO", None, "monero.png",
      ["orange", "yellow"], ["coal", "slate"]),
     ("minecraft", "MINECRAFT", None, "minecraft.png",
      ["lime", "green"], ["moss", "olive"]),
     ("dragonball", "DRAGON", "BALL", "dragonball.png",
      ["yellow", "orange"], ["coal", "slate"]),
     ("strategy", "GRAND", "STRATEGY", "strategy.png",
      ["blue", "violet"], ["navy", "sky"])],

    # Culture, home, and football, with Chile between them.
    [("latine", "LINGVA", "LATINA", "aquila.png",
      ["violet", "magenta"], ["tyrian", "maroon"]),
     ("santiago", "SANTIAGO", None, "santiago.png",
      ["red", "magenta"], ["bone-field", "maroon"]),
     ("chile", "CHILE", None, "gunelve.png",
      ["blue", "green"], ["crimson", "navy"]),
     ("laroja", "LA ROJA", None, "laroja.png",
      ["red", "orange"], ["navy", "coal"]),
     ("lazio", "SS LAZIO", None, "lazio.png",
      ["lime", "blue"], ["sky", "slate"]),
     ("futbol", "FOOTBALL", None, "futbol.png",
      ["green", "yellow"], ["coal", "moss"]),
     ("synthwave", "SYNTHWAVE", None, "synthwave.png",
      ["magenta", "violet"], ["tyrian", "sky"])],
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


def solve(index, pool):
    """Give each cell a colour no neighbour holds, by preference."""
    chosen = {}
    for r in range(ROWS):
        for c in range(COLS):
            taken = {chosen[n] for n in neighbours(r, c) if n in chosen}
            for want in WALL[r][c][index]:
                if want not in taken:
                    chosen[(r, c)] = want
                    break
            else:
                spare = [k for k in pool if k not in taken]
                if not spare:
                    raise SystemExit(f"no colour left for {WALL[r][c][0]}")
                chosen[(r, c)] = spare[0]
    return chosen


def check(chosen, label):
    """Every touching pair must differ. Fail loudly if one does not."""
    for r in range(ROWS):
        for c in range(COLS):
            for n in neighbours(r, c):
                if chosen[(r, c)] == chosen[n]:
                    raise SystemExit(
                        f"{label}: {WALL[r][c][0]} touches "
                        f"{WALL[n[0]][n[1]][0]}, both {chosen[(r, c)]}")
    print(f"  {label}: {len(set(chosen.values()))} colours in use, "
          f"no touching pair shares one")


def draw_line(d, text, y, colour, cell):
    """Centre one caption line at the given advance per character."""
    width = W - CANTON
    x = CANTON + (width - len(text) * cell) // 2
    for ch in text:
        d.text((x, y), ch, font=font, fill=colour)
        x += cell


def stamp(name, caption, sub, logo, accent, ground):
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, CANTON, H - 1], fill=ground)
    mark = Image.open(f"{LOGOS}/{logo}").convert("RGBA")
    ratio = min(BOX / mark.width, BOX / mark.height)
    mark = mark.resize((max(1, int(mark.width * ratio)),
                        max(1, int(mark.height * ratio))), Image.LANCZOS)
    img.paste(mark, ((CANTON - mark.width) // 2 + 1,
                     (H - mark.height) // 2), mark)
    d.line([CANTON, 2, CANTON, H - 3], fill=accent)

    # Terminus leaves a pixel of air beside each glyph; dropping it lets a
    # long caption keep clear of the border without changing the face.
    def line(text, y, colour):
        draw_line(d, text, y, colour, 5 if len(text) > 9 else CELL)

    if sub:
        line(caption, 15, BONE)
        line(sub, 29, MUTED)
    else:
        line(caption, 22, BONE)

    d.rectangle([0, 0, W - 1, H - 1], outline=accent)
    img.save(f"{OUT}/{name}.png")


borders = solve(4, BORDERS)
grounds = solve(5, GROUNDS)
check(borders, "borders")
check(grounds, "grounds")

for r in range(ROWS):
    for c in range(COLS):
        name, caption, sub, logo, _, _ = WALL[r][c]
        stamp(name, caption, sub, logo, BORDERS[borders[(r, c)]],
              GROUNDS[grounds[(r, c)]])

print(f"\n{ROWS * COLS} wall stamps -> {OUT}\n")
for r in range(ROWS):
    print("  " + "  ".join(
        f"{WALL[r][c][0][:10]:>10s} {borders[(r, c)][:4]}/{grounds[(r, c)][:5]}"
        for c in range(COLS)))
