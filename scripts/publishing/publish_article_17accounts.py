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

title = "Area Man Who Flies 17 Accounts Still Can't Win 1-V-1 Fight"

content = """<p><strong>JITA</strong> — In a development that has shocked absolutely no one who has ever flown with him, a local pilot who operates seventeen accounts simultaneously has once again failed to win a one-versus-one engagement, sources confirmed Tuesday.</p>

<p>"Look, when you're managing seventeen pilots at once, there's a lot of cognitive load," said the pilot, who has been "elite PVPing" for fifteen years but has never successfully landed a kill without bringing at least three fully-staged fleets. "It's not about the individual skill of any one toon. It's about the collective."</p>

<p>Fellow corporation members reported that the pilot, who insists on being called "The Commander" despite having no actual leadership position, recently held up an entire roam for forty-five minutes while waiting for his alt characters to "get into position."</p>

<p>"He had his logistics character bookmarking a safespot while his main was warp-disrupting a Catalyst," said one frustrated corp mate who requested anonymity because they still needed the pilot's moon mining payouts. "Meanwhile, his three alt Catalysts were just sitting there, probably alt-tabbed to another screen."</p>

<p>The pilot's killboard, which he describes as "tactically selective," shows seventeen losses and zero solo kills across all accounts over the past month. When asked about this, he became defensive.</p>

<p>"Wins are a social construct," he said, while simultaneously attempting to sell the interviewer a skill injector for one of his alts. "The real victory is the friends you made along the way, even if they're all you."</p>

<p><em>CCP Games has declined to comment, citing a policy of not interfering with what they describe as "natural selection in action."</em></p>"""

data = {
    'title': title,
    'content': content,
    'status': 'publish',
    'slug': 'area-man-17-accounts-cant-win-1v1',
}

r = requests.post(url, headers=headers, json=data, timeout=30)
print(f'Create: {r.status_code}')
if r.status_code in (200, 201):
    print(f'Post ID: {r.json().get("id")}')
else:
    print(r.text[:300])
