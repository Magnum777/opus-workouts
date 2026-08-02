import sqlite3
import json
import os

db_path = os.path.join(os.environ.get('TEMP', ''), 'firefox_cookies_copy2.sqlite')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name, value, host, path, isSecure, isHttpOnly, expiry FROM moz_cookies WHERE host LIKE '%torrentday%'")
rows = cur.fetchall()

cookies = {}
for name, value, host, path, secure, httponly, expiry in rows:
    cookies[name] = {"value": value, "host": host, "path": path, "secure": bool(secure), "httponly": bool(httponly)}

print(json.dumps(cookies, indent=2))
conn.close()