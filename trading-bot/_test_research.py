import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
import research_v2 as r
import datetime
print(f'[{datetime.datetime.utcnow().isoformat()}] research_v2 loaded')
result = r.research_portfolio()
print(f'Done. Keys: {list(result.keys())[:5]}')
