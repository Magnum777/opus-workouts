import sqlite3

path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio.db'
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f'Tables: {tables}')
for t in tables:
    cur.execute(f'SELECT * FROM "{t}" ORDER BY rowid DESC LIMIT 5')
    rows = cur.fetchall()
    cur.execute(f'PRAGMA table_info("{t}")')
    cols = [c[1] for c in cur.fetchall()]
    print(f'  {t}: cols={cols}')
    for r in rows:
        print(f'    {r}')
conn.close()
