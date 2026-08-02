"""
TorrentDay Scanner & Download Station Manager
Full browse scan (freeleech + regular), cross-seed detection, ratio monitoring

Usage:
  python td_manager.py scan          # Scan TD for hot torrents (freeleech + popular)
  python td_manager.py crossseed     # Cross-seed check: match TD torrents against DS library
  python td_manager.py add           # Add top picks to DS (freeleech + cross-seeds)
  python td_manager.py stats         # Show TD ratio + DS stats + top performers
  python td_manager.py topseeders    # Show DS top seeders (highest upload performers)
  python td_manager.py prune         # Remove completed torrents above ratio target
  python td_manager.py refresh       # Refresh Firefox cookies
  python td_manager.py run           # Full cycle: scan + crossseed + add + stats
"""

import requests
import re
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timedelta
from html.parser import HTMLParser

# --- Config ---
SECRETS_PATH = r"C:\Users\compj\.openclaw\workspace\.secrets"
STATE_PATH = r"C:\Users\compj\.openclaw\workspace\scripts\td_state.json"
COOKIE_REFRESH_HOURS = 168
MAX_ADD_PER_RUN = 5          # Max new torrents to add per run
MIN_SEEDERS_FREE = 3         # Minimum seeders for freeleech picks
MIN_LEECHERS_FREE = 2        # Minimum leechers for freeleech picks
MIN_LEECHERS_REGULAR = 15    # Higher bar for non-freeleech (costs download)
MAX_SIZE_GB = 50             # Skip torrents bigger than this
CROSSSEED_SIZE_TOLERANCE = 0.02  # 2% size tolerance for cross-seed matching

PREFERRED_CATS = [1, 2, 3, 5, 7, 11, 13, 14, 21, 22, 24, 25, 26, 31, 32, 33, 34, 44, 46, 48, 82, 96, 103, 104]
CAT_NAMES = {
    1: "Movies/XviD", 2: "TV/XviD", 3: "Movies/DVD-R", 4: "PC/Games", 5: "Movies/Bluray-Full",
    7: "TV/x264", 8: "PSP", 9: "Xbox", 10: "Nintendo", 11: "Movies/Bluray",
    13: "Movies/Packs", 14: "TV/Packs", 17: "Music/Audio", 18: "PS", 21: "Movies/MP4",
    22: "Movies/Non-English", 24: "TV/480p", 25: "Movies/480p", 26: "TV/SD/x264",
    31: "TV/DVD-Rip", 32: "TV/Bluray", 33: "TV/DVD-R", 34: "TV/x265",
    44: "Movies/SD/x264", 46: "TV/Mobile", 48: "Movies/x265", 82: "TV/Non-English",
    96: "Movies/4K", 103: "Movies/Cam", 104: "TV/4K"
}

TD_BASE = "https://www.torrentday.com"

# --- Load secrets ---
def load_secrets():
    creds = {"torrentday": {}, "nas": {}}
    section = ""
    with open(SECRETS_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("["):
                section = line.strip("[]")
                continue
            if "=" in line and section in creds:
                key, val = line.split("=", 1)
                creds[section][key] = val
    return creds

# --- Load/save state ---
def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"added_torrents": {}, "last_scan": None, "last_cookie_refresh": None,
            "ratio_history": [], "scan_results": [], "crossseed_candidates": [],
            "ds_library": []}

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

# --- TD Session ---
def td_session(secrets):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    })
    td = secrets["torrentday"]
    session.cookies.set("uid", td.get("uid", ""), domain=".torrentday.com", path="/")
    session.cookies.set("pass", td.get("pass_cookie", ""), domain=".torrentday.com", path="/")
    session.cookies.set("td_theme", "dark", domain="www.torrentday.com", path="/")
    return session

# --- DS Session ---
def ds_session(secrets):
    import urllib3
    urllib3.disable_warnings()
    session = requests.Session()
    session.verify = False
    nas = secrets["nas"]
    encoded_pass = urllib.parse.quote(nas["password"])
    login_url = f"https://{nas['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account={nas['user']}&passwd={encoded_pass}&format=sid"
    resp = session.get(login_url)
    data = resp.json()
    if data.get("success"):
        return session, data["data"]["sid"]
    else:
        raise Exception(f"DSM login failed: {data}")

def ds_logout(session, sid):
    nas_creds = load_secrets()["nas"]
    session.get(f"https://{nas_creds['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={sid}")

# --- Parse size string to bytes ---
def parse_size(size_str):
    """Convert '1.65 GB' to bytes"""
    if not size_str or size_str == "Unknown":
        return 0
    match = re.match(r'([\d.]+)\s*([TGMK]?B)', size_str, re.I)
    if not match:
        return 0
    val = float(match.group(1))
    unit = match.group(2).upper()
    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    return int(val * multipliers.get(unit, 1))

# --- Extract release name from title ---
def extract_release_name(title):
    """Extract the scene/release name for cross-seed matching.
    e.g. 'Avatar Aang The Last Airbender 2026 1080p AMZN WEB-DL DDP5 1 H 264-N1H4L'
    -> normalized: 'avatar.aang.the.last.airbender.2026.1080p.amzn.web-dl.ddp5.1.h.264-n1h4l'
    """
    # Remove extension dots, normalize separators
    name = title.lower().strip()
    # Replace dots and spaces with dots (scene style)
    name = re.sub(r'[\s.]+', '.', name)
    # Remove trailing .torrent
    name = re.sub(r'\.torrent$', '', name)
    return name

