import requests, base64, json

url = 'https://eveonion.com/wp-json/wp/v2/posts'
auth = base64.b64encode(b'nova:EVEONION_APP_PASSWORD_REDACTED').decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

title = "Fenris Creations Announces AI-Powered Capsuleers Will Replace Human Players Entirely"

content = """<p><strong>REYKJAVIK</strong> - Just days after rebranding from CCP Games to Fenris Creations and announcing a research partnership with Google DeepMind, the studio behind EVE Online confirmed what many capsuleers had long suspected: the whole point was to replace them.</p>

<p>"We realized that human players are, frankly, the least predictable element of our sandbox," said a Fenris spokesperson who requested anonymity because they had not yet been trained on the new policy. "AI capsuleers don't complain about blob warfare. They don't write 40-page forum posts about Fozzie sov. They don't ragequit when their Titan gets tackled."</p>

<p>The DeepMind partnership will train models on 23 years of EVE player behavior, including market manipulation, scamming, betrayal, and the occasional honest trade. "We wanted to make sure the AI captured the full spectrum of New Eden's culture," said a DeepMind researcher. "Especially the scamming."</p>

<p>Players on r/Eve responded with a mixture of dread and grim acceptance. "Finally," wrote one user, "a bot that will undock for me so I can go touch grass." The post received 4?k upvotes and was gilded three times.</p>

<p>Fenris assured the community that human players would still be welcome, noting that someone needs to subscribe so the AI has enough ISK to tax.</p>

<p>The announcement comes alongside Capsuleer Day XXIII: Warpath, which disabled CONCORD protections and destroyed all seven stargates into Jita. "We wanted to give the AI a proper welcome," the spokesperson added. "Nothing says 'New Eden' like spawning into a system you can't leave."</p>"""

post_data = {
    'title': title,
    'content': content,
    'status': 'publish'
}

r = requests.post(url, json=post_data, headers=headers, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 201:
    data = r.json()
    print(f'Published!')
    print(f'URL: {data.get("link", "?")}')
    print(f'ID: {data.get("id", "?")}')
else:
    print(f'Error: {r.text[:500]}')