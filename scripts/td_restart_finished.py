"""Restart all finished (not seeding) torrents in Download Station."""
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
    """Get ALL tasks with details"""
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

def restart_task(session, sid, nas, task_id, task_title):
    """Resume a finished task to start seeding again"""
    base = f"https://{nas['hostname']}:5001/webapi/DownloadStation/task.cgi"
    resp = session.post(base, data={
        "api": "SYNO.DownloadStation.Task",
        "version": "3",
        "method": "resume",
        "id": task_id,
        "_sid": sid
    })
    result = resp.json()
    return result.get("success", False)

def main():
    secrets = load_secrets()
    session, sid = ds_session(secrets)
    nas = secrets["nas"]

    print("Fetching all DS tasks...")
    tasks = get_all_tasks(session, sid, nas)

    # Find finished tasks that aren't seeding
    finished = [t for t in tasks if t.get("status") == "finished"]
    seeding = [t for t in tasks if t.get("status") in ("seeding", 8)]
    downloading = [t for t in tasks if t.get("status") in ("downloading", 5)]
    error = [t for t in tasks if t.get("status") == "error"]

    print(f"Total tasks: {len(tasks)}")
    print(f"Seeding: {len(seeding)}")
    print(f"Finished (not seeding): {len(finished)}")
    print(f"Downloading: {len(downloading)}")
    print(f"Errors: {len(error)}")
    print()

    if not finished:
        print("No finished tasks to restart.")
        return

    print(f"Restarting {len(finished)} finished tasks...")
    success = 0
    fail = 0

    for t in finished:
        task_id = t.get("id", "")
        title = t.get("title", "Unknown")
        result = restart_task(session, sid, nas, task_id, title)
        if result:
            success += 1
            print(f"  [OK] {title[:60]}")
        else:
            fail += 1
            print(f"  [FAIL] {title[:60]}")

    print(f"\nDone! Restarted {success} tasks, {fail} failed.")

    # Also check error tasks
    if error:
        print(f"\n--- Error tasks ({len(error)}) ---")
        for t in error:
            detail = t.get("additional", {}).get("detail", {})
            err = detail.get("error", 0)
            title = t.get("title", "Unknown")
            print(f"  Error {err}: {title[:60]}")

    # Logout
    session.get(f"https://{nas['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={sid}")

if __name__ == "__main__":
    main()