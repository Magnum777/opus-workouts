import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')

# Read the content from file
with open(r'C:\Users\compj\.openclaw\workspace\article.html', 'r', encoding='utf-8') as f:
    content = f.read().strip()

title = 'AI Customer Service Automation: A 2026 Enterprise Playbook'

# Now call publisher
from publisher import main
import argparse

# Build args like: publisher.py aibusinessinsider.org create --title "..." --content "..." --status publish
sys.argv = [
    'publisher.py',
    'aibusinessinsider.org',
    'create',
    '--title', title,
    '--content', content,
    '--status', 'publish'
]

try:
    main()
except SystemExit as e:
    print(f'Exit code: {e.code}')
