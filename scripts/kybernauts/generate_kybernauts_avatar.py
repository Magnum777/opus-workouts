#!/usr/bin/env python3
"""Generate Kybernauts Nova Avatar using Replicate API"""
import os
import sys
import requests
from pathlib import Path

API_KEY = "r8_aazLeCLHukkf8grYpSCssQjsdpR8BV62pPGZJ"
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"

def generate_image(prompt: str, output_filename: str):
    """Generate image using FLUX.1-schnell via Replicate"""
    
    model_version = "black-forest-labs/flux-schnell"
    
    payload = {
        "version": model_version,
        "input": {
            "prompt": prompt,
            "aspect_ratio": "3:2",
            "num_outputs": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    
    print(f"Generating Kybernauts avatar...")
    
    response = requests.post(REPLICATE_API_URL, json=payload, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    
    if "output" in data:
        image_url = data["output"][0] if isinstance(data["output"], list) else data["output"]
    else:
        print("No output in response")
        print(data)
        return None
    
    # Download
    img_response = requests.get(image_url)
    filepath = Path(__file__).parent / output_filename
    filepath.write_bytes(img_response.content)
    
    print(f"Image saved to: {filepath}")
    return str(filepath)

if __name__ == "__main__":
    prompt = """A full-body portrait of an anthropomorphic cyberpunk raccoon character sitting at a futuristic command desk in a high-tech control center. The raccoon has charcoal fur, glowing teal eyes, and wears a dark tactical jacket with glowing cyan accents and holographic panels. The character looks confident and focused at a console with multiple holographic screens showing data streams and ship schematics. On the wall behind the desk is the Kybernauts Clade logo - a Triglavian Collective symbol with three interlocking triangles and angular Triglavian script. The room has a dark cyberpunk aesthetic with neon blue and purple lighting, glowing circuit patterns on surfaces. The raccoon's bushy tail is visible behind the chair. Style is detailed digital art with synthwave/cyberpunk influences."""
    
    generate_image(prompt, "nova-kybernauts-command-2026.webp")
