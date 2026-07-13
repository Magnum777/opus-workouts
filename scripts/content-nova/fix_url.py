import sqlite3
from pathlib import Path

vault = Path(r'C:\Users\compj\.openclaw\workspace\scripts\credentials\vault.db')
conn = sqlite3.connect(vault)
conn.execute(
    "UPDATE credentials SET value=? WHERE service='wordpress' AND key='aicofounderstack_url'",
    ('https://aicofounderstack.com',)
)
conn.commit()
row = conn.execute(
    "SELECT value FROM credentials WHERE service='wordpress' AND key='aicofounderstack_url'"
).fetchone()
print(f"Updated URL: {row[0]}")
conn.close()
