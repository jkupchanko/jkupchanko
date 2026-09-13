"""The hero panel: a real HNSW index serving a query, drawn as an instrument.

README images load inside an <img> sandbox - no JS, no network, no external
fonts. Everything here is declarative CSS animation and data-URI fonts.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fonts
import glasshouse as G
import hnsw

W, H = 1280, 560
LEFT, RIGHT = 64, 1216
GX0, GX1 = 144, 1216           # graph gutter, leaves room for layer labels
DIVIDER_Y = 208
BAND_Y = {2: 256, 1: 352, 0: 448}
BAND_H = 64                    # band height; ASPECT in hnsw.py must match (GX1-GX0)/BAND_H
RAIL_TOP, RAIL_BOT = 56, 512

SEED = 162
IX = hnsw.build(seed=SEED, sizes=(200, 36, 9), m=(3, 2, 2), query=(12.9, 0.42))

LOOP = 8.0                      # query cycle, seconds
BOOT_TAIL = 2.6                 # query starts once the boot has settled
STEP = 0.26                     # one traversal transition


def place():
    """Map every node's scalar position onto the band it lives in."""
    for lv, layer in enumerate(IX["layers"]):
        base = BAND_Y[lv]
        for n in layer:
            n.x = GX0 + (n.u / hnsw.ASPECT) * (GX1 - GX0)
            n.y = base + (n.v - 0.5) * BAND_H


place()

# Layer-0 nodes that were promoted upward get a faint ring: that hierarchy is
# the whole point of the structure, so it should be visible standing still.
PROMOTED = {
    0: {(round(n.u, 9), round(n.v, 9)) for n in IX["layers"][1]},
    1: {(round(n.u, 9), round(n.v, 9)) for n in IX["layers"][2]},
}


HIGHWAY = 90                   # px: beyond this an edge is a long-range link


def bow(a, b):
    """Short links stay straight so the local mesh reads clean; long-range
    links arc above the band, which is exactly what they are."""
    dx = abs(a.x - b.x)
    if dx < HIGHWAY:
        return "M%.1f %.1f L%.1f %.1f" % (a.x, a.y, b.x, b.y)
    mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
    lift = min(26.0, dx * 0.10 + 6.0)
    return "M%.1f %.1f Q%.1f %.1f %.1f %.1f" % (a.x, a.y, mx, my - lift, b.x, b.y)


def path_len(a, b):
    """Good-enough arc length for the stroke-dash draw-on."""
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5 * 1.12 + 6


def timeline():
    """Flatten the descent into one ordered list of stops."""
    stops = []
    layers = IX["layers"]
    top = len(layers) - 1
    for i, route in enumerate(IX["routes"]):
        lv = top - i
        for j, idx in enumerate(route):
            stops.append({"lv": lv, "node": layers[lv][idx], "drop": j == 0 and i > 0})
    return stops


STOPS = timeline()
TRANSITIONS = len(STOPS) - 1
TRAVEL = TRANSITIONS * STEP


def pct(t):
    return max(0.0, min(100.0, t / LOOP * 100.0))


