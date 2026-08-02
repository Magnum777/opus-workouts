"""
Seed indefinitely enforcer for Download Station.
Resumes finished (non-seeding) completed tasks and sets seeding policy.
Run periodically or via cron.
"""
import requests, urllib3, json, sys
urllib3.disable_warnings()

SECRETS_PATH = r"C:\Users\compj\.openclaw\workspace\.secrets"

def load_secrets():
    secrets = {}
    section = ""
    with open(SECRETS_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("["):
                section = line.strip("[]")
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                secrets.setdefault(section, {})[k] = v
    return secrets

def main():
    try:
        _main()
    except Exception as e:
        print(f"FATAL: ds_seed_enforcer crashed: {e}", file=sys.stderr)
        sys.exit(1)

def _main():
    secrets = load_secrets()
    nas = secrets["nas"]
    
    session = requests.Session()
    session.verify = False
    session.timeout = 15  # Default timeout for all requests
    
    # Login
    r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
        "api": "SYNO.API.Auth", "version": "6", "method": "login",
        "account": nas["user"], "passwd": nas["password"], "format": "sid"
    })
    result = r.json()
    if not result.get("success"):
        print("Login failed:", result)
        return
    sid = result["data"]["sid"]
    print("DSM login OK")
    
    base = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])
    
    # Try to set seeding policy via API
    print("\n=== Setting seeding policy to indefinite ===")
    
    # DS1 setconfig
    r = session.get(base, params={
        "api": "SYNO.DownloadStation.Info", "version": "1", "method": "setconfig",
        "seed_ratio": "0",          # 0 = no limit
        "seed_time": "0",            # 0 = no limit
        "bt_max_download": "-1",     # unlimited
        "bt_max_upload": "-1",       # unlimited
        "_sid": sid
    })
    print("DS1 setconfig:", r.json())
    
    # DS2 settings
    base2 = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])
    r = session.get(base2, params={
        "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "setglobalconfig",
        "seed_ratio": "0",
        "seed_time": "0",
        "_sid": sid
    })
    print("DS2 setconfig:", r.json())
    
    # Try BT-specific settings
    r = session.get(base, params={
        "api": "SYNO.DownloadStation.BTSearch", "version": "1", "method": "setconfig",
        "seed_ratio": "0",
        "seed_time": "0",
        "_sid": sid
    })
    print("BT setconfig:", r.json())
    
    # Get all finished (non-seeding) tasks and resume them
    print("\n=== Resuming finished tasks ===")
    offset = 0
    resumed = 0
    errors = 0
    finished_ids = []
    
    while True:
        r = session.get(base, params={
            "api": "SYNO.DownloadStation.Task", "version": "3", "method": "list",
            "additional": "detail,transfer", "_sid": sid, "offset": offset, "limit": 100
        })
        data = r.json()
        if not data.get("success"):
            break
        tasks = data.get("data", {}).get("tasks", [])
        if not tasks:
            break
        
        for t in tasks:
            if t.get("status") == "finished":
                tid = t.get("id")
                title = t.get("title", "?")[:60]
                finished_ids.append((tid, title))
        
        offset += 100
        if len(tasks) < 100:
            break
    
    print("Found {} finished (non-seeding) tasks".format(len(finished_ids)))
    
    # Resume them in batches
    batch_size = 25
    for i in range(0, len(finished_ids), batch_size):
        batch = finished_ids[i:i+batch_size]
        ids = ",".join([tid for tid, _ in batch])
        r = session.get(base, params={
            "api": "SYNO.DownloadStation.Task", "version": "3", "method": "resume",
            "id": ids, "_sid": sid
        })
        result = r.json()
        if result.get("success"):
            # Check which ones actually resumed
            for item in result.get("data", []):
                if item.get("error", 0) == 0:
                    resumed += 1
                else:
                    errors += 1
            print("  Resumed batch {}/{} ({} tasks)".format(i//batch_size+1, (len(finished_ids)+batch_size-1)//batch_size, len(batch)))
        else:
            print("  Batch resume failed: {}".format(result))
            errors += len(batch)
    
    print("\n=== Results ===")
    print("Resumed: {}/{} tasks".format(resumed, len(finished_ids)))
    if errors:
        print("Errors: {}".format(errors))
    
    # Verify
    print("\n=== Verifying status ===")
    r = session.get(base, params={
        "api": "SYNO.DownloadStation.Task", "version": "3", "method": "list",
        "additional": "", "_sid": sid, "offset": 0, "limit": 1
    })
    
    # Count statuses
    offset = 0
    statuses = {}
    while True:
        r = session.get(base, params={
            "api": "SYNO.DownloadStation.Task", "version": "3", "method": "list",
            "additional": "", "_sid": sid, "offset": offset, "limit": 100
        })
        data = r.json()
        if not data.get("success"): break
        tasks = data.get("data", {}).get("tasks", [])
        if not tasks: break
        for t in tasks:
            s = t.get("status")
            statuses[s] = statuses.get(s, 0) + 1
        offset += 100
        if len(tasks) < 100: break
    
    print("Status counts: {}".format(statuses))
    
    # Logout
    session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
        "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
    })

if __name__ == "__main__":
    main()