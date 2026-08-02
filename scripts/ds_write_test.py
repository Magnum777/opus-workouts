"""Check Nova's write permissions on NAS shares and try writing a file"""
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

base = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])

# 1. Check Nova's groups
print("=== Nova's Groups ===")
r = session.get(base, params={
    "api": "SYNO.Core.User", "version": "5", "method": "get", "_sid": sid,
    "name": nas["user"]
})
user_data = r.json()
print(json.dumps(user_data, indent=2)[:3000])

# 2. List all users with full detail
print("\n=== All Users ===")
r = session.get(base, params={
    "api": "SYNO.Core.User", "version": "5", "method": "list", "_sid": sid,
    "additional": "group"
})
users = r.json()
if users.get("success"):
    for u in users.get("data", {}).get("users", []):
        print("  {} (uid: {}) groups: {} admin: {}".format(
            u.get("name"), u.get("uid"), u.get("groups", []), u.get("is_admin", "?")))

# 3. Check share permissions for Nova
print("\n=== Share Permissions ===")
r = session.get(base, params={
    "api": "SYNO.Core.Share", "version": "1", "method": "list", "_sid": sid,
    "additional": "share_group,share_user"
})
shares = r.json()
if shares.get("success"):
    for s in shares.get("data", {}).get("shares", []):
        name = s.get("name")
        # Check if Nova has permissions
        user_perms = s.get("additional", {}).get("share_user", [])
        group_perms = s.get("additional", {}).get("share_group", [])
        nova_perm = [p for p in user_perms if p.get("name") == "Nova"]
        admin_perm = [p for p in group_perms if p.get("name") == "administrators"]
        if nova_perm or admin_perm:
            print("  Share '{}': Nova={} admins={}".format(
                name, 
                nova_perm[0].get("privilege", "?") if nova_perm else "no direct perm",
                admin_perm[0].get("privilege", "?") if admin_perm else "none"
            ))

# 4. Try writing a small test file via SMB
print("\n=== Testing SMB write ===")
import subprocess
try:
    # Create a test file locally
    test_file = r"C:\Users\compj\.openclaw\workspace\scripts\test_write.txt"
    with open(test_file, "w") as f:
        f.write("Nova write test - delete me\n")
    
    # Copy to NAS home share
    result = subprocess.run(
        ['powershell', '-Command', 
         'Copy-Item -Path "{}" -Destination "\\\\MND\\home\\" -Force; if ($?) { Write-Output "SMB write OK" } else { Write-Output "SMB write FAILED" }'.format(test_file)],
        capture_output=True, text=True, timeout=15
    )
    print("  SMB write: {}".format(result.stdout.strip()))
    print("  Stderr: {}".format(result.stderr.strip()[:200] if result.stderr else "none"))
    
    # Clean up
    import os
    os.remove(test_file)
except Exception as e:
    print("  Error: {}".format(e))

# 5. Try writing via FileStation API with proper path
print("\n=== FileStation upload to /home ===")
import io
files = {"file": ("test.txt", io.BytesIO(b"Nova write test"), "text/plain")}
data = {
    "api": "SYNO.FileStation.Upload", "version": "2", "method": "upload",
    "dest_path": "/home", "create_parents": "true", "overwrite": "true", "_sid": sid
}
r = session.post(base, data=data, files=files)
print("  Upload to /home: {}".format(r.json()))

# Try /video share
files = {"file": ("test.txt", io.BytesIO(b"Nova write test"), "text/plain")}
data = {
    "api": "SYNO.FileStation.Upload", "version": "2", "method": "upload",
    "dest_path": "/video", "create_parents": "true", "overwrite": "true", "_sid": sid
}
r = session.post(base, data=data, files=files)
print("  Upload to /video: {}".format(r.json()))

# Try /downloads share
files = {"file": ("test.txt", io.BytesIO(b"Nova write test"), "text/plain")}
data = {
    "api": "SYNO.FileStation.Upload", "version": "2", "method": "upload",
    "dest_path": "/downloads", "create_parents": "true", "overwrite": "true", "_sid": sid
}
r = session.post(base, data=data, files=files)
print("  Upload to /downloads: {}".format(r.json()))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})