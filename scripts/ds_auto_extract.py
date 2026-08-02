"""Disable DS auto-extract and check current DS settings"""
import requests, urllib3, json
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
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]
print("Login OK")

base = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])
base2 = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])

# Get current DS config
print("\n=== Current DS Config ===")
r = session.get(base, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
config = r.json()
print(json.dumps(config, indent=2))

# Try DS2 settings
print("\n=== DS2 Settings ===")
r = session.get(base2, params={
    "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "getglobalconfig", "_sid": sid
})
print(json.dumps(r.json(), indent=2))

# Check for auto-extract/unzip settings
print("\n=== Checking auto-extract settings ===")
# DS1 auto-extract is controlled via bt_auto_extract or similar
r = session.get(base, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
conf = r.json()
if conf.get("success"):
    data = conf.get("data", {})
    print("Auto extract enabled: {}".format(data.get("auto_extract_enabled", data.get("bt_auto_extract", "not found"))))
    print("Unzip password: {}".format(data.get("unzip_password", "not found")))
    print("All config keys: {}".format(list(data.keys()) if isinstance(data, dict) else data))
    
    # Print full config for inspection
    print("\nFull DS config data:")
    print(json.dumps(data, indent=2))

# Try to set auto_extract to false
print("\n=== Disabling auto-extract via DS1 ===")
r = session.get(base, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "setconfig", 
    "auto_extract_enabled": "false",
    "_sid": sid
})
print("DS1 setconfig result: {}".format(r.json()))

# Also try DS2
print("\n=== Disabling auto-extract via DS2 ===")
r = session.get(base2, params={
    "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "setglobalconfig",
    "auto_extract_enabled": "false",
    "_sid": sid
})
print("DS2 setconfig result: {}".format(r.json()))

# Verify settings took effect
print("\n=== Verify DS Config After Change ===")
r = session.get(base, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
print(json.dumps(r.json(), indent=2))

# Also check storage via a different API
print("\n=== NAS Storage via Core.System ===")
r = session.get(base2, params={
    "api": "SYNO.Core.System", "version": "1", "method": "info", "_sid": sid
})
info = r.json()
if info.get("success"):
    data = info.get("data", {})
    print("  Uptime: {}".format(data.get("up_time", "N/A")))

# Try volume info
r = session.get(base2, params={
    "api": "SYNO.Core.System.Storage", "version": "1", "method": "list", "_sid": sid
})
storage = r.json()
if storage.get("success"):
    for vol in storage.get("data", {}).get("volumes", []):
        used = vol.get("used", 0) / (1024**3)
        total = vol.get("total", 0) / (1024**3)
        pct = used / max(total, 1) * 100
        print("  Volume {}: {:.0f} GB used / {:.0f} GB total ({:.1f}%)".format(vol.get("id", "?"), used, total, pct))

# Logout
session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})