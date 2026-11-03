"""Generate assets/banner.svg: a terminal-style profile banner.

Pixel-font title, a dot portrait made from the GitHub avatar, and a
framed panel listing stack, projects and research.

Usage: python scripts/make_banner.py path/to/avatar.png
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "banner.svg"

TITLE = "ZONDER"
HEADER = "Arief Muhammad Usry · Fullstack Developer · Bekasi, Indonesia"

SECTIONS = [
    ("Stack", [
        ("web", "Go, Laravel, Next.js, React, TypeScript"),
        ("mobile", "Flutter, Dart"),
        ("data & ml", "Python, TensorFlow, scikit-learn, Pandas, FastAPI"),
        ("database", "PostgreSQL, MySQL, Supabase, Neon, Prisma"),
        ("infra", "Docker, Nginx, AWS EC2, Cloudflare, Vercel"),
    ]),
    ("Featured Projects", [
        ("blister64", "diecast auction, escrow wallet, AI search"),
        ("lajur", "AI-assisted job tracker for job seekers"),
        ("commission-tracker", "order tracker for illustrators"),
        ("indeta, sugih", "client platforms (freelance)"),
    ]),
    ("Research", [
        ("IC2IE 2026", "ER-LBD toxicity, ANN + Grey Wolf Optimizer"),
    ]),
]

FOOTER = [
    ("Rie", " · Telkom University", "#e8232f", "#9a3b40"),
    ("GPA 3.76", " · cum laude", "#e6e6e6", "#9a3b40"),
    ("ariefusry.me", "", "#6b6b6b", "#6b6b6b"),
]

FONT = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
GOLD, AMBER, BRONZE = "#ff6b6b", "#e8232f", "#8e1620"
DIM, TEXT, BG = "#9a3b40", "#e6e6e6", "#0c0c0c"

GLYPHS = {
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
}


def title_svg(x0, y0, px):
    """Pixel title: banded gradient fill plus two offset outline strokes."""
    cells = []
    x = x0
    for ch in TITLE:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "#":
                    cells.append((x + c * px, y0 + r * px))
        x += (len(g[0]) + 1) * px
    filled = set(cells)
    segs = []
    for cx, cy in cells:
        if (cx, cy - px) not in filled:
            segs.append(f"M{cx} {cy}h{px}")
        if (cx, cy + px) not in filled:
            segs.append(f"M{cx} {cy + px}h{px}")
        if (cx - px, cy) not in filled:
            segs.append(f"M{cx} {cy}v{px}")
        if (cx + px, cy) not in filled:
            segs.append(f"M{cx + px} {cy}v{px}")
    outline = "".join(segs)
    rects = "".join(f'<rect x="{cx}" y="{cy}" width="{px + 0.5}" height="{px + 0.5}"/>' for cx, cy in cells)
    h = 7 * px
    return (
        f'<linearGradient id="tg" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y0 + h}">'
        f'<stop offset="0" stop-color="{GOLD}"/><stop offset=".42" stop-color="{GOLD}"/>'
        f'<stop offset=".42" stop-color="{AMBER}"/><stop offset=".72" stop-color="{AMBER}"/>'
        f'<stop offset=".72" stop-color="{BRONZE}"/><stop offset="1" stop-color="{BRONZE}"/></linearGradient>'
        f'<path d="{outline}" transform="translate(11 11)" stroke="{BRONZE}" stroke-width="2" fill="none"/>'
        f'<path d="{outline}" transform="translate(6 6)" stroke="{AMBER}" stroke-width="2" fill="none"/>'
        f'<g fill="url(#tg)">{rects}</g>'
    ), x - px - x0, h


def portrait_svg(avatar, x0, y0, n, pitch, threshold=170):
    """Dot portrait: full dots on shape edges, a sparse checker fill inside."""
    img = ImageOps.autocontrast(Image.open(avatar).convert("L"), cutoff=2)
    mask = img.resize((n, n), Image.LANCZOS).point(lambda v: 255 if v > threshold else 0)
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
    dots = []
    for y in range(n):
        for x in range(n):
            if edge.getpixel((x, y)) or (mask.getpixel((x, y)) and (x + y) % 2 == 0):
                dots.append(f'<circle cx="{x0 + x * pitch:.1f}" cy="{y0 + y * pitch:.1f}" r="1.15"/>')
    grad = (
        f'<linearGradient id="pg" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y0 + n * pitch}">'
        f'<stop offset="0" stop-color="{GOLD}"/><stop offset=".55" stop-color="{AMBER}"/>'
        f'<stop offset="1" stop-color="{BRONZE}"/></linearGradient>'
    )
    return grad + f'<g fill="url(#pg)">{"".join(dots)}</g>'


def text(x, y, parts, size=17, weight="normal"):
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">{spans}</text>'


def main(avatar):
    W, px = 1240, 20
    title, tw, th = title_svg(0, 24, px)
    title_x = (W - tw) // 2

    panel_y = 24 + th + 52
    n, pitch = 120, 3.1
    left_x, art_y = 56, panel_y + 40
    right_x, lh = 450, 24

    body = []
    y = panel_y + 52
    for head, items in SECTIONS:
        body.append(text(right_x, y, [(head, AMBER)], weight="bold"))
        y += lh
        for k, v in items:
            body.append(text(right_x, y, [(k + ": ", DIM), (v, TEXT)]))
            y += lh
        y += lh * 0.6

    fy = art_y + n * pitch + 34
    for a, b, ca, cb in FOOTER:
        body.append(text(left_x, fy, [(a, ca), (b, cb)]))
        fy += lh
    panel_h = max(y, fy) - panel_y + 6
    H = panel_y + panel_h + 24

    hw = len(HEADER) * 9.4 + 28
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" font-family="{FONT}">
<rect width="100%" height="100%" rx="14" fill="{BG}"/>
<g transform="translate({title_x} 0)">{title}</g>
<rect x="24" y="{panel_y}" width="{W - 48}" height="{panel_h:.0f}" rx="10" fill="none" stroke="{BRONZE}" stroke-width="1.5"/>
<rect x="{(W - hw) / 2:.0f}" y="{panel_y - 12}" width="{hw:.0f}" height="24" fill="{BG}"/>
<text x="{W / 2}" y="{panel_y + 6}" text-anchor="middle" font-size="17" font-weight="bold" fill="{GOLD}">{escape(HEADER)}</text>
{portrait_svg(avatar, left_x, art_y, n, pitch)}
{"".join(body)}
</svg>
"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({W}x{H:.0f}, {len(svg) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
