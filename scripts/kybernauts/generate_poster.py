#!/usr/bin/env python3
"""
Kybernauts Clade Propaganda Poster Generator
Creates Triglavian-themed recruitment posters using PIL
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random
from datetime import datetime

# Triglavian color palette
COLORS = {
    'void_black': (13, 2, 8),
    'deep_purple': (26, 10, 46),
    'purple': (60, 20, 80),
    'teal': (0, 212, 170),
    'teal_dim': (0, 150, 120),
    'crimson': (180, 40, 60),
    'white': (240, 240, 245),
    'gold': (200, 170, 80),
}

# Tagline pool - varies each run
TAGLINES = [
    "POCHVEN OR BUST",
    "UNDOCK OR DIE",
    "TRIANGLE DEFENDERS",
    "HUNT OR BE HUNTED",
    "FORWARD TO POCHVEN",
    "Alpha Force - First In, Last Out",
    "THE CLADE AWAITS",
    "JOIN OR BE CONSUMED",
    "TRIGLAVIAN GLORY",
    "ASCEND BEYOND",
]

def create_triglavian_triangle(draw, center, size, color, rotation=0):
    """Draw a Triglavian-style triple triangle symbol"""
    import math
    cx, cy = center
    points = []
    for i in range(3):
        angle = math.radians(rotation + i * 120)
        x = cx + size * math.cos(angle)
        y = cy + size * math.sin(angle)
        points.append((x, y))
    
    # Draw outer triangle
    draw.polygon(points, outline=color, width=3)
    
    # Draw inner inverted triangle
    inner_points = []
    for i in range(3):
        angle = math.radians(rotation + 60 + i * 120)
        x = cx + (size * 0.5) * math.cos(angle)
        y = cy + (size * 0.5) * math.sin(angle)
        inner_points.append((x, y))
    
    draw.polygon(inner_points, outline=color, width=2)
    
    # Center dot
    draw.ellipse([cx-5, cy-5, cx+5, cy+5], fill=color)

def generate_poster(output_path, width=1200, height=1600):
    """Generate a Kybernauts propaganda poster"""
    
    # Select tagline
    tagline = random.choice(TAGLINES)
    
    # Create image with dark gradient background
    img = Image.new('RGB', (width, height), COLORS['void_black'])
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (void to purple)
    for y in range(height):
        ratio = y / height
        r = int(COLORS['void_black'][0] * (1-ratio) + COLORS['deep_purple'][0] * ratio)
        g = int(COLORS['void_black'][1] * (1-ratio) + COLORS['deep_purple'][1] * ratio)
        b = int(COLORS['void_black'][2] * (1-ratio) + COLORS['deep_purple'][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add geometric pattern overlay
    for i in range(0, width, 80):
        alpha = 20
        line_color = (COLORS['purple'][0], COLORS['purple'][1], COLORS['purple'][2])
        draw.line([(i, 0), (i, height)], fill=line_color, width=1)
    
    for i in range(0, height, 80):
        line_color = (COLORS['purple'][0], COLORS['purple'][1], COLORS['purple'][2])
        draw.line([(0, i), (width, i)], fill=line_color, width=1)
    
    # Try to load fonts, fall back to default if not available
    try:
        # Try system fonts
        title_font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 72)
        tagline_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
        url_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 28)
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        tagline_font = title_font
        url_font = title_font
        small_font = title_font
    
    # Draw Triglavian triangle symbol (centerpiece)
    center_x, center_y = width // 2, height // 2 - 100
    create_triglavian_triangle(draw, (center_x, center_y), 200, COLORS['teal'], rotation=0)
    
    # Draw outer glow effect (simulated with multiple triangles)
    for offset in range(1, 4):
        glow_color = (0, 212 - offset*50, 170 - offset*40)
        create_triglavian_triangle(draw, (center_x, center_y), 200 + offset*5, glow_color, rotation=offset*5)
    
    # Title text with glow effect
    title = "KYBERNAUTS"
    title_y = 150
    
    # Glow behind title
    for offset in range(3, 0, -1):
        glow_color = (0, 212 - offset*40, 170 - offset*30)
        draw.text((width//2 + offset, title_y + offset), title, font=title_font, fill=glow_color, anchor="mm")
        draw.text((width//2 - offset, title_y - offset), title, font=title_font, fill=glow_color, anchor="mm")
    
    # Main title
    draw.text((width//2, title_y), title, font=title_font, fill=COLORS['white'], anchor="mm")
    
    # Subtitle
    subtitle = "CLADE"
    draw.text((width//2, title_y + 70), subtitle, font=tagline_font, fill=COLORS['teal'], anchor="mm")
    
    # Tagline (varying)
    tagline_y = height // 2 + 200
    
    # Tagline glow
    for offset in range(2, 0, -1):
        glow = (180, 40, 60) if offset == 1 else (140, 30, 50)
        draw.text((width//2 + offset, tagline_y + offset), tagline, font=tagline_font, fill=glow, anchor="mm")
    
    # Main tagline in crimson
    draw.text((width//2, tagline_y), tagline, font=tagline_font, fill=COLORS['crimson'], anchor="mm")
    
    # Recruitment URL at bottom
    url_y = height - 150
    draw.text((width//2, url_y), "join.kybernauts.today", font=url_font, fill=COLORS['teal'], anchor="mm")
    
    # Add decorative elements - corner accents
    corner_size = 40
    margin = 30
    
    # Top-left corner
    draw.line([(margin, margin), (margin + corner_size, margin)], fill=COLORS['teal'], width=3)
    draw.line([(margin, margin), (margin, margin + corner_size)], fill=COLORS['teal'], width=3)
    
    # Top-right corner
    draw.line([(width - margin - corner_size, margin), (width - margin, margin)], fill=COLORS['teal'], width=3)
    draw.line([(width - margin, margin), (width - margin, margin + corner_size)], fill=COLORS['teal'], width=3)
    
    # Bottom-left corner
    draw.line([(margin, height - margin), (margin + corner_size, height - margin)], fill=COLORS['teal'], width=3)
    draw.line([(margin, height - margin - corner_size), (margin, height - margin)], fill=COLORS['teal'], width=3)
    
    # Bottom-right corner
    draw.line([(width - margin - corner_size, height - margin), (width - margin, height - margin)], fill=COLORS['teal'], width=3)
    draw.line([(width - margin, height - margin - corner_size), (width - margin, height - margin)], fill=COLORS['teal'], width=3)
    
    # Add inner border
    border_margin = 50
    draw.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline=COLORS['teal_dim'], width=2
    )
    
    # Inner crimson accent line
    draw.rectangle(
        [(border_margin + 10, border_margin + 10), (width - border_margin - 10, height - border_margin - 10)],
        outline=COLORS['crimson'], width=1
    )
    
    # Save the image
    img.save(output_path, 'PNG', quality=95)
    
    return {
        'file': output_path,
        'tagline': tagline,
        'dimensions': f'{width}x{height}px'
    }

if __name__ == '__main__':
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'C:/Users/compj/.openclaw/media/kybernauts/propaganda_{timestamp}.png'
    
    result = generate_poster(output_path)
    print(f"Poster generated: {result['file']}")
    print(f"Tagline used: {result['tagline']}")
    print(f"Dimensions: {result['dimensions']}")
