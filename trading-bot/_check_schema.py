import sqlite3
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\trading_bot.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("PRAGMA table_info(portfolio_snapshots)")
for row in cur.fetchall():
    print(row)
cur.execute("SELECT value, timestamp FROM portfolio_snapshots ORDER BY timestamp DESC LIMIT 1")
row = cur.fetchone()
print(f'Last row: value={row[0]!r}, timestamp={row[1]!r}')
conn.close()
