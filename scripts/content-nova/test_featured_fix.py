import sys, json
sys.path.insert(0, '.')
import featured_image
from pathlib import Path

# Test 1: Search
img = featured_image.search_unsplash_image('AI automation business')
print('TEST 1 - Search:', json.dumps(img, indent=2))

# Test 2: Download
temp_dir = Path(__file__).parent / 'temp_images'
temp_dir.mkdir(exist_ok=True)
img_path = temp_dir / f"{img['id']}.jpg"

ok = featured_image.download_image(img['url'], str(img_path))
print(f'TEST 2 - Download: {ok}, size: {img_path.stat().st_size if img_path.exists() else 0} bytes')

# Test 3: Upload to aicofounderstack (safe test site)
if ok and img_path.exists():
    result = featured_image.upload_to_wordpress(
        'aicofounderstack.com',
        str(img_path),
        post_id=None,
        alt_text='Test image for AI article'
    )
    print('TEST 3 - Upload:', json.dumps(result, indent=2))
    
    if result.get('ok'):
        # Clean up
        img_path.unlink(missing_ok=True)
        print('Cleaned up temp file. SUCCESS.')
    else:
        print('Upload failed - check credentials')
else:
    print('Download failed, skipping upload test')
