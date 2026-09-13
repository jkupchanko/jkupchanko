"""Subset the GLASSHOUSE typefaces and emit base64 @font-face blocks.

SVGs referenced from a README load through an <img> sandbox: no network, no
external resources. A data: URI is not an external resource, so embedding the
woff2 inline is the only way to keep the instrument typography.
"""
import base64
import io
import os

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
EPOCH = 3439756800   # 2009-01-01 in OpenType epoch seconds; any fixed value works
SRC = os.path.join(HERE, "fonts")
CACHE = os.path.join(SRC, "subset")

# Generous ASCII: every glyph any panel might need, still tiny after subsetting.
CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    r" .,:;!?'" + '"' + r"()[]{}/\|-_+=<>@#$%&*^~`"
    "→·—–•×"  # arrow, middot, dashes, bullet, times
)

FACES = {
    "grotesk700": ("space-grotesk-700.woff2", "Grotesk", 700),
    "grotesk500": ("space-grotesk-500.woff2", "Grotesk", 500),
    "mono400": ("jetbrains-mono-400.woff2", "Mono", 400),
    "mono500": ("jetbrains-mono-500.woff2", "Mono", 500),
    "inter400": ("inter-400.woff2", "Inter", 400),
    "inter500": ("inter-500.woff2", "Inter", 500),
}

_cache = {}


def _subset_b64(filename, rebuild=False):
    """Base64 of the subsetted face, from the committed cache when present.

    fontTools subsetting is not byte-reproducible across processes (glyph
    ordering rides on set iteration, so PYTHONHASHSEED changes the output).
    Subsetting once and committing the result keeps every later render
    deterministic, which is what lets the scheduled workflow no-op cleanly.
    """
    if filename in _cache:
        return _cache[filename]
    cached = os.path.join(CACHE, filename)
    if os.path.exists(cached) and not rebuild:
        with open(cached, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        _cache[filename] = b64
        return b64

    font = TTFont(os.path.join(SRC, filename))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    # fontTools stamps head.modified with the wall clock on save, which makes
    # every rebuild a different file and every scheduled run a fresh commit.
    opts.recalc_timestamp = False
    opts.layout_features = ["kern", "liga", "calt", "tnum"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text=CHARS)
    subsetter.subset(font)
    # belt and braces: pin both timestamps so the bytes depend only on input
    head = font.get("head")
    if head is not None:
        head.created = head.modified = EPOCH
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    font.close()
    raw = buf.getvalue()
    os.makedirs(CACHE, exist_ok=True)
    with open(cached, "wb") as f:
        f.write(raw)
    b64 = base64.b64encode(raw).decode("ascii")
    _cache[filename] = b64
    return b64


def face_css(*keys):
    """Return @font-face rules for the named faces, fonts inlined as data URIs."""
    out = []
    for key in keys:
        filename, family, weight = FACES[key]
        b64 = _subset_b64(filename)
        out.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}" % (family, weight, b64)
        )
    return "".join(out)


if __name__ == "__main__":
    import sys

    rebuild = "--rebuild" in sys.argv
    if rebuild:
        _cache.clear()
    for key in FACES:
        filename = FACES[key][0]
        raw = os.path.getsize(os.path.join(SRC, filename))
        sub = len(base64.b64decode(_subset_b64(filename, rebuild=rebuild)))
        print(f"{key:12s} {raw:7,d} B  ->  {sub:6,d} B subset  ({sub * 4 // 3:,d} B base64)")
    print()
    print("cache:", os.path.relpath(CACHE), "(commit it; renders read from here)")
