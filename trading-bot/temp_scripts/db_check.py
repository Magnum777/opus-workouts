import sqlite3
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio.db'
con = sqlite3.connect(db_path)
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [t[0] for t in tables])
for t in [r[0] for r in tables]:
    cols = con.execute("PRAGMA table_info(%s)" % t).fetchall()
    print("\n=== %s ===" % t)
    print("Columns:", [c[1] for c in cols])
    rows = con.execute("SELECT * FROM %s ORDER BY rowid DESC LIMIT 3" % t).fetchall()
    for r in rows:
        print(r)
con.close()
