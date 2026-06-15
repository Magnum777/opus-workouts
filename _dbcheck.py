import sqlite3, os

path = r'C:\Users\compj\.openclaw\workspace\trading-bot'
for f in sorted(os.listdir(path)):
    if f.endswith('.db') or f.endswith('.sqlite'):
        fp = os.path.join(path, f)
        conn = sqlite3.connect(fp)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for t in tables:
            cols = conn.execute('PRAGMA table_info("' + t[0] + '")').fetchall()
            col_str = ', '.join([c[1] + ' (' + c[2] + ')' for c in cols[:6]])
            print(f + ' -> ' + t[0] + ': [' + col_str + ']')
            try:
                rows = conn.execute('SELECT * FROM "' + t[0] + '" ORDER BY rowid DESC LIMIT 1').fetchall()
                if rows:
                    print('  Last: ' + str(rows[0]))
            except:
                pass
        conn.close()
