#!/usr/bin/env python3
"""EVE Online Kybernauts Propaganda Poster Generator"""

from PIL import Image, ImageDraw, ImageFont
import random

# Varying taglines and slogans for variety
TAGLINES = [
    "POCHVEN OR BUST",
    "UNDOCK OR DIE", 
    "TRIANGLE DEFENDERS",
    "HUNT OR BE HUNTED",
    "CLAIM YOUR KILLS",
    "BLOOD FOR THE EMPIRE",
    "NULL SEC OR NOTHING"
]

SLOGANS = [
    "Join the fiercest hunters in New Eden",
    "Where capsuleers become legends",
    "Victory is the only option",
    "Together we conquer the stars",
    "Your war begins here",
    "Forge your legacy in fire",
    "The galaxy belongs to the bold"
]

# Paths
CORP_LOGO = r"C:\Users\compj\.openclaw\media\inbound\7a0c66f1-e99a-4654-9eeb-630d9845dd34.png"
ALLIANCE_LOGO = r"C:\Users\compj\.openclaw\media\inbound\83d47323-e855-4009-8a70-f5490d658f29.png"
OUTPUT = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

# Select random variants
tagline = random.choice(TAGLINES)
slogan = random.choice(SLOGANS)

print(f"Creating poster with:")
print(f"  Tagline: {tagline}")
print(f"  Slogan: {slogan}")

# Create background (1080x1350 - Twitter portrait ratio)
width, height = 1080, 1350
bg_color = (20, 10, 10)  # Dark red/black
img = Image.new('RGB', (width, height), bg_color)
draw = ImageDraw.Draw(img)

# Load logos
try:
    corp_logo = Image.open(CORP_LOGO).convert('RGBA')
    alliance_logo = Image.open(ALLIANCE_LOGO).convert('RGBA')
    
    # Resize logos to fit (maintain aspect ratio)
    logo_size = (200, 200)
    corp_logo = corp_logo.resize(logo_size, Image.Resampling.LANCZOS)
    alliance_logo = alliance_logo.resize(logo_size, Image.Resampling.LANCZOS)
    
    # Paste logos
    img.paste(corp_logo, (50, 50), corp_logo)  # Top left
    img.paste(alliance_logo, (width - 250, 50), alliance_logo)  # Top right
    
    print("  Logos placed successfully")
except Exception as e:
    print(f"  Warning: Logo loading issue: {e}")
    # Continue without logos if needed

# Try to load a font (use default if not available)
try:
    # Try common Windows fonts
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\verdanab.ttf",
    ]
    font_large = None
    font_medium = None
    
    for fp in font_paths:
        try:
            font_large = ImageFont.truetype(fp, 72)
            font_medium = ImageFont.truetype(fp, 36)
            break
        except:
            continue
    
    if not font_large:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        
    print("  Fonts loaded")
except Exception as e:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    print(f"  Using default font: {e}")

# Add tagline (centered, large)
tagline_bbox = draw.textbbox((0, 0), tagline, font=font_large)
tagline_width = tagline_bbox[2] - tagline_bbox[0]
tagline_x = (width - tagline_width) // 2
tagline_y = 350

# Draw text with shadow effect for visibility
shadow_offset = 3
draw.text((tagline_x + shadow_offset, tagline_y + shadow_offset), tagline, fill=(0, 0, 0), font=font_large)
draw.text((tagline_x - shadow_offset, tagline_y - shadow_offset), tagline, fill=(0, 0, 0), font=font_large)
draw.text((tagline_x, tagline_y), tagline, fill=(255, 50, 50), font=font_large)  # Bright red

print(f"  Tagline added: {tagline}")

# Add slogan (centered, medium)
slogan_bbox = draw.textbbox((0, 0), slogan, font=font_medium)
slogan_width = slogan_bbox[2] - slogan_bbox[0]
slogan_x = (width - slogan_width) // 2
slogan_y = 450

draw.text((slogan_x, slogan_y), slogan, fill=(200, 200, 200), font=font_medium)
print(f"  Slogan added: {slogan}")

# Add link (near bottom)
link_text = "join.kybernauts.today"
link_bbox = draw.textbbox((0, 0), link_text, font=font_medium)
link_width = link_bbox[2] - link_bbox[0]
link_x = (width - link_width) // 2
link_y = height - 200

draw.text((link_x, link_y), link_text, fill=(100, 200, 255), font=font_medium)  # Light blue
print("  Link added: join.kybernauts.today")

# Add hashtag (bottom)
hashtag_text = "#EVEOnline"
hashtag_bbox = draw.textbbox((0, 0), hashtag_text, font=font_medium)
hashtag_width = hashtag_bbox[2] - hashtag_bbox[0]
hashtag_x = (width - hashtag_width) // 2
hashtag_y = height - 140

draw.text((hashtag_x, hashtag_y), hashtag_text, fill=(150, 150, 255), font=font_medium)  # Light purple
print("  Hashtag added: #EVEOnline")

# Add decorative elements (battle damage effect)
import random
for _ in range(50):
    x = random.randint(0, width)
    y = random.randint(0, height)
    size = random.randint(1, 3)
    brightness = random.randint(100, 255)
    draw.rectangle([x, y, x+size, y+size], fill=(brightness, brightness//3, brightness//3))

print("  Decorative effects added")

# Save
img.save(OUTPUT, 'PNG', quality=95)
print(f"\n[OK] Poster saved to: {OUTPUT}")
print(f"  Dimensions: {width}x{height}")
