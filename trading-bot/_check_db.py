import sqlite3, json, datetime
db = sqlite3.connect(r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracker.db')
c = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", [t[0] for t in tables])
for t in tables:
    cols = db.execute(f"PRAGMA table_info({t[0]})").fetchall()
    print(f"  {t[0]} columns:", [(c[1], c[2]) for c in cols])
    rows = db.execute(f"SELECT * FROM {t[0]} ORDER BY rowid DESC LIMIT 3").fetchall()
    for r in rows:
        print(f"    {r}")
db.close()
