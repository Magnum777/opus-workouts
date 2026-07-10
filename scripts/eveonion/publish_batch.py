import requests, base64
from pathlib import Path

url = 'https://eveonion.com/wp-json/wp/v2/posts'
auth = base64.b64encode(b'nova:EVEONION_APP_PASSWORD_REDACTED').decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
}

ARTICLES = [
    {
        'file': 'eveonion/articles/2026-07-04-carbon-engine-open-source-drama.md',
        'title': 'CCP Open-Sources Carbon Engine; Community Immediately Finds Working Space Tetris, 15-Year-Old Easter Eggs, and Code Comments Saying "TODO: Fix This Never"'
    },
    {
        'file': 'eveonion/articles/2026-07-04-community-july-4th-lull.md',
        'title': 'EVE Online Community Celebrates July 4th the Only Way It Knows How: By Not Doing Anything and Having a Very Good Time Doing It'
    },
    {
        'file': 'eveonion/articles/2026-07-04-frt-input-broadcaster-rorqual.md',
        'title': 'CCP Issues 47th Warning to Known Input Broadcaster; Community Starts Betting Pool on Whether He\'ll Be Banned Before Server Shutdown'
    }
]

for article in ARTICLES:
    with open(article['file']) as f:
        content = f.read()

    # Extract HTML body - convert markdown to basic HTML
    lines = content.split('\n')
    html_parts = []
    in_body = False
    for line in lines:
        if line.startswith('**') and '—' in line and not in_body:
            # Location tag - convert to bold
            location = line.replace('**', '<strong>').replace('</strong>**', '</strong> —')
            html_parts.append(f'<p>{location} — </p>')
            in_body = True
            continue
        if line.startswith('#') or line.startswith('---') or line.startswith('*EVE Onion'):
            continue
        if line.strip():
            html_parts.append(f'<p>{line.strip()}</p>')

    html_content = '\n'.join(html_parts)
    post_data = {'title': article['title'], 'content': html_content, 'status': 'publish'}
    r = requests.post(url, json=post_data, headers=headers, timeout=15)
    print(f"[{article['file'].split('/')[-1]}] Status: {r.status_code}")
    if r.status_code == 201:
        data = r.json()
        print(f"  ID: {data.get('id')} | URL: {data.get('link')}")
    else:
        print(f"  Error: {r.text[:200]}")
