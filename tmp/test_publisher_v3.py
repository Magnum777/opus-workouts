import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher_v3 import list_posts

posts = list_posts('aicofounderstack.com', per_page=2)
if isinstance(posts, list):
    for p in posts:
        title = p['title']['rendered'][:50]
        print(f"ID:{p['id']} | {title} | {p['status']}")
else:
    print(f"Error: {posts}")
