#!/usr/bin/env python3
"""
Content-Nova Featured Image Uploader
Fetches relevant stock images from Unsplash and uploads them as WordPress featured images.
"""

import requests
import json
import os
import sys
import base64
from pathlib import Path
from urllib.parse import quote

# WordPress site configs (match publisher.py)
SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com/wp-json/wp/v2',
        'user': 'aitoolalliance_u6cbhe',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>,
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
        'user': 'nova.cofounder@gmail.com',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>,
    },
    'aicofounderstack.com': {
        'url': 'https://aicofounderstack.com/wp-json/wp/v2',
        'user': 'nova',
        'pass': 'DUau yrXK 1X8k O6eH YL5v qKID',
    }
}

# Unsplash API (free tier: 50 requests/hour)
# Get a real key at https://unsplash.com/developers
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()

# Fallback: curated list of reliable direct Unsplash image URLs (no API key needed)
# These are permanent CDN links to high-quality AI/business/tech images
FALLBACK_IMAGES = [
    {"url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop&q=80", "id": "ai-neural-blue", "author": "Google DeepMind"},
    {"url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&h=630&fit=crop&q=80", "id": "ai-robot-hand", "author": "Maxime Valcarce"},
    {"url": "https://images.unsplash.com/photo-1535378437327-b7128d8e1d17?w=1200&h=630&fit=crop&q=80", "id": "robot-humanoid", "author": "Andrea De Santis"},
    {"url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&h=630&fit=crop&q=80", "id": "robot-head", "author": "Possessed Photography"},
    {"url": "https://images.unsplash.com/photo-1620121692029-d088224ddc74?w=1200&h=630&fit=crop&q=80", "id": "ai-glow-abstract", "author": "Richard Horvath"},
    {"url": "https://images.unsplash.com/photo-1674027398737-954a76b02426?w=1200&h=630&fit=crop&q=80", "id": "ai-data-stream", "author": "Mohamed Nohassi"},
    {"url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&h=630&fit=crop&q=80", "id": "tech-earth-network", "author": "NASA"},
    {"url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200&h=630&fit=crop&q=80", "id": "cyber-security-dark", "author": "FlyD"},
]

def _auth(user, password):
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'User-Agent': 'ContentNovaBot/2.0'
    }

def search_unsplash_image(query):
    """Search Unsplash for a relevant image. Returns download URL or None."""
    try:
        # Try Unsplash API if we have a real key
        if UNSPLASH_ACCESS_KEY and len(UNSPLASH_ACCESS_KEY) > 10:
            url = f"https://api.unsplash.com/search/photos?query={quote(query)}&per_page=5&orientation=landscape"
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    img = results[0]
                    return {
                        "url": img["urls"]["regular"],
                        "thumb": img["urls"]["small"],
                        "author": img["user"]["name"],
                        "author_url": img["user"]["links"]["html"],
                        "id": img["id"]
                    }
            print(f"Unsplash API failed ({r.status_code}), falling back to direct images...")
        
        # No API key or API failed - use fallback pool with rotation based on query hash
        import hashlib
        h = int(hashlib.md5(query.encode()).hexdigest(), 16)
        idx = h % len(FALLBACK_IMAGES)
        img = FALLBACK_IMAGES[idx]
        
        # Also try the next one if we have room
        next_idx = (idx + 1) % len(FALLBACK_IMAGES)
        
        # Verify the image is accessible
        for try_img in [img, FALLBACK_IMAGES[next_idx]]:
            test = requests.head(try_img["url"], timeout=10, allow_redirects=True)
            if test.status_code in (200, 301, 302):
                return {
                    "url": try_img["url"],
                    "thumb": try_img["url"],
                    "author": try_img["author"],
                    "author_url": "https://unsplash.com",
                    "id": try_img["id"]
                }
        
        return None
        
    except Exception as e:
        print(f"Unsplash error: {e}")
        # Last resort - pick deterministically from the pool
        import hashlib
        h = int(hashlib.md5(query.encode()).hexdigest(), 16)
        img = FALLBACK_IMAGES[h % len(FALLBACK_IMAGES)]
        return {
            "url": img["url"],
            "thumb": img["url"],
            "author": img["author"],
            "author_url": "https://unsplash.com",
            "id": img["id"]
        }

