import sys, re, html
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')
from publisher import create_post

with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\draft_aicofounderstack.md', 'r', encoding='utf-8') as f:
    raw = f.read()

# Split title (first line) and body
lines = raw.split('\n')
title = lines[0].lstrip('# ').strip()
body_lines = lines[1:]

# Convert markdown to basic HTML for WordPress
def md_to_html(lines):
    out = []
    in_list = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if in_list:
                out.append('</ul>')
                in_list = False
            i += 1
            continue

        if line.startswith('## '):
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<h2>{html.escape(line[3:])}</h2>')
            i += 1
            continue

        if line.startswith('### '):
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<h3>{html.escape(line[4:])}</h3>')
            i += 1
            continue

        if line.startswith('- '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            item = html.escape(line[2:])
            # Handle bold inside list items
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            out.append(f'<li>{item}</li>')
            i += 1
            continue

        # Regular paragraph — handle bold
        if in_list:
            out.append('</ul>')
            in_list = False
        para = html.escape(line)
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
        out.append(f'<p>{para}</p>')
        i += 1

    if in_list:
        out.append('</ul>')
    return '\n'.join(out)

body = md_to_html(body_lines)

excerpt = 'AI marketing automation saves solopreneurs 6+ hours per week. Discover the 5 pillars every solo founder needs to scale without hiring a team.'

res = create_post('aicofounderstack.com', title, body, status='publish', excerpt=excerpt)
print(res)
