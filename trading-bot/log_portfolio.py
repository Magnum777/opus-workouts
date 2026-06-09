import sqlite3
from datetime import datetime

db_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\portfolio_tracking.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get last entry
c.execute('SELECT * FROM portfolio_snapshots ORDER BY rowid DESC LIMIT 1')
last = c.fetchone()
print('Last:', last)

now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
total = 89.99
details = 'SOL:2.60 USDC:50.97 TRUMP:18.33 ORCA:18.10'

c.execute('INSERT INTO portfolio_snapshots (timestamp, total, details) VALUES (?, ?, ?)',
          (now, total, details))
conn.commit()
print('Inserted:', now, total)
conn.close()
