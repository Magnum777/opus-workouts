import sqlite3
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracker.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('select value, timestamp from portfolio_check order by id desc limit 2')
rows = cur.fetchall()
print("Last 2 entries:")
for r in rows:
    print(f"   at {r[1]}")
if len(rows) >= 2:
    diff = abs(rows[0][0] - rows[1][0])
    print(f"Difference: ")
    if diff <= 1:
        print("SKIP - within ")
    else:
        print(f"CHANGE - diff ")
elif len(rows) == 1:
    print("First entry only - no comparison available")
else:
    print("No entries")
conn.close()
