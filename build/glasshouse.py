"""GLASSHOUSE design tokens: one light, one room.

Near-white instrument line-work on cold blue-black. The reactor is the only
thing that emits. Accents stay under 8% of pixels and mean live state.
"""

# --- ground -----------------------------------------------------------------
CANVAS = "#06080B"          # never pure black
S1, S2, S3, S4 = "#0B0E13", "#11151C", "#171B24", "#1C212B"  # depth by steps

# --- hairlines --------------------------------------------------------------
RULE = "#23272F"
RULE_HI = "#2F343E"
EDGE_HIGHLIGHT = "rgba(255,255,255,.06)"   # one top-edge highlight per lifted panel

# --- text ladder ------------------------------------------------------------
T1, T2, T3, T4 = "#EAF0F7", "#98A1AD", "#5C636E", "#444B55"   # never pure white

# --- HUD line-work ----------------------------------------------------------
HUD = "#DDE7F2"             # used at 40-70% opacity, never solid

# --- accents (live state only) ----------------------------------------------
COOL_HOT = "#EAF6FF"        # reactor core
COOL = "#9CC4DC"            # reactor falloff
WARM = "#E6A24C"            # alerts only, never decoration

# --- authored curves --------------------------------------------------------
SETTLE = "cubic-bezier(.22,1,.36,1)"
SNAP = "cubic-bezier(.16,1,.3,1)"
OVERSHOOT = "cubic-bezier(.34,1.56,.64,1)"
LINEAR = "linear"

GRID = 8                    # strict 8px grid


def grain(idn="grain", opacity=0.05, freq=0.82):
    """Full-canvas feTurbulence at 4-6%, overlay-blended.

    Kills banding and reads as a real display rather than a flat vector.
    """
    return (
        f'<filter id="{idn}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" stitchTiles="stitch"/>'
        f'<feColorMatrix type="saturate" values="0"/>'
        f"</filter>"
    ), opacity


def grain_rect(w, h, idn="grain", opacity=0.05):
    return (
        f'<rect width="{w}" height="{h}" filter="url(#{idn})" '
        f'opacity="{opacity}" style="mix-blend-mode:overlay" pointer-events="none"/>'
    )


def vignette(idn="vig", w=1280, h=440):
    """Cool vignette - the room falling away from the light."""
    return (
        f'<radialGradient id="{idn}" cx="50%" cy="46%" r="78%">'
        f'<stop offset="0%" stop-color="#0B1018" stop-opacity="0"/>'
        f'<stop offset="62%" stop-color="#05070A" stop-opacity=".35"/>'
        f'<stop offset="100%" stop-color="#03050A" stop-opacity=".85"/>'
        f"</radialGradient>"
    )


def tiny_wide(x, y, text, fill=None, size=11, anchor="start", weight=500, cls="", extra=""):
    """11px uppercase at 0.24em - the tiny-wide half of the type contrast."""
    fill = fill or T3
    return (
        f'<text x="{x}" y="{y}" class="mono {cls}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" letter-spacing="{0.24 * size:.2f}" text-anchor="{anchor}" '
        f'{extra}>{text}</text>'
    )
