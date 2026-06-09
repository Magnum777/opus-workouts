import json, sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
import portfolio_db_v2 as pdb

# Hard write truth
db = pdb.create_default_db()
db['portfolio']['sol_balance'] = 0.052837
db['portfolio']['sol_price_usd'] = 94.71
db['portfolio']['usdc_balance'] = 94.68
db['portfolio']['total_value_usd'] = 99.69
db['portfolio']['positions_count'] = 0
db['portfolio']['cost_basis_total'] = 94.68

# Only successfully executed trades
with open(r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.json') as f:
    all_trades = json.load(f)
db['trades'] = [t for t in all_trades if t['action'] in ('BUY','SELL')]

# NO positions - clean slate
db['positions'] = []

pdb.save_db(db)
print('Wrote clean DB')
print(json.dumps({'usdc': db['portfolio']['usdc_balance'], 'total': db['portfolio']['total_value_usd'], 'positions': len(db['positions']), 'trades': len(db['trades'])}))
