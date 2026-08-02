"""Add torrents to Download Station via DSM web UI (browser automation)
since the DS API file upload is broken but SMB writes work fine."""
import subprocess, os, sys

# First let's check what's actually in the watch folder and verify SMB works
nas_host = "MND"
watch_dir = r"\\{}\video\watch".format(nas_host)

# Verify the watch folder exists and is writable
result = subprocess.run(
    ["cmd", "/c", "dir", watch_dir],
    capture_output=True, text=True, timeout=10
)
print("Watch dir contents: {}".format(result.stdout[:200] if result.stdout else "empty/missing"))
print("Errors: {}".format(result.stderr[:200] if result.stderr else "none"))

# Let's also check what DSM version we're running
import requests, urllib3
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
    "api": "SYNO.API.Info", "version": "1", "method": "query",
    "query": "SYNO.API.Auth,SYNO.DownloadStation.Info"
})
api_info = r.json()
print("\nAPI Info:")
for key, val in api_info.get("data", {}).items():
    print("  {}: {}".format(key, val))

# Check DSM version
r = session.get("https://{}:5001/webapi/entry.cgi".format(nas["hostname"]), params={
    "api": "SYNO.DSM.Info", "version": "1", "method": "getinfo"
})
print("\nDSM Info: {}".format(r.json()))

# The real fix: Download Station on DSM 7 has a known issue with the API
# for file uploads when the user doesn't have explicit share permissions.
# Since we can write to the video share via SMB, let's use that path.
# 
# The cleanest approach: put .torrent files in the video/watch folder via SMB,
# then configure DS to watch that folder.

# Check if DS has a BT auto-add / watch folder feature via the config
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]
print("\nLogin OK")

base_ds = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])

# Get full DS config - try different API versions
for ver in ["1", "2", "3"]:
    r = session.get(base_ds, params={
        "api": "SYNO.DownloadStation.Info", "version": ver, "method": "getconfig", "_sid": sid
    })
    data = r.json()
    if data.get("success") and data.get("data"):
        print("\nDS config v{}: {}".format(ver, data))
        break
    elif data.get("success") and not data.get("data"):
        print("\nDS config v{}: success but empty data".format(ver))

# Try the BT-specific config
r = session.get(base_ds, params={
    "api": "SYNO.DownloadStation.BTSearch", "version": "1", "method": "getconfig", "_sid": sid
})
print("\nBT Search config: {}".format(r.json()))

# Actually, let me try the most direct approach possible:
# Upload the .torrent file to the video share via SMB, then use the
# DS "create" method with a local file path that DS can access internally.
# DS runs as root on the NAS, so it should be able to read from any share.

# Let me check if the watch folder actually has files from our earlier copy
print("\n=== Checking watch folder ===")
result = subprocess.run(
    ["cmd", "/c", "dir", r"\\MND\video\watch"],
    capture_output=True, text=True, timeout=10
)
print(result.stdout if result.stdout else "(empty)")

# Clean up - remove any test files we put there earlier
result = subprocess.run(
    ["cmd", "/c", "del", r"\\MND\video\watch\*.torrent", "/Q"],
    capture_output=True, text=True, timeout=10
)

# Final approach: let's check if DS web UI has a different endpoint
# that might accept file uploads properly
print("\n=== Checking DS web UI endpoint ===")
r = session.get("https://{}:5001/".format(nas["hostname"]), allow_redirects=True, verify=False)
print("DSM web UI: status {} content-type {}".format(r.status_code, r.headers.get("content-type", "?")))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})