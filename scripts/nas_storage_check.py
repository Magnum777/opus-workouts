"""Check NAS storage and DS auto-extract config"""
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

# Login
params = {
    "api": "SYNO.API.Auth",
    "version": "6",
    "method": "login",
    "account": nas["user"],
    "passwd": nas["password"],
    "format": "sid"
}
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params=params)
d = r.json()
if not d.get("success"):
    print("Login failed:", d)
    exit(1)
sid = d["data"]["sid"]
print("Login OK")

# Storage
r = session.get("https://{}:5001/webapi/entry.cgi".format(nas["hostname"]), params={
    "api": "SYNO.Storage.CGI.Storage", "version": "1", "method": "getinfo", "_sid": sid
})
st = r.json()
if st.get("success"):
    for v in st.get("data", {}).get("volumes", []):
        used = v.get("used", 0) / (1024**3)
        total = v.get("total", 0) / (1024**3)
        pct = v.get("used", 0) / max(v.get("total", 0), 1) * 100
        print("Volume {}: {:.0f} GB used / {:.0f} GB total ({:.1f}% used)".format(v.get("id", "?"), used, total, pct))
else:
    print("Storage error:", st.get("error"))

# DS config
print("\n=== DS Config ===")
r = session.get("https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"]), params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
print(json.dumps(r.json(), indent=2))

# Shares
print("\n=== Shares ===")
r = session.get("https://{}:5001/webapi/entry.cgi".format(nas["hostname"]), params={
    "api": "SYNO.FileStation.List", "version": "2", "method": "list_share", "_sid": sid
})
fs = r.json()
if fs.get("success"):
    for sh in fs.get("data", {}).get("shares", []):
        print("  {} ({})".format(sh.get("name"), sh.get("vol_path", "?")))

# Check video folder size via SMB
print("\n=== Video Folder Size ===")
import subprocess
try:
    result = subprocess.run(
        ['powershell', '-Command', 
         '(Get-ChildItem -Path "\\\\MND\\video" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1GB'],
        capture_output=True, text=True, timeout=60
    )
    print("  Video share: {} GB".format(float(result.stdout.strip()) if result.stdout.strip() else "N/A"))
except Exception as e:
    print("  Error checking video size: {}".format(e))

# Check for unpacked content in video share (look for .mp4, .mkv, .avi alongside .rar)
print("\n=== Checking for unpacked content ===")
try:
    # Count media files vs archive files
    result = subprocess.run(
        ['powershell', '-Command',
         '$media = (Get-ChildItem -Path "\\\\MND\\video" -Recurse -Include *.mp4,*.mkv,*.avi -File -ErrorAction SilentlyContinue | Measure-Object).Count; '
         '$archives = (Get-ChildItem -Path "\\\\MND\\video" -Recurse -Include *.rar,*.zip,*.7z -File -ErrorAction SilentlyContinue | Measure-Object).Count; '
         'Write-Output "Media: $media, Archives: $archives"'],
        capture_output=True, text=True, timeout=120
    )
    print("  " + result.stdout.strip())
except Exception as e:
    print("  Error: {}".format(e))

# Logout
session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})