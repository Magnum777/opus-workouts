import sys, json
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher import create_post

with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\article-draft.md', 'r', encoding='utf-8') as f:
    content = f.read()

title = "Healthcare AI in 2026: The Enterprise ROI Reality"
excerpt = "Healthcare AI adoption hits 70% in 2026 with measurable ROI. Discover where enterprises are seeing 200-400% returns and what leaders should do now."

res = create_post('aibusinessinsider.org', title, content, status='publish', excerpt=excerpt)
print(json.dumps(res, indent=2))
