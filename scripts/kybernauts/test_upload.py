import subprocess, json, os

API_KEY = 'UPLOADPOST_API_KEY_REDACTED'

image_path = 'C:/Users/compj/.openclaw/workspace/data/kybernauts/propaganda/with_url/01_liberate_with_url.png'
text = 'Test: The stars belong to the Clade. http://join.kybernauts.today #EVEOnline #Pochven'

# Verify image exists
print(f'Image exists: {os.path.exists(image_path)}')

cmd = [
    'curl', '-s', '-X', 'POST',
    'https://api.upload-post.com/api/upload_photos',
    '-H', f'Authorization: Apikey {API_KEY}',
    '-F', 'user=Kybernauts',
    '-F', 'platform[]=x',
    '-F', f'photos[]={image_path}',
    '-F', f'title={text}',
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(f'Exit code: {result.returncode}')
print(f'stdout: {result.stdout[:800]}')

try:
    data = json.loads(result.stdout)
    print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print(f'JSON parse error: {e}')
