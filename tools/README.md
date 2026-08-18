<!--
tools/README.md
@fraxgut
CC-BY-SA-4.0
How the generated assets and the translated pages are produced
-->

# Tools

These scripts produce everything in `assets/` and the three pages under
`i18n/`. They read from the repository and write back into it, so they
run from any directory:

```sh
python3 tools/make_stamps.py     # assets/stamps/*.png
python3 tools/make_blinkies.py   # assets/stamps/*.gif, from those PNGs
python3 tools/make_badges.py     # assets/badges/*.svg
python3 tools/localise.py        # i18n/{en,es,la}/README.md from README.md
python3 tools/check.py           # verifies links, alt text and box widths
```

They need Python with Pillow, and the Terminus console font at
`/usr/share/fonts/terminus`. `make_stamps.py` unpacks the gzipped face
into a temporary directory; the repository holds no font.

## The order that matters

`make_stamps.py` writes PNGs and `make_blinkies.py` turns them into the
animated GIFs the pages reference. Run the two together, then delete the
leftover PNGs:

```sh
python3 tools/make_stamps.py && python3 tools/make_blinkies.py
rm -f assets/stamps/*.png
```

## Editing the profile

Edit `README.md` alone. `localise.py` rebuilds the other three pages
from it: it rewrites the asset paths, swaps the language selector, and
applies the dictionary for each language. Editing a page under `i18n/`
directly means the next run overwrites the change.

A new phrase in `README.md` needs its entry in the `ES` and `LA`
dictionaries inside `localise.py`. The script reports any entry it could
not find, which catches a phrase that moved.

## The wall

`make_stamps.py` holds the wall as a grid and colours it: two stamps
that touch, diagonals included, take different border colours and
different canton grounds. It verifies that after solving and stops
rather than writing a clash.

The grid is three rows of seven. Seven per row is the ceiling that still
fits the narrower profile column, so add stamps only in sevens.

## The marks

`tools/marks/` holds the white silhouettes the badges embed. Everything
in `assets/logos/` is a logotype from its owner or a drawing made here;
`LICENCE.md` records where each one came from.
