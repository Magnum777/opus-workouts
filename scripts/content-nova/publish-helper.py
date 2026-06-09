import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher import create_post

site = 'aitoolalliance.com'
title = "The Best AI Code Assistants in 2026: A Developer's Guide"
status = 'publish'

with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\article-draft.md', 'r', encoding='utf-8') as f:
    content = f.read()

excerpt = "Compare GitHub Copilot, Cursor, and Claude Code in 2026. Discover which AI code assistant fits your workflow, pricing, features, and productivity data."

res = create_post(site, title, content, status, excerpt=excerpt)
print(res)
