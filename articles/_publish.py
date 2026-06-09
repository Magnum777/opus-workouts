import sys, re, html
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
import publisher

with open(r'C:\Users\compj\.openclaw\workspace\articles\aicofounderstack-solopreneur-ai-toolkit.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

# Extract title
m = re.search(r'<h1>(.*?)</h1>', html_text, re.DOTALL)
title = m.group(1).strip() if m else 'The Solopreneur AI Toolkit: Build a One-Person Unicorn in 2026'

# Keep HTML content for WordPress (WP handles it fine)
content = html_text
# Remove h1 since WP uses its own title
content = re.sub(r'<h1>.*?</h1>\s*', '', content, flags=re.DOTALL)
# Remove SEO comment block
content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
content = content.strip()

excerpt = 'The 2026 solopreneur AI toolkit that replaces a team. 7 tools, real costs, and a rollout plan to scale without hiring.'

print(f'Title: {title}')
print(f'Content length: {len(content)} chars')
print('Publishing to aicofounderstack.com ...')

res = publisher.create_post('aicofounderstack.com', title, content, status='publish', excerpt=excerpt)
print(res)
