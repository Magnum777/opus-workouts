from PIL import Image, ImageDraw, ImageFont
import random

# Load logos
corp_logo = Image.open(r'C:\Users\compj\.openclaw\media\inbound\7a0c66f1-e99a-4654-9eeb-630d9845dd34.png')
alliance_logo = Image.open(r'C:\Users\compj\.openclaw\media\inbound\83d47323-e855-4009-8a70-f5490d658f29.png')

# Resize logos for poster
corp_logo = corp_logo.resize((150, 150), Image.Resampling.LANCZOS)
alliance_logo = alliance_logo.resize((150, 150), Image.Resampling.LANCZOS)

# Create background (dark red/black)
width, height = 1080, 1350  # Twitter portrait ratio
background = Image.new('RGB', (width, height), (20, 10, 10))

# Paste logos
background.paste(corp_logo, (30, 30), corp_logo if corp_logo.mode == 'RGBA' else None)
background.paste(alliance_logo, (width - 180, 30), alliance_logo if alliance_logo.mode == 'RGBA' else None)

# Varying taglines and slogans
taglines = [
    'POCHVEN OR BUST',
    'UNDOCK OR DIE', 
    'TRIANGLE DEFENDERS',
    'HUNT OR BE HUNTED',
    'CLAIM YOUR KILLS',
    'BLOOD FOR THE EMPIRE',
    'AMARR STRONGHOLD',
    'FAITH AND FURY'
]

slogans = [
    'The Imperium awaits your service',
    'Join the eternal crusade',
    'Glory through combat',
    'Defend the faithful',
    'Purge the heretics',
    'Rise with the sunrise',
    'Victory or oblivion',
    'The empire strikes back'
]

# Select random variants
tagline = random.choice(taglines)
slogan = random.choice(slogans)

# Draw text
draw = ImageDraw.Draw(background)

# Try to load a bold font, fall back to default
try:
    font_large = ImageFont.truetype('arialbd.ttf', 72)
    font_medium = ImageFont.truetype('arial.ttf', 48)
    font_small = ImageFont.truetype('arial.ttf', 36)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Calculate text positions (centered)
tagline_bbox = draw.textbbox((0, 0), tagline, font=font_large)
tagline_width = tagline_bbox[2] - tagline_bbox[0]
tagline_x = (width - tagline_width) // 2

slogan_bbox = draw.textbbox((0, 0), slogan, font=font_medium)
slogan_width = slogan_bbox[2] - slogan_bbox[0]
slogan_x = (width - slogan_width) // 2

# Draw tagline (gold/yellow)
draw.text((tagline_x, 400), tagline, fill=(255, 215, 0), font=font_large)

# Draw slogan (white)
draw.text((slogan_x, 520), slogan, fill=(255, 255, 255), font=font_medium)

# Draw link (cyan, lower third)
link_text = 'join.kybernauts.today'
link_bbox = draw.textbbox((0, 0), link_text, font=font_medium)
link_width = link_bbox[2] - link_bbox[0]
link_x = (width - link_width) // 2
draw.text((link_x, 900), link_text, fill=(0, 255, 255), font=font_medium)

# Draw hashtag (bottom)
hashtag_text = '#EVEOnline'
hashtag_bbox = draw.textbbox((0, 0), hashtag_text, font=font_small)
hashtag_width = hashtag_bbox[2] - hashtag_bbox[0]
hashtag_x = (width - hashtag_width) // 2
draw.text((hashtag_x, 1050), hashtag_text, fill=(128, 128, 128), font=font_small)

# Save
background.save(r'C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png')
print(f'Poster created: tagline="{tagline}", slogan="{slogan}"')
