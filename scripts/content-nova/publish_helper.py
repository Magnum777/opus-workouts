import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher import create_post

# Read the draft
draft_path = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\drafts\ai-tools-one-person-companies.md'
with open(draft_path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Extract title from first line
lines = raw.splitlines()
title_line = lines[0].strip()
title = title_line.replace('Title:', '').strip()

# Find where body starts (after meta description separator)
body_start = 0
for i, line in enumerate(lines):
    if line.strip() == '---' and i > 0:
        body_start = i + 1
        break

# Also skip a second --- if present
if body_start < len(lines) and lines[body_start].strip() == '---':
    body_start += 1

body = '\n'.join(lines[body_start:]).strip()

# Publish
result = create_post('aicofounderstack.com', title, body, status='publish')
print(result)
