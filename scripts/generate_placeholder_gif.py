#!/usr/bin/env python3
"""
Generate a retro terminal / cyber pixel placeholder GIF for assets/gifs/profile.gif.
Designed so that Harish can simply drop in his own GIF (e.g. Ronaldo GIF) anytime.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "gifs", "profile.gif")

WIDTH, HEIGHT = 380, 360
NUM_FRAMES = 24

def create_frames():
    frames = []
    
    # Try finding standard monospace font or default
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf",
    ]
    font_small = None
    font_large = None
    for f in font_candidates:
        if os.path.exists(f):
            font_small = ImageFont.truetype(f, 13)
            font_large = ImageFont.truetype(f, 16)
            font_title = ImageFont.truetype(f, 11)
            break
    if font_small is None:
        font_small = ImageFont.load_default()
        font_large = font_small
        font_title = font_small

    for i in range(NUM_FRAMES):
        # Create dark background
        img = Image.new("RGBA", (WIDTH, HEIGHT), color=(13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # Outer frame
        draw.rounded_rectangle([(2, 2), (WIDTH - 3, HEIGHT - 3)], radius=10, outline=(48, 54, 61, 255), width=1)
        
        # Titlebar
        draw.line([(2, 30), (WIDTH - 3, 30)], fill=(48, 54, 61, 255), width=1)
        # Window buttons
        draw.ellipse([(14, 11), (22, 19)], fill=(255, 95, 86, 255))
        draw.ellipse([(28, 11), (36, 19)], fill=(255, 189, 46, 255))
        draw.ellipse([(42, 11), (50, 19)], fill=(39, 201, 63, 255))
        
        # Title text
        draw.text((WIDTH // 2 - 60, 10), "dev_session.sh", font=font_title, fill=(125, 133, 144, 255))
        
        # Subtle scanline effect
        scan_y = int(32 + ((i * 14) % (HEIGHT - 40)))
        draw.line([(4, scan_y), (WIDTH - 5, scan_y)], fill=(56, 189, 248, 30), width=2)
        
        # Terminal lines
        draw.text((20, 48), "Harish-tig@github ~ $", font=font_small, fill=(57, 211, 83, 255))
        draw.text((195, 48), "./launch.sh", font=font_small, fill=(240, 246, 252, 255))
        
        draw.text((20, 72), "[SYSTEM] Initializing SDE Environment...", font=font_small, fill=(125, 133, 144, 255))
        draw.text((20, 94), "[BACKEND] FastAPI & Django : READY", font=font_small, fill=(168, 85, 247, 255))
        draw.text((20, 116), "[DATA] PostgreSQL + MongoDB : ACTIVE", font=font_small, fill=(56, 189, 248, 255))
        draw.text((20, 138), "[AIML] Neural Nets & Models : LOADED", font=font_small, fill=(255, 189, 46, 255))
        
        # Retro Pixel Art Football / Globe in Center
        cx, cy = WIDTH // 2, 215
        radius = 42
        
        # Pulse animation
        pulse = math.sin(i * math.pi * 2 / NUM_FRAMES) * 3
        r = int(radius + pulse)
        
        # Circular cyber border
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(168, 85, 247, 180), width=2)
        draw.ellipse([(cx - r + 8, cy - r + 8), (cx + r - 8, cy + r - 8)], outline=(56, 189, 248, 120), width=1)
        
        # Pixel-style football hexagon/pentagon center
        rot = (i * math.pi * 2 / NUM_FRAMES)
        pts = []
        for p in range(6):
            ang = rot + p * (math.pi / 3)
            px = cx + int(math.cos(ang) * (r * 0.45))
            py = cy + int(math.sin(ang) * (r * 0.45))
            pts.append((px, py))
        draw.polygon(pts, fill=(240, 246, 252, 220))
        
        # Radiating radar/cyber ticks
        for p in range(6):
            ang = rot + p * (math.pi / 3)
            p1x = cx + int(math.cos(ang) * (r * 0.45))
            p1y = cy + int(math.sin(ang) * (r * 0.45))
            p2x = cx + int(math.cos(ang) * (r * 0.85))
            p2y = cy + int(math.sin(ang) * (r * 0.85))
            draw.line([(p1x, p1y), (p2x, p2y)], fill=(168, 85, 247, 220), width=2)
            
        # Subtle status tag below art
        draw.text((cx - 72, 280), "✦ READY TO REPLACE ✦", font=font_small, fill=(168, 85, 247, 255))
        draw.text((cx - 86, 302), "(drop custom GIF in assets/gifs/)", font=font_title, fill=(125, 133, 144, 255))
        
        # Blinking cursor at bottom
        if (i // 6) % 2 == 0:
            draw.rectangle([(20, 328), (28, 342)], fill=(57, 211, 83, 255))
            draw.text((34, 328), "status: ONLINE", font=font_small, fill=(125, 133, 144, 255))
        else:
            draw.text((34, 328), "status: ONLINE", font=font_small, fill=(125, 133, 144, 255))

        # Convert to P mode with palette for clean GIF output
        frames.append(img.convert("RGB"))
        
    return frames

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    frames = create_frames()
    frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True
    )
    print(f"Generated {OUT_PATH} ({len(frames)} frames)")

if __name__ == "__main__":
    main()
