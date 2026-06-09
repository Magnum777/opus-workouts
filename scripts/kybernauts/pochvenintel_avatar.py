"""
PochvenIntel Avatar Generator
Creates a 400x400 avatar for @PochvenIntel Twitter/X account.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# Triglavian/Kybernauts color palette
TRIGLAVIAN_PURPLE = (45, 20, 60)
BIO_TEAL = (0, 255, 200)
VOID_BLACK = (10, 5, 15)
ACCENT_RED = (200, 50, 80)
GOLD = (255, 200, 100)
DARK_TEAL = (0, 180, 150)

def hexagon_points(center_x, center_y, radius):
    """Generate points for a hexagon"""
    points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def triangle_points(center_x, center_y, radius, rotation=0):
    """Generate points for an equilateral triangle"""
    points = []
    for i in range(3):
        angle = (2 * math.pi / 3 * i) + rotation - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def create_gradient_background(width, height, color1, color2):
    """Create a vertical gradient background"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def create_avatar(output_path, size=400):
    """Generate PochvenIntel avatar"""
    
    # Create base image with gradient
    img = create_gradient_background(size, size, VOID_BLACK, TRIGLAVIAN_PURPLE)
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # === Outer hexagon frame ===
    hex_r = size * 0.45
    hex_points = hexagon_points(cx, cy, hex_r)
    
    # Glow effect for hexagon
    for i in range(5, 0, -1):
        glow_points = [(x + (cx - x) * (i * 0.005), y + (cy - y) * (i * 0.005)) for x, y in hex_points]
        draw.polygon(glow_points, outline=(0, 255 - i * 40, 200 - i * 30), width=1)
    
    draw.polygon(hex_points, outline=BIO_TEAL, width=2)
    
    # === Inner triangles (Triglavian triple-triangle) ===
    inner_r = size * 0.22
    # Three small triangles forming the Triglavian symbol
    for angle_offset in [0, 2 * math.pi / 3, 4 * math.pi / 3]:
        tri_points = triangle_points(
            cx + inner_r * 0.6 * math.cos(angle_offset),
            cy + inner_r * 0.6 * math.sin(angle_offset),
            inner_r * 0.4,
            rotation=angle_offset
        )
        draw.polygon(tri_points, outline=ACCENT_RED, fill=(200, 50, 80, 30), width=2)
    
    # === Central eye / radar motif ===
    # Outer circle
    eye_r = size * 0.12
    draw.ellipse([cx - eye_r, cy - eye_r, cx + eye_r, cy + eye_r], 
                 outline=BIO_TEAL, width=2)
    
    # Inner circle (pupil)
    pupil_r = size * 0.05
    draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r],
                 outline=ACCENT_RED, fill=ACCENT_RED)
    
    # Radar sweep line
    for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        x2 = cx + eye_r * 1.3 * math.cos(angle)
        y2 = cy + eye_r * 1.3 * math.sin(angle)
        draw.line([(cx, cy), (x2, y2)], fill=DARK_TEAL, width=1)
    
    # === Orbiting dots (satellites/stars) ===
    orbit_r = size * 0.38
    for i in range(8):
        angle = (2 * math.pi / 8) * i + math.pi / 8
        dot_x = cx + orbit_r * math.cos(angle)
        dot_y = cy + orbit_r * math.sin(angle)
        dot_size = 2 + (i % 3)
        draw.ellipse([dot_x - dot_size, dot_y - dot_size, 
                      dot_x + dot_size, dot_y + dot_size],
                     fill=BIO_TEAL)
    
    # === Geometric grid lines (radar grid) ===
    # Concentric hexagons (faint)
    for r_mult in [0.15, 0.30]:
        r = size * r_mult
        hex_p = hexagon_points(cx, cy, r)
        draw.polygon(hex_p, outline=(0, 255, 200, 40), width=1)
    
    # === Noise/texture overlay ===
    import random
    pixels = img.load()
    for i in range(0, size, 3):
        for j in range(0, size, 3):
            r, g, b = pixels[i, j]
            noise = random.randint(-8, 8)
            pixels[i, j] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
    
    # === Subtle border ===
    border = 8
    draw.rectangle([border, border, size - border, size - border],
                   outline=BIO_TEAL, width=2)
    draw.rectangle([border + 2, border + 2, size - border - 2, size - border - 2],
                   outline=(0, 255, 200, 60), width=1)
    
    # Save
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    out = "media/kybernauts/pochvenintel_avatar.png"
    path = create_avatar(out, size=400)
    print(f"Avatar created: {path}")
