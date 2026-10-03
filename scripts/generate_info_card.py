#!/usr/bin/env python3
"""
Generate a clean, perfectly aligned JSON-style terminal info card SVG.
Used as the right column in the INFO / whoami section of the README.

Eliminates text overlaps with fixed column grid alignment:
Key column (x=20) | Colon (x=140) | Value column (x=152)
"""
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "svg", "info-card.svg")

W = 480
PAD_L = 20
COLON_X = 140
VAL_X = 152
TITLEBAR_H = 30
LH = 21.5     # comfortable line height without vertical crowding

# Color palette
BG        = "#0d1117"
SURFACE   = "#131b28"
BORDER    = "#30363d"
MUTED     = "#64748b"
FG        = "#c9d1d9"
GREEN     = "#3fb950"
ORANGE    = "#ff7b72"
CYAN      = "#79c0ff"
PURPLE    = "#d2a8ff"
COMMENT   = "#7d8590"
STRING    = "#a5d6ff"
NUMBER    = "#f2cc60"

# Content definition
ROWS = [
    ("host",),
    ("sep",),
    ("comment", "// identity"),
    ("kv", "name",        '"Harish Nadar"',                  STRING),
    ("kv", "role",        '"Software Engineer (Backend/AI)"', STRING),
    ("kv", "location",    '"Mumbai, India"',                 STRING),
    ("gap",),
    ("comment", "// internships"),
    ("kv", "10x_growth",   '"Flutter Developer"',             STRING),
    ("kv", "onlinesavaari",'"Backend Developer"',             STRING),
    ("gap",),
    ("comment", "// education (past)"),
    ("kv", "degree",      '"Pursued B.E. AI & ML"',          STRING),
    ("kv", "university",  '"University of Mumbai"',          STRING),
    ("kv", "class",       "2026",                            NUMBER),
    ("kv", "cgpa",        "7.5",                             NUMBER),
    ("gap",),
    ("comment", "// stack & tools"),
    ("kv", "backend",     '["FastAPI", "Django", "Express.js"]', CYAN),
    ("kv", "languages",   '["Python", "JavaScript", "SQL", "C"]', CYAN),
    ("kv", "databases",   '["PostgreSQL", "MongoDB", "Redis"]', PURPLE),
    ("gap",),
    ("comment", "// highlights"),
    ("kv", "hackathon",   '"SIH Finalist 2024"',             STRING),
    ("kv", "award",       '"1st — TCSC Algo Dev 2025"',      STRING),
    ("gap",),
    ("comment", "// outside_terminal"),
    ("kv", "hobby",       '"football"',                      STRING),
]


def text_el(x, y, txt, fill, size=11.8, weight="400", anchor="start"):
    t = html.escape(str(txt))
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{t}</text>')


def rise(inner, i):
    delay = 0.05 + i * 0.035
    return (f'<g opacity="0">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.3f}s" dur="0.3s" fill="freeze"/></g>')


def build_rows():
    mono = "ui-monospace,'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"
    parts = []
    y = TITLEBAR_H + 26
    i = 0

    for row in ROWS:
        kind = row[0]
        if kind == "gap":
            y += LH * 0.4
            continue
        if kind == "host":
            inner = (text_el(PAD_L, y, "harish", GREEN, size=13, weight="700") +
                     text_el(PAD_L + 46, y, "@", MUTED, size=13) +
                     text_el(PAD_L + 58, y, "github", CYAN, size=13, weight="700") +
                     f'<line x1="{PAD_L}" y1="{y+5}" x2="{W-PAD_L}" y2="{y+5}" stroke="{BORDER}" stroke-width="0.8"/>')
            parts.append(f'<g font-family="{mono}">{rise(inner, i)}</g>')
        elif kind == "sep":
            parts.append(f'<line x1="{PAD_L}" y1="{y-4}" x2="{W-PAD_L}" y2="{y-4}" stroke="{BORDER}" stroke-opacity="0.5" stroke-width="0.6"/>')
            y -= LH * 0.3
        elif kind == "comment":
            inner = text_el(PAD_L, y, row[1], COMMENT, size=11, weight="500")
            parts.append(f'<g font-family="{mono}" font-style="italic">{rise(inner, i)}</g>')
        elif kind == "kv":
            _, key, val, vcol = row
            # Fixed grid positioning: keys start at PAD_L, colon at COLON_X, values at VAL_X
            inner = (
                text_el(PAD_L, y, f'"{key}"', ORANGE, size=11.6, weight="600") +
                text_el(COLON_X, y, ":", MUTED, size=11.6, weight="600") +
                text_el(VAL_X, y, val, vcol, size=11.6, weight="400")
            )
            parts.append(f'<g font-family="{mono}">{rise(inner, i)}</g>')
        i += 1
        y += LH

    return parts, y


def generate_svg():
    body_parts, final_y = build_rows()
    card_h = int(final_y) + 16

    mono = "ui-monospace,'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"

    svg = f'''\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {card_h}" width="{W}" height="{card_h}" font-family="{mono}">
  <!-- Card Background -->
  <rect width="{W}" height="{card_h}" rx="10" fill="{BG}"/>
  <rect x="0" y="{TITLEBAR_H}" width="{W}" height="{card_h - TITLEBAR_H}" rx="10" fill="{SURFACE}" opacity="0.4"/>
  <rect x="0.6" y="0.6" width="{W-1.2:.1f}" height="{card_h-1.2:.1f}" rx="10" fill="none" stroke="{BORDER}" stroke-width="1.1"/>

  <!-- Titlebar -->
  <line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{BORDER}" stroke-width="0.8"/>
  <circle cx="16" cy="{TITLEBAR_H/2:.1f}" r="4" fill="#ef4444"/>
  <circle cx="29" cy="{TITLEBAR_H/2:.1f}" r="4" fill="#eab308"/>
  <circle cx="42" cy="{TITLEBAR_H/2:.1f}" r="4" fill="#22c55e"/>

  <text x="{W//2}" y="{TITLEBAR_H/2+4:.1f}" fill="{MUTED}" font-size="10.5" text-anchor="middle" font-weight="600">
    harish@github: ~$ ./info.sh
  </text>

  <!-- Mini Among Us crewmate accent in header -->
  <g transform="translate({W - 38}, 8) scale(0.28)">
    <rect x="0" y="16" width="12" height="32" rx="5" fill="#7e22ce" stroke="#1e1b4b" stroke-width="2.5"/>
    <path d="M 8 18 C 8 6, 38 6, 38 18 L 38 48 C 38 52, 34 56, 29 56 L 27 56 C 24 56, 23 53, 23 50 L 23 44 L 20 44 L 20 50 C 20 53, 19 56, 16 56 L 14 56 C 9 56, 6 52, 6 48 Z"
          fill="#9333ea" stroke="#1e1b4b" stroke-width="2.5"/>
    <rect x="18" y="14" width="24" height="15" rx="7.5" fill="#38bdf8" stroke="#1e1b4b" stroke-width="2"/>
    <ellipse cx="26" cy="18" rx="8" ry="3" fill="#ffffff" opacity="0.85"/>
  </g>

  <!-- Grid Rows -->
  {"".join(body_parts)}
</svg>'''
    return svg


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    svg = generate_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {OUT_PATH} ({len(svg)} bytes, height={svg.split('height=')[2].split('\"')[1]}px)")


if __name__ == "__main__":
    main()
