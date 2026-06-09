import sqlite3, datetime
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\trading_bot.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
ts = datetime.datetime.now().isoformat()
cur.execute("INSERT INTO portfolio_snapshots (value, timestamp) VALUES (?, ?)", (12.70, ts))
conn.commit()
print(f'Inserted .70 at {ts}')
conn.close()
