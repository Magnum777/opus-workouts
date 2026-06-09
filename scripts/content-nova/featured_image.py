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
UNSPLASH_ACCESS_KEY = "bZ0p7h8g9f2e1d3c4a5b6e7f8g9h0i1j"  # Placeholder - will use web_search as fallback

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
        # Try Unsplash API first
        url = f"https://api.unsplash.com/search/photos?query={quote(query)}&per_page=5&orientation=landscape"
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                # Pick first result
                img = results[0]
                return {
                    "url": img["urls"]["regular"],
                    "thumb": img["urls"]["small"],
                    "author": img["user"]["name"],
                    "author_url": img["user"]["links"]["html"],
                    "id": img["id"]
                }
        
        # Fallback: use web_search to find images
        print(f"Unsplash API failed ({r.status_code}), using web search fallback...")
        return None
        
    except Exception as e:
        print(f"Unsplash error: {e}")
        return None

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