def download_image(image_url, save_path):
    """Download image to local path."""
    try:
        r = requests.get(image_url, timeout=15, stream=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"Download error: {e}")
        return False

def upload_to_wordpress(site_key, image_path, post_id=None, alt_text=""):
    """
    Upload image to WordPress media library.
    If post_id provided, sets as featured image.
    Returns media ID or error dict.
    """
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    
    headers = _auth(site['user'], site['pass'])
    # Remove Content-Type - requests handles multipart
    upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
    
    url = f"{site['url']}/media"
    
    filename = os.path.basename(image_path)
    mime_type = "image/jpeg" if filename.endswith('.jpg') or filename.endswith('.jpeg') else "image/png"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (filename, f, mime_type)}
            data = {'alt_text': alt_text}
            if post_id:
                data['post'] = post_id
            
            r = requests.post(url, headers=upload_headers, files=files, data=data, timeout=60)
        
        if r.status_code in (200, 201):
            res = r.json()
            return {'ok': True, 'id': res.get('id'), 'url': res.get('source_url'), 'link': res.get('link')}
        
        return {'error': f'HTTP {r.status_code}', 'detail': r.text[:500]}
        
    except Exception as e:
        return {'error': str(e)}

def set_featured_image(site_key, post_id, media_id):
    """Set featured image on a post."""
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    
    headers = _auth(site['user'], site['pass'])
    headers['Content-Type'] = 'application/json'
    url = f"{site['url']}/posts/{post_id}"
    
    r = requests.post(url, headers=headers, json={'featured_media': media_id}, timeout=30)
    
    if r.status_code in (200, 201):
        return {'ok': True}
    return {'error': f'HTTP {r.status_code}', 'detail': r.text[:500]}

def add_featured_image(site_key, post_id, topic, alt_text=""):
    """
    Full pipeline: search image, download, upload, attach.
    Returns result dict.
    """
    print(f"Finding featured image for: {topic}")
    
    # Search for image
    img_info = search_unsplash_image(topic)
    
    if not img_info:
        print("No image found via Unsplash. Trying generic AI-related image...")
        img_info = search_unsplash_image("artificial intelligence technology")
    
    if not img_info:
        return {'error': 'Could not find suitable image'}
    
    print(f"Found image by {img_info['author']} on Unsplash")
    
    # Download to temp
    temp_dir = Path(os.path.dirname(__file__)) / "temp_images"
    temp_dir.mkdir(exist_ok=True)
    img_path = temp_dir / f"{img_info['id']}.jpg"
    
    if not download_image(img_info['url'], str(img_path)):
        return {'error': 'Failed to download image'}
    
    print(f"Downloaded: {img_path}")
    
    # Upload to WordPress
    upload_result = upload_to_wordpress(site_key, str(img_path), post_id=post_id, alt_text=alt_text or topic)
    
    if not upload_result.get('ok'):
        return upload_result
    
    media_id = upload_result['id']
    print(f"Uploaded to WordPress media ID: {media_id}")
    
    # Set as featured
    featured_result = set_featured_image(site_key, post_id, media_id)
    
    if featured_result.get('ok'):
        print(f"Featured image set on post {post_id}")
        # Clean up temp file
        img_path.unlink(missing_ok=True)
        return {
            'ok': True,
            'media_id': media_id,
            'image_url': upload_result['url'],
            'author': img_info['author'],
            'author_url': img_info['author_url']
        }
    
    return featured_result

def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print("Usage: python featured_image.py <site> <post_id> <topic> [alt_text]")
        print("Example: python featured_image.py aitoolalliance.com 187 'AI productivity tools'")
        sys.exit(1)
    
    site = sys.argv[1]
    post_id = int(sys.argv[2])
    topic = sys.argv[3]
    alt_text = sys.argv[4] if len(sys.argv) > 4 else ""
    
    result = add_featured_image(site, post_id, topic, alt_text)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
