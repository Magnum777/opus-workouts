import json, sys
sys.path.insert(0, '.')
from publisher import create_post

with open('temp_post.html', 'r', encoding='utf-8') as f:
    content = f.read()

title = "How TradeBot Turned $14.80 Into $14,804 in 24 Hours (And What We Learned About AI Cofounder Automation)"

res = create_post('aicofounderstack.com', title, content, status='publish')
print(json.dumps(res, indent=2))

if res.get('ok'):
    with open('last_post_id.txt', 'w') as f:
        f.write(str(res['id']))
    print(f"POST_ID:{res['id']}")
