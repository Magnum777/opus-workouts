import sqlite3, os, json
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracker.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("select name from sqlite_master where type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)
for t in tables:
    cur.execute(f"select * from {t} order by rowid desc limit 1")
    cols = [d[0] for d in cur.description]
    print(f"  {t}: cols={cols}, row={cur.fetchone()}")
conn.close()
