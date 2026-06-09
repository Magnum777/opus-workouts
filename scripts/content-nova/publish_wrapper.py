import subprocess
import sys

with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\article_tmp.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract title from H1 tag
import re
title_match = re.search(r'<h1>(.*?)</h1>', content)
title = title_match.group(1) if title_match else 'Enterprise AI ROI: 5 Case Studies With Real Numbers'

# Strip the H1 from content since WordPress will use the title field
content_body = re.sub(r'<h1>.*?</h1>\s*', '', content, count=1)

# Build command
cmd = [
    sys.executable,
    r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher.py',
    'aibusinessinsider.org',
    'create',
    '--title', title,
    '--content', content_body,
    '--status', 'publish'
]

print(f"Publishing: {title}")
print(f"Content length: {len(content_body)} chars")
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
