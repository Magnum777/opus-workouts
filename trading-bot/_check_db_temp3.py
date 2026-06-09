import sqlite3
db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracker.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('select value, timestamp, typeof(value) from portfolio_check order by id desc limit 2')
rows = cur.fetchall()
for r in rows:
    print(repr(r))
    print(f"  value={r[0]}, type={r[2]}")
if len(rows) >= 2:
    v1 = float(rows[0][0]) if rows[0][0] is not None else 0
    v2 = float(rows[1][0]) if rows[1][0] is not None else 0
    diff = abs(v1 - v2)
    print(f"Diff: {diff:.2f}")
    if diff <= 1:
        print("SKIP - within ")
    else:
        print(f"CHANGE - diff ")
conn.close()
