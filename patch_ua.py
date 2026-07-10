import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\publishing')

with open(r'C:\Users\compj\.openclaw\workspace\scripts\publishing\wp_rest_api.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'User-Agent' not in content:
    # Patch _auth function to include User-Agent
    old = "    return {\n        'Authorization': f'Basic {token}',\n        'Accept': 'application/json',\n        'Content-Type': 'application/json'\n    }"
    new = "    return {\n        'Authorization': f'Basic {token}',\n        'Accept': 'application/json',\n        'Content-Type': 'application/json',\n        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'\n    }"
    content = content.replace(old, new)
    
    # Also patch upload_media (no Content-Type header)
    old2 = "    headers.pop('Content-Type', None)"
    new2 = "    headers.pop('Content-Type', None)\n    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'"
    content = content.replace(old2, new2)
    
    with open(r'C:\Users\compj\.openclaw\workspace\scripts\publishing\wp_rest_api.py', 'w') as f:
        f.write(content)
    print("Patched wp_rest_api.py with browser User-Agent")
else:
    print("Already patched or UA present")
