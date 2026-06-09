#!/usr/bin/env python3
"""Generate Kybernauts propaganda poster with varying content"""

from PIL import Image, ImageDraw, ImageFont
import random
import os

# Paths
CORP_LOGO = r"C:\Users\compj\.openclaw\media\inbound\7a0c66f1-e99a-4654-9eeb-630d9845dd34.png"
ALLIANCE_LOGO = r"C:\Users\compj\.openclaw\media\inbound\83d47323-e855-4009-8a70-f5490d658f29.png"
OUTPUT = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

# Varying taglines
TAGLINES = [
    "POCHVEN OR BUST",
    "UNDOCK OR DIE", 
    "TRIANGLE DEFENDERS",
    "HUNT OR BE HUNTED",
    "CLAIM YOUR KILLS",
    "NULL SEC OR NOTHING",
    "BLOOD FOR THE EMPIRE",
    "SOVEREIGNTY IS WAR",
]

# Varying slogans
SLOGANS = [
    "Join the Kybernauts - Where Capsuleers Become Legends",
    "Elite PvP Corporation Seeking Warriors",
    "The Triangle's Most Feared Hunters",
    "Ruthless. Relentless. Kybernauts.",
    "Your Killboard Ends Here",
    "Fleet Ops Daily - Bring Your Best",
    "Null Sec Veterans - No Rookies",
    "War is Our Profession",
]

# Random selections
tagline = random.choice(TAGLINES)
slogan = random.choice(SLOGANS)

print(f"Selected tagline: {tagline}")
print(f"Selected slogan: {slogan}")

# Create background (1080x1080 for Twitter)
width, height = 1080, 1080
bg_color = (20, 10, 10)  # Dark red/black
img = Image.new('RGB', (width, height), bg_color)
draw = ImageDraw.Draw(img)

# Load logos
try:
    corp_logo = Image.open(CORP_LOGO).convert('RGBA')
    alliance_logo = Image.open(ALLIANCE_LOGO).convert('RGBA')
    
    # Resize logos to fit (keep aspect ratio)
    logo_size = (200, 200)
    corp_logo = corp_logo.resize(logo_size, Image.Resampling.LANCZOS)
    alliance_logo = alliance_logo.resize(logo_size, Image.Resampling.LANCZOS)
    
    # Paste logos: top left and top right
    img.paste(corp_logo, (30, 30), corp_logo)
    img.paste(alliance_logo, (width - 230, 30), alliance_logo)
    
except Exception as e:
    print(f"Error loading logos: {e}")
    # Create placeholder rectangles if logos fail
    draw.rectangle([30, 30, 230, 230], fill=(100, 50, 50))
    draw.rectangle([width-230, 30, width-30, 230], fill=(100, 50, 50))

# Try to load a font, fall back to default
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
        if os.path.exists(fp):
            font_large = ImageFont.truetype(fp, 72)
            font_medium = ImageFont.truetype(fp, 36)
            break
    
    if font_large is None:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        
except Exception as e:
    print(f"Font error: {e}")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()

# Add tagline (centered, upper middle)
tagline_bbox = draw.textbbox((0, 0), tagline, font=font_large)
tagline_width = tagline_bbox[2] - tagline_bbox[0]
tagline_x = (width - tagline_width) // 2
tagline_y = 280

# Draw text with outline effect
for dx in [-2, -1, 0, 1, 2]:
    for dy in [-2, -1, 0, 1, 2]:
        if dx != 0 or dy != 0:
            draw.text((tagline_x + dx, tagline_y + dy), tagline, font=font_large, fill=(0, 0, 0))

draw.text((tagline_x, tagline_y), tagline, font=font_large, fill=(255, 50, 50))

# Add slogan (centered, middle)
slogan_bbox = draw.textbbox((0, 0), slogan, font=font_medium)
slogan_width = slogan_bbox[2] - slogan_bbox[0]
slogan_x = (width - slogan_width) // 2
slogan_y = 500

draw.text((slogan_x, slogan_y), slogan, font=font_medium, fill=(200, 200, 200))

# Add link and hashtag (bottom)
link_text = "join.kybernauts.today"
hashtag_text = "#EVEOnline"

link_bbox = draw.textbbox((0, 0), link_text, font=font_medium)
link_width = link_bbox[2] - link_bbox[0]
link_x = (width - link_width) // 2
link_y = 750

draw.text((link_x, link_y), link_text, font=font_medium, fill=(100, 200, 255))

hashtag_bbox = draw.textbbox((0, 0), hashtag_text, font=font_medium)
hashtag_width = hashtag_bbox[2] - hashtag_bbox[0]
hashtag_x = (width - hashtag_width) // 2
hashtag_y = 820

draw.text((hashtag_x, hashtag_y), hashtag_text, font=font_medium, fill=(150, 150, 255))

# Save
img.save(OUTPUT, 'PNG')
print(f"Poster saved to: {OUTPUT}")
print(f"Dimensions: {width}x{height}")
