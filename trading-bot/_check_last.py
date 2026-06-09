import sqlite3
conn = sqlite3.connect(r'C:\Users\compj\.openclaw\workspace\trading-bot\trades.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('Tables:', tables)

# Try known table names
for tbl in ['portfolio_history', 'portfolio_snapshots', 'check_history', 'balance_log']:
    try:
        c.execute(f'SELECT value, timestamp FROM {tbl} ORDER BY timestamp DESC LIMIT 1')
        row = c.fetchone()
        if row:
            print(f'Table {tbl}: last value \ at {row[1]}')
    except:
        print(f'Table {tbl}: not found or no data')
conn.close()
