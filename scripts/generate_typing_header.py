#!/usr/bin/env python3
"""
Generate an animated typing-style terminal introduction SVG.
Title:   "Harish - SDE | Backend | AIML"
Tagline: "learning a little bit of this and a little bit of that aahhh techie"

Design: Dark space terminal, Among Us-inspired subtle crewmate silhouette in corner,
        dot-matrix grid background texture, green prompt, monospace type animation.
Pure SMIL SVG — zero JS, fully GitHub-compatible.
"""
import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "svg", "typing-header.svg")

W, H = 860, 138

TITLE_TEXT   = "Harish - SDE | Backend | AIML"
TAGLINE_TEXT = 'learning a little bit of this and a little bit of that aahhh techie'

TYPE_DUR = 2.0   # seconds for typing animation
TAGLINE_START = TYPE_DUR + 0.6

# Among Us crewmate pixel path (simplified 12x16 pixel silhouette)
# Each tuple is (col, row) of a filled pixel
CREWMATE_PIXELS = [
    # visor / head
    (3,0),(4,0),(5,0),(6,0),(7,0),
    (2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),
    (2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),
    (2,3),(5,3),(6,3),(7,3),(8,3),
    (2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),
    # body
    (1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),
    (1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),
    (1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),
    (1,8),(2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),
    (1,9),(2,9),(8,9),(9,9),
    # legs
    (1,10),(2,10),(3,10),(7,10),(8,10),(9,10),
    (1,11),(2,11),(3,11),(7,11),(8,11),(9,11),
]

def crewmate_svg(ox, oy, px=4, color="#a855f7", opacity="0.28"):
    rects = []
    for (c, r) in CREWMATE_PIXELS:
        x = ox + c * px
        y = oy + r * px
        rects.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{color}" opacity="{opacity}"/>')
    # visor highlight (lighter)
    visor = [(3,1),(4,1),(5,1),(3,2),(4,2),(5,2),(3,3),(4,3)]
    for (c, r) in visor:
        x = ox + c * px
        y = oy + r * px
        rects.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="#e9d5ff" opacity="{float(opacity)+0.12:.2f}"/>')
    return "\n  ".join(rects)

def generate_svg():
    crewmate = crewmate_svg(ox=W - 82, oy=16, px=4, color="#a855f7", opacity="0.22")

    svg = f'''\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <style>
      .tm {{ font-family: ui-monospace,"JetBrains Mono","SF Mono",Menlo,Consolas,monospace; }}
    </style>
    <clipPath id="tc">
      <rect x="22" y="52" height="36" width="0">
        <animate attributeName="width" from="0" to="720" dur="{TYPE_DUR:.1f}s" begin="0.35s" fill="freeze" calcMode="linear"/>
      </rect>
    </clipPath>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="11" fill="#0d1117"/>

  <!-- Subtle dot-grid texture -->
  <pattern id="dots" x="0" y="0" width="18" height="18" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.8" fill="#21262d"/>
  </pattern>
  <rect width="{W}" height="{H}" rx="11" fill="url(#dots)"/>

  <!-- Border -->
  <rect x="0.7" y="0.7" width="{W-1.4:.1f}" height="{H-1.4:.1f}" rx="11" fill="none" stroke="#30363d" stroke-width="1.2"/>

  <!-- Titlebar -->
  <line x1="0" y1="28" x2="{W}" y2="28" stroke="#21262d" stroke-width="1"/>
  <circle cx="16" cy="14" r="4.2" fill="#ff5f56"/>
  <circle cx="30" cy="14" r="4.2" fill="#ffbd2e"/>
  <circle cx="44" cy="14" r="4.2" fill="#27c93f"/>
  <text class="tm" x="{W//2}" y="18.5" fill="#484f58" font-size="10.5" text-anchor="middle">Harish-tig@terminal: ~ [session]</text>

  <!-- Crewmate silhouette (decorative) -->
  {crewmate}

  <!-- Prompt -->
  <text class="tm" x="22" y="48" fill="#3fb950" font-size="13" font-weight="700">❯</text>
  <text class="tm" x="37" y="48" fill="#7d8590" font-size="12.5">./introduce.sh</text>

  <!-- Typed title -->
  <g clip-path="url(#tc)">
    <text class="tm" x="22" y="82" fill="#e6edf3" font-size="25" font-weight="700" letter-spacing="-0.4">{html.escape(TITLE_TEXT)}</text>
  </g>

  <!-- Blinking cursor -->
  <rect y="62" width="14" height="26" fill="#3fb950" rx="1">
    <animate attributeName="x" from="22" to="592" dur="{TYPE_DUR:.1f}s" begin="0.35s" fill="freeze" calcMode="linear"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="0.9s" begin="{TYPE_DUR+0.35:.2f}s" repeatCount="indefinite"/>
  </rect>

  <!-- Tagline (fades in) -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.7s" begin="{TAGLINE_START:.2f}s" fill="freeze"/>
    <text class="tm" x="23" y="114" fill="#6e7681" font-size="12.5" font-style="italic">{html.escape(TAGLINE_TEXT)}</text>
  </g>
</svg>
'''
    return svg

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    svg = generate_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {OUT_PATH}  ({len(svg)} bytes)")

if __name__ == "__main__":
    main()
