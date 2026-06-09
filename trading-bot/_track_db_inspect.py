import sqlite3, os
path = "C:\\Users\\compj\\.openclaw\\workspace\\trading-bot\\portfolio_tracker.db"
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
for t in tables:
    print("Table:", t[0])
    c.execute('PRAGMA table_info("' + t[0] + '")')
    cols = [col[1] for col in c.fetchall()]
    print("  Columns:", ", ".join(cols))
    c.execute('SELECT * FROM "' + t[0] + '" ORDER BY rowid DESC LIMIT 3')
    rows = c.fetchall()
    for r in rows:
        print("  ", r)
conn.close()
