import sqlite3, os
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracking.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)
for t in tables:
    c.execute('PRAGMA table_info("%s")' % t)
    cols = [r[1] for r in c.fetchall()]
    print('  %s cols: %s' % (t, cols))
    c.execute('SELECT * FROM "%s" ORDER BY rowid DESC LIMIT 3' % t)
    for r in c.fetchall():
        print('    ', r)
conn.close()
