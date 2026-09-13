"""Regenerate every panel in assets/.

Deterministic: the same inputs produce byte-identical SVGs, so a scheduled
run that finds no new data leaves the tree clean and commits nothing.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ASSETS = os.path.join(HERE, "..", "assets")
PANELS = ["hero", "shelf", "activity"]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    changed = []
    for name in PANELS:
        mod = importlib.import_module(name)
        svg = mod.build_svg().encode("utf-8")
        path = os.path.join(ASSETS, "%s.svg" % name)
        old = open(path, "rb").read() if os.path.exists(path) else None
        if old != svg:
            with open(path, "wb") as f:
                f.write(svg)
            changed.append(name)
        print("%-10s %9s bytes  %s" % (name, format(len(svg), ","),
                                       "updated" if old != svg else "unchanged"))
    print("\n%d of %d panels changed" % (len(changed), len(PANELS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
