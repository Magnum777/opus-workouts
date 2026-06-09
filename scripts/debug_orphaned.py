import requests, base64

auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
headers = {'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://eveonion.com/wp-json/wp/v2/media?per_page=30&orderby=date&order=desc', headers=headers)
items = r.json()
orphaned = []
attached = []
for item in items:
    post = item.get('post')
    fname = item['source_url'].split('/')[-1][:35]
    entry = f'ID {item["id"]} | post={post} | {fname}'
    if post is None:
        orphaned.append(entry)
    else:
        attached.append(entry)

print('ATTACHED:')
for a in attached:
    print(f'  {a}')
print()
print('ORPHANED:')
for o in orphaned:
    print(f'  {o}')