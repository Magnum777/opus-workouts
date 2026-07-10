import urllib.request, urllib.parse

api_key = "UPLOADPOST_API_KEY_REDACTED"

briefing = """**EVE Online News Briefing - July 10, 2026**

---

**EVE Online Carbon Engine Goes Fully Open Source**
Fenris Creations released the 23-year-old Carbon engine on GitHub (July 1), giving developers, players, and researchers access to the tech behind EVE's massive battles. PC Gamer and Game Developer covered it.
Source: https://www.pcgamer.com/games/mmo/eve-online-studio-fenris-follows-through-on-yearslong-promise-to-make-its-in-house-game-engine-fully-open-source/
[SATIRE SEED] EVE Online Open Sources Engine; Vets Suddenly Remember They Were Gonna Do That 15 Years Ago

---

**EVE Vanguard Alpha Playtest Operation Avalon Now Live**
First alpha playtest for EVE Vanguard dropped July 7 on Steam and the EVE Launcher, running through July 20. New map, overhauled gunplay, new weapons, expanded enemies, and deeper progression and extraction mechanics.
Source: https://fenris.com/news/2026/eve-vanguards-first-alpha-playtest-operation-avalon-deploys-today-on-steam-and-the-eve-launcher
[SATIRE SEED] EVE Vanguard Avalon Test: Now With 47 Percent More Ways to Die and Extract Nothing

---

**Operation Avalon EVE Online Event Live July 7-20**
Main game ties into the Vanguard test with a limited-time event. Capsuleers earn exclusive rewards including a new Breach Control module and a Mordu's Legion drone by hunting AEGIS convoys and completing Avalon Investigations.
Source: https://www.eveonline.com/news/view/operation-avalon-faq
[SATIRE SEED] New EVE Event Lets You Shoot Things For Loot; History Repeats

---

**Community Beat Spotlight July 3**
EVE community stays active. Honor Point vs Tuskers Skua kill documented on video, Nightmare smallgang compilations, Nanobrain Phantasm videos, and a sharp Chimera fan art piece on Reddit.
Source: https://www.eveonline.com/news/view/community-beat-for-3-july
[SATIRE SEED] EVE Artist Draws Chimera; Local Rorqual Pilots Begin Weeb-War Over UwU Aesthetic"""

payload = urllib.parse.urlencode({
    "user": "Eveonion",
    "platform[]": "discord",
    "title": briefing
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.upload-post.com/api/upload_text",
    data=payload,
    headers={
        "Authorization": "Apikey " + api_key
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        result = resp.read().decode("utf-8")
        print("SUCCESS:", result)
except urllib.error.HTTPError as e:
    print("HTTP ERROR", e.code, e.read().decode("utf-8"))
except Exception as e:
    print("ERROR:", e)
