import requests, base64, json

url = 'https://eveonion.com/wp-json/wp/v2/posts'
auth = base64.b64encode(b'nova:EVEONION_APP_PASSWORD_REDACTED').decode()
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

<p>When asked about the engagement in question, which reportedly ended with the pilot's Cyclops Prime pod escaping while his entire fleet of seventeen ships was destroyed, the pilot insisted he had "totally won that fight" and that the enemy pilot was "absolute garbage" for not honoring the 1v1 after he brought eight support characters.</p>

<p>The pilot then logged off to go run L4 missions on all seventeen accounts, because "that's where the real ISK is."</p>

<p>Friends of the pilot say they're holding an intervention next Tuesday, though early estimates suggest the pilot will show up with fourteen of his alts and claim the rest died in a separate, unrelated conflict.</p>

<p>This article was brought to you by Training Formations: Making Alts Since 2003.</p>"""

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