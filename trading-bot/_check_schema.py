import sqlite3
db="C:/Users/compj/.openclaw/workspace/trading-bot/portfolio_history.db"
conn = sqlite3.connect(db)
c = conn.cursor()
# Check schemas
for t in ["portfolio_snapshots", "snapshots"]:
    try:
        info = c.execute(f"PRAGMA table_info({t})").fetchall()
        print(f"{t} schema: {info}")
    except Exception as e:
        print(f"{t}: {e}")
conn.close()