def build_svg():
    layers = IX["layers"]
    land = STOPS[-1]["node"]
    n_nodes = sum(len(l) for l in layers)

    css = [fonts.face_css("grotesk700", "mono500")]
    css.append(
        ".mono{font-family:'Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
        "font-feature-settings:'tnum' 1}"
        ".mark{font-family:'Grotesk',system-ui,sans-serif}"
    )

    defs = [G.vignette("vig", W, H)]
    gfilter, gop = G.grain("grain", 0.055, 0.86)
    defs.append(gfilter)
    defs.append(
        '<radialGradient id="halo" cx="50%%" cy="50%%" r="50%%">'
        '<stop offset="0%%" stop-color="%s" stop-opacity=".55"/>'
        '<stop offset="45%%" stop-color="%s" stop-opacity=".18"/>'
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>'
        "</radialGradient>" % (G.COOL_HOT, G.COOL, G.COOL)
    )
    defs.append(
        '<radialGradient id="room" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#16202E" stop-opacity=".55"/>'
        '<stop offset="100%" stop-color="#16202E" stop-opacity="0"/>'
        "</radialGradient>"
    )

    body = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, G.CANVAS)]
    # the room's only ambient lift, sitting under where the reactor comes to rest
    body.append(
        '<ellipse class="room" cx="%.0f" cy="%.0f" rx="340" ry="170" fill="url(#room)"/>'
        % (land.x, land.y)
    )

    # instrument frame: corner brackets, not a full box
    b = 18
    for cx, cy, sx, sy in ((40, 40, 1, 1), (W - 40, 40, -1, 1),
                           (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)):
        body.append(
            '<path class="rail" d="M%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="1"/>'
            % (cx, cy + sy * b, cx, cy, cx + sx * b, cy, G.RULE_HI)
        )
    for y in (RAIL_TOP, RAIL_BOT):
        body.append(
            '<path class="rail" d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none"/>'
            % (LEFT, y, RIGHT, y, G.RULE)
        )
    body.append(
        '<path class="rail" d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none" '
        'stroke-dasharray="1 5" opacity=".8"/>' % (LEFT, DIVIDER_Y, RIGHT, DIVIDER_Y, G.RULE)
    )

    # rail telemetry - every number below is computed, none of it is filler
    body.append(
        '<g class="reveal r-rail">'
        + G.tiny_wide(LEFT, 40, "JKUPCHANKO &#183; GITHUB", G.T3)
        + G.tiny_wide(RIGHT, 40, "HNSW &#183; L=3 &#183; M=3 &#183; N=%d" % n_nodes, G.T4, anchor="end")
        + G.tiny_wide(LEFT, 536, "QUERY (%.2f, %.2f) &#183; HOPS %d &#183; EDGES %d"
                      % (IX["query"][0], IX["query"][1], IX["hops"], IX["edges"]), G.T3)
        + G.tiny_wide(RIGHT, 536, "RECALL@1 1.00 &#183; EXACT", G.T3, anchor="end")
        + "</g>"
    )

    # wordmark: big-tight against the tiny-wide subtitle
    body.append(
        '<g class="mark-wrap"><text x="%d" y="150" class="mark" fill="%s" font-size="72" '
        'font-weight="700" letter-spacing="-2.16">JOHN KUPCHANKO</text></g>' % (LEFT, G.T1)
    )
    body.append(
        '<g class="sub-wrap">'
        + G.tiny_wide(LEFT + 2, 182,
                      "DEVELOPER RELATIONS &#183; VECTOR SEARCH &#183; QDRANT", G.T2)
        + "</g>"
    )

    for i, (k, v) in enumerate((("LAYERS", "3"), ("NODES", str(n_nodes)),
                                ("EDGES", str(IX["edges"])), ("HOPS", str(IX["hops"])))):
        y = 100 + i * 24
        body.append(
            '<g class="reveal r-tel" style="--d:%.2fs">' % (1.80 + i * 0.09)
            + G.tiny_wide(1012, y, k, G.T4)
            + '<path d="M1090 %d L1160 %d" stroke="%s" stroke-width="1" opacity=".55"/>'
              % (y - 4, y - 4, G.RULE)
            + '<text x="%d" y="%d" class="mono" fill="%s" font-size="13" font-weight="500" '
              'text-anchor="end">%s</text>' % (RIGHT, y, G.T2, v)
            + "</g>"
        )

    for lv in (2, 1, 0):
        y = BAND_Y[lv]
        body.append(
            '<g class="reveal r-lab" style="--d:%.2fs">' % (1.0 + (2 - lv) * 0.08)
            + G.tiny_wide(LEFT, y + 4, "L%d" % lv, G.T3)
            + '<text x="%d" y="%d" class="mono" fill="%s" font-size="10">%d</text>'
              % (LEFT + 32, y + 4, G.T4, len(layers[lv]))
            + "</g>"
        )

    # edges, dimmest at the dense bottom so the hierarchy reads by weight
    edge_style = {0: (0.135, 0.70), 1: (0.175, 0.80), 2: (0.225, 0.90)}
    for lv in (0, 1, 2):
        op, sw = edge_style[lv]
        layer = layers[lv]
        drawn, parts = set(), []
        for n in layer:
            for nb in n.nbrs:
                key = (min(n.idx, nb), max(n.idx, nb))
                if key in drawn:
                    continue
                drawn.add(key)
                o = layer[nb]
                L = path_len(n, o)
                parts.append(
                    '<path d="%s" stroke-dasharray="%.0f" stroke-dashoffset="%.0f" '
                    'style="--L:%.0f;--d:%.2fs"/>'
                    % (bow(n, o), L, L, L, 0.62 + (2 - lv) * 0.10 + (n.x / W) * 0.34)
                )
        body.append(
            '<g class="edges" stroke="%s" stroke-opacity="%s" stroke-width="%s" fill="none">%s</g>'
            % (G.HUD, op, sw, "".join(parts))
        )

    # drop connectors: where the search falls out of one layer into the next
    for i, st in enumerate(STOPS):
        if not st["drop"]:
            continue
        src, dst = STOPS[i - 1]["node"], st["node"]
        body.append(
            '<path class="drop" d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-opacity=".18" '
            'stroke-width=".8" stroke-dasharray="2 4" fill="none"/>'
            % (src.x, src.y, dst.x, dst.y, G.HUD)
        )

    node_style = {0: (2.2, 0.42), 1: (2.8, 0.56), 2: (3.4, 0.70)}
    for lv in (0, 1, 2):
        r, op = node_style[lv]
        parts = []
        for n in layers[lv]:
            d = 0.35 + (2 - lv) * 0.20 + (n.x / W) * 0.30
            if lv < 2 and (round(n.u, 9), round(n.v, 9)) in PROMOTED[lv]:
                parts.append(
                    '<circle cx="%.1f" cy="%.1f" r="5.8" fill="none" stroke="%s" '
                    'stroke-opacity=".22" stroke-width=".7" style="--d:%.2fs"/>'
                    % (n.x, n.y, G.HUD, d)
                )
            parts.append('<circle cx="%.1f" cy="%.1f" r="%s" style="--d:%.2fs"/>' % (n.x, n.y, r, d))
        body.append(
            '<g class="nodes" fill="%s" fill-opacity="%s">%s</g>' % (G.HUD, op, "".join(parts))
        )

    # the traversed route is the only thing in the frame that emits
    fire_css = []
    for i in range(TRANSITIONS):
        a, bn = STOPS[i]["node"], STOPS[i + 1]["node"]
        drop = STOPS[i + 1]["drop"]
        d = ("M%.1f %.1f L%.1f %.1f" % (a.x, a.y, bn.x, bn.y)) if drop else bow(a, bn)
        L = path_len(a, bn)
        t0 = pct(i * STEP)
        body.append(
            '<path class="fire f%d" d="%s" fill="none" stroke="%s" stroke-width="1.5" '
            'stroke-linecap="round" stroke-dasharray="%.0f" stroke-dashoffset="%.0f" opacity="0"/>'
            % (i, d, G.COOL, L, L)
        )
        fire_css.append(
            "@keyframes fire%d{0%%,%.2f%%{stroke-dashoffset:%.0f;opacity:0}"
            "%.2f%%{opacity:.95}%.2f%%{stroke-dashoffset:0;opacity:.95}"
            "%.2f%%{stroke-dashoffset:0;opacity:.30}%.2f%%,100%%{stroke-dashoffset:0;opacity:.16}}"
            % (i, t0, L, t0 + 0.2, pct(i * STEP + STEP),
               pct(i * STEP + STEP + 1.1), pct(TRAVEL + 2.0))
        )
        fire_css.append(".f%d{animation:fire%d %ss linear %ss infinite both}" % (i, i, LOOP, BOOT_TAIL))

    body.append(
        '<circle class="land" cx="%.1f" cy="%.1f" r="4" fill="none" stroke="%s" '
        'stroke-width="1.2" opacity="0"/>' % (land.x, land.y, G.COOL_HOT)
    )
    # fresnel-ish reactor: halo falls off, core stays hot
    body.append(
        '<g class="reactor" opacity="0"><circle r="17" fill="url(#halo)"/>'
        '<circle r="3.1" fill="%s"/></g>' % G.COOL_HOT
    )

    first = STOPS[0]["node"]
    dot = ["0%%{opacity:0;transform:translate(%.1fpx,%.1fpx)}" % (first.x, first.y),
           "0.6%%{opacity:1;transform:translate(%.1fpx,%.1fpx);animation-timing-function:%s}"
           % (first.x, first.y, G.SETTLE)]
    for i in range(1, len(STOPS)):
        n = STOPS[i]["node"]
        ease = G.SNAP if STOPS[i]["drop"] else G.SETTLE
        dot.append("%.2f%%{opacity:1;transform:translate(%.1fpx,%.1fpx);animation-timing-function:%s}"
                   % (pct(i * STEP), n.x, n.y, ease))
    dot.append("%.2f%%{opacity:1;transform:translate(%.1fpx,%.1fpx)}"
               % (pct(TRAVEL + 0.9), land.x, land.y))
    dot.append("%.2f%%,100%%{opacity:0;transform:translate(%.1fpx,%.1fpx)}"
               % (pct(TRAVEL + 1.6), land.x, land.y))

    css.append("@keyframes travel{%s}" % "".join(dot))
    css.append(".reactor{animation:travel %ss linear %ss infinite both}" % (LOOP, BOOT_TAIL))
    css.append(
        "@keyframes landing{0%%,%.2f%%{r:4;opacity:0;stroke-width:1.4}"
        "%.2f%%{r:5;opacity:.9;stroke-width:1.4}"
        "%.2f%%{r:22;opacity:0;stroke-width:.5}100%%{r:22;opacity:0}}"
        % (pct(TRAVEL - STEP), pct(TRAVEL), pct(TRAVEL + 1.0))
    )
    css.append(".land{animation:landing %ss %s %ss infinite both}" % (LOOP, G.SETTLE, BOOT_TAIL))
    css.append(
        "@keyframes roomglow{0%,100%{opacity:.30}50%{opacity:.50}}"
        ".room{opacity:.30;animation:roomglow 7.4s ease-in-out 3s infinite}"
    )

    # boot choreography: reveals are stroke-draw and clip wipes, never fades
    css.append(
        "@keyframes draw{from{stroke-dashoffset:var(--L,180)}to{stroke-dashoffset:0}}"
        "@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}"
        "@keyframes wipe{from{clip-path:inset(0 100%% 0 0)}to{clip-path:inset(0 -2%% 0 0)}}"
        ".rail{stroke-dasharray:1400;stroke-dashoffset:1400;--L:1400;"
        "animation:draw .8s %s .05s 1 both}"
        ".edges path{animation:draw .9s %s var(--d) 1 both}"
        ".nodes circle{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:pop .5s %s var(--d) 1 both}"
        ".drop{stroke-dasharray:90;stroke-dashoffset:90;--L:90;animation:draw .6s %s 1.05s 1 both}"
        ".mark-wrap{animation:wipe 1.0s %s 1.30s 1 both}"
        ".sub-wrap{animation:wipe .7s %s 1.62s 1 both}"
        ".reveal{animation:wipe .6s %s var(--d,2.0s) 1 both}"
        ".r-rail{--d:2.0s}"
        % (G.SETTLE, G.SETTLE, G.OVERSHOOT, G.SETTLE, G.SNAP, G.SNAP, G.SNAP)
    )
    css.extend(fire_css)

    body.append('<rect width="%d" height="%d" fill="url(#vig)" pointer-events="none"/>' % (W, H))
    body.append(G.grain_rect(W, H, "grain", gop))

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="John Kupchanko, Developer Relations, vector search, Qdrant. '
        'An animated three-layer HNSW index routing a query down to its nearest neighbour.">'
        "<defs>%s</defs><style>%s</style>%s</svg>"
        % (W, H, W, H, "".join(defs), "".join(css), "".join(body))
    )


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "hero.svg")
    svg = build_svg()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/hero.svg  %s bytes  stops=%d transitions=%d travel=%.2fs"
          % (format(len(svg.encode("utf-8")), ","), len(STOPS), TRANSITIONS, TRAVEL))
