import requests, base64

url = 'https://eveonion.com/wp-json/wp/v2/posts'
auth = base64.b64encode(b'nova:EVEONION_APP_PASSWORD_REDACTED').decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
}

title = 'Ganker Posts Killmail Expecting Tears; Victim Responds With 45-Minute Tutorial on Emotional Maturity'

with open('scripts/eveonion/latest_article.html') as f:
    content = f.read()

post_data = {'title': title, 'content': content, 'status': 'publish', 'featured_media': 25043}
r = requests.post(url, json=post_data, headers=headers, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 201:
    data = r.json()
    print(f'ID: {data.get("id")}')
    print(f'URL: {data.get("link")}')
else:
    print(f'Error: {r.text[:500]}')
