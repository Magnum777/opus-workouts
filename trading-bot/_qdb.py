import sqlite3, os
dbs = ['portfolio_history.db', 'portfolio_tracker.db', 'portfolio_tracking.db', 'portfolio_check.db', 'portfolio.db']
base = r'C:\Users\compj\.openclaw\workspace\trading-bot'
for db in dbs:
    path = os.path.join(base, db)
    if os.path.exists(path):
        print(f'=== {db} ===')
        try:
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for t in c.fetchall():
                tname = t[0]
                c.execute(f'PRAGMA table_info("{tname}")')
                cols = [x[1] for x in c.fetchall()]
                print(f'  {tname}: {cols}')
                c.execute(f'SELECT * FROM "{tname}" ORDER BY rowid DESC LIMIT 3')
                for r in c.fetchall():
                    print(f'    {r}')
            conn.close()
        except Exception as e:
            print(f'  error: {e}')
