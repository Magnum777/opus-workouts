import requests

url = 'https://api.coingecko.com/api/v3/coins/markets'
params = {
    'vs_currency': 'usd',
    'order': 'volume_desc',
    'per_page': 50,
    'page': 1,
    'sparkline': 'false'
}
r = requests.get(url, params=params, timeout=15)
print('Status:', r.status_code)
if r.status_code == 200:
    coins = r.json()
    solana_coins = []
    for c in coins:
        platforms = c.get('platforms', {})
        if 'solana' in platforms and platforms['solana']:
            mint = platforms['solana']
            if mint and len(mint) > 20:  # Not SOL itself
                solana_coins.append({
                    'symbol': c.get('symbol', '').upper(),
                    'name': c.get('name', ''),
                    'mint': mint,
                    'volume': c.get('total_volume', 0),
                    'price': c.get('current_price', 0)
                })
    
    print(f'Solana tokens found: {len(solana_coins)}')
    for c in solana_coins[:10]:
        print(f"  {c['symbol']}: {c['mint'][:30]} vol=${c['volume']:,.0f}")
