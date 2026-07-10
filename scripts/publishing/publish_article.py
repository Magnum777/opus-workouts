import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

import requests, base64, json

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

url = f'{EVE_URL}/wp-json/wp/v2/posts'
auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
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

<p><em>Fenris Creations has clarified that human players will still be permitted in New Eden "for now," and that any AI uprising will be handled through the existing war declaration system.</em></p>"""

data = {
    'title': title,
    'content': content,
    'status': 'publish',
    'slug': 'fenris-ai-capsuleers-replace-humans',
}

r = requests.post(url, headers=headers, json=data, timeout=30)
print(f'Create: {r.status_code}')
if r.status_code in (200, 201):
    print(f'Post ID: {r.json().get("id")}')
else:
    print(r.text[:300])
