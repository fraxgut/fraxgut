#!/usr/bin/env python3
"""Check the profile pages: box widths, links and alt text.

Run it after any edit. It reports every problem it finds and exits
non-zero, so it also works as a pre-commit gate.
"""

import os
import pathlib
import re
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS = ["README.md", "LICENCE.md"] + sorted(
    str(p.relative_to(REPO)) for p in REPO.glob("i18n/*/README.md"))

BOX_CHARS = set("┌┐└┘├┤─│╔╗╚╝║═┬┴┼")


def width(text):
    """Terminal cell width, counting the wide glyphs as two."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1
               for c in text)


def check_boxes(doc, lines, problems):
    """Every line of an ASCII box must come out the same width."""
    inside, block, start = False, [], 0
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if inside:
                widths = {width(b) for b in block if b and b[0] in BOX_CHARS}
                if len(widths) > 1:
                    problems.append(
                        f"{doc}:{start} box lines differ in width: "
                        f"{sorted(widths)}")
                inside, block = False, []
            else:
                inside, start = True, n
            continue
        if inside:
            block.append(line)


def check_targets(doc, text, problems):
    """Every relative link and image must point at a file that exists."""
    base = os.path.dirname(REPO / doc)
    targets = (re.findall(r'\]\(([^)#]+?)\)', text)
    + re.findall(r'src="([^"]+)"', text))
    for target in targets:
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        resolved = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(resolved):
            problems.append(f"{doc}: missing target {target}")


def check_alt(doc, text, problems):
    """Every image carries alt text; a decorative one carries an empty one."""
    for img in re.findall(r'<img\b[^>]*>', text, re.DOTALL):
        if "alt=" not in img:
            problems.append(f"{doc}: img without alt: {img[:70]}")


def main():
    problems = []
    for doc in DOCS:
        path = REPO / doc
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        check_boxes(doc, text.split("\n"), problems)
        check_targets(doc, text, problems)
        check_alt(doc, text, problems)

    if problems:
        print(f"{len(problems)} problems\n")
        for problem in problems:
            print(" ", problem)
        return 1
    print("All boxes aligned, all links resolve, every image has alt text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