def normalize_for_match(title):
    """Ultra-normalized title for fuzzy cross-seed matching.
    Strips quality tags, codecs, group names to get the core release name.
    """
    name = title.lower().strip()
    # Remove common quality/source tags for matching
    name = re.sub(r'\b(2160p|1080p|720p|480p|uhd|4k|hdr|dv|hdr10|webrip|web-dl|bluray|bdrip|brrip|hdtv|dvdrip|cam|ts|amzn|nf|hulu|dsnp|atv|hmax|pmtp|starz|it|cr|cc)\b', '', name)
    # Remove codec tags
    name = re.sub(r'\b(x264|x265|h264|h265|h\.264|h\.265|hevc|avc|avi|mp4|mkv)\b', '', name)
    # Remove audio tags
    name = re.sub(r'\b(ddp5\.?1|ddp7\.?1|atmos|dts-hd|dts|aac|ac3|flac|dd5\.?1|truehd)\b', '', name)
    # Remove group name after last dash
    name = re.sub(r'-[a-z0-9]+$', '', name)
    # Normalize whitespace/dots
    name = re.sub(r'[\s.]+', ' ', name)
    # Remove year for some matching
    name = re.sub(r'\b(19\d{2}|20\d{2})\b', '', name)
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# --- Scan TD browse page ---
def scan_td_page(session, url, label=""):
    """Parse a TD browse page and return torrent list"""
    print(f"  Fetching: {url}")
    r = session.get(url, allow_redirects=True, timeout=30)
    if len(r.text) < 5000:
        print(f"  WARNING: Short response ({len(r.text)} chars), may need cookie refresh")
        return []

    torrents = []
    blocks = re.findall(r'<tr[^>]*>.*?</tr>', r.text, re.DOTALL)

    for block in blocks:
        id_match = re.search(r'/t/(\d+)', block)
        title_match = re.search(r'/t/\d+[^>]*>([^<]+)', block)
        dl_match = re.search(r'/download\.php/(\d+)/([^"]+)', block)

        if not id_match:
            continue

        tid = id_match.group(1)
        title = title_match.group(1).strip() if title_match else f"Torrent {tid}"
        dl_file = dl_match.group(2) if dl_match else f"{tid}.torrent"

        is_free = bool(re.search(r'free[_ ]?leech|freeleech', block, re.I))

        seed_match = re.search(r'(?:seeders?|S:)[^\d]*(\d+)', block, re.I)
        leech_match = re.search(r'(?:leechers?|L:)[^\d]*(\d+)', block, re.I)

        seeders = int(seed_match.group(1)) if seed_match else 0
        leechers = int(leech_match.group(1)) if leech_match else 0

        cat_match = re.search(r'\?(\d+)#torrents', block)
        cat = int(cat_match.group(1)) if cat_match else 0

        size_match = re.search(r'([\d.]+\s*[TGMK]B)', block, re.I)
        size_str = size_match.group(1) if size_match else "Unknown"
        size_bytes = parse_size(size_str)

        # Score: freeleech is always worth it (zero download cost).
        # Regular torrents need high leechers to be worth the download cost.
        # Weight: freeleech gets 3x multiplier, leechers weighted heavily.
        if is_free:
            score = (seeders * 1) + (leechers * 5)  # Free = pure profit
        else:
            # Regular: must earn its download back. Score = expected upload ratio
            # Only worth it if leechers >> seeders (high demand, easy upload)
            if leechers > 0 and seeders > 0:
                demand_ratio = leechers / seeders  # Higher = more leechers per seeder
                score = (leechers * 3) + (demand_ratio * 10) - 20  # Penalty for non-free
            else:
                score = 0

        torrents.append({
            "id": tid,
            "title": title,
            "release_name": extract_release_name(title),
            "match_key": normalize_for_match(title),
            "download_url": f"{TD_BASE}/download.php/{tid}/{dl_file}",
            "seeders": seeders,
            "leechers": leechers,
            "size_str": size_str,
            "size_bytes": size_bytes,
            "category": cat,
            "category_name": CAT_NAMES.get(cat, f"cat-{cat}"),
            "freeleech": is_free,
            "score": score,
            "source": label,
        })

    return torrents

# --- Get DS library for cross-seed matching ---
def get_ds_library(session, sid, nas_creds):
    """Get full DS task list as a library for cross-seed matching"""
    base = f"https://{nas_creds['hostname']}:5001/webapi/DownloadStation/task.cgi"

    all_tasks = []
    offset = 0
    limit = 100

    while True:
        resp = session.get(base, params={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "list",
            "additional": "detail,transfer",
            "_sid": sid,
            "offset": offset,
            "limit": limit
        })
        data = resp.json()
        if not data.get("success"):
            print(f"  DS library fetch error at offset {offset}: {data}")
            break

        tasks = data.get("data", {}).get("tasks", [])
        if not tasks:
            break

        for task in tasks:
            detail = task.get("additional", {}).get("detail", {})
            transfer = task.get("additional", {}).get("transfer", {})
            title = task.get("title", "Unknown")
            # size can be 0 for some torrents, use downloaded as fallback
            size = detail.get("size", 0)
            if size == 0 and transfer.get("size_downloaded", 0) > 0:
                size = transfer["size_downloaded"]
            all_tasks.append({
                "id": task.get("id", ""),
                "title": title,
                "status": task.get("status", ""),
                "size": size,
                "uploaded": transfer.get("size_uploaded", 0),
                "downloaded": transfer.get("size_downloaded", 0),
                "release_name": extract_release_name(title),
                "match_key": normalize_for_match(title),
            })

        offset += limit
        # DS API may report wrong total; just keep fetching until no tasks returned
        reported_total = data.get("data", {}).get("total", 0)
        if reported_total > 0 and offset >= reported_total:
            break
        # Safety: don't loop forever
        if len(tasks) < limit:
            break
        if offset > 2000:  # Hard cap
            break

    return all_tasks

# --- Get DS top seeders ---
def get_ds_top_seeders(session, sid, nas_creds, top_n=20):
    """Get DS tasks sorted by upload (top performers)"""
    library = get_ds_library(session, sid, nas_creds)
    # Sort by upload descending
    seeded = sorted(library, key=lambda t: t.get("uploaded", 0), reverse=True)
    return seeded[:top_n]

# --- Scan TD (full browse: freeleech + recent popular) ---
def cmd_scan():
    secrets = load_secrets()
    session = td_session(secrets)
    state = load_state()

    print("=== Scanning TorrentDay ===\n")

    all_torrents = {}

    # 1. Freeleech (always worth it)
    print("Scanning freeleech...")
    free = scan_td_page(session, f"{TD_BASE}/t?free=1", "freeleech")
    for t in free:
        t["freeleech"] = True  # Override since we're on freeleech page
        t["score"] = (t["seeders"] * 1) + (t["leechers"] * 5)
        all_torrents[t["id"]] = t

    # 2. Full browse (recent + popular, includes non-freeleech)
    print("Scanning recent torrents...")
    recent = scan_td_page(session, f"{TD_BASE}/t", "browse")
    for t in recent:
        if t["id"] not in all_torrents:
            all_torrents[t["id"]] = t

    # 3. Movies category (high value for seeding)
    print("Scanning movies...")
    movies = scan_td_page(session, f"{TD_BASE}/t?25", "movies")
    for t in movies:
        if t["id"] not in all_torrents:
            all_torrents[t["id"]] = t

    # 4. TV category (consistent seeders)
    print("Scanning TV...")
    tv = scan_td_page(session, f"{TD_BASE}/t?7", "tv")
    for t in tv:
        if t["id"] not in all_torrents:
            all_torrents[t["id"]] = t

    # Sort by score
    sorted_torrents = sorted(all_torrents.values(), key=lambda x: x["score"], reverse=True)

    # Filter by preferences
    filtered = []
    for t in sorted_torrents:
        size_gb = t["size_bytes"] / (1024**3) if t["size_bytes"] else 0
        if size_gb > MAX_SIZE_GB:
            continue
        if t["category"] not in PREFERRED_CATS and t["category"] != 0:
            continue
        if t["freeleech"]:
            if t["seeders"] < MIN_SEEDERS_FREE or t["leechers"] < MIN_LEECHERS_FREE:
                continue
        else:
            if t["leechers"] < MIN_LEECHERS_REGULAR:
                continue
        filtered.append(t)

    free_count = sum(1 for t in filtered if t["freeleech"])
    reg_count = sum(1 for t in filtered if not t["freeleech"])

    print(f"\n=== Scan Results ===")
    print(f"Total found: {len(all_torrents)}")
    print(f"Freeleech candidates: {free_count}")
    print(f"Regular (high-demand) candidates: {reg_count}")

    print(f"\n{'Score':>6} {'Free':>4} {'S':>4} {'L':>4} {'Cat':>18} {'Size':>8} Title")
    print("-" * 110)
    for t in filtered[:30]:
        free_tag = "YES" if t["freeleech"] else "no"
        print(f"{t['score']:>6} {free_tag:>4} {t['seeders']:>4} {t['leechers']:>4} {t['category_name']:>18} {t['size_str']:>8} {t['title'][:60]}")

    state["last_scan"] = datetime.now().isoformat()
    state["scan_results"] = filtered[:80]
    save_state(state)
    print(f"\nScan saved. {len(filtered)} candidates after filtering.")

# --- Cross-seed detection ---
def cmd_crossseed():
    """Match TD scan results against DS library for cross-seed opportunities"""
    secrets = load_secrets()
    state = load_state()
    td_results = state.get("scan_results", [])
    if not td_results:
        print("No scan results. Run 'scan' first.")
        return

    print("=== Cross-Seed Detection ===\n")

    # Get DS library (full, paginated)
    print("Loading DS library...")
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]
    library = get_ds_library(ds_sess, sid, nas)
    ds_logout(ds_sess, sid)
    print(f"DS library: {len(library)} torrents loaded")

    # Build lookup: normalized match key -> DS task
    ds_lookup = {}
    for task in library:
        key = task["match_key"]
        if key not in ds_lookup:
            ds_lookup[key] = []
        ds_lookup[key].append(task)

    # Also build a size lookup for exact matching
    ds_by_size = {}
    for task in library:
        size = task.get("size", 0)
        if size > 0:
            if size not in ds_by_size:
                ds_by_size[size] = []
            ds_by_size[size].append(task)

    matches = []       # Exact matches (same release name or same size)
    near_matches = []   # Fuzzy matches (similar name)

    for td_torrent in td_results:
        td_key = td_torrent["match_key"]
        td_size = td_torrent.get("size_bytes", 0)
        td_name = td_torrent["release_name"]

        # Check 1: Normalized name match
        if td_key in ds_lookup:
            for ds_task in ds_lookup[td_key]:
                # Size check - if both have sizes, they must be close
                ds_size = ds_task.get("size", 0)
                if ds_size > 0 and td_size > 0:
                    size_diff = abs(td_size - ds_size) / max(td_size, ds_size)
                    if size_diff < CROSSSEED_SIZE_TOLERANCE:
                        matches.append({
                            "td": td_torrent,
                            "ds": ds_task,
                            "match_type": "name+size",
                            "size_match": f"{td_torrent['size_str']} = {ds_size/(1024**3):.2f}GB",
                        })
                    else:
                        near_matches.append({
                            "td": td_torrent,
                            "ds": ds_task,
                            "match_type": "name-size_mismatch",
                            "td_size": td_torrent["size_str"],
                            "ds_size": f"{ds_size/(1024**3):.2f}GB",
                            "size_diff_pct": f"{size_diff*100:.1f}%",
                        })
                else:
                    matches.append({
                        "td": td_torrent,
                        "ds": ds_task,
                        "match_type": "name-only",
                        "size_match": "unknown",
                    })

        # Check 2: Exact size match (different release, same content)
        if td_size > 0 and td_size in ds_by_size:
            for ds_task in ds_by_size[td_size]:
                # Skip if already matched by name
                if any(m["ds"]["id"] == ds_task["id"] and m["td"]["id"] == td_torrent["id"] for m in matches):
                    continue
                matches.append({
                    "td": td_torrent,
                    "ds": ds_task,
                    "match_type": "exact-size",
                    "size_match": f"{td_torrent['size_str']} = {ds_task['size']/(1024**3):.2f}GB",
                })

    # Sort matches: freeleech first, then by score
    matches.sort(key=lambda m: (0 if m["td"]["freeleech"] else 1, -m["td"]["score"]))
    near_matches.sort(key=lambda m: (0 if m["td"]["freeleech"] else 1, -m["td"]["score"]))

    print(f"\n=== Exact Cross-Seed Matches: {len(matches)} ===")
    for m in matches[:20]:
        free_tag = "FREE" if m["td"]["freeleech"] else "REG"
        print(f"  [{m['match_type']:>12}] [{free_tag}] S:{m['td']['seeders']:>3} L:{m['td']['leechers']:>3} "
              f"TD: {m['td']['title'][:45]:<45} "
              f"DS: {m['ds']['title'][:45]:<45} "
              f"Size: {m['size_match']}")

    if near_matches:
        print(f"\n=== Near Matches (name hit, size mismatch): {len(near_matches)} ===")
        for m in near_matches[:10]:
            free_tag = "FREE" if m["td"]["freeleech"] else "REG"
            print(f"  [{m['match_type']:>18}] [{free_tag}] TD: {m['td']['size_str']:>8} vs DS: {m['ds_size']:>8} ({m['size_diff_pct']} off) "
                  f"TD: {m['td']['title'][:40]}")

    # Save cross-seed candidates (exact matches that are freeleech = pure profit)
    free_crossseeds = [m for m in matches if m["td"]["freeleech"]]
    all_crossseeds = [m for m in matches if m["td"]["freeleech"] or m["td"]["score"] > 50]

    print(f"\nFreeleech cross-seeds (PURE PROFIT - add these!): {len(free_crossseeds)}")
    for m in free_crossseeds:
        print(f"  + {m['td']['title'][:60]} ({m['td']['size_str']})")

    state["crossseed_candidates"] = matches
    state["ds_library"] = [{"title": t["title"], "size": t["size"], "uploaded": t["uploaded"],
                            "release_name": t["release_name"], "match_key": t["match_key"]}
                           for t in library]
    save_state(state)

# --- Add torrents to DS ---
def cmd_add(max_add=None):
    if max_add is None:
        max_add = MAX_ADD_PER_RUN
    secrets = load_secrets()
    state = load_state()
    td_results = state.get("scan_results", [])
    crossseed = state.get("crossseed_candidates", [])
    if not td_results:
        print("No scan results. Run 'scan' first.")
        return

    added_ids = set(state.get("added_torrents", {}).keys())

    # Priority 1: Freeleech cross-seeds (zero download, pure upload)
    # Priority 2: Freeleech high-score picks
    # Priority 3: High-demand regular picks (only if really hot)

    to_add = []

    # Add freeleech cross-seeds first
    for m in crossseed:
        if str(m["td"]["id"]) not in added_ids and m["td"]["freeleech"]:
            to_add.append(("crossseed-free", m["td"]))

    # Add freeleech picks by score
    for t in td_results:
        if str(t["id"]) not in added_ids and t["freeleech"] and t["id"] not in [x[1]["id"] for x in to_add]:
            to_add.append(("freeleech", t))

    # Add regular high-demand picks (only top tier)
    for t in td_results:
        if str(t["id"]) not in added_ids and not t["freeleech"] and t["score"] > 100:
            to_add.append(("regular", t))

    # Dedupe by ID
    seen = set()
    unique = []
    for kind, t in to_add:
        if t["id"] not in seen:
            seen.add(t["id"])
            unique.append((kind, t))
    to_add = unique[:max_add]

    if not to_add:
        print("No new torrents to add.")
        return

    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    print(f"Adding {len(to_add)} torrents to Download Station:")
    added = 0
    for kind, t in to_add:
        print(f"\n  [{kind.upper()}] {t['title'][:60]}")
        print(f"    S:{t['seeders']} L:{t['leechers']} Score:{t['score']} Size:{t['size_str']}")
        success = add_to_ds(ds_sess, sid, t["download_url"], nas)
        if success:
            state.setdefault("added_torrents", {})[str(t["id"])] = {
                "title": t["title"],
                "added_at": datetime.now().isoformat(),
                "seeders": t["seeders"],
                "leechers": t["leechers"],
                "category": t.get("category_name", ""),
                "freeleech": t["freeleech"],
                "size": t.get("size_str", ""),
                "source": kind,
            }
            added += 1
        time.sleep(2)

    ds_logout(ds_sess, sid)
    save_state(state)
    print(f"\nAdded {added}/{len(to_add)} torrents to Download Station")

# --- Add torrent to DS ---
def add_to_ds(session, sid, torrent_url, nas_creds, torrent_title=""):
    """Add a torrent to Download Station via watch folder.
    
    DS API file upload is broken (error 101) and URL-based create leaves tasks
    stuck in 'waiting' because DS can't auth with TorrentDay.
    
    Instead: download .torrent files ourselves (with TD cookies), copy to
    \\MND\video\torrents via SMB, and DS auto-adds from the watch folder.
    """
    import subprocess
    
    # Download .torrent file with TD cookies
    secrets = load_secrets()
    resp = requests.get(torrent_url,
                        cookies={"uid": secrets["torrentday"]["uid"],
                                  "pass": secrets["torrentday"]["pass_cookie"]},
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                        timeout=30)
    
    if resp.status_code != 200 or not resp.content.startswith(b'd8:'):
        print(f"    Failed to download .torrent: HTTP {resp.status_code} ({len(resp.content)} bytes)")
        return False
    
    # Save to local temp, then copy to NAS watch folder
    local_temp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_torrents")
    os.makedirs(local_temp, exist_ok=True)
    
    safe_title = "".join(c for c in (torrent_title or "td") if c.isalnum() or c in ".-_")[:60]
    if not safe_title:
        safe_title = "td_" + torrent_url.split("/")[-1].replace(".torrent", "")
    local_file = os.path.join(local_temp, f"{safe_title}.torrent")
    
    with open(local_file, "wb") as f:
        f.write(resp.content)
    
    # Copy to NAS watch folder via SMB
    watch_folder = f"\\\\{nas_creds['hostname']}\\video\\torrents"
    result = subprocess.run(
        ["cmd", "/c", "copy", "/Y", local_file, f"{watch_folder}\\"],
        capture_output=True, text=True, timeout=15
    )
    
    if result.returncode == 0:
        print(f"    Copied to NAS watch folder ({len(resp.content)} bytes)")
        # Clean up local temp
        try:
            os.remove(local_file)
        except OSError:
            pass
        return True
    else:
        # Try establishing SMB connection first
        subprocess.run(
            ["net", "use", f"\\\\{nas_creds['hostname']}\\video",
             "/user:Nova", nas_creds['password'], "/persistent:no"],
            capture_output=True, timeout=10
        )
        result = subprocess.run(
            ["cmd", "/c", "copy", "/Y", local_file, f"{watch_folder}\\"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print(f"    Copied to NAS watch folder (retry, {len(resp.content)} bytes)")
            try:
                os.remove(local_file)
            except OSError:
                pass
            return True
        else:
            print(f"    SMB copy failed: {result.stderr.strip()[:100]}")
            return False

# --- TD stats ---
def get_td_stats(session, secrets):
    """Get TorrentDay user ratio and stats"""
    uid = secrets["torrentday"].get("uid", "")
    r = session.get(f"{TD_BASE}/u/{uid}", allow_redirects=True, timeout=15)

    ratio_match = re.search(r'class="ratio"[^>]*>([^<]+)', r.text, re.I)
    if not ratio_match:
        ratio_match = re.search(r'ratio[^"]*"[^>]*>([^<]+)', r.text, re.I)

    up_match = re.search(r'Up[^<]*?([\d.]+\s*[TGMK]?B)', r.text, re.I)
    dn_match = re.search(r'Dn[^<]*?([\d.]+\s*[TGMK]?B)', r.text, re.I)

    if not up_match:
        up_match = re.search(r'uploaded[^<]*?([\d.]+\s*[TGMK]?B)', r.text, re.I)
    if not dn_match:
        dn_match = re.search(r'downloaded[^<]*?([\d.]+\s*[TGMK]?B)', r.text, re.I)

    ratio_val = None
    if ratio_match:
        try:
            ratio_val = float(ratio_match.group(1).strip())
        except:
            pass

    return {
        "ratio": ratio_val,
        "uploaded": up_match.group(1) if up_match else None,
        "downloaded": dn_match.group(1) if dn_match else None,
        "timestamp": datetime.now().isoformat()
    }

# --- DS stats ---
def get_ds_stats(session, sid, nas_creds):
    """Get Download Station task statistics"""
    base = f"https://{nas_creds['hostname']}:5001/webapi/entry.cgi"
    resp = session.get(base, params={
        "api": "SYNO.DownloadStation2.Task.Statistic",
        "version": "1",
        "method": "get",
        "_sid": sid
    })
    return resp.json().get("data", {})

def get_ds_tasks(session, sid, nas_creds):
    """Get all DS tasks with details via DS1 API (paginated)"""
    base = f"https://{nas_creds['hostname']}:5001/webapi/DownloadStation/task.cgi"
    all_tasks = []
    offset = 0
    limit = 100

    while True:
        resp = session.get(base, params={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "list",
            "additional": "detail,transfer",
            "_sid": sid,
            "offset": offset,
            "limit": limit
        })
        data = resp.json()
        if not data.get("success"):
            break
        tasks = data.get("data", {}).get("tasks", [])
        if not tasks:
            break
        for task in tasks:
            detail = task.get("additional", {}).get("detail", {})
            transfer = task.get("additional", {}).get("transfer", {})
            size = detail.get("size", 0)
            if size == 0 and transfer.get("size_downloaded", 0) > 0:
                size = transfer["size_downloaded"]
            all_tasks.append({
                "id": task.get("id", ""),
                "title": task.get("title", "Unknown"),
                "status": task.get("status", ""),
                "size": size,
                "uploaded": transfer.get("size_uploaded", 0),
                "downloaded": transfer.get("size_downloaded", 0),
                "seeders": detail.get("seeders", 0),
                "leechers": detail.get("leechers", 0),
            })
        offset += limit
        # Keep fetching until no more tasks
        if len(tasks) < limit:
            break
        if offset > 2000:
            break
    return all_tasks

# --- Stats command ---
def cmd_stats():
    secrets = load_secrets()

    print("=== TorrentDay Stats ===")
    td_sess = td_session(secrets)
    td_stats = get_td_stats(td_sess, secrets)
    print(f"  Ratio: {td_stats.get('ratio', 'N/A')}")
    print(f"  Uploaded: {td_stats.get('uploaded', 'N/A')}")
    print(f"  Downloaded: {td_stats.get('downloaded', 'N/A')}")

    print("\n=== Download Station Stats ===")
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    tasks = get_ds_tasks(ds_sess, sid, nas)
    seeding = [t for t in tasks if t["status"] in ("seeding", 8)]
    downloading = [t for t in tasks if t["status"] in ("downloading", 5)]
    finished = [t for t in tasks if t["status"] == "finished"]
    errors = [t for t in tasks if t["status"] == "error"]

    total_up = sum(t["uploaded"] for t in tasks) / (1024**3)
    total_dn = sum(t["downloaded"] for t in tasks) / (1024**3)
    ds_ratio = total_up / total_dn if total_dn > 0 else 0

    print(f"  Total tasks: {len(tasks)}")
    print(f"  Seeding: {len(seeding)} | Downloading: {len(downloading)} | Finished: {len(finished)} | Errors: {len(errors)}")
    print(f"  Total uploaded: {total_up:.1f} GB")
    print(f"  Total downloaded: {total_dn:.1f} GB")
    print(f"  DS overall ratio: {ds_ratio:.3f}")

    # Top 15 seeders
    top = sorted(seeding, key=lambda t: t.get("uploaded", 0), reverse=True)[:15]
    print(f"\n  Top 15 Uploaders (seeding now):")
    for i, t in enumerate(top, 1):
        ul_gb = t["uploaded"] / (1024**3)
        dl_gb = t["downloaded"] / (1024**3)
        sz_gb = t["size"] / (1024**3) if t["size"] else 0
        r = t["uploaded"] / max(t["downloaded"], 1)
        print(f"    {i:>2}. {t['title'][:48]:<48} UL:{ul_gb:>7.1f}GB DL:{dl_gb:>7.1f}GB Size:{sz_gb:>5.1f}GB R:{r:.2f}")

    ds_logout(ds_sess, sid)

    # Save ratio history
    state = load_state()
    if td_stats.get("ratio"):
        state.setdefault("ratio_history", []).append({
            "ratio": td_stats["ratio"],
            "timestamp": datetime.now().isoformat()
        })
        state["ratio_history"] = state["ratio_history"][-30:]
        save_state(state)

# --- Top seeders command ---
def cmd_topseeders():
    """Show DS top seeders by upload volume"""
    secrets = load_secrets()
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    print("=== Download Station Top Seeders ===\n")
    top = get_ds_top_seeders(ds_sess, sid, nas, top_n=25)

    print(f"{'Rank':>4} {'Upload (GB)':>12} {'DL (GB)':>10} {'Size (GB)':>10} {'Ratio':>7} {'Title'}")
    print("-" * 120)
    for i, t in enumerate(top, 1):
        ul_gb = t["uploaded"] / (1024**3)
        dl_gb = t["downloaded"] / (1024**3)
        sz_gb = t["size"] / (1024**3) if t["size"] else 0
        r = t["uploaded"] / max(t["downloaded"], 1)
        print(f"{i:>4} {ul_gb:>12.1f} {dl_gb:>10.1f} {sz_gb:>10.1f} {r:>7.2f} {t['title'][:55]}")

    ds_logout(ds_sess, sid)

# --- Prune command ---
def cmd_prune(min_ratio=2.0, min_seed_hours=72):
    """Remove torrents that have seeded past target ratio AND minimum seed time.
    
    H&R compliance: only prune if BOTH conditions met:
    - ratio >= min_ratio (default 2.0)
    - seed time >= min_seed_hours (default 72 hours = TD's H&R rule)
    """
    secrets = load_secrets()
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    tasks = get_ds_tasks(ds_sess, sid, nas)
    seeding = [t for t in tasks if t["status"] in ("seeding", 8)]

    # Load added_torrents timestamps for seed time check
    state = load_state()
    added_times = {}
    for tid, info in state.get("added_torrents", {}).items():
        added_times[info.get("title", "").lower()[:30]] = info.get("added_at", "")

    to_remove = []
    for t in seeding:
        dl = t.get("downloaded", 0) or t.get("size", 1)
        ul = t.get("uploaded", 0)
        if dl > 0:
            ratio = ul / dl
            if ratio < min_ratio:
                continue
        else:
            continue

        # Check seed time - use added_at from state if available
        title_key = t["title"].lower()[:30]
        seed_hours = None
        if title_key in added_times:
            try:
                added_time = datetime.fromisoformat(added_times[title_key])
                seed_hours = (datetime.now() - added_time).total_seconds() / 3600
            except:
                pass

        # Only prune if we know seed time and it exceeds minimum
        # If we don't have the timestamp, err on the side of keeping it
        if seed_hours is not None and seed_hours < min_seed_hours:
            continue
        elif seed_hours is None:
            # No timestamp = unknown, keep it seeding to be safe
            continue

        to_remove.append((t, ratio, seed_hours))

    if not to_remove:
        print(f"No torrents eligible for pruning (ratio >={min_ratio:.1f} AND seed >={min_seed_hours}h)")
        ds_logout(ds_sess, sid)
        return

    print(f"Found {len(to_remove)} torrents eligible for pruning:")
    for t, r, hours in sorted(to_remove, key=lambda x: x[1], reverse=True)[:20]:
        ul_gb = t["uploaded"] / (1024**3)
        print(f"  R:{r:.2f} UL:{ul_gb:.1f}GB Seeded:{hours:.0f}h {t['title'][:50]}")

    # Delete via DS1 API
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
    for t, r, hours in to_remove:
        resp = ds_sess.get(base, params={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "delete",
            "id": t["id"],
            "delete_files": "true",
            "_sid": sid
        })
        result = resp.json()
        status = "OK" if result.get("success") else f"FAIL: {result}"
        print(f"  Deleted {t['title'][:50]} (R:{r:.2f}, {hours:.0f}h): {status}")

    ds_logout(ds_sess, sid)
    print(f"Pruned {len(to_remove)} torrents")

# --- Refresh cookies ---
def cmd_refresh():
    import sqlite3
    import shutil

    src = r"C:\Users\compj\AppData\Roaming\Mozilla\Firefox\Profiles\dnhgd3mm.default-release\cookies.sqlite"
    dst = os.path.join(os.environ['TEMP'], 'firefox_cookies_refresh.sqlite')
    shutil.copy2(src, dst)

    conn = sqlite3.connect(dst)
    cur = conn.cursor()
    cur.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%torrentday%'")
    cookies = dict(cur.fetchall())
    conn.close()
    os.unlink(dst)

    if "uid" not in cookies or "pass" not in cookies:
        print("ERROR: Could not find TorrentDay cookies in Firefox!")
        return False

    secrets = load_secrets()
    secrets["torrentday"]["uid"] = cookies["uid"]
    secrets["torrentday"]["pass_cookie"] = cookies["pass"]

    # Rewrite secrets
    lines = []
    section = ""
    td_written = False
    with open(SECRETS_PATH) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("[nas]"):
                if not td_written:
                    lines.append("[torrentday]")
                    for k, v in secrets["torrentday"].items():
                        lines.append(f"{k}={v}")
                    lines.append("")
                    td_written = True
                lines.append(line)
                section = "nas"
                continue
            elif stripped.startswith("["):
                section = stripped.strip("[]")
                if section == "torrentday":
                    td_written = True
                    lines.append("[torrentday]")
                    for k, v in secrets["torrentday"].items():
                        lines.append(f"{k}={v}")
                    continue
            elif section != "torrentday":
                lines.append(line)

    if not td_written:
        lines.append("")
        lines.append("[torrentday]")
        for k, v in secrets["torrentday"].items():
            lines.append(f"{k}={v}")

    with open(SECRETS_PATH, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Cookies refreshed: uid={cookies['uid']}, pass=***")
    state = load_state()
    state["last_cookie_refresh"] = datetime.now().isoformat()
    save_state(state)
    return True

# --- Auto-resume finished tasks ---
def cmd_resume():
    """Resume all finished (not seeding) torrents so they keep seeding for H&R compliance."""
    secrets = load_secrets()
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    tasks = get_ds_tasks(ds_sess, sid, nas)
    finished = [t for t in tasks if t.get("status") == "finished"]

    if not finished:
        print("No finished tasks to resume.")
        ds_logout(ds_sess, sid)
        return 0

    print(f"Resuming {len(finished)} finished tasks...")
    resumed = 0
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
    for t in finished:
        resp = ds_sess.post(base, data={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "resume",
            "id": t["id"],
            "_sid": sid
        })
        result = resp.json()
        if result.get("success"):
            resumed += 1
        else:
            print(f"  FAILED to resume: {t['title'][:50]}")
    print(f"Resumed {resumed}/{len(finished)} tasks.")
    ds_logout(ds_sess, sid)
    return resumed

# --- Clean up dead weight ---
def cmd_cleanup():
    """Remove error tasks and TD-tracked dead weight that can't clear H&Rs.
    
    SAFETY: Only deletes torrents that are in the added_torrents state file
    (i.e., ones WE added via the scanner). Never touches user's own downloads.
    """
    secrets = load_secrets()
    ds_sess, sid = ds_session(secrets)
    nas = secrets["nas"]

    # Load TD-tracked titles so we only delete OUR stuff
    state = load_state()
    td_titles = set()
    for tid, info in state.get("added_torrents", {}).items():
        title = info.get("title", "").lower()[:40]
        td_titles.add(title)

    tasks = get_ds_tasks(ds_sess, sid, nas)

    # 1. Error tasks that are TD-tracked
    error_tasks = [t for t in tasks if t.get("status") == "error"]
    td_errors = [t for t in error_tasks if t["title"].lower()[:40] in td_titles]
    non_td_errors = [t for t in error_tasks if t["title"].lower()[:40] not in td_titles]
    if non_td_errors:
        print(f"  Skipping {len(non_td_errors)} non-TD error tasks (not ours to manage)")

    # 2. Zero-upload TD-tracked tasks only
    td_dead_weight = []
    for t in tasks:
        if t.get("status") not in ("error",) and t["title"].lower()[:40] in td_titles:
            dl = t.get("downloaded", 0)
            ul = t.get("uploaded", 0)
            if dl > 0 and ul == 0:
                td_dead_weight.append(t)

    to_delete = td_errors + td_dead_weight
    # Dedupe by id
    seen_ids = set()
    unique = []
    for t in to_delete:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique.append(t)
    to_delete = unique

    if not to_delete:
        print("No TD-tracked error or dead-weight tasks to clean up.")
        ds_logout(ds_sess, sid)
        return 0

    print(f"Cleaning up {len(to_delete)} TD-tracked tasks ({len(td_errors)} errors, {len(td_dead_weight)} zero-upload)")
    deleted = 0
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
    for t in to_delete:
        resp = ds_sess.post(base, data={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "delete",
            "id": t["id"],
            "delete_files": "true",
            "_sid": sid
        })
        result = resp.json()
        if result.get("success"):
            deleted += 1
        else:
            print(f"  FAILED to delete: {t['title'][:50]}")
    print(f"Deleted {deleted}/{len(to_delete)} TD-tracked tasks.")
    ds_logout(ds_sess, sid)
    return deleted

# --- Full run ---
def cmd_run():
    """Full cycle: refresh cookies, resume finished, scan, cross-seed, add, stats"""
    state = load_state()

    # Refresh cookies if stale
    last_refresh = state.get("last_cookie_refresh")
    if last_refresh:
        hours_ago = (datetime.now() - datetime.fromisoformat(last_refresh)).total_seconds() / 3600
        if hours_ago > COOKIE_REFRESH_HOURS:
            print("Cookies stale, refreshing from Firefox...")
            cmd_refresh()
    else:
        print("No cookie refresh recorded, refreshing from Firefox...")
        cmd_refresh()

    # Resume finished torrents (H&R compliance)
    print("\n=== Resuming finished torrents ===")
    cmd_resume()

    cmd_scan()
    cmd_crossseed()
    cmd_add()
    cmd_stats()

# --- Entry point ---
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"

    commands = {
        "scan": cmd_scan,
        "crossseed": cmd_crossseed,
        "add": cmd_add,
        "stats": cmd_stats,
        "topseeders": cmd_topseeders,
        "prune": cmd_prune,
        "refresh": cmd_refresh,
        "resume": cmd_resume,
        "cleanup": cmd_cleanup,
        "run": cmd_run,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(f"Usage: python td_manager.py [{'|'.join(commands.keys())}]")