import sqlite3
db='C:/Users/compj/.openclaw/workspace/trading-bot/portfolio_history.db'
conn = sqlite3.connect(db)
c = conn.cursor()
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])
for t_name in [t[0] for t in tables]:
    rows = c.execute(f'SELECT * FROM "{t_name}" ORDER BY rowid DESC LIMIT 1').fetchall()
    print(f'{t_name}: {rows}')
conn.close()
