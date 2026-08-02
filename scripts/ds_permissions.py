"""Check and fix DS permissions for Nova user"""
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

# Login as Nova (admin)
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]
print("Nova login OK, SID: {}".format(sid[:8]))

base = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])

# 1. Check Nova's DSM group membership
print("\n=== Nova's DSM Groups ===")
r = session.get(base, params={
    "api": "SYNO.Core.User", "version": "1", "method": "get", "_sid": sid,
    "name": nas["user"]
})
print(json.dumps(r.json(), indent=2))

# 2. List all DSM users
print("\n=== All DSM Users ===")
r = session.get(base, params={
    "api": "SYNO.Core.User", "version": "1", "method": "list", "_sid": sid
})
users = r.json()
if users.get("success"):
    for u in users.get("data", {}).get("users", []):
        print("  {} (groups: {})".format(u.get("name"), u.get("groups", "?")))

# 3. Check Download Station permissions
print("\n=== Download Station Permissions ===")
r = session.get(base, params={
    "api": "SYNO.Core.Group", "version": "1", "method": "list", "_sid": sid
})
print(json.dumps(r.json(), indent=2)[:2000])

# 4. Check DS task creation permission specifically
# DS has its own permission system - check if Nova has download permission
print("\n=== DS Task Permission Check ===")
r = session.get(base, params={
    "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "getglobalconfig", "_sid": sid
})
print("DS2 global config: {}".format(json.dumps(r.json(), indent=2)))

# 5. Try the DS1 getconfig - it returned empty data before
base_ds = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])
r = session.get(base_ds, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
conf = r.json()
print("\nDS1 getconfig: {}".format(json.dumps(conf, indent=2)))

# 6. Check if there's a package-specific permission system
print("\n=== Package Permission Check ===")
r = session.get(base, params={
    "api": "SYNO.Core.Package.Permission", "version": "1", "method": "get", "_sid": sid,
    "package": "DownloadStation"
})
print("DS package perm: {}".format(json.dumps(r.json(), indent=2)[:2000]))

# 7. Try getting DS settings via DS2 Setting API
r = session.get(base, params={
    "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "get", "_sid": sid
})
print("\nDS2 settings: {}".format(json.dumps(r.json(), indent=2)[:2000]))

# 8. Check the destination sharing settings
r = session.get(base, params={
    "api": "SYNO.DownloadStation2.Setting", "version": "1", "method": "getlocation", "_sid": sid
})
print("\nDS2 locations: {}".format(json.dumps(r.json(), indent=2)[:2000]))

# 9. Try DSM Core share permissions
r = session.get(base, params={
    "api": "SYNO.Core.Share.Permission", "version": "1", "method": "get", "_sid": sid
})
print("\nShare permissions: {}".format(json.dumps(r.json(), indent=2)[:2000]))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})