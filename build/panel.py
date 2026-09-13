"""The shared room every panel is lit in.

One ground, one vignette, one grain, one set of corner brackets and rails.
Panels differ in what they put inside; they never differ in the room.
"""
import glasshouse as G


def _defs(w, h, uid):
    gfilter, _ = G.grain("grain-%s" % uid, 0.055, 0.86)
    return "".join([
        G.vignette("vig-%s" % uid, w, h),
        gfilter,
        '<radialGradient id="halo-%s" cx="50%%" cy="50%%" r="50%%">'
        '<stop offset="0%%" stop-color="%s" stop-opacity=".55"/>'
        '<stop offset="45%%" stop-color="%s" stop-opacity=".18"/>'
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>'
        "</radialGradient>" % (uid, G.COOL_HOT, G.COOL, G.COOL),
    ])


BOOT_CSS = (
    "@keyframes draw{from{stroke-dashoffset:var(--L,180)}to{stroke-dashoffset:0}}"
    "@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}"
    "@keyframes wipe{from{clip-path:inset(0 100%% 0 0)}to{clip-path:inset(0 -2%% 0 0)}}"
    "@keyframes lift{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}"
    ".rail{stroke-dasharray:1400;stroke-dashoffset:1400;--L:1400;animation:draw .8s %s .05s 1 both}"
    ".reveal{animation:wipe .6s %s var(--d,.6s) 1 both}"
    % (G.SETTLE, G.SNAP)
)


def open_svg(w, h, uid, label):
    """Everything from <svg> through the frame, ready for panel content."""
    body = ['<rect width="%d" height="%d" fill="%s"/>' % (w, h, G.CANVAS)]
    b = 18
    for cx, cy, sx, sy in ((40, 40, 1, 1), (w - 40, 40, -1, 1),
                           (40, h - 40, 1, -1), (w - 40, h - 40, -1, -1)):
        body.append(
            '<path class="rail" d="M%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="1"/>'
            % (cx, cy + sy * b, cx, cy, cx + sx * b, cy, G.RULE_HI)
        )
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'role="img" aria-label="%s">' % (w, h, w, h, label)), body


def close_svg(w, h, uid, defs_extra, css, body):
    body = list(body)
    body.append('<rect width="%d" height="%d" fill="url(#vig-%s)" pointer-events="none"/>' % (w, h, uid))
    body.append(G.grain_rect(w, h, "grain-%s" % uid, 0.055))
    return "<defs>%s</defs><style>%s</style>%s</svg>" % (
        _defs(w, h, uid) + defs_extra, "".join(css), "".join(body)
    )


def card(x, y, w, h, uid, delay=0.0, lifted=True):
    """A lifted surface: one step up the ladder, one top-edge highlight, no shadow."""
    out = [
        '<g class="card" style="--d:%.2fs">' % delay,
        '<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s"/>' % (x, y, w, h, G.S2),
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" stroke="%s" '
        'stroke-width="1"/>' % (x + 0.5, y + 0.5, w - 1, h - 1, G.RULE),
    ]
    if lifted:
        out.append(
            '<path d="M%d %.1f L%d %.1f" stroke="%s" stroke-width="1"/>'
            % (x + 3, y + 0.5, x + w - 3, y + 0.5, G.EDGE_HIGHLIGHT)
        )
    return out
