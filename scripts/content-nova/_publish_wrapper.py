import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publisher import create_post

site = 'aibusinessinsider.org'
title = "AI Data Privacy: The Enterprise Threat No One's Talking About"

with open(r'C:\Users\compj\.openclaw\workspace\articles\aibusinessinsider-ai-data-privacy.md', encoding='utf-8') as f:
    content = f.read()

# Strip the SEO Title / Meta Description lines from bottom if present
lines = content.splitlines()
while lines and (
    lines[-1].strip().startswith('**SEO Title') or
    lines[-1].strip().startswith('**Meta Description') or
    lines[-1].strip() == '---' or
    lines[-1].strip() == ''
):
    lines.pop()

content = '\n'.join(lines)

res = create_post(site, title, content, status='publish')
print(res)
