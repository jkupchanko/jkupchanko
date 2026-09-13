"""The activity panel: a signal trace, not a scoreboard.

Everything is read from build/data/live.json, which the scheduled workflow
refreshes. A year of contributions is drawn as weekly signal with the daily
calendar underneath as texture, so a quiet stretch reads as a quiet stretch
rather than as an empty grid.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fonts
import glasshouse as G
import panel

W, H = 1280, 528
LEFT, RIGHT = 64, 1216
GX0, GX1 = 144, 1216

RAIL_TOP, RAIL_BOT = 56, 476
TEL_LABEL_Y, TEL_VALUE_Y = 82, 106
HEAD_DIV = 126
BASELINE = 300
BAR_MAX = 140
HEAT_Y, HEAT_CELL, HEAT_GAP = 318, 4, 1
MIX_DIV = 372
MIX_BAR_Y, MIX_BAR_H = 408, 20

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "live.json")

# Assigned by rank, not by language: the mix bar is one accent falling off
# into line-work, so no single language gets a brand colour it didn't earn.
MIX_STEPS = [(G.COOL_HOT, 0.92), (G.COOL, 0.72), (G.HUD, 0.46),
             (G.HUD, 0.32), (G.HUD, 0.22), (G.HUD, 0.15), (G.HUD, 0.10)]


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def build_svg():
    d = load()
    cal, langs, repos = d["calendar"], d["languages"], d["repos"]
    weeks = cal["weeks"]
    weekly = [sum(w) for w in weeks]
    peak = max(weekly) or 1
    peak_i = weekly.index(peak)
    col_w = (GX1 - GX0) / len(weeks)

    uid = "act"
    head, body = panel.open_svg(
        W, H, uid,
        "Activity for jkupchanko: %d contributions across %d weeks, peak week %d, "
        "longest streak %d days, and a recency-weighted language mix."
        % (cal["total"], len(weeks), peak, cal["longest_streak"]))

    css = [fonts.face_css("grotesk500", "mono500")]
    css.append(
        ".mono{font-family:'Mono',ui-monospace,Consolas,monospace;font-feature-settings:'tnum' 1}"
        ".mark{font-family:'Grotesk',system-ui,sans-serif}"
    )
    css.append(panel.BOOT_CSS)
    css.append(
        "@keyframes rise{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
        ".bar{transform-box:fill-box;transform-origin:bottom;"
        "animation:rise .7s %s var(--d) 1 both}"
        ".cell{opacity:0;animation:wipe .01s linear var(--d) 1 both,"
        "cellin .4s ease-out var(--d) 1 both}"
        "@keyframes cellin{from{opacity:0}to{opacity:1}}"
        "@keyframes pulse{0%%,100%%{opacity:.35}50%%{opacity:.8}}"
        ".peakline{animation:pulse 5s ease-in-out 2s infinite}"
        % G.SETTLE
    )

    for y in (RAIL_TOP, RAIL_BOT):
        body.append('<path class="rail" d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none"/>'
                    % (LEFT, y, RIGHT, y, G.RULE))
    for y in (HEAD_DIV, MIX_DIV):
        body.append('<path class="rail" d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none" '
                    'stroke-dasharray="1 5" opacity=".8"/>' % (LEFT, y, RIGHT, y, G.RULE))

    body.append(
        '<g class="reveal" style="--d:.35s">'
        + G.tiny_wide(LEFT, 40, "ACTIVITY", G.T2)
        + G.tiny_wide(RIGHT, 40, "%s &#8594; %s" % (cal["from"], cal["to"]), G.T4, anchor="end")
        + G.tiny_wide(LEFT, 500, "SELF-UPDATING &#183; DATA THROUGH %s" % cal["to"], G.T4)
        + G.tiny_wide(RIGHT, 500, "%d REPOS &#183; %d PUBLIC" % (repos["owned"], repos["public"]),
                      G.T4, anchor="end")
        + "</g>"
    )

    # telemetry cells - aligned, tabular, and all of it measured
    cells = [
        ("CONTRIBUTIONS", cal["total"]), ("COMMITS", cal["commits"]),
        ("PULL REQUESTS", cal["prs"]), ("ACTIVE DAYS", cal["active_days"]),
        ("LONGEST STREAK", cal["longest_streak"]), ("PEAK DAY", cal["peak_day"]),
    ]
    step = (RIGHT - LEFT) / len(cells)
    for i, (k, v) in enumerate(cells):
        x = LEFT + i * step
        body.append(
            '<g class="reveal" style="--d:%.2fs">' % (0.5 + i * 0.07)
            + G.tiny_wide(x, TEL_LABEL_Y, k, G.T4, size=9)
            + '<text x="%.0f" y="%d" class="mono" fill="%s" font-size="22" font-weight="500">%d</text>'
              % (x, TEL_VALUE_Y, G.T1, v)
            + "</g>"
        )
        if i:
            body.append('<path d="M%.0f %d L%.0f %d" stroke="%s" stroke-width="1" opacity=".7"/>'
                        % (x - 18, TEL_LABEL_Y - 12, x - 18, TEL_VALUE_Y + 4, G.RULE))

    # weekly signal trace
    body.append('<path d="M%d %d L%d %d" stroke="%s" stroke-width="1" fill="none" class="rail"/>'
                % (GX0, BASELINE, GX1, BASELINE, G.RULE_HI))
    for i, v in enumerate(weekly):
        x = GX0 + i * col_w
        bh = (v / peak) * BAR_MAX
        is_peak = i == peak_i
        if v == 0:
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="2" fill="%s" '
                        'fill-opacity=".10"/>' % (x + 2, BASELINE - 2, col_w - 4, G.HUD))
            continue
        body.append(
            '<rect class="bar" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
            'fill-opacity="%s" style="--d:%.2fs"/>'
            % (x + 2, BASELINE - bh, col_w - 4, bh,
               G.COOL_HOT if is_peak else G.HUD, ".95" if is_peak else ".40",
               0.8 + i * 0.012)
        )
    px = GX0 + peak_i * col_w + col_w / 2
    body.append('<path class="peakline" d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="1" '
                'stroke-dasharray="2 3" opacity=".35"/>'
                % (px, BASELINE - BAR_MAX - 11, px, BASELINE - BAR_MAX - 3, G.COOL))
    body.append(G.tiny_wide(px, BASELINE - BAR_MAX - 18, "PEAK %d" % peak, G.COOL, size=9,
                            anchor="middle"))

    # daily calendar underneath, as texture rather than as the headline
    for wi, week in enumerate(weeks):
        x = GX0 + wi * col_w
        for di, count in enumerate(week):
            y = HEAT_Y + di * (HEAT_CELL + HEAT_GAP)
            if count == 0:
                op, fill = 0.10, G.HUD
            else:
                t = min(1.0, count / max(1, cal["peak_day"]))
                op = 0.34 + 0.6 * t
                fill = G.COOL_HOT if t > 0.7 else (G.COOL if t > 0.3 else G.HUD)
            body.append('<rect class="cell" x="%.1f" y="%d" width="%.1f" height="%d" fill="%s" '
                        'fill-opacity="%.2f" style="--d:%.2fs"/>'
                        % (x + 2, y, max(2.0, col_w - 5), HEAT_CELL, fill, op, 1.0 + wi * 0.008))
    body.append(G.tiny_wide(LEFT, HEAT_Y + 12, "DAILY", G.T4, size=9))

    # language mix
    mix = langs["mix"]
    body.append(
        '<g class="reveal" style="--d:1.5s">'
        + G.tiny_wide(LEFT, 396, "LANGUAGE MIX", G.T2)
        + G.tiny_wide(RIGHT, 396, "RECENCY-WEIGHTED &#183; %d REPOS" % langs["repos_counted"],
                      G.T4, anchor="end")
        + "</g>"
    )
    x = float(GX0)
    total_w = GX1 - GX0
    legend = []
    for i, m in enumerate(mix):
        seg = m["share"] * total_w
        if seg < 1:
            continue
        fill, op = MIX_STEPS[min(i, len(MIX_STEPS) - 1)]
        body.append(
            '<rect class="reveal" style="--d:%.2fs" x="%.1f" y="%d" width="%.1f" height="%d" '
            'fill="%s" fill-opacity="%s"/>'
            % (1.6 + i * 0.08, x, MIX_BAR_Y, max(1.0, seg - 2), MIX_BAR_H, fill, op)
        )
        legend.append((x, m, fill, op))
        x += seg
    for lx, m, fill, op in legend:
        if m["share"] < 0.04:
            continue
        body.append('<circle cx="%.1f" cy="%d" r="2.4" fill="%s" fill-opacity="%s"/>'
                    % (lx + 4, 446, fill, op))
        body.append(G.tiny_wide(lx + 12, 450, "%s %d%%" % (m["name"].upper(),
                                                           round(m["share"] * 100)), G.T3, size=9))

    return head + panel.close_svg(W, H, uid, "", css, body)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "activity.svg")
    svg = build_svg()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/activity.svg  %s bytes" % format(len(svg.encode("utf-8")), ","))
