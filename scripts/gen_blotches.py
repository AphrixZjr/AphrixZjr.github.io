#!/usr/bin/env python
"""
Generate public/textures/blotches.svg — the clashing-color irregular curved
blotch texture for the card-page margins (§10.2, replaces the rainbow stripes).

Hard-edge organic blobs (closed Catmull-Rom→bezier curves) in the operating
palette, some with a black keyline to keep the brutalist language. Seeded for
reproducibility. Re-run: python scripts/gen_blotches.py
"""
from __future__ import annotations
import math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "textures" / "blotches.svg"

W, H = 1440, 1080
random.seed(42)

# operating palette (mirrors tokens.css) — clashing fills
PAPER  = "#f3ecdd"
COLORS = [
        "#3b2bf0", "#ccff00",
        "#ff2e6e", "#8fefc9",
        "#ff5a1e", "#ffc4dd"
        ]
INK    = "#0e0e0e"


def blob_path(cx, cy, r, points=12, jitter=0.15):
    """Closed organic path through jittered points, smoothed Catmull-Rom→cubic."""
    pts = []
    for i in range(points):
        a = 2 * math.pi * i / points
        rr = r * (1 + random.uniform(-jitter, jitter))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    n = len(pts)
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + "Z"


def main():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
    ]
    # large background blobs first, smaller clashing ones layered on top
    layers = [
        (16, (120, 200), 0.30),   # big base blobs
        (26, (70, 150), 0.40),    # medium
        (22, (30, 80), 0.46),     # small speckles
    ]
    prev = None
    for count, (rmin, rmax), jit in layers:
        for _ in range(count):
            cx = random.uniform(-80, W + 80)
            cy = random.uniform(-80, H + 80)
            r = random.uniform(rmin, rmax)
            color = random.choice([c for c in COLORS if c != prev])
            prev = color
            d = blob_path(cx, cy, r, points=random.choice([7, 8, 9, 10]), jitter=jit)
            parts.append(f'<path d="{d}" fill="{color}"/>')
    parts.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
