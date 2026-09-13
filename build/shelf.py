"""Selected work, as instrument cards.

Each card carries a glyph that says what the project actually does, rather
than a language badge that says nothing.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fonts
import glasshouse as G
import panel

W = 1280
LEFT, RIGHT = 64, 1216
CARD_W, CARD_H, GUT = 368, 176, 24
ROW_Y = (96, 296)
H = 520

PUBLIC, PRIVATE, CONTRIB = "PUBLIC", "PRIVATE", "CONTRIB"

PROJECTS = [
    dict(name="qdrant-hnsw-live", state=PUBLIC, glyph="layers",
         href="https://github.com/jkupchanko/qdrant-hnsw-live",
         desc="HNSW traversal rendered live in the browser: watch the graph route a query.",
         meta="TYPESCRIPT / 233 KB / AUG 2026"),
    dict(name="code-search-bench", state=PRIVATE, glyph="fusion",
         desc="Retrieval benchmark for code-search embeddings. Dense models, BM25 and RRF "
              "fusion over 5,000 Rust functions.",
         meta="PYTHON / BENCHMARK / SEP 2026"),
    dict(name="elden-ring-vector-search", state=PRIVATE, glyph="constellation",
         desc="The Tarnished's Guide. Elden Ring as a Qdrant vector-search demo, built for "
              "an SF meetup talk.",
         meta="PYTHON / DEMO / AUG 2026"),
    dict(name="qdrant-geometry-viewer", state=PRIVATE, glyph="axes",
         desc="Vector-space geometry made visible: projections, distances and the shapes "
              "behind the metrics.",
         meta="TYPESCRIPT / TOOL / SEP 2026"),
    dict(name="debate-night", state=PRIVATE, glyph="votes",
         desc="Live event app for a one-on-one debate night: host control, projector "
              "display, phone voting, ranked finals.",
         meta="TYPESCRIPT / EVENT APP / AUG 2026"),
    dict(name="qdrant/landing_page", state=CONTRIB, glyph="grid",
         href="https://github.com/qdrant/landing_page",
         desc="qdrant.tech. Articles, docs and site work shipped as a contributor.",
         meta="HUGO / CONTRIBUTOR / SEP 2026"),
]

STATE_COLOR = {PUBLIC: G.COOL, PRIVATE: G.T4, CONTRIB: G.T3}


def wrap(text, chars):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) > chars and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def glyph(kind, x, y, uid):
    """A 56x36 mark. Line-work only; at most one element carries the accent."""
    g = ['<g class="glyph" transform="translate(%d %d)" fill="none" stroke="%s" '
         'stroke-opacity=".42" stroke-width="1">' % (x, y, G.HUD)]
    dot = '<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" fill-opacity="%s" stroke="none"/>'

    if kind == "layers":
        for i, yy in enumerate((4, 18, 32)):
            step = (14, 9, 6)[i]
            for xx in range(0, 57, step):
                g.append(dot % (xx, yy, 1.3, G.HUD, 0.5))
            g.append('<path d="M0 %d L56 %d" stroke-opacity=".16"/>' % (yy, yy))
        g.append('<path class="gl-a" d="M8 4 L26 18 L40 32" stroke="%s" stroke-opacity=".9" '
                 'stroke-width="1.3"/>' % G.COOL)
        g.append(dot % (40, 32, 2.4, G.COOL_HOT, 1))
    elif kind == "fusion":
        for i in range(6):
            g.append('<path d="M0 %d L14 %d" stroke-opacity=".45"/>' % (2 + i * 6, 2 + i * 6))
            g.append('<path d="M22 %d L36 %d" stroke-opacity=".45"/>' % (2 + i * 6, 2 + i * 6))
        g.append('<path class="gl-a" d="M38 4 C48 4 46 18 56 18" stroke="%s" stroke-opacity=".85"/>' % G.COOL)
        g.append('<path class="gl-a" d="M38 32 C48 32 46 18 56 18" stroke="%s" stroke-opacity=".85"/>' % G.COOL)
        g.append(dot % (56, 18, 2.2, G.COOL_HOT, 1))
    elif kind == "constellation":
        pts = [(5, 8), (17, 26), (26, 6), (35, 20), (48, 11), (44, 31), (12, 17), (55, 24)]
        for px, py in pts:
            g.append(dot % (px, py, 1.5, G.HUD, 0.5))
        g.append('<path d="M5 8 L17 26 L35 20 L26 6 Z" stroke-opacity=".2"/>')
        g.append('<circle class="gl-a" cx="35" cy="20" r="6" stroke="%s" stroke-opacity=".85"/>' % G.COOL)
        g.append(dot % (35, 20, 2.2, G.COOL_HOT, 1))
    elif kind == "axes":
        g.append('<path d="M6 34 L6 2 M6 34 L56 34" stroke-opacity=".5"/>')
        for px, py in ((16, 24), (24, 14), (33, 27), (41, 9), (49, 20)):
            g.append(dot % (px, py, 1.5, G.HUD, 0.5))
        g.append('<path class="gl-a" d="M6 12 L41 9" stroke="%s" stroke-opacity=".3" '
                 'stroke-dasharray="2 3"/>' % G.COOL)
        g.append('<path class="gl-a" d="M41 9 L41 34" stroke="%s" stroke-opacity=".3" '
                 'stroke-dasharray="2 3"/>' % G.COOL)
        g.append(dot % (41, 9, 2.4, G.COOL_HOT, 1))
    elif kind == "votes":
        heights = (12, 27, 18, 34, 8)
        for i, hh in enumerate(heights):
            xx = 4 + i * 12
            col = G.COOL if hh == 34 else G.HUD
            op = 0.9 if hh == 34 else 0.35
            g.append('<rect x="%d" y="%d" width="6" height="%d" fill="%s" fill-opacity="%s" '
                     'stroke="none" class="%s"/>' % (xx, 36 - hh, hh, col, op,
                                                     "gl-a" if hh == 34 else ""))
        g.append('<path d="M0 36 L56 36" stroke-opacity=".4"/>')
    elif kind == "grid":
        for i in range(3):
            g.append('<rect x="%d" y="0" width="14" height="36" stroke-opacity=".3"/>' % (i * 21))
        for i in range(3):
            g.append('<path d="M%d 10 L%d 10 M%d 18 L%d 18" stroke-opacity=".22"/>'
                     % (i * 21 + 3, i * 21 + 11, i * 21 + 3, i * 21 + 11))
        g.append('<rect class="gl-a" x="0" y="0" width="14" height="36" stroke="%s" '
                 'stroke-opacity=".85"/>' % G.COOL)
    g.append("</g>")
    return "".join(g)


def build_svg():
    uid = "shelf"
    head, body = panel.open_svg(W, H, uid, "Selected work by John Kupchanko: six projects "
                                           "across vector search, benchmarking and live events.")
    css = [fonts.face_css("grotesk500", "mono500", "inter400")]
    css.append(
        ".mono{font-family:'Mono',ui-monospace,Consolas,monospace;font-feature-settings:'tnum' 1}"
        ".mark{font-family:'Grotesk',system-ui,sans-serif}"
        ".body{font-family:'Inter',system-ui,sans-serif}"
    )
    css.append(panel.BOOT_CSS)
    css.append(
        ".card{opacity:0;animation:lift .7s %s var(--d) 1 both}"
        "@keyframes glow{0%%,100%%{opacity:.55}50%%{opacity:1}}"
        ".gl-a{animation:glow 4.2s ease-in-out var(--d,0s) infinite}"
        % G.SETTLE
    )

    for y in (56, H - 56):
        body.append('<path class="rail" d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none"/>'
                    % (LEFT, y, RIGHT, y, G.RULE))

    body.append(
        '<g class="reveal" style="--d:.35s">'
        + G.tiny_wide(LEFT, 40, "SELECTED WORK", G.T2)
        + G.tiny_wide(RIGHT, 40, "%d PROJECTS &#183; %d PUBLIC" % (
            len(PROJECTS), sum(1 for p in PROJECTS if p["state"] != PRIVATE)), G.T4, anchor="end")
        + "</g>"
    )

    for i, p in enumerate(PROJECTS):
        col, row = i % 3, i // 3
        x = LEFT + col * (CARD_W + GUT)
        y = ROW_Y[row]
        delay = 0.45 + row * 0.14 + col * 0.09
        parts = panel.card(x, y, CARD_W, CARD_H, uid, delay)

        sc = STATE_COLOR[p["state"]]
        parts.append('<circle cx="%d" cy="%d" r="2.6" fill="%s" fill-opacity="%s"/>'
                     % (x + 22, y + 25, sc, ".95" if p["state"] != PRIVATE else ".5"))
        parts.append(G.tiny_wide(x + 32, y + 29, p["state"], sc, size=9))
        parts.append(glyph(p["glyph"], x + CARD_W - 76, y + 18, uid))

        parts.append('<text x="%d" y="%d" class="mark" fill="%s" font-size="19" font-weight="500" '
                     'letter-spacing="-.4">%s</text>' % (x + 20, y + 62, G.T1, p["name"]))

        for li, line in enumerate(wrap(p["desc"], 52)[:3]):
            parts.append('<text x="%d" y="%d" class="body" fill="%s" font-size="12.5">%s</text>'
                         % (x + 20, y + 88 + li * 17, G.T2, line))

        parts.append('<path d="M%d %d L%d %d" stroke="%s" stroke-width="1"/>'
                     % (x + 20, y + CARD_H - 34, x + CARD_W - 20, y + CARD_H - 34, G.RULE))
        parts.append(G.tiny_wide(x + 20, y + CARD_H - 16, p["meta"].replace("/", "&#183;"),
                                 G.T4, size=9))
        parts.append("</g>")
        body.append("".join(parts))

    return head + panel.close_svg(W, H, uid, "", css, body)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "shelf.svg")
    svg = build_svg()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/shelf.svg  %s bytes  %d cards" % (format(len(svg.encode("utf-8")), ","), len(PROJECTS)))
