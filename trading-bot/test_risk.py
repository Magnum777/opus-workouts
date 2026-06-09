import sys; sys.path.insert(0, '.')
from risk_manager import *
print('=== V3 Risk Manager Test ===')

# Test cooldown system
record_sell_cooldown('BONK', 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263')
on_cd, remaining = is_on_cooldown('BONK', 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263')
print('BONK cooldown:', 'ACTIVE (%.1fh)' % remaining if on_cd else 'NONE')

# Test no cooldown for unknown token
on_cd2, _ = is_on_cooldown('TRUMP', '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN')
print('TRUMP cooldown:', 'ACTIVE' if on_cd2 else 'NONE (good)')

# Test trade allowed
db = load_db()
pf = db['portfolio']
print('Portfolio value: $%.2f' % pf['total_value_usd'])

# Test BUY with new risk rules
ok, reason = check_trade_allowed('TRUMP', 'BUY', pf['total_value_usd'], 30.0, mint='6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN')
print('BUY TRUMP $30:', 'ALLOWED' if ok else reason)

# Test BUY that's too large
ok2, reason2 = check_trade_allowed('NEWTOKEN', 'BUY', pf['total_value_usd'], 50.0, mint='fake')
print('BUY NEWTOKEN $50:', 'ALLOWED' if ok2 else reason2)

# Test BUY on cooldown token
ok3, reason3 = check_trade_allowed('BONK', 'BUY', pf['total_value_usd'], 30.0, mint='DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263')
print('BUY BONK $30:', 'ALLOWED' if ok3 else reason3)

summary = get_risk_summary()
print('Risk summary:', summary)
