#!/usr/bin/env python3
"""
Generate a compact JSON-style terminal info card SVG.
Used as the right column in the INFO / whoami section of the README.

Visual concept: neofetch-style dark panel, key:value pairs styled like JSON,
section headers as comments, subtle Among Us crewmate accents, no emojis.
"""
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "svg", "info-card.svg")

W, H = 440, 388
PAD_L  = 18
PAD_T  = 48   # below titlebar
TITLEBAR_H = 28
LH = 19.5     # line height

# Colour palette
BG        = "#0d1117"
SURFACE   = "#111722"
BORDER    = "#30363d"
MUTED     = "#484f58"
FG        = "#c9d1d9"
GREEN     = "#3fb950"
ORANGE    = "#ffa657"
CYAN      = "#79c0ff"
PURPLE    = "#d2a8ff"
COMMENT   = "#6e7681"
STRING    = "#a5d6ff"
NUMBER    = "#f2cc60"

# ─── Content definition ────────────────────────────────────────────────────
# Row types:
#   ("host",)              -> user@host header line
#   ("sep",)               -> thin separator line
#   ("comment", text)      -> // comment line
#   ("kv", key, value, val_color)  -> "key": value
#   ("gap",)               -> small vertical gap
ROWS = [
    ("host",),
    ("sep",),
    ("comment", "// identity"),
    ("kv", "name",     '"Harish Nadar"',      STRING),
    ("kv", "role",     '"Software Engineer"', STRING),
    ("kv", "location", '"Mumbai, India"',     STRING),
    ("gap",),
    ("comment", "// education"),
    ("kv", "degree",     '"B.E. AI & Machine Learning"', STRING),
    ("kv", "university", '"University of Mumbai"',        STRING),
    ("kv", "year",       "2026",                          NUMBER),
    ("kv", "cgpa",       "7.5",                           NUMBER),
    ("gap",),
    ("comment", "// focus"),
    ("kv", "primary",   '"Backend Engineering"', STRING),
    ("kv", "secondary", '"Applied ML / AI"',     STRING),
    ("gap",),
    ("comment", "// languages"),
    ("kv", "code", '["Python", "JavaScript", "SQL", "C"]', CYAN),
    ("gap",),
    ("comment", "// highlights"),
    ("kv", "hackathon", '"SIH Finalist 2024"',          STRING),
    ("kv", "award",     '"1st — TCSC Algo Dev 2025"',   STRING),
    ("gap",),
    ("comment", "// outside_terminal"),
    ("kv", "hobby", '"football"', STRING),
]

# Among Us crewmate silhouette pixels (col, row)
CREWMATE = [
    (2,0),(3,0),(4,0),(5,0),
    (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
    (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
    (1,3),(4,3),(5,3),(6,3),
    (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
    (0,5),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),
    (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),
    (0,7),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),
    (0,8),(1,8),(7,8),
    (0,9),(1,9),(6,9),(7,9),
]
VISOR = [(2,1),(3,1),(2,2),(3,2),(2,3),(3,3)]


def crewmate_svg(ox, oy, px=3, color="#a855f7", visor_col="#c084fc", alpha=0.30):
    parts = []
    for (c, r) in CREWMATE:
        x, y = ox + c * px, oy + r * px
        parts.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{color}" opacity="{alpha:.2f}"/>')
    for (c, r) in VISOR:
        x, y = ox + c * px, oy + r * px
        parts.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{visor_col}" opacity="{min(alpha+0.15, 1):.2f}"/>')
    return "\n  ".join(parts)


def rise(inner, i):
    delay = 0.08 + i * 0.045
    return (f'<g opacity="0">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/></g>')


def text_el(x, y, txt, fill, size=12.5, weight="400", anchor="start"):
    t = html.escape(str(txt))
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{t}</text>')


def build_rows():
    mono = "ui-monospace,'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"
    parts = []
    y = PAD_T + 22
    i = 0
    for row in ROWS:
        kind = row[0]
        if kind == "gap":
            y += LH * 0.45
            continue
        if kind == "host":
            inner = (text_el(PAD_L, y, "harish", GREEN, size=13.5, weight="700") +
                     text_el(PAD_L + 42, y, "@", MUTED, size=13.5) +
                     text_el(PAD_L + 55, y, "github", CYAN, size=13.5, weight="700") +
                     f'<line x1="{PAD_L}" y1="{y+4}" x2="{W-PAD_L}" y2="{y+4}" stroke="{BORDER}" stroke-width="0.8"/>')
            parts.append(f'<g font-family="{mono}">{rise(inner, i)}</g>')
        elif kind == "sep":
            parts.append(f'<line x1="{PAD_L}" y1="{y-4}" x2="{W-PAD_L}" y2="{y-4}" stroke="{BORDER}" stroke-opacity="0.5" stroke-width="0.6"/>')
            y -= LH * 0.4
        elif kind == "comment":
            inner = text_el(PAD_L, y, row[1], COMMENT, size=11.5)
            parts.append(f'<g font-family="{mono}" font-style="italic">{rise(inner, i)}</g>')
        elif kind == "kv":
            _, key, val, vcol = row
            # Key in orange
            kw = len(key) * 7.2 + 2
            inner = (text_el(PAD_L, y, f'"{key}"', ORANGE, size=12.2, weight="600") +
                     text_el(PAD_L + kw + 14, y, ":", MUTED, size=12.2) +
                     text_el(PAD_L + kw + 22, y, val, vcol, size=12.2))
            parts.append(f'<g font-family="{mono}">{rise(inner, i)}</g>')
        i += 1
        y += LH
    return parts, y


def generate_svg():
    body_parts, final_y = build_rows()

    # Dynamically size card height
    card_h = max(H, int(final_y) + 24)
    crewmate = crewmate_svg(ox=W - 52, oy=TITLEBAR_H + 6, px=3, color="#a855f7", alpha=0.20)

    mono = "ui-monospace,'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"

    svg = f'''\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {card_h}" width="{W}" height="{card_h}" font-family="{mono}">
  <!-- Background -->
  <rect width="{W}" height="{card_h}" rx="10" fill="{BG}"/>

  <!-- Subtle surface tint on body -->
  <rect x="0" y="{TITLEBAR_H}" width="{W}" height="{card_h - TITLEBAR_H}" rx="10" fill="{SURFACE}" opacity="0.4"/>

  <!-- Border -->
  <rect x="0.6" y="0.6" width="{W-1.2:.1f}" height="{card_h-1.2:.1f}" rx="10" fill="none" stroke="{BORDER}" stroke-width="1.1"/>

  <!-- Titlebar separator -->
  <line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{BORDER}" stroke-width="0.8"/>

  <!-- Window dots -->
  <circle cx="14" cy="{TITLEBAR_H/2:.1f}" r="3.8" fill="#ff5f56"/>
  <circle cx="26" cy="{TITLEBAR_H/2:.1f}" r="3.8" fill="#ffbd2e"/>
  <circle cx="38" cy="{TITLEBAR_H/2:.1f}" r="3.8" fill="#27c93f"/>

  <!-- Titlebar label -->
  <text x="{W//2}" y="{TITLEBAR_H/2+4:.1f}" fill="{MUTED}" font-size="10" text-anchor="middle">harish@github: ~$ ./info.sh</text>

  <!-- Crewmate decoration (subtle) -->
  {crewmate}

  <!-- Content rows -->
  {"".join(body_parts)}
</svg>'''
    return svg


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    svg = generate_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {OUT_PATH}  ({len(svg)} bytes,  height={svg.split('height=')[2].split('"')[1]}px)")


if __name__ == "__main__":
    main()
