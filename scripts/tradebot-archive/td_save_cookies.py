import sqlite3
import os
import re

# Copy and extract cookies from Firefox
src = r"C:\Users\compj\AppData\Roaming\Mozilla\Firefox\Profiles\dnhgd3mm.default-release\cookies.sqlite"
dst = os.path.join(os.environ['TEMP'], 'firefox_cookies_copy3.sqlite')
import shutil
shutil.copy2(src, dst)

conn = sqlite3.connect(dst)
cur = conn.cursor()
cur.execute("SELECT name, value, host FROM moz_cookies WHERE host LIKE '%torrentday%'")
rows = cur.fetchall()
conn.close()

# Build cookie dict
cookies = {}
for name, value, host in rows:
    cookies[name] = value

# Read existing .secrets
secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
with open(secrets_path) as f:
    content = f.read()

# Update/add torrentday section
new_section = f"""[torrentday]
username=opusmagnum
password=Dr34k3r!123123
uid={cookies.get('uid', '')}
pass_cookie={cookies.get('pass', '')}
td_theme={cookies.get('td_theme', 'dark')}"""

# Replace existing torrentday section or append
if '[torrentday]' in content:
    content = re.sub(r'\[torrentday\].*?(?=\n\[|\Z)', new_section, content, flags=re.DOTALL)
else:
    content = content.rstrip() + '\n\n' + new_section + '\n'

with open(secrets_path, 'w') as f:
    f.write(content)

print("Cookies saved to .secrets:")
print(f"  uid={cookies.get('uid', 'NOT FOUND')}")
print(f"  pass_cookie={cookies.get('pass', '')[:10]}...")