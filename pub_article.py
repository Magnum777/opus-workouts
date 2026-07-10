import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\publishing')
from wp_rest_api import create_post, update_post

with open(r'C:\Users\compj\.openclaw\workspace\tmp_article.html', 'r', encoding='utf-8') as f:
    content = f.read()

title = "New Breach Control Module Leaves EVE Players Asking What a Breacher Pod Is"
pid = create_post('eveonion.com', title, content, 'publish')
print(f'Post ID: {pid}')
