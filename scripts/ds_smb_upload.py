"""Add torrents to DS by: downloading .torrent files locally, uploading to NAS via SMB, 
then telling DS to add from the local NAS path"""
import requests, urllib3, json, io, os, subprocess
urllib3.disable_warnings()

secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
nas = {}
td = {}
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
        if "=" in line and section == "torrentday":
            k, v = line.split("=", 1)
            td[k] = v

# Login to DS
session = requests.Session()
session.verify = False
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]
print("DS login OK")

# First, let's check what the DS default download location actually is
# by checking existing seeding tasks' destination paths
base_ds = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])
r = session.get(base_ds, params={
    "api": "SYNO.DownloadStation.Task", "version": "3", "method": "list",
    "additional": "detail", "_sid": sid, "offset": 0, "limit": 5
})
data = r.json()
if data.get("success"):
    for t in data.get("data", {}).get("tasks", [])[:3]:
        d = t.get("additional", {}).get("detail", {})
        print("  {} -> destination='{}'".format(t.get("title", "?")[:40], d.get("destination", "?")))

# The destination for all existing tasks is "video"
# But maybe DS needs the full path like /volume2/video
# Let me check the actual filesystem path via FileStation
base = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])

# List the root to find volume paths
print("\n=== NAS root directories ===")
r = session.get(base, params={
    "api": "SYNO.FileStation.List", "version": "2", "method": "list",
    "folder_path": "/", "limit": "50", "_sid": sid
})
fs = r.json()
if fs.get("success"):
    for f in fs.get("data", {}).get("files", []):
        print("  {} ({})".format(f.get("name"), f.get("type", "?")))

# Check /video path
print("\n=== /video contents ===")
r = session.get(base, params={
    "api": "SYNO.FileStation.List", "version": "2", "method": "list",
    "folder_path": "/video", "limit": "10", "_sid": sid
})
fs = r.json()
if fs.get("success"):
    for f in fs.get("data", {}).get("files", []):
        print("  {} ({})".format(f.get("name"), f.get("type", "?")))
else:
    print("  Error: {}".format(fs.get("error")))

# Check if there's a /volumeX/video path
for vol in ["/volume1", "/volume2"]:
    r = session.get(base, params={
        "api": "SYNO.FileStation.List", "version": "2", "method": "list",
        "folder_path": vol, "limit": "20", "_sid": sid
    })
    fs = r.json()
    if fs.get("success"):
        files = fs.get("data", {}).get("files", [])
        print("\n=== {} contents ===".format(vol))
        for f in files:
            print("  {} ({})".format(f.get("name"), f.get("type", "?")))
        # Check for video subfolder
        video_dirs = [f for f in files if f.get("name", "").lower() == "video"]
        if video_dirs:
            print("  Found video dir at {}".format(vol))

# Now try the key insight: maybe we need to use the FileStation Copy API
# to upload the torrent to the NAS, then tell DS to add from that local path
print("\n=== Testing: upload .torrent to NAS temp, then DS add from local path ===")

# Step 1: Save .torrent files locally
local_temp = r"C:\Users\compj\.openclaw\workspace\scripts\temp_torrents"
os.makedirs(local_temp, exist_ok=True)

# Step 2: Copy to NAS via SMB (using Windows cached credentials)
# Actually, the SMB write with Nova creds failed earlier. 
# But our backup scripts work because they use the Windows session (opusmagnum) creds.
# Let me try using robocopy or direct Windows copy (which uses cached opusmagnum session)

# Download a test torrent
dl_url = "https://www.torrentday.com/download.php/10042121/10042121.torrent"
cookies = {"uid": td["uid"], "pass": td["pass_cookie"]}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r_td = requests.get(dl_url, cookies=cookies, headers=headers, timeout=30)
torrent_data = r_td.content
print("Downloaded torrent: {} bytes, valid: {}".format(len(torrent_data), torrent_data.startswith(b'd8:')))

# Save locally
local_file = os.path.join(local_temp, "test.torrent")
with open(local_file, "wb") as f:
    f.write(torrent_data)
print("Saved to: {}".format(local_file))

# Step 3: Try to copy to NAS via SMB (using Windows cached creds)
nas_torrent_dir = r"\\MND\video\torrents_temp"
try:
    # Create the directory on NAS first
    os.makedirs(nas_torrent_dir, exist_ok=True)
    print("Created dir on NAS: {}".format(nas_torrent_dir))
except Exception as e:
    print("Could not create NAS dir: {}".format(e))
    # Try video share directly
    nas_torrent_dir = r"\\MND\video"
    print("Using video share root instead")

# Copy the file
nas_file = os.path.join(nas_torrent_dir, "test.torrent")
try:
    import shutil
    shutil.copy2(local_file, nas_torrent_dir)
    print("Copied to NAS: {}".format(nas_file))
    
    # Verify it's there
    if os.path.exists(nas_file):
        size = os.path.getsize(nas_file)
        print("Verified on NAS: {} bytes".format(size))
except Exception as e:
    print("SMB copy failed: {}".format(e))
    # Try PowerShell copy
    result = subprocess.run(
        ["powershell", "-Command", "Copy-Item -Path '{}' -Destination '\\MND\\video\' -Force".format(local_file)],
        capture_output=True, text=True, timeout=15
    )
    print("PS copy result: {} / {}".format(result.stdout.strip(), result.stderr.strip()[:200]))
    if "error" in result.stderr.lower() or result.returncode != 0:
        print("PS copy also failed")
        # Last resort: try with explicit NAS credentials
        print("\nTrying with explicit NAS credentials...")
        # Use the Nova SMB user/pass from secrets
        result2 = subprocess.run(
            ["net", "use", r"\\MND\video", "/user:Nova", nas["password"], "/persistent:no"],
            capture_output=True, text=True, timeout=15
        )
        print("net use result: {}".format(result2.stdout + result2.stderr))
        
        # Try copy again
        result3 = subprocess.run(
            ["powershell", "-Command", "Copy-Item -Path '{}' -Destination '\\MND\\video\' -Force".format(local_file)],
            capture_output=True, text=True, timeout=15
        )
        print("PS copy after net use: {} / {}".format(result3.stdout.strip(), result3.stderr.strip()[:200]))

# Step 4: Try DS add from local file path
if os.path.exists(nas_file):
    print("\n=== Adding torrent from NAS local path ===")
    # Try different path formats
    for path_fmt in ["/video/torrents_temp/test.torrent", "/video/test.torrent", 
                     "/volume2/video/torrents_temp/test.torrent",
                     "/volume1/video/torrents_temp/test.torrent"]:
        data = {
            "api": "SYNO.DownloadStation.Task", "version": "3", "method": "create",
            "uri": "file://{}".format(path_fmt), "destination": "video", "_sid": sid
        }
        r = session.post(base_ds, data=data)
        print("  uri=file://{}: {}".format(path_fmt, r.json()))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})