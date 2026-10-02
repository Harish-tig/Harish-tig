#!/usr/bin/env python3
"""
Generate a retro pixel-art inspired Life Progress bar SVG with an animated tombstone.
Configurable birth date, age, and lifespan.
Outputs to assets/svg/life-progress.svg.
"""
import os
import math
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "svg", "life-progress.svg")

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# You can set your exact birth date here (YYYY-MM-DD).
# If set to "YYYY-MM-DD", CURRENT_AGE below is used directly.
BIRTH_DATE = "YYYY-MM-DD"

# Age explicitly specified by Harish (22)
CURRENT_AGE = 22.0

# Expected lifespan in years (configurable)
EXPECTED_LIFESPAN = 80.0
# ==============================================================================

W, H = 840, 150

def calculate_progress():
    if BIRTH_DATE != "YYYY-MM-DD":
        try:
            b_date = datetime.strptime(BIRTH_DATE, "%Y-%m-%d").date()
            today = date.today()
            age_years = (today - b_date).days / 365.25
        except Exception:
            age_years = CURRENT_AGE
    else:
        age_years = CURRENT_AGE
    
    pct = min(100.0, max(0.0, (age_years / EXPECTED_LIFESPAN) * 100.0))
    return age_years, pct

def generate_svg():
    age, pct = calculate_progress()
    bar_width = 650
    bar_height = 24
    bar_x = 30
    bar_y = 75
    fill_w = int((pct / 100.0) * bar_width)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;family=JetBrains+Mono:wght@400;600;700&amp;display=swap');

      .pixel-font {{
        font-family: 'Press Start 2P', 'Courier New', monospace;
      }}
      .mono-font {{
        font-family: 'JetBrains Mono', ui-monospace, monospace;
      }}
      
      .gradient-fill {{
        fill: url(#life-gradient);
      }}
      
      @keyframes floatGhost {{
        0% {{ transform: translateY(0px); opacity: 0.85; }}
        50% {{ transform: translateY(-5px); opacity: 1; }}
        100% {{ transform: translateY(0px); opacity: 0.85; }}
      }}
      
      .floating-ghost {{
        animation: floatGhost 2.4s ease-in-out infinite;
      }}
    </style>
    
    <linearGradient id="life-gradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="50%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#a855f7" />
    </linearGradient>

    <!-- Clip path to animate progress bar fill -->
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" height="{bar_height}" width="0">
        <animate attributeName="width" from="0" to="{fill_w}" dur="1.8s" begin="0.3s" fill="freeze" calcMode="spline" keySplines="0.1 0.8 0.2 1" />
      </rect>
    </clipPath>
  </defs>

  <!-- Container Box with Terminal Styling -->
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1.2"/>
  
  <!-- Terminal Header -->
  <line x1="1" y1="30" x2="{W - 1}" y2="30" stroke="#21262d" stroke-width="1"/>
  <circle cx="18" cy="15" r="4.5" fill="#ff5f56"/>
  <circle cx="33" cy="15" r="4.5" fill="#ffbd2e"/>
  <circle cx="48" cy="15" r="4.5" fill="#27c93f"/>
  
  <text class="mono-font" x="{W // 2}" y="19" fill="#6e7681" font-size="11.5" text-anchor="middle" font-weight="500">
    Harish-tig@terminal: ~/life.sh --status
  </text>
  
  <!-- Terminal Command Line & Stats Header -->
  <g transform="translate(30, 52)">
    <text class="mono-font" x="0" y="0" fill="#39d353" font-weight="700" font-size="13">sys_metric</text>
    <text class="mono-font" x="80" y="0" fill="#7d8590" font-size="13">:: life_progress --age {age:.1f}y / {EXPECTED_LIFESPAN:.0f}y</text>
    <text class="mono-font" x="510" y="0" fill="#a855f7" font-weight="700" font-size="13">[ {pct:.1f}% CONSUMED ]</text>
  </g>

  <!-- Progress Bar Outer Track (Retro Pixel Border) -->
  <rect x="{bar_x - 2}" y="{bar_y - 2}" width="{bar_width + 4}" height="{bar_height + 4}" rx="5" fill="#161b22" stroke="#30363d" stroke-width="1.5" />
  
  <!-- Empty Bar Grid / Segment Dots -->
  <g fill="#21262d">
'''
    # Segment indicators along the bar
    for step in range(1, 10):
        sx = bar_x + int((step / 10.0) * bar_width)
        svg += f'    <line x1="{sx}" y1="{bar_y}" x2="{sx}" y2="{bar_y + bar_height}" stroke="#21262d" stroke-width="1.5" />\n'

    svg += f'''  </g>

  <!-- Filled Animated Progress Bar -->
  <g clip-path="url(#bar-clip)">
    <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="3" fill="url(#life-gradient)" />
    <!-- Pixel scan lines across fill -->
    <line x1="{bar_x}" y1="{bar_y + 4}" x2="{bar_x + bar_width}" y2="{bar_y + 4}" stroke="#ffffff" stroke-opacity="0.2" stroke-width="1" />
    <line x1="{bar_x}" y1="{bar_y + 12}" x2="{bar_x + bar_width}" y2="{bar_y + 12}" stroke="#000000" stroke-opacity="0.15" stroke-width="1" />
  </g>

  <!-- Animated Pixel-Art Tombstone at the End of Bar -->
  <!-- Target X: around bar_x + bar_width + 25 -->
  <g transform="translate({bar_x + bar_width + 18}, {bar_y - 28})">
    <!-- Floating Pixel Spirit / Ghost -->
    <g transform="translate(48, 6)">
      <animateTransform attributeName="transform" type="translate" values="48 8; 48 2; 48 8" dur="2.2s" repeatCount="indefinite" />
      <!-- Pixel flame/ghost body -->
      <path d="M 0 0 L 8 0 L 10 4 L 10 10 L 8 12 L 6 10 L 4 12 L 2 10 L 0 12 Z" fill="#c084fc" opacity="0.85" />
      <!-- Eyes -->
      <rect x="2" y="3" width="2" height="2" fill="#0d1117" />
      <rect x="6" y="3" width="2" height="2" fill="#0d1117" />
      <!-- Glow aura -->
      <circle cx="5" cy="5" r="8" fill="#a855f7" opacity="0.25">
        <animate attributeName="r" values="7;11;7" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite" />
      </circle>
    </g>

    <!-- Retro Pixel Tombstone Stone Body -->
    <!-- Base stone outline & fill -->
    <path d="M 8 20 Q 24 6 40 20 L 42 56 L 6 56 Z" fill="#21262d" stroke="#8b949e" stroke-width="1.6"/>
    <!-- Shadow side -->
    <path d="M 28 11 Q 38 18 40 20 L 42 56 L 36 56 L 36 22 Z" fill="#161b22" opacity="0.6"/>
    
    <!-- Stone Engraving: RIP -->
    <text class="pixel-font" x="24" y="32" fill="#c9d1d9" font-size="7" text-anchor="middle" font-weight="700">RIP</text>
    <line x1="16" y1="36" x2="32" y2="36" stroke="#484f58" stroke-width="1"/>
    <!-- Little cross icon -->
    <rect x="23" y="40" width="2" height="8" fill="#8b949e"/>
    <rect x="20" y="42" width="8" height="2" fill="#8b949e"/>

    <!-- Ground turf / pixel rocks -->
    <rect x="2" y="55" width="44" height="3" fill="#30363d" rx="1"/>
    <rect x="8" y="54" width="6" height="2" fill="#238636"/>
    <rect x="32" y="54" width="8" height="2" fill="#238636"/>
  </g>

  <!-- Footnote detail below progress bar -->
  <g transform="translate(30, 125)">
    <text class="mono-font" x="0" y="0" fill="#6e7681" font-size="11">
      STATUS: Level {age:.0f} reached • {EXPECTED_LIFESPAN - age:.1f} years to terminal state • Configurable via scripts/generate_life_progress.py
    </text>
  </g>
</svg>
'''
    return svg
    
def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    content = generate_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {OUT_PATH} ({len(content)} bytes)")

if __name__ == "__main__":
    main()
