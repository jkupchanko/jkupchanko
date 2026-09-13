"""Warm editorial profile: a masthead and a row of link plates.

The rule this follows, after looking at what is actually out there: one
beautiful thing and a lot of restraint. No badge wall, no widget stack, no
emoji headings. Display typography lives in these SVGs; every word of body
copy stays in the README as real markdown, so it is selectable, searchable
and follows the reader's own theme.

Two palettes, swapped by <picture> on prefers-color-scheme, because paper
that glares on a dark profile is not elegant, it is loud.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fonts

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# --- palettes ---------------------------------------------------------------
LIGHT = dict(
    ground="#FAF7F2", raised="#FFFDFA", ink="#1C1915", soft="#56503F",
    muted="#8B8375", rule="#E0D8CB", accent="#8A5A2B", grain=0.030,
)
DARK = dict(
    ground="#14120F", raised="#1A1713", ink="#F2EDE4", soft="#A9A093",
    muted="#7A7268", rule="#2E2A24", accent="#C98A4B", grain=0.045,
)

SETTLE = "cubic-bezier(.22,1,.36,1)"

NAME = "John Kupchanko"
EYEBROW = "DEVELOPER  ·  TECHNICAL EDUCATOR"
STATEMENT = "I build things and help people understand how they work."


def grain_defs(idn, amount):
    return (
        '<filter id="%s" x="0" y="0" width="100%%" height="100%%">'
        '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
        '<feColorMatrix type="saturate" values="0"/>'
        "</filter>" % idn
    ), (
        '<rect width="100%%" height="100%%" filter="url(#%s)" opacity="%.3f" '
        'style="mix-blend-mode:multiply" pointer-events="none"/>' % (idn, amount)
    )


# ============================================================ masthead
W_HEAD, H_HEAD = 1280, 440
MX = 96                         # generous editorial margin


def masthead(theme, uid):
    p = theme
    chars = NAME + EYEBROW + STATEMENT + " ·"
    css = [fonts.face_css("serif400", "serifitalic", chars=chars)]
    css.append(
        ".d{font-family:'Serif',Georgia,'Times New Roman',serif}"
        ".i{font-family:'SerifItalic','Serif',Georgia,serif;font-style:italic}"
    )
    css.append(
        "@keyframes wipe{from{clip-path:inset(0 100%% 0 0)}to{clip-path:inset(0 -2%% 0 0)}}"
        "@keyframes draw{from{stroke-dashoffset:1100}to{stroke-dashoffset:0}}"
        ".w{animation:wipe .95s %s var(--d) 1 both}"
        ".r{stroke-dasharray:1100;stroke-dashoffset:1100;animation:draw 1.1s %s .55s 1 both}"
        % (SETTLE, SETTLE)
    )

    gfilter, grect = grain_defs("g" + uid, p["grain"])
    body = ['<rect width="%d" height="%d" fill="%s"/>' % (W_HEAD, H_HEAD, p["ground"])]

    # eyebrow
    body.append(
        '<g class="w" style="--d:.12s"><text x="%d" y="112" class="d" fill="%s" font-size="19" '
        'letter-spacing="4.2">%s</text></g>' % (MX, p["accent"], EYEBROW)
    )
    # the name, given the room it deserves
    body.append(
        '<g class="w" style="--d:.28s"><text x="%d" y="238" class="d" fill="%s" font-size="118" '
        'letter-spacing="-1.2">%s</text></g>' % (MX - 4, p["ink"], NAME)
    )
    body.append(
        '<path class="r" d="M%d 288 L%d 288" stroke="%s" stroke-width="1" fill="none"/>'
        % (MX, W_HEAD - MX, p["rule"])
    )
    body.append(
        '<g class="w" style="--d:.78s"><text x="%d" y="342" class="i" fill="%s" font-size="35">%s</text></g>'
        % (MX, p["soft"], STATEMENT)
    )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="John Kupchanko, developer and technical educator. '
        'I build things and help people understand how they work.">'
        "<defs>%s</defs><style>%s</style>%s%s</svg>"
        % (W_HEAD, H_HEAD, W_HEAD, H_HEAD, gfilter, "".join(css), "".join(body), grect)
    )


# ============================================================ link plates
TW, TH = 516, 140               # authored at 2x, shown at 258x70

LINKS = [
    dict(key="linkedin", label="LinkedIn", handle="IN/JOHN-KUPCHANKO",
         href="https://www.linkedin.com/in/john-kupchanko/"),
    dict(key="youtube", label="YouTube", handle="BLOCKCHAIN BUILDERS",
         href="https://www.youtube.com/@BlockchainBuilders/"),
    dict(key="repos", label="Repositories", handle="23 PROJECTS",
         href="https://github.com/jkupchanko?tab=repositories"),
]


def icon(key, accent):
    """Line icons on a 24px grid, one stroke weight, scaled 2x to the plate."""
    s = ('<g transform="translate(30 48) scale(1.75)" fill="none" stroke="%s" '
         'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' % accent)
    if key == "linkedin":
        s += ('<rect x="1.5" y="1.5" width="21" height="21" rx="3.5"/>'
              '<path d="M7 10.5V17"/><circle cx="7" cy="6.9" r="1.05" fill="%s" stroke="none"/>'
              '<path d="M11.5 17v-4a2.6 2.6 0 0 1 5.2 0v4"/>' % accent)
    elif key == "youtube":
        s += ('<rect x="1.5" y="4" width="21" height="16" rx="4.5"/>'
              '<path d="M10 8.6l6 3.4-6 3.4z" fill="%s" stroke="none"/>' % accent)
    elif key == "repos":
        s += ('<circle cx="6.5" cy="5.5" r="2.4"/><circle cx="6.5" cy="18.5" r="2.4"/>'
              '<circle cx="17.5" cy="9" r="2.4"/><path d="M6.5 7.9v8.2"/>'
              '<path d="M17.5 11.4v1.1a4 4 0 0 1-4 4H9"/>')
    return s + "</g>"


def plate(link, theme, uid):
    p = theme
    chars = link["label"] + link["handle"] + " -·"
    css = [fonts.face_css("serif400", chars=chars)]
    css.append(".d{font-family:'Serif',Georgia,'Times New Roman',serif}")
    css.append(
        "@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
        ".p{animation:fade .7s %s .25s 1 both}" % SETTLE
    )
    gfilter, grect = grain_defs("g" + uid, p["grain"])

    body = [
        '<rect width="%d" height="%d" fill="%s"/>' % (TW, TH, p["ground"]),
        '<g class="p">',
        '<rect x="1" y="1" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="2"/>'
        % (TW - 2, TH - 2, p["raised"], p["rule"]),
        icon(link["key"], p["accent"]),
        '<text x="94" y="74" class="d" fill="%s" font-size="38" letter-spacing="-.3">%s</text>'
        % (p["ink"], link["label"]),
        '<text x="96" y="104" class="d" fill="%s" font-size="21" letter-spacing="2.4">%s</text>'
        % (p["muted"], link["handle"]),
        "</g>",
    ]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="%s, %s">'
        "<defs>%s</defs><style>%s</style>%s%s</svg>"
        % (TW, TH, TW, TH, link["label"], link["handle"].title(),
           gfilter, "".join(css), "".join(body), grect)
    )


def main():
    os.makedirs(OUT, exist_ok=True)
    written = []
    for name, theme in (("light", LIGHT), ("dark", DARK)):
        files = [("header-%s.svg" % name, masthead(theme, "h" + name))]
        for link in LINKS:
            files.append(("link-%s-%s.svg" % (link["key"], name),
                          plate(link, theme, link["key"] + name)))
        for filename, svg in files:
            path = os.path.join(OUT, filename)
            data = svg.encode("utf-8")
            old = open(path, "rb").read() if os.path.exists(path) else None
            if old != data:
                with open(path, "wb") as f:
                    f.write(data)
            written.append((filename, len(data), old != data))

    for filename, size, changed in written:
        print("%-28s %8s bytes  %s" % (filename, format(size, ","),
                                       "updated" if changed else "unchanged"))
    print("\n%d files, %s bytes total"
          % (len(written), format(sum(s for _, s, _ in written), ",")))


if __name__ == "__main__":
    main()
