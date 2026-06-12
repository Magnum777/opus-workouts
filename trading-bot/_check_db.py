import sqlite3, os
base = r'C:\Users\compj\.openclaw\workspace\trading-bot'
for fname in ['portfolio_tracker.db', 'portfolio_history.db', 'portfolio_check.db', 'portfolio_tracking.db', 'portfolio.db']:
    path = os.path.join(base, fname)
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f'=== {fname} || tables: {tables} ===')
    for t in tables:
        try:
            c.execute(f'SELECT * FROM "{t}" ORDER BY rowid DESC LIMIT 3')
            cols = [d[0] for d in c.description]
            rows = c.fetchall()
            print(f'  [{t}] cols={cols}')
            for r in rows: print(f'    {r}')
        except Exception as e:
            print(f'  [{t}] error: {e}')
    conn.close()
    print()
