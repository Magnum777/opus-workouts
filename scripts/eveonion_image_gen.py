"""
EveOnion Article Image Generator
Uses pollinations.ai (free, no API key needed)

Usage:
  python eveonion_image_gen.py generate "your prompt here"
  python eveonion_image_gen.py article "Headline" "teaser description"
  python eveonion_image_gen.py upload <image_path> <post_id>
"""
import requests, base64, os
from datetime import datetime

WP_URL = 'https://eveonion.com/wp-json/wp/v2'
WP_USER = 'nova'
WP_PASS = 'EVEONION_APP_PASSWORD_REDACTED'
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'media', 'generated')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_image(prompt: str, filename: str = None, width: int = 1024, height: int = 1024, seed: int = None) -> str:
    """Generate an image using pollinations.ai. Returns path to saved file."""
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    params = {}
    if seed is not None:
        params['seed'] = seed
    params['width'] = width
    params['height'] = height

    print(f"Generating image...")
    print(f"Prompt: {prompt[:100]}...")

    r = requests.get(url, params=params, timeout=120, allow_redirects=True)
    if r.status_code != 200 or 'image' not in r.headers.get('content-type', ''):
        raise Exception(f"Generation failed: {r.status_code}")

    if filename is None:
        filename = datetime.now().strftime('%Y%m%d-%H%M%S')
    ext = 'jpg'

    output_path = os.path.join(OUTPUT_DIR, f"{filename}.{ext}")
    with open(output_path, 'wb') as f:
        f.write(r.content)
    print(f"[OK] Saved: {output_path} ({len(r.content)//1024} KB)")
    return output_path


def upload_to_wordpress(image_path: str, post_id: int = None) -> dict:
    """Upload image to WordPress and optionally attach as featured image."""
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    with open(image_path, 'rb') as f:
        image_data = f.read()

    print(f"Uploading {os.path.basename(image_path)} ({len(image_data)//1024} KB)...")

    r = requests.post(
        f'{WP_URL}/media',
        headers=headers,
        files={'file': (os.path.basename(image_path), image_data, 'image/jpeg')},
        data={'title': os.path.basename(image_path), 'alt_text': 'EVE Onion article feature image'}
    )

    if r.status_code not in (200, 201):
        raise Exception(f"Upload failed: {r.status_code} - {r.text[:200]}")

    media = r.json()
    print(f"  Uploaded! Media ID: {media['id']}")
    print(f"  URL: {media['source_url']}")

    if post_id:
        r2 = requests.post(f'{WP_URL}/posts/{post_id}', headers=headers, json={'featured_media': media['id']})
        if r2.status_code == 200:
            print(f"  Attached as featured image to post {post_id}")
        else:
            print(f"  Warning: featured attachment failed: {r2.status_code} - {r2.text[:100]}")

    return media


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python eveonion_image_gen.py generate \"prompt\" [width] [height]")
        print("  python eveonion_image_gen.py article \"Headline\" \"teaser\"")
        print("  python eveonion_image_gen.py upload <image_path> <post_id>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "generate":
        prompt = sys.argv[2] if len(sys.argv) > 2 else "EVE Online spaceship in space"
        w = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
        h = int(sys.argv[4]) if len(sys.argv) > 4 else 628
        path = generate_image(prompt, width=w, height=h)
        print(f"Image: {path}")

    elif cmd == "article":
        title = sys.argv[2] if len(sys.argv) > 2 else "EVE Online News"
        teaser = sys.argv[3] if len(sys.argv) > 3 else ""
        style = "cinematic sci-fi editorial, news feature image, dramatic lighting, space setting, digital art"
        full_prompt = f"{title} {teaser} {style}".strip()[:500]
        path = generate_image(full_prompt, width=1200, height=628)
        print(f"Image: {path}")

    elif cmd == "upload":
        if len(sys.argv) < 4:
            print("Usage: python eveonion_image_gen.py upload <image_path> <post_id>")
            sys.exit(1)
        image_path = sys.argv[2]
        post_id = int(sys.argv[3])
        result = upload_to_wordpress(image_path, post_id)
        print(f"Done! Media ID: {result['id']}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)