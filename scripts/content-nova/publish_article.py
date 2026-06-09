import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher import create_post

# Read article content
with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\article.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Strip the H1 heading from content since WordPress will use title
lines = content.split('\n')
if lines[0].startswith('# '):
    content = '\n'.join(lines[1:]).strip()

# Strip the meta description line if present
if content.startswith('**Meta Description:**'):
    content = '\n'.join(content.split('\n')[1:]).strip()

# Convert markdown bold to HTML bold for WP
content = content.replace('**', '<strong>', 1)
# This won't handle all cases well, but let's keep it as markdown for now
# WordPress can handle markdown via Jetpack or plugins

title = "7 AI Business Models Solo Founders Can Start Today"
excerpt = "Discover 7 proven AI business models solo founders can launch in 2026. Low overhead, high margins, and built for the one-person startup."

res = create_post('aicofounderstack.com', title, content, status='publish', excerpt=excerpt)
print(res)
