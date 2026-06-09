import requests, json

tokens = {
    'JUP': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
    'RAY': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
    'PENGU': '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv',
    'FARTCOIN': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',
    'ORCA': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE',
    'TRUMP': '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
}

for name, mint in sorted(tokens.items()):
    try:
        r = requests.get('https://api.dexscreener.com/latest/dex/tokens/' + mint, timeout=10)
        data = r.json()
        pairs = data.get('pairs', [])
        best = None
        for p in pairs:
            if p.get('chainId') != 'solana':
                continue
            liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
            if liq < 5000:
                continue
            vol = float(p.get('volume', {}).get('h24', 0) or 0)
            if best is None or vol > best['vol']:
                best = p
                best['vol'] = vol

        if best:
            price = float(best.get('priceUsd', 0) or 0)
            ch5 = float(best.get('priceChange', {}).get('m5', 0) or 0)
            ch1 = float(best.get('priceChange', {}).get('h1', 0) or 0)
            ch24 = float(best.get('priceChange', {}).get('h24', 0) or 0)
            vol24 = best['vol']
            liq = float(best.get('liquidity', {}).get('usd', 0) or 0)
            buys = int(best.get('txns', {}).get('h24', {}).get('buys', 0) or 0)
            sells = int(best.get('txns', {}).get('h24', {}).get('sells', 0) or 0)
            ratio = buys / sells if sells > 0 else 99

            print(name)
            print('  Price: $%.6f' % price)
            print('  5m: %+.2f%% | 1h: %+.2f%% | 24h: %+.2f%%' % (ch5, ch1, ch24))
            print('  Vol 24h: $%.0fK | Liq: $%.0fK' % (vol24/1000, liq/1000))
            print('  Trades: %d (B:%d / S:%d) Ratio: %.2f' % (buys+sells, buys, sells, ratio))

            # Signal assessment
            if ch5 > 0.5 and ratio > 1.5 and vol24 > 10000:
                print('  >> STRONG_MOMENTUM')
            elif ch1 > 0 and ratio > 1.0:
                print('  >> MILD_UP')
            elif ch5 < -0.5:
                print('  >> DIPPING')
            else:
                print('  >> FLAT')
            print()
    except Exception as e:
        print('%s: %s' % (name, e))
        print()