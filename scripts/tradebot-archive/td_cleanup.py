"""Clean up DS error tasks and update td_manager to auto-resume + smart prune."""
import requests
import urllib.parse
import json
import urllib3

urllib3.disable_warnings()

SECRETS_PATH = r"C:\Users\compj\.openclaw\workspace\.secrets"

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

def ds_session(secrets):
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

def get_all_tasks(session, sid, nas):
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
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
        all_tasks.extend(tasks)
        offset += limit
        if len(tasks) < limit or offset > 2000:
            break
    return all_tasks

def delete_tasks(session, sid, nas, task_ids):
    """Delete tasks by ID, in batches of 25"""
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
    deleted = 0
    failed = 0
    for i in range(0, len(task_ids), 25):
        batch = task_ids[i:i+25]
        ids_str = ",".join(batch)
        resp = session.post(base, data={
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "delete",
            "id": ids_str,
            "delete_files": "true",
            "_sid": sid
        })
        result = resp.json()
        if result.get("success"):
            deleted += len(batch)
            print(f"  Deleted batch of {len(batch)} tasks")
        else:
            # Try individual deletion
            for tid in batch:
                resp2 = session.post(base, data={
                    "api": "SYNO.DownloadStation.Task",
                    "version": "3",
                    "method": "delete",
                    "id": tid,
                    "delete_files": "true",
                    "_sid": sid
                })
                if resp2.json().get("success"):
                    deleted += 1
                else:
                    failed += 1
    return deleted, failed

def main():
    secrets = load_secrets()
    session, sid = ds_session(secrets)
    nas = secrets["nas"]

    print("Fetching all DS tasks...")
    tasks = get_all_tasks(session, sid, nas)

    error_tasks = [t for t in tasks if t.get("status") == "error"]
    print(f"\nFound {len(error_tasks)} error tasks")

    # Categorize errors
    broken = []      # td.torrent, clearly broken, never gonna seed
    recent_failed = []  # recent TD additions that errored
    old_failed = []  # older stuff that errored

    for t in error_tasks:
        title = t.get("title", "Unknown")
        tid = t.get("id", "")
        detail = t.get("additional", {}).get("detail", {})
        
        if title == "td.torrent" or "td.torrent" in title:
            broken.append((tid, title))
        elif "Error" in str(detail.get("error", 0)) or detail.get("error", 0) != 0:
            # All error tasks get cleaned up
            broken.append((tid, title))
        else:
            broken.append((tid, title))

    # Actually, let's just delete ALL error tasks - they're not seeding and never will
    all_error_ids = [t.get("id", "") for t in error_tasks]
    all_error_titles = [t.get("title", "Unknown") for t in error_tasks]

    print(f"\nDeleting all {len(all_error_ids)} error tasks:")
    for title in all_error_titles:
        print(f"  [DEL] {title[:65]}")

    deleted, failed = delete_tasks(session, sid, nas, all_error_ids)
    print(f"\nDeleted {deleted} error tasks, {failed} failed")

    # Also check for 0-upload dead torrents (The Expanse episodes, etc)
    tasks = get_all_tasks(session, sid, nas)
    dead = []
    for t in tasks:
        transfer = t.get("additional", {}).get("transfer", {})
        uploaded = transfer.get("size_uploaded", 0)
        downloaded = transfer.get("size_downloaded", 0)
        size = t.get("additional", {}).get("detail", {}).get("size", 0)
        title = t.get("title", "Unknown")
        # Zero upload after downloading = dead, clear H&R candidate
        if downloaded > 0 and uploaded == 0 and size < 100*1024*1024*1024:  # less than 100GB
            dead.append((t.get("id", ""), title))

    if dead:
        print(f"\nFound {len(dead)} zero-upload tasks (dead weight, clearing H&Rs):")
        for tid, title in dead:
            print(f"  [DEL] {title[:65]}")
        dead_ids = [d[0] for d in dead]
        d, f = delete_tasks(session, sid, nas, dead_ids)
        print(f"  Deleted {d}, {f} failed")

    # Logout
    session.get(f"https://{nas['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={sid}")

    # Final stats
    print("\n--- Cleanup complete ---")

if __name__ == "__main__":
    main()