"""The stats strip: real numbers that roll into place like an odometer.

Digits are stacked 0-9 twice inside a clipped column and translated upward,
so each number lands on its value after one full revolution. Pure CSS
transforms, which is the only kind of motion a README image is allowed.

Numbers come from build/data/stats.json, refreshed by build/stats.py.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fonts
from editorial import DARK, LIGHT, SETTLE, grain_defs

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stats.json")

W, H = 1280, 236
MX = 96
CELL = (W - MX * 2) // 4

DIGIT_W, DIGIT_H = 46, 88        # column box; H also sets the roll distance
NUM_SIZE = 74
NUM_TOP = 96                     # top of the digit boxes
LABEL_Y = 62


def cells(d):
    return [
        ("CONTRIBUTIONS", str(d["contributions"])),
        ("ACTIVE DAYS", str(d["active_days"])),
        ("LONGEST STREAK", str(d["longest_streak"])),
        ("ON GITHUB SINCE", str(d["since"])),
    ]


def odometer(value, x, y, theme, uid, delay):
    """One number as a row of rolling digit columns."""
    parts, css = [], []
    for i, ch in enumerate(str(value)):
        col = "%s%d" % (uid, i)
        cx = x + i * DIGIT_W
        target = 10 + int(ch)                    # one full turn, then land
        parts.append('<clipPath id="c%s"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>'
                     % (col, cx, y, DIGIT_W, DIGIT_H))
        digits = "".join(
            '<text x="%d" y="%d" class="d" fill="%s" font-size="%d" text-anchor="middle">%d</text>'
            % (cx + DIGIT_W // 2, y + k * DIGIT_H + int(DIGIT_H * 0.74), theme["ink"],
               NUM_SIZE, k % 10)
            for k in range(20)
        )
        parts.append('<g clip-path="url(#c%s)"><g class="roll r%s">%s</g></g>' % (col, col, digits))
        css.append(
            "@keyframes roll%s{from{transform:translateY(0)}to{transform:translateY(-%dpx)}}"
            ".r%s{animation:roll%s 1.5s %s %.2fs 1 both}"
            % (col, target * DIGIT_H, col, col, SETTLE, delay + i * 0.09)
        )
    return parts, css


def build(theme, uid):
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)

    rows = cells(d)
    chars = "0123456789" + "".join(k for k, _ in rows)
    css = [fonts.face_css("serif400", chars=chars)]
    css.append(".d{font-family:'Serif',Georgia,'Times New Roman',serif}")
    css.append("@keyframes wipe{from{clip-path:inset(0 100%% 0 0)}to{clip-path:inset(0 -2%% 0 0)}}"
               ".w{animation:wipe .7s %s var(--d) 1 both}" % SETTLE)

    gfilter, grect = grain_defs("g" + uid, theme["grain"])
    defs = [gfilter]
    body = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, theme["ground"])]

    for i, (label, value) in enumerate(rows):
        x = MX + i * CELL
        if i:
            body.append('<path d="M%d 52 L%d 186" stroke="%s" stroke-width="1" fill="none"/>'
                        % (x - 28, x - 28, theme["rule"]))
        body.append('<g class="w" style="--d:%.2fs"><text x="%d" y="%d" class="d" fill="%s" '
                    'font-size="17" letter-spacing="3.6">%s</text></g>'
                    % (0.15 + i * 0.08, x, LABEL_Y, theme["muted"], label))
        parts, kf = odometer(value, x, NUM_TOP, theme, "%s%d" % (uid, i), 0.35 + i * 0.13)
        defs.extend(p for p in parts if p.startswith("<clipPath"))
        body.extend(p for p in parts if not p.startswith("<clipPath"))
        css.extend(kf)

    label = ("%s contributions across %s active days, longest streak %s days, "
             "on GitHub since %s."
             % (d["contributions"], d["active_days"], d["longest_streak"], d["since"]))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'role="img" aria-label="%s"><defs>%s</defs><style>%s</style>%s%s</svg>'
            % (W, H, W, H, label, "".join(defs), "".join(css), "".join(body), grect))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, theme in (("light", LIGHT), ("dark", DARK)):
        svg = build(theme, "s" + name).encode("utf-8")
        path = os.path.join(OUT, "stats-%s.svg" % name)
        old = open(path, "rb").read() if os.path.exists(path) else None
        if old != svg:
            with open(path, "wb") as f:
                f.write(svg)
        print("stats-%-6s %9s bytes  %s" % (name + ".svg", format(len(svg), ","),
                                            "updated" if old != svg else "unchanged"))


if __name__ == "__main__":
    main()
