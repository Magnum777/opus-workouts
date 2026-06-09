import requests, json

# Raydium has a public API
resp = requests.get('https://api.raydium.io/v2/main/pairs', timeout=10)
data = resp.json()

print('Status:', resp.status_code)
print('Type:', type(data))

# It's a list
pairs = data if isinstance(data, list) else data.get('data', [])
print('Total pairs:', len(pairs))

# Find SOL pairs
for p in pairs[:50]:
    base = p.get('baseToken', {}).get('symbol', '')
    quote = p.get('quoteToken', {}).get('symbol', '')
    if 'SOL' in base or base == 'SOL':
        print(f"{base} / {quote}: {p.get('price')}")
