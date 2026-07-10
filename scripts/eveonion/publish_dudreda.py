import requests, base64

url = 'https://eveonion.com/wp-json/wp/v2/posts'
auth = base64.b64encode(b'nova:EVEONION_APP_PASSWORD_REDACTED').decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
}

with open('eveonion/articles/2026-07-04-strait-of-dudreda-propaganda-war.md') as f:
    content = f.read()

lines = content.split('\n')
html_parts = []
for line in lines:
    if line.startswith('**') and '—' in line:
        html_parts.append(f'<p><strong>{line.replace("**","")} — </p>')
        continue
    if line.startswith('#') or line.startswith('---') or line.startswith('*EVE Onion'):
        continue
    if line.strip():
        html_parts.append(f'<p>{line.strip()}</p>')

html_content = '\n'.join(html_parts)
title = 'Strait of Dudreda Propaganda War Escalates; One Side Accidentally Uses CCP Promotional Video, Other Side Publishes 4,000-Word Treatise on Maritime Law'
post_data = {'title': title, 'content': html_content, 'status': 'publish'}
r = requests.post(url, json=post_data, headers=headers, timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    print(f"URL: {r.json().get('link')}")
else:
    print(f"Error: {r.text[:200]}")
