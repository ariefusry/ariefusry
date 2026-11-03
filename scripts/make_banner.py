"""Generate assets/banner.svg: a terminal-style profile banner.

An animated dot portrait made from the GitHub avatar inside a framed panel listing stack, projects and research.

Usage: python scripts/make_banner.py path/to/avatar.png
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "banner.svg"

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

def portrait_svg(avatar, x0, y0, n, pitch, threshold=170, band=8, cycle=6):
    """Animated dot portrait.

    Dots sit on shape edges plus a sparse checker fill inside. Each cycle a
    bright scan line sweeps down the face, then a few horizontal slices glitch
    sideways while a cyan ghost flashes. Pure SMIL, so it runs inside <img>.
    """
    img = ImageOps.autocontrast(Image.open(avatar).convert("L"), cutoff=2)
    mask = img.resize((n, n), Image.LANCZOS).point(lambda v: 255 if v > threshold else 0)
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
    glitch = {3: (9, -6), 7: (-7, 5), 8: (12, -4), 11: (-5, 8)}
    bands = []
    for b in range(0, n, band):
        dots = []
        for y in range(b, min(b + band, n)):
            for x in range(n):
                if edge.getpixel((x, y)) or (mask.getpixel((x, y)) and (x + y) % 2 == 0):
                    dots.append(f'<circle cx="{x0 + x * pitch:.1f}" cy="{y0 + y * pitch:.1f}" r="1.15"/>')
        anim = ""
        if b // band in glitch:
            d1, d2 = glitch[b // band]
            anim = (
                f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
                f'values="0 0;{d1} 0;{d2} 0;0 0" keyTimes="0;.62;.65;.68" dur="{cycle}s" repeatCount="indefinite"/>'
            )
        bands.append(f'<g>{anim}{"".join(dots)}</g>')
    size = n * pitch
    return f"""<defs>
<linearGradient id="pg" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y0 + size}"><stop offset="0" stop-color="{GOLD}"/><stop offset=".55" stop-color="{AMBER}"/><stop offset="1" stop-color="{BRONZE}"/></linearGradient>
<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="scan" maskUnits="userSpaceOnUse" x="{x0 - 20}" y="{y0 - 60}" width="{size + 40}" height="{size + 120}"><rect x="{x0 - 20}" y="{y0 - 50}" width="{size + 40}" height="46" fill="url(#sg)"><animate attributeName="y" values="{y0 - 50};{y0 + size};{y0 + size}" keyTimes="0;.55;1" dur="{cycle}s" repeatCount="indefinite"/></rect></mask>
<g id="dots">{"".join(bands)}</g>
</defs>
<use href="#dots" fill="url(#pg)"/>
<use href="#dots" fill="#ffd6d6" mask="url(#scan)"/>
<use href="#dots" fill="#3ee8ff" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;.35;0" keyTimes="0;.62;.68" dur="{cycle}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="0 0;-4 0;0 0" keyTimes="0;.62;.68" dur="{cycle}s" repeatCount="indefinite"/></use>"""


def text(x, y, parts, size=17, weight="normal"):
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">{spans}</text>'


def main(avatar):
    W = 1240
    panel_y = 36
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
