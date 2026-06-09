import sqlite3, os
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\trading_bot.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", tables)
cur.execute("SELECT value, timestamp FROM portfolio_snapshots ORDER BY timestamp DESC LIMIT 1")
row = cur.fetchone()
if row:
    print(f'Last value:  at {row[1]}')
else:
    print('No previous snapshot found')
conn.close()
