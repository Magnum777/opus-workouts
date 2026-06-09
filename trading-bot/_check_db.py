import sqlite3, os

dbs = ['portfolio_tracker.db', 'portfolio.db', 'portfolio_history.db', 'portfolio_check.db', 'portfolio_tracking.db']

for db in dbs:
    path = os.path.join(r'C:\Users\compj\.openclaw\workspace\trading-bot', db)
    if not os.path.exists(path):
        continue
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f'\n=== {db} === Tables: {tables}')
    
    for t in tables:
        try:
            c.execute(f'SELECT * FROM "{t}" ORDER BY rowid DESC LIMIT 3')
            rows = c.fetchall()
            cols = [d[0] for d in c.description]
            for r in rows:
                print(f'  {dict(zip(cols, r))}')
        except Exception as e:
            print(f'  {t}: {e}')
    conn.close()
