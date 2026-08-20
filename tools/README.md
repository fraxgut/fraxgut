<!--
tools/README.md
@guterion
CC-BY-SA-4.0
How to rebuild the assets and the translated pages
-->

# Tools

These scripts write everything in `assets/` and the pages under `i18n/`.
They need Python with Pillow, and Terminus at `/usr/share/fonts/terminus`.

```sh
python3 tools/make_stamps.py     # assets/stamps/*.png
python3 tools/make_blinkies.py   # turns those into *.gif
python3 tools/make_badges.py     # assets/badges/*.svg
python3 tools/localise.py        # i18n/{en,es,la}/ from README.md
python3 tools/check.py           # links, alt text, box widths
```

## Stamps

Run the two stamp scripts together, then delete the intermediate files:

```sh
python3 tools/make_stamps.py && python3 tools/make_blinkies.py
rm -f assets/stamps/*.png
```

`make_stamps.py` holds the wall as a grid. It gives each stamp a border
colour that no neighbour holds, diagonals included, and it stops if it
cannot. The canton ground comes from the logotype: the script averages
the mark and darkens it. A pale mark averages to grey, so name its
ground in `FIXED`.

## Pages

Edit `README.md`. Then run `localise.py`, which writes the other three
pages. A page edited under `i18n/` loses that edit on the next run.

A new phrase needs an entry in the `ES` and `LA` dictionaries inside
`localise.py`. The script reports each entry that it cannot find.

## Marks

`tools/marks/` holds the white silhouettes that the badges embed.
`assets/logos/` holds the logotypes. `LICENCE.md` records the source of
each one.
