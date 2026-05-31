#!/usr/bin/env python3
"""Convert tradebot_guide.md to a styled PDF."""
import markdown, os, subprocess, sys

MD_FILE = "C:\\Users\\compj\\.openclaw\\workspace\\output\\tradebot_guide.md"
PDF_FILE = "C:\\Users\\compj\\.openclaw\\workspace\\output\\solana_tradebot_guide.pdf"

# Read markdown
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert to HTML
html_body = markdown.markdown(md_text, extensions=['extra', 'codehilite', 'tables', 'fenced_code'])

# Wrap in a styled document
html_doc = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>How to Build a Solana Memecoin Trading Bot</title>
<style>
@page {{
    size: letter;
    margin: 1in;
}}
body {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}}
h1 {{
    font-size: 24pt;
    color: #1a1a2e;
    border-bottom: 3px solid #e94560;
    padding-bottom: 0.3em;
    margin-top: 1.5em;
    page-break-before: always;
}}
h1:first-of-type {{
    page-break-before: avoid;
    margin-top: 0;
}}
h2 {{
    font-size: 16pt;
    color: #16213e;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.2em;
    margin-top: 1.2em;
}}
h3 {{
    font-size: 13pt;
    color: #0f3460;
    margin-top: 1em;
}}
code {{
    font-family: "Consolas", "Monaco", monospace;
    background: #f4f4f4;
    padding: 0.1em 0.3em;
    border-radius: 3px;
    font-size: 10pt;
}}
pre {{
    background: #1a1a2e;
    color: #eee;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.4;
    page-break-inside: avoid;
}}
pre code {{
    background: transparent;
    color: #eee;
    padding: 0;
}}
blockquote {{
    border-left: 4px solid #e94560;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #fafafa;
    font-style: italic;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}}
th {{
    background: #16213e;
    color: white;
}}
tr:nth-child(even) {{
    background: #f9f9f9;
}}
strong {{
    color: #e94560;
}}
a {{
    color: #0f3460;
    text-decoration: none;
}}
hr {{
    border: none;
    border-top: 2px solid #e94560;
    margin: 2em 0;
}}
ul, ol {{
    margin: 0.5em 0;
    padding-left: 1.5em;
}}
li {{
    margin: 0.3em 0;
}}
.cover {{
    text-align: center;
    padding: 3em 1em;
    page-break-after: always;
}}
.cover h1 {{
    font-size: 32pt;
    border: none;
    color: #1a1a2e;
    margin-bottom: 0.5em;
}}
.cover .subtitle {{
    font-size: 14pt;
    color: #666;
    margin-bottom: 2em;
}}
.cover .meta {{
    font-size: 11pt;
    color: #888;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>'''

# Save HTML temp file
html_path = MD_FILE.replace('.md', '.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_doc)

# Convert to PDF using wkhtmltopdf
wkhtmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
if not os.path.exists(wkhtmltopdf):
    # Try alternate path
    wkhtmltopdf = "wkhtmltopdf"

cmd = [
    wkhtmltopdf,
    '--page-size', 'Letter',
    '--margin-top', '0.75in',
    '--margin-bottom', '0.75in',
    '--margin-left', '0.75in',
    '--margin-right', '0.75in',
    '--enable-local-file-access',
    '--footer-center', '[page] / [topage]',
    '--footer-font-size', '8',
    html_path,
    PDF_FILE
]

print("Converting to PDF...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    size_kb = os.path.getsize(PDF_FILE) / 1024
    print(f"PDF created: {PDF_FILE} ({size_kb:.1f} KB)")
    # Clean up HTML
    os.remove(html_path)
else:
    print(f"Error: {result.stderr}")
    sys.exit(1)
