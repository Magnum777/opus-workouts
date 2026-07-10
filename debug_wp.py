import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\publishing')
from wp_rest_api import list_posts

posts = list_posts('eveonion.com', per_page=2)
print(f'Found {len(posts)} posts')
for p in posts:
    print(str(p['id']) + ': ' + p['title']['rendered'])
