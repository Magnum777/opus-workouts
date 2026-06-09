"""
Kybernauts Clade Propaganda Poster Generator
Creates stylized recruitment/propaganda posters for EVE Online's Triglavian-aligned alliance
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
from datetime import datetime

# Color palette - Triglavian/Kybernauts theme (dark purple, bio-luminescent teal, void black)
TRIGLAVIAN_PURPLE = (45, 20, 60)
BIO_TEAL = (0, 255, 200)
VOID_BLACK = (10, 5, 15)
ACCENT_RED = (200, 50, 80)
GOLD = (255, 200, 100)

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

def draw_triglavian_symbol(draw, center_x, center_y, size):
    """Draw a stylized Triglavian triple-triangle symbol"""
    # Three overlapping triangles representing the Clades
    triangle_size = size
    
    # Top triangle
    top_points = [
        (center_x, center_y - triangle_size),
        (center_x - triangle_size * 0.866, center_y + triangle_size * 0.5),
        (center_x + triangle_size * 0.866, center_y + triangle_size * 0.5)
    ]
    
    # Draw with glow effect
    for i in range(3, 0, -1):
        glow_color = (0, 255 - i*50, 200 - i*40)
        draw.polygon([
            (p[0], p[1] - i*2) for p in top_points
        ], outline=glow_color, width=2)
    
    draw.polygon(top_points, outline=BIO_TEAL, fill=None, width=3)
    
    # Add smaller inner triangles
    inner_size = triangle_size * 0.4
    inner_points = [
        (center_x, center_y - inner_size),
        (center_x - inner_size * 0.866, center_y + inner_size * 0.5),
        (center_x + inner_size * 0.866, center_y + inner_size * 0.5)
    ]
    draw.polygon(inner_points, outline=ACCENT_RED, fill=None, width=2)

def add_noise_texture(img, intensity=20):
    """Add subtle noise/grain for that propaganda poster feel"""
    import random
    pixels = img.load()
    width, height = img.size
    
    for i in range(0, width, 2):
        for j in range(0, height, 2):
            r, g, b = pixels[i, j]
            noise = random.randint(-intensity, intensity)
            pixels[i, j] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
    
    return img

def get_random_tagline():
    """Return a random propaganda tagline"""
    taglines = [
        "THE FLOW ENLIGHTENS",
        "JOIN THE CLADE",
        "BEYOND THE VEIL",
        "PROVING GROUND AWAITS",
        "ASCEND THROUGH CONFLICT",
        "THE COLLECTIVE CALLS",
        "FORWARD TO POCHVEN",
        "EMBRACE THE TRANSFORMATION",
        "KIMOTOROS GUIDES",
        "PERUN CLADE PREVAILS",
        "SVRABA CLADE ENDURES",
        "VELES CLADE DISCERNS",
        "PROVE YOUR WORTH",
        "BECOME IMMORTAL",
        "THE ABYSS CLAIMS ALL",
        "TECHNOLOGY IS SALVATION",
    ]
    return random.choice(taglines)

def create_propaganda_poster(output_path, tagline=None):
    """Generate a Kybernauts Clade propaganda poster"""
    width, height = 1200, 1600
    
    if tagline is None:
        tagline = get_random_tagline()
    
    # Create gradient background (void-like)
    img = create_gradient_background(width, height, VOID_BLACK, TRIGLAVIAN_PURPLE)
    draw = ImageDraw.Draw(img)
    
    # Add some Triglavian-style geometric patterns
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(50, 200)
        opacity = random.randint(20, 60)
        
        # Draw faint geometric shapes
        shape_type = random.choice(['circle', 'triangle', 'line'])
        if shape_type == 'circle':
            draw.ellipse([x, y, x+size, y+size], outline=(0, 255, 200, opacity), width=1)
        elif shape_type == 'line':
            angle = random.uniform(0, 3.14159 * 2)
            end_x = x + int(size * 0.5 * random.uniform(-1, 1))
            end_y = y + int(size * 0.5 * random.uniform(-1, 1))
            draw.line([(x, y), (end_x, end_y)], fill=(0, 255, 200, opacity), width=1)
    
    # Draw central Triglavian symbol
    draw_triglavian_symbol(draw, width // 2, height // 3, 200)
    
    # Try to load fonts, fall back to defaults if not available
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 100)
        subtitle_font = ImageFont.truetype("arial.ttf", 48)
        body_font = ImageFont.truetype("arial.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw main title with glow effect
    title = "KYBERNAUTS"
    title_y = height // 2 + 50
    
    # Glow effect
    for offset in range(10, 0, -2):
        alpha = int(50 / offset)
        glow_color = (0, 255 - alpha*5, 200 - alpha*5)
        draw.text((width//2, title_y), title, font=title_font, fill=glow_color, anchor="mm")
    
    # Main title
    draw.text((width//2, title_y), title, font=title_font, fill=BIO_TEAL, anchor="mm")
    
    # Subtitle
    subtitle_y = title_y + 90
    draw.text((width//2, subtitle_y), "CLADE", font=subtitle_font, fill=GOLD, anchor="mm")
    
    # Tagline with decorative brackets
    tagline_y = subtitle_y + 120
    tagline_text = f"◄ {tagline} ►"
    draw.text((width//2, tagline_y), tagline_text, font=body_font, fill=ACCENT_RED, anchor="mm")
    
    # Horizontal divider
    divider_y = tagline_y + 80
    draw.line([(width//4, divider_y), (width*3//4, divider_y)], fill=BIO_TEAL, width=2)
    
    # Recruitment text
    recruit_y = divider_y + 60
    draw.text((width//2, recruit_y), "POCHVEN AWAITS", font=body_font, fill=BIO_TEAL, anchor="mm")
    
    # URL at bottom
    url_y = height - 100
    draw.text((width//2, url_y), "join.kybernauts.today", font=small_font, fill=GOLD, anchor="mm")
    
    # Add subtle border
    border_width = 20
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline=BIO_TEAL, width=3)
    
    # Inner border
    draw.rectangle([border_width+5, border_width+5, width-border_width-5, height-border_width-5], 
                   outline=ACCENT_RED, width=1)
    
    # Save the poster
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    img.save(output_path, quality=95)
    
    return output_path, tagline

if __name__ == "__main__":
    output_dir = "media/kybernauts"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/propaganda_{timestamp}.png"
    
    path, tagline = create_propaganda_poster(output_path)
    print(f"Created: {path}")
    print(f"Tagline: {tagline}")
