#!/usr/bin/env python3
"""Add URL overlay to Kybernauts propaganda images"""
from PIL import Image, ImageDraw, ImageFont
import os

INPUT_DIR = "data/kybernauts/propaganda"
OUTPUT_DIR = "data/kybernauts/propaganda/with_url"

def add_url_to_image(input_path, output_path):
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    
    # Try to load a font, fall back to default
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 36)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
        except:
            font = ImageFont.load_default()
    
    url_text = "join.kybernauts.today"
    
    # Calculate text size for centering
    bbox = draw.textbbox((0, 0), url_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position: bottom center with padding
    x = (width - text_width) // 2
    y = height - text_height - 40
    
    # Draw semi-transparent dark background bar for contrast
    bar_padding = 15
    draw.rectangle(
        [(x - bar_padding, y - bar_padding//2), 
         (x + text_width + bar_padding, y + text_height + bar_padding//2)],
        fill=(0, 0, 0, 180)
    )
    
    # Draw URL text in bright teal/cyan
    draw.text((x, y), url_text, font=font, fill=(0, 212, 170))
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"Saved: {output_path}")

# Process all 6 images
images = [
    ("01_liberate.png", "01_liberate_with_url.png"),
    ("02_p92.png", "02_p92_with_url.png"),
    ("03_kkp07.png", "03_kkp07_with_url.png"),
    ("04_chatgpt.png", "04_chatgpt_with_url.png"),
    ("05_p09.png", "05_p09_with_url.png"),
    ("06_p93.png", "06_p93_with_url.png"),
]

for input_name, output_name in images:
    input_path = os.path.join(INPUT_DIR, input_name)
    output_path = os.path.join(OUTPUT_DIR, output_name)
    if os.path.exists(input_path):
        add_url_to_image(input_path, output_path)
    else:
        print(f"NOT FOUND: {input_path}")

print("\nDone. Updated images saved to:", OUTPUT_DIR)
