import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
import research_v2 as r

# Research first
result = r.research_portfolio()
print(f'Research: {len(result.get("analyses", []))} analyses, conf={result.get("avg_confidence")}')

# Try buy signals
print('Getting buy signals...')
buy = r.get_buy_signals(min_confidence=80)
print(f'Buy signals: {len(buy)}')

print('Getting sell signals...')
sell = r.get_sell_signals()
print(f'Sell signals: {len(sell)}')

print('SIGNALS COMPLETE')
