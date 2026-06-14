import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')

from publisher import create_post

# Read the content from file
with open(r'C:\Users\compj\.openclaw\workspace\article.html', 'r', encoding='utf-8') as f:
    content = f.read().strip()

title = 'AI Customer Service Automation: A 2026 Enterprise Playbook'

res = create_post('aibusinessinsider.org', title, content, status='publish')
print('Result:', res)
