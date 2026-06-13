#!/usr/bin/env python
"""
Offline acid-portrait pipeline (FRONTEND_DESIGN §10.1).

Output is a 3-layer misregistration composite (stacked top → bottom):
  TOP     white-black grayscale portrait, centered    (the key image; face stays legible)
  MIDDLE  dot grid (.mark-dots motif), nudged RIGHT
  BOTTOM  white-pink grayscale portrait, nudged LEFT
The small offsets make a pink ghost poke out on the left and dots on the right —
a risograph/editorial misregistration look.

Matte (去背): isnet-general-use raw mask + an ALPHA LEVELS boost. The boost lifts
low-confidence regions (e.g. a dark skirt that the model returns at ~0.3 alpha) to
opaque while the pure-black background stays out, and hardens soft hair edges so the
warm fringe halo disappears.

Output:  public/images/<name>-acid.png            transparent composite (final asset)
         scripts/_preview/<name>-on-acid.png      composited on the acid block (review)

Usage:   python scripts/process_portraits.py            # all configured portraits
         python scripts/process_portraits.py portrait1  # subset
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "public" / "images"
OUT_DIR = ROOT / "public" / "images"
PREVIEW_DIR = ROOT / "scripts" / "_preview"

# ── palette (mirrors src/styles/tokens.css; no new colors) ──
PAPER = (0xF3, 0xEC, 0xDD)
PINK  = (0xFF, 0xC4, 0xDD)
INK   = (0x0E, 0x0E, 0x0E)
ACID  = (0xCC, 0xFF, 0x00)

# ── global tunables ──
OUT_W       = 760     # output width (px)
CONTRAST    = 1.06    # gentle; keep face midtones (no blow-out)
OFFSET_FRAC = 0.036   # layer offset as a fraction of width (~14px @760)
DOT_SPACING = 15      # px between dot centers
DOT_RADIUS  = 2.6     # px dot radius

# ── per-image config ──
# alpha_lo / alpha_hi: levels window applied to the raw mask. Pixels below lo → 0,
# above hi → 1. Lower `lo` recovers faint regions (portrait1's dark skirt).
PORTRAITS = {
    "portrait1": dict(model="isnet-general-use", alpha_lo=0.13, alpha_hi=0.50),
    "portrait2": dict(model="isnet-general-use", alpha_lo=0.30, alpha_hi=0.62),
}

_sessions: dict[str, object] = {}
def session(name: str):
    if name not in _sessions:
        _sessions[name] = new_session(name)
    return _sessions[name]


def matte(img: Image.Image, cfg) -> Image.Image:
    """Raw mask → alpha levels boost → clean RGBA subject."""
    mask = remove(img, session=session(cfg["model"]), only_mask=True)
    a = np.asarray(mask, dtype=float) / 255.0
    lo, hi = cfg["alpha_lo"], cfg["alpha_hi"]
    a = np.clip((a - lo) / (hi - lo), 0, 1)              # boost faint regions, drop bg
    alpha = Image.fromarray((a * 255).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.MaxFilter(3))        # close 1px pinholes
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))   # re-soften the cut edge
    rgba = img.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def _tone(rgba: Image.Image, shadow, highlight) -> Image.Image:
    """Map luminance through a 2-stop duotone (shadow→highlight), keep alpha."""
    arr = np.asarray(rgba, dtype=float)
    rgb, a = arr[..., :3], arr[..., 3]
    g = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    g = np.clip((g - 0.5) * CONTRAST + 0.5, 0, 1)[..., None]
    s = np.array(shadow, dtype=float)
    h = np.array(highlight, dtype=float)
    out = s * (1 - g) + h * g
    return Image.fromarray(
        np.dstack([out.clip(0, 255).astype(np.uint8), a.astype(np.uint8)]), "RGBA")


def gray_layer(rgba):  # white-black grayscale (on-palette endpoints)
    return _tone(rgba, INK, PAPER)

def pink_layer(rgba):  # white-pink grayscale
    return _tone(rgba, PINK, PAPER)


def dots_layer(rgba: Image.Image) -> Image.Image:
    """Ink dot grid clipped to the subject silhouette (transparent elsewhere)."""
    w, h = rgba.size
    dots = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(dots)
    for y in range(0, h + DOT_SPACING, DOT_SPACING):
        for x in range(0, w + DOT_SPACING, DOT_SPACING):
            d.ellipse([x - DOT_RADIUS, y - DOT_RADIUS, x + DOT_RADIUS, y + DOT_RADIUS],
                      fill=INK + (255,))
    subj = np.asarray(rgba)[..., 3]
    da = np.asarray(dots)[..., 3]
    da = (da * (subj > 8)).astype(np.uint8)               # clip dots to subject
    out = np.asarray(dots).copy()
    out[..., 3] = da
    return Image.fromarray(out, "RGBA")


def compose(rgba: Image.Image) -> Image.Image:
    """Stack the three layers with the misregistration offsets."""
    w, h = rgba.size
    off = round(w * OFFSET_FRAC)
    cw = w + 2 * off
    canvas = Image.new("RGBA", (cw, h), (0, 0, 0, 0))
    canvas.alpha_composite(pink_layer(rgba), (off - off, 0))   # BOTTOM: left  (x = 0)
    canvas.alpha_composite(dots_layer(rgba), (off + off, 0))   # MIDDLE: right (x = 2*off)
    canvas.alpha_composite(gray_layer(rgba), (off, 0))         # TOP: centered (x = off)
    return canvas


def preview_on_acid(p: Image.Image) -> Image.Image:
    pad = 48
    fw, fh = p.width + pad * 2, p.height + pad * 2
    canvas = Image.new("RGBA", (fw, fh), ACID + (255,))
    canvas.alpha_composite(p, (pad, pad))
    d = ImageDraw.Draw(canvas)
    d.rectangle([2, 2, fw - 3, fh - 3], outline=INK + (255,), width=5)
    return canvas


def process(name: str, cfg):
    img = Image.open(SRC_DIR / f"{name}.jpg").convert("RGB")
    img = img.resize((OUT_W, round(OUT_W * img.height / img.width)), Image.LANCZOS)
    subject = matte(img, cfg)
    comp = compose(subject)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{name}-acid.png"
    comp.save(out)
    preview_on_acid(comp).convert("RGB").save(PREVIEW_DIR / f"{name}-on-acid.png", quality=92)
    print(f"  {name}: {out.relative_to(ROOT)}  ({comp.width}×{comp.height})")


def main():
    names = sys.argv[1:] or list(PORTRAITS)
    print(f"acid-portrait pipeline (3-layer) → {len(names)} image(s)")
    for n in names:
        process(n, PORTRAITS[n])
    print("done. previews in scripts/_preview/")


if __name__ == "__main__":
    main()
