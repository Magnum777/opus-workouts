"""Prune all error-status torrents from Download Station"""
import requests, urllib3, urllib.parse
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
login_url = (
    "https://{}:5001/webapi/auth.cgi"
    "?api=SYNO.API.Auth&version=6&method=login"
    "&account={}&passwd={}&format=sid"
).format(nas_creds["hostname"], nas_creds["user"], encoded_pass)

session = requests.Session()
session.verify = False
resp = session.get(login_url)
data = resp.json()
sid = data["data"]["sid"]
print("Logged in")

base = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas_creds["hostname"])

# Collect all error task IDs
offset = 0
limit = 100
error_ids = []
error_names = []
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
    for t in tasks:
        if t.get("status") == "error":
            error_ids.append(t.get("id", ""))
            error_names.append(t.get("title", "Unknown")[:60])
    offset += limit
    if len(tasks) < limit:
        break

print("Found {} error tasks, deleting...".format(len(error_ids)))

deleted = 0
failed = 0
for i, eid in enumerate(error_ids):
    resp = session.get(base, params={
        "api": "SYNO.DownloadStation.Task",
        "version": "3",
        "method": "delete",
        "id": eid,
        "delete_files": "true",
        "_sid": sid
    })
    result = resp.json()
    if result.get("success"):
        deleted += 1
        print("  OK: {}".format(error_names[i]))
    else:
        failed += 1
        print("  FAIL: {} - {}".format(error_names[i], result.get("error", {})))

print()
print("Done: {} deleted, {} failed".format(deleted, failed))

session.get(
    "https://{}:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={}"
    .format(nas_creds["hostname"], sid)
)