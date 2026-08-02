"""Quick test: fetch all DS tasks via paginated DS1 API"""
import requests, json, urllib3, urllib.parse
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
            k, v = line.split("=", 1)
            nas_creds[k] = v

encoded_pass = urllib.parse.quote(nas_creds["password"])
login_url = "https://{}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account={}&passwd={}&format=sid".format(nas_creds["hostname"], nas_creds["user"], encoded_pass)

session = requests.Session()
session.verify = False
resp = session.get(login_url)
data = resp.json()
sid = data["data"]["sid"]
print("Logged in OK")

base = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas_creds["hostname"])

# Get total count first
resp = session.get(base, params={
    "api": "SYNO.DownloadStation.Task",
    "version": "3",
    "method": "list",
    "additional": "detail,transfer",
    "_sid": sid,
    "offset": 0,
    "limit": 1
})
data = resp.json()
total = data.get("data", {}).get("total", 0)
print("Total tasks: {}".format(total))

# Paginate through all tasks
all_tasks = []
offset = 0
limit = 100
while offset < total:
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
        print("Error at offset {}: {}".format(offset, data))
        break
    tasks = data.get("data", {}).get("tasks", [])
    if not tasks:
        break
    all_tasks.extend(tasks)
    print("  Fetched {} tasks (offset {}), total so far: {}".format(len(tasks), offset, len(all_tasks)))
    offset += limit

print("\nTotal fetched: {}".format(len(all_tasks)))

# Show top 20 by upload
all_tasks.sort(key=lambda t: t.get("additional", {}).get("transfer", {}).get("size_uploaded", 0), reverse=True)
print("\nTop 20 by upload:")
for i, t in enumerate(all_tasks[:20], 1):
    tr = t.get("additional", {}).get("transfer", {})
    dt = t.get("additional", {}).get("detail", {})
    ul_gb = tr.get("size_uploaded", 0) / (1024**3)
    dl_gb = tr.get("size_downloaded", 0) / (1024**3)
    sz_gb = dt.get("size", 0) / (1024**3) if dt.get("size", 0) else 0
    title = t.get("title", "Unknown")[:55]
    status = t.get("status", "")
    print("  {:>2}. UL:{:>7.1f}GB DL:{:>7.1f}GB Size:{:>6.1f}GB [{}] {}".format(i, ul_gb, dl_gb, sz_gb, status, title))

# Show top release names for cross-seed matching
print("\nTop 50 release names (for cross-seed matching):")
for t in all_tasks[:50]:
    title = t.get("title", "")
    sz = t.get("additional", {}).get("detail", {}).get("size", 0)
    ul = t.get("additional", {}).get("transfer", {}).get("size_uploaded", 0)
    print("  {} | {} bytes | {} bytes up".format(title[:70], sz, ul))

# Logout
session.get("https://{}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={}".format(nas_creds["hostname"], sid))