"""Check the 5 recently added torrents in DS"""
import requests, urllib3, urllib.parse, json
urllib3.disable_warnings()

secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
nas = {}
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "nas":
            k, v = line.split("=", 1)
            nas[k] = v

session = requests.Session()
session.verify = False

r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]
print("Login OK")

base = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])

# Search for the recently added torrents
search_terms = ["American.Dad", "Bill and Ted", "Groundhog"]
for term in search_terms:
    r = session.get(base, params={
        "api": "SYNO.DownloadStation.Task",
        "version": "3",
        "method": "list",
        "additional": "detail,transfer",
        "_sid": sid,
        "offset": 0,
        "limit": 100
    })
    data = r.json()
    if data.get("success"):
        for t in data.get("data", {}).get("tasks", []):
            title = t.get("title", "")
            if term.lower().replace(" ", "") in title.lower().replace(" ", ""):
                detail = t.get("additional", {}).get("detail", {})
                transfer = t.get("additional", {}).get("transfer", {})
                print("\nFound: {}".format(title))
                print("  Status: {}".format(t.get("status")))
                print("  Size: {} bytes".format(detail.get("size", 0)))
                print("  Downloaded: {} bytes".format(transfer.get("size_downloaded", 0)))
                print("  Uploaded: {} bytes".format(transfer.get("size_uploaded", 0)))
                print("  Seeders: {}".format(detail.get("connected_seeders", "N/A")))
                print("  Leechers: {}".format(detail.get("connected_leechers", "N/A")))
                print("  Error: {}".format(detail.get("error", "none")))
                print("  Create time: {}".format(detail.get("create_time", "N/A")))
                print("  URI: {}".format(detail.get("uri", "N/A")[:100] if detail.get("uri") else "N/A"))

# Also check for any tasks with status "downloading" or "waiting" or "error"
print("\n=== Checking recent tasks (by create time) ===")
# Get all tasks sorted by create time, find the newest ones
all_recent = []
offset = 0
while True:
    r = session.get(base, params={
        "api": "SYNO.DownloadStation.Task",
        "version": "3",
        "method": "list",
        "additional": "detail,transfer",
        "_sid": sid,
        "offset": offset,
        "limit": 100
    })
    data = r.json()
    if not data.get("success"):
        break
    tasks = data.get("data", {}).get("tasks", [])
    if not tasks:
        break
    for t in tasks:
        detail = t.get("additional", {}).get("detail", {})
        ct = detail.get("create_time", 0)
        if ct and ct > 1753500000:  # Recent timestamps (after July 2025)
            all_recent.append({
                "title": t.get("title", "?"),
                "status": t.get("status"),
                "size": detail.get("size", 0),
                "dl": t.get("additional", {}).get("transfer", {}).get("size_downloaded", 0),
                "create_time": ct,
                "error": detail.get("error", 0),
            })
    offset += 100
    if len(tasks) < 100:
        break

# Sort by create time descending
all_recent.sort(key=lambda x: x.get("create_time", 0), reverse=True)
print("Most recent tasks:")
for t in all_recent[:10]:
    sz = "{:.1f} GB".format(t["size"]/(1024**3)) if t["size"] else "0 GB"
    dl = "{:.1f} GB".format(t["dl"]/(1024**3)) if t["dl"] else "0 GB"
    from datetime import datetime
    ct = datetime.fromtimestamp(t["create_time"]).strftime("%Y-%m-%d %H:%M") if t["create_time"] else "?"
    print("  [{}] {} Size:{} DL:{} err:{} {}".format(t["status"], ct, sz, dl, t["error"], t["title"][:60]))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})