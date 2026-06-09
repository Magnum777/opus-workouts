import sqlite3, json
from datetime import datetime
db = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracker.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT value FROM portfolio_check ORDER BY id DESC LIMIT 1')
row = cur.fetchone()
last_val = row[0] if row else 0
current = 71.15
change = abs(current - last_val)
print(f"Last: ${last_val:.2f}, Current: ${current:.2f}, Change: ${change:.2f}")
if change > 1.0:
    ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    cur.execute('INSERT INTO portfolio_check (value, timestamp) VALUES (?, ?)', (current, ts))
    bd = json.dumps({"SOL": 0.21, "USDC": 70.94})
    cur.execute('INSERT OR REPLACE INTO snapshots (ts, total, breakdown) VALUES (?, ?, ?)', (ts, current, bd))
    conn.commit()
    print(f"Recorded new snapshot at {ts}")
else:
    print("Change within $1 threshold, skipping")
conn.close()
