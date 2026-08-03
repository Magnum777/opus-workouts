# Extract TorrentDay cookies from Firefox SQLite database
# Firefox locks the DB while running, so we copy it first
$dbPath = "C:\Users\compj\AppData\Roaming\Mozilla\Firefox\Profiles\dnhgd3mm.default-release\cookies.sqlite"
$tmpPath = "$env:TEMP\firefox_cookies_copy.sqlite"

# Copy to temp (avoids lock issues)
Copy-Item $dbPath $tmpPath -Force
Write-Host "Copied cookies database"

# Query using System.Data.SQLite or just parse with strings as fallback
# Try loading the SQLite DLL from Firefox
Add-Type -Path "C:\Program Files\Mozilla Firefox\mozsqlite3.dll" -ErrorAction SilentlyContinue

# Use the copy with Python which has sqlite3 built-in
$python = @"
import sqlite3
import json
import os

db_path = os.environ['TEMP'] + r'\firefox_cookies_copy.sqlite'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Search for torrentday cookies
cur.execute("SELECT name, value, host, path, isSecure, isHttpOnly, expiry FROM moz_cookies WHERE host LIKE '%torrentday%'")
rows = cur.fetchall()

if rows:
    print(f"Found {len(rows)} TorrentDay cookies:")
    cookies = {}
    for name, value, host, path, secure, httponly, expiry in rows:
        print(f"  {name}={value[:30]}... host={host} secure={secure} httponly={httponly}")
        cookies[name] = value
    print(f"\nKey cookies: uid={cookies.get('uid', 'NOT FOUND')}, pass={cookies.get('pass', 'NOT FOUND')[:20]}...")
else:
    print("No torrentday cookies found. Checking all domains...")
    cur.execute("SELECT DISTINCT host FROM moz_cookies ORDER BY host")
    for row in cur.fetchall():
        print(f"  {row[0]}")

conn.close()
"@

$python | python