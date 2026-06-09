import sqlite3, os
d = os.path.join(os.path.expanduser('~'),'.openclaw','workspace','trading-bot','portfolio.db')
conn = sqlite3.connect(d)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)
for t in tables:
    c.execute(f"SELECT * FROM {t} ORDER BY rowid DESC LIMIT 3")
    rows = c.fetchall()
    print(f'{t}:', rows)
conn.close()
