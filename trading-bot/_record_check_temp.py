import sqlite3, os, json, datetime

db = os.path.join(r'C:\Users\compj\.openclaw\workspace\trading-bot', 'portfolio.db')
conn = sqlite3.connect(db)
c = conn.cursor()

new_total = 89.66
new_details = json.dumps({
    "sol": {"qty": 0.037438, "price": 81.91, "value": 3.07},
    "usdc": 3.4995,
    "pengu": {"qty": 3198.080279, "price": 0.007868, "value": 25.1625},
    "trump": {"qty": 15.344546, "price": 1.953568, "value": 29.9766},
    "orca": {"qty": 0.327836, "price": 1.278881, "value": 0.4193},
    "bonk": {"qty": 5507690.079230, "price": 0.000005, "value": 27.5385}
})

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
c.execute("INSERT INTO portfolio_checks (checked_at, total, details) VALUES (?, ?, ?)", (now, new_total, new_details))
c.execute("INSERT INTO portfolio_history (timestamp, total, details) VALUES (?, ?, ?)", (now, new_total, new_details))
conn.commit()

# get prev for comparison
c.execute("SELECT total FROM portfolio_checks ORDER BY id DESC LIMIT 2")
rows = c.fetchall()
prev = rows[1][0] if len(rows) > 1 else None
print(f'Recorded total={new_total}, prev={prev}, diff={new_total - prev if prev else "N/A"}')
conn.close()
