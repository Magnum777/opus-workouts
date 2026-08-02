"""Fix DS task listing - use correct API endpoint"""
import requests
import json
import urllib3
urllib3.disable_warnings()

secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
nas_creds = {}
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "nas":
            key, val = line.split("=", 1)
            nas_creds[key] = val

import urllib.parse
encoded_pass = urllib.parse.quote(nas_creds["password"])
login_url = f"https://{nas_creds['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account={nas_creds['user']}&passwd={encoded_pass}&format=sid"

session = requests.Session()
session.verify = False
resp = session.get(login_url)
data = resp.json()
if not data.get("success"):
    print(f"Login failed: {data}")
    exit(1)
sid = data["data"]["sid"]
print(f"DSM login OK, SID: {sid[:10]}...")

base = f"https://{nas_creds['hostname']}:5001/webapi/entry.cgi"

# Try DS2 Task List with different versions and params
print("\n=== DS2 Task List v1 ===")
resp = session.get(base, params={
    "api": "SYNO.DownloadStation2.Task.List",
    "version": "1",
    "method": "list",
    "_sid": sid
})
data = resp.json()
print(f"Success: {data.get('success')}")
if data.get("success"):
    print(f"Keys: {list(data.get('data', {}).keys())}")
    tasks = data.get("data", {}).get("task_list", data.get("data", {}).get("tasks", []))
    print(f"Tasks: {len(tasks)}")
    if tasks:
        for t in tasks[:5]:
            print(f"  [{t.get('status')}] {t.get('title', 'N/A')[:60]}")
else:
    print(f"Error: {data.get('error')}")

# Try DS2 Task v2
print("\n=== DS2 Task v2 ===")
resp = session.get(base, params={
    "api": "SYNO.DownloadStation2.Task",
    "version": "2",
    "method": "list",
    "_sid": sid
})
data = resp.json()
print(f"Success: {data.get('success')}")
if data.get("success"):
    print(f"Data: {json.dumps(data.get('data', {}), indent=2)[:500]}")

# Try DS1 Task API with different endpoint
print("\n=== DS1 Task API (task.cgi) ===")
resp = session.get(f"https://{nas_creds['hostname']}:5001/webapi/DownloadStation/task.cgi", params={
    "api": "SYNO.DownloadStation.Task",
    "version": "3",
    "method": "list",
    "additional": "detail,transfer,tracker",
    "_sid": sid
})
data = resp.json()
print(f"Success: {data.get('success')}")
if data.get("success"):
    total = data.get("data", {}).get("total", 0)
    tasks = data.get("data", {}).get("tasks", [])
    print(f"Total tasks: {total}, Returned: {len(tasks)}")
    
    # Count by status
    statuses = {}
    upload_total = 0
    download_total = 0
    for t in tasks:
        s = t.get("status")
        statuses[s] = statuses.get(s, 0) + 1
        if t.get("additional", {}).get("transfer", {}).get("size_uploaded"):
            upload_total += t["additional"]["transfer"]["size_uploaded"]
        if t.get("additional", {}).get("transfer", {}).get("size_downloaded"):
            download_total += t["additional"]["transfer"]["size_downloaded"]
    
    print(f"Statuses: {statuses}")
    print(f"Total uploaded: {upload_total / 1024**3:.2f} GB")
    print(f"Total downloaded: {download_total / 1024**3:.2f} GB")
    
    # Top uploaders
    sorted_tasks = sorted(tasks, key=lambda t: t.get("additional", {}).get("transfer", {}).get("size_uploaded", 0), reverse=True)
    print(f"\nTop 10 uploaders:")
    for t in sorted_tasks[:10]:
        ul = t.get("additional", {}).get("transfer", {}).get("size_uploaded", 0) / 1024**2
        dl = t.get("additional", {}).get("transfer", {}).get("size_downloaded", 0) / 1024**2
        sz = t.get("additional", {}).get("detail", {}).get("size", 0) / 1024**2
        ratio = t["additional"]["transfer"]["size_uploaded"] / max(t["additional"]["detail"]["size"], 1) if t.get("additional", {}).get("detail", {}).get("size") else 0
        print(f"  R:{ratio:.2f} UL:{ul:.0f}MB DL:{dl:.0f}MB Size:{sz:.0f}MB [{t.get('status')}] {t.get('title', 'N/A')[:50]}")
    
    # Currently seeding count
    seeding = [t for t in tasks if t.get("status") == "seeding" or t.get("status") == 8]
    downloading = [t for t in tasks if t.get("status") == "downloading" or t.get("status") == 5]
    print(f"\nCurrently seeding: {len(seeding)}")
    print(f"Currently downloading: {len(downloading)}")
else:
    print(f"Error: {data.get('error')}")

# Logout
session.get(f"https://{nas_creds['hostname']}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={sid}")
print("\nDone")