"""
PochvenIntel Avatar Generator v2 — Red & Triglavian
Aggressive blood-red Triglavian aesthetic for @PochvenIntel
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random
import os

# === TRIGLAVIAN RED PALETTE ===
BLOOD_RED = (180, 20, 20)          # Deep crimson
HELLFIRE = (255, 60, 0)            # Bright inferno orange-red
VOID_BLACK = (5, 2, 2)             # Near-black with red tint
ASH_GREY = (120, 110, 110)         # Metallic steel
DARK_CRIMSON = (80, 5, 5)          # Shadow red
BRIGHT_RED = (255, 30, 30)         # Alert red
PALE_RED = (255, 180, 160)         # Faded / ghost red

def create_gradient(width, height, c1, c2, direction="radial"):
    """Create a radial or linear gradient"""
    img = Image.new('RGB', (width, height), c1)
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2
    max_dist = math.sqrt(cx**2 + cy**2)
    
    if direction == "radial":
        # Radial gradient from center
        for y in range(0, height, 2):
            for x in range(0, width, 2):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                ratio = min(dist / max_dist, 1.0)
                r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
                g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
                b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
                draw.point((x, y), fill=(r, g, b))
    else:
        # Vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def triangle_points(cx, cy, radius, rotation=0):
    points = []
    for i in range(3):
        angle = (2 * math.pi / 3 * i) + rotation - math.pi / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def hexagon_points(cx, cy, radius):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def draw_glow_line(draw, x1, y1, x2, y2, color, width=2, glow_layers=3):
    """Draw a line with a glow effect"""
    for i in range(glow_layers, 0, -1):
        alpha = int(80 / i)
        glow_color = (min(255, color[0] + alpha), max(0, color[1] - 20), max(0, color[2] - 20))
        draw.line([(x1, y1), (x2, y2)], fill=glow_color, width=width + i * 2)
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

def create_avatar(output_path, size=400):
    img = create_gradient(size, size, DARK_CRIMSON, VOID_BLACK, "radial")
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    
    # === Background energy burst lines ===
    for angle in [0, math.pi/6, math.pi/3, math.pi/2, 2*math.pi/3, 5*math.pi/6,
                  math.pi, 7*math.pi/6, 4*math.pi/3, 3*math.pi/2, 5*math.pi/3, 11*math.pi/6]:
        x2 = cx + (size * 0.48) * math.cos(angle)
        y2 = cy + (size * 0.48) * math.sin(angle)
        # Faint burst lines
        draw.line([(cx, cy), (x2, y2)], fill=(255, 30, 30, 30), width=1)
    
    # === Outer hexagon (sharp, metallic) ===
    hex_r = size * 0.44
    hex_pts = hexagon_points(cx, cy, hex_r)
    
    # Glow layers for hexagon
    for i in range(6, 0, -1):
        glow_pts = [(x + (cx - x) * (i * 0.003), y + (cy - y) * (i * 0.003)) for x, y in hex_pts]
        glow_col = (min(255, 180 + i * 10), max(0, 20 - i), max(0, 20 - i))
        draw.polygon(glow_pts, outline=glow_col, width=1)
    
    draw.polygon(hex_pts, outline=HELLFIRE, width=3)
    draw.polygon(hex_pts, outline=BRIGHT_RED, width=1)
    
    # === Inner hexagon (rotated, smaller) ===
    hex_r2 = size * 0.30
    hex_pts2 = [(cx + hex_r2 * math.cos(math.pi/3 * i - math.pi/6 + math.pi/12),
                 cy + hex_r2 * math.sin(math.pi/3 * i - math.pi/6 + math.pi/12)) for i in range(6)]
    draw.polygon(hex_pts2, outline=ASH_GREY, width=1)
    
    # === Triple-triangle Triglavian symbol (the Clades) ===
    tri_r = size * 0.18
    for i, angle_offset in enumerate([0, 2*math.pi/3, 4*math.pi/3]):
        tri_center_r = size * 0.10
        tri_cx = cx + tri_center_r * math.cos(angle_offset)
        tri_cy = cy + tri_center_r * math.sin(angle_offset)
        tri_pts = triangle_points(tri_cx, tri_cy, tri_r * 0.5, rotation=angle_offset)
        
        # Fill each triangle with slightly different red shade
        if i == 0:
            fill_col = (120, 10, 10, 80)   # Perun — dark
        elif i == 1:
            fill_col = (160, 15, 15, 80)   # Svarog — medium
        else:
            fill_col = (200, 25, 25, 80)   # Veles — bright
        
        draw.polygon(tri_pts, outline=HELLFIRE, fill=fill_col[:3], width=2)
    
    # === Central "eye" / proving ground portal ===
    portal_r = size * 0.10
    # Outer ring with intense glow
    for i in range(8, 0, -1):
        glow_r = portal_r + i * 2
        glow_alpha = int(60 / i)
        glow_col = (min(255, 255), max(0, 40 - glow_alpha), max(0, 20 - glow_alpha))
        draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
                     outline=glow_col, width=1)
    
    draw.ellipse([cx - portal_r, cy - portal_r, cx + portal_r, cy + portal_r],
                 outline=HELLFIRE, width=3)
    draw.ellipse([cx - portal_r, cy - portal_r, cx + portal_r, cy + portal_r],
                 outline=BRIGHT_RED, width=1)
    
    # Inner pupil — dark void
    pupil_r = size * 0.045
    draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r],
                 fill=VOID_BLACK, outline=HELLFIRE, width=2)
    
    # Crosshair / targeting lines through center
    for angle in [0, math.pi/2]:
        x1 = cx + portal_r * 1.2 * math.cos(angle)
        y1 = cy + portal_r * 1.2 * math.sin(angle)
        x2 = cx + (size * 0.42) * math.cos(angle)
        y2 = cy + (size * 0.42) * math.sin(angle)
        draw_glow_line(draw, x1, y1, x2, y2, ASH_GREY, width=1, glow_layers=2)
    
    # === Corner accents (Triglavian tech motifs) ===
    corner_len = size * 0.08
    corners = [
        (corner_len, corner_len, -1, -1),           # top-left
        (size - corner_len, corner_len, 1, -1),       # top-right
        (corner_len, size - corner_len, -1, 1),       # bottom-left
        (size - corner_len, size - corner_len, 1, 1), # bottom-right
    ]
    for bx, by, dx, dy in corners:
        draw.line([(bx, by), (bx + corner_len * dx, by)], fill=HELLFIRE, width=2)
        draw.line([(bx, by), (bx, by + corner_len * dy)], fill=HELLFIRE, width=2)
    
    # === Orbiting threat indicators ===
    orbit_r = size * 0.38
    for i in range(6):
        angle = (2 * math.pi / 6) * i + math.pi / 12
        dot_x = cx + orbit_r * math.cos(angle)
        dot_y = cy + orbit_r * math.sin(angle)
        dot_size = 3 if i % 2 == 0 else 2
        # Alternating bright/dim
        dot_col = HELLFIRE if i % 2 == 0 else (120, 20, 20)
        draw.ellipse([dot_x - dot_size, dot_y - dot_size,
                      dot_x + dot_size, dot_y + dot_size],
                     fill=dot_col, outline=(255, 80, 20) if i % 2 == 0 else ASH_GREY, width=1)
    
    # === Scratch / wear texture ===
    pixels = img.load()
    for _ in range(size * 3):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        r, g, b = pixels[x, y]
        # Slight scratches (brighter)
        if random.random() > 0.7:
            pixels[x, y] = (min(255, r + 15), max(0, g - 5), max(0, b - 5))
        else:
            pixels[x, y] = (max(0, r - 8), max(0, g - 8), max(0, b - 8))
    
    # === Aggressive border ===
    border = 6
    draw.rectangle([border, border, size - border, size - border],
                   outline=HELLFIRE, width=3)
    draw.rectangle([border + 3, border + 3, size - border - 3, size - border - 3],
                   outline=(80, 10, 10), width=1)
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    out = "media/kybernauts/pochvenintel_avatar_v2.png"
    path = create_avatar(out, size=400)
    print(f"Avatar v2 created: {path}")
