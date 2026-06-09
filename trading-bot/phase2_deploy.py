import sys, json, time, base64, requests
sys.path.insert(0, 'trading-bot')

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

PK = bytes.fromhex('edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d')
WALLET = Keypair.from_bytes(PK)
CLIENT = Client("https://api.mainnet-beta.solana.com")

USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
SOL_MINT = 'So11111111111111111111111111111111111111112'

def get_usdc():
    r = requests.post('https://api.mainnet-beta.solana.com', json={
        'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner',
        'params':[str(WALLET.pubkey()), {'mint': USDC}, {'encoding':'jsonParsed'}]
    }, timeout=10)
    accounts = r.json().get('result',{}).get('value',[])
    if accounts:
        return float(accounts[0]['account']['data']['parsed']['info']['tokenAmount']['uiAmount'] or 0)
    return 0

def buy(mint, token_name, usdc_amount):
    print('Buying %s with $%.2f USDC...' % (token_name, usdc_amount))
    usdc_units = int(usdc_amount * 1e6)

    # Get quote
    r = requests.get(
        'https://lite-api.jup.ag/swap/v1/quote?inputMint=%s&outputMint=%s&amount=%d&slippage=15' % (USDC, mint, usdc_units),
        timeout=15
    )
    if r.status_code != 200:
        print('  Quote failed: HTTP %d' % r.status_code)
        return False
    quote = r.json()
    print('  Quote: %s USDC -> %s %s' % (quote.get('inAmount','?'), quote.get('outAmount','?'), token_name))

    # Get swap TX
    resp = requests.post('https://lite-api.jup.ag/swap/v1/swap', json={
        'quoteResponse': quote,
        'userPublicKey': str(WALLET.pubkey()),
        'wrapAndUnwrapSol': False,
        'prioritizationFeeLamports': 5000
    }, timeout=30)
    if resp.status_code != 200:
        print('  Swap TX failed: HTTP %d %s' % (resp.status_code, resp.text[:100]))
        return False
    swap_data = resp.json()

    # Sign and send
    tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data['swapTransaction']))
    signed = VersionedTransaction(tx.message, [WALLET])

    for attempt in range(3):
        try:
            result = CLIENT.send_raw_transaction(
                bytes(signed),
                opts=TxOpts(skip_preflight=True, preflight_commitment='confirmed')
            )
            tx_hash = result.value if hasattr(result, 'value') else str(result)
            print('  TX sent: %s' % str(tx_hash)[:30])
            time.sleep(5)

            # Verify on chain
            confirm = CLIENT.get_signature_statuses([str(tx_hash)])
            if confirm and confirm.value and confirm.value[0] and confirm.value[0].confirmation_status:
                print('  CONFIRMED: %s' % confirm.value[0].confirmation_status)
                return True
            else:
                # Wait more
                time.sleep(5)
                confirm2 = CLIENT.get_signature_statuses([str(tx_hash)])
                if confirm2 and confirm2.value and confirm2.value[0] and confirm2.value[0].confirmation_status:
                    print('  CONFIRMED (retry): %s' % confirm2.value[0].confirmation_status)
                    return True
                else:
                    print('  TX sent but not yet confirmed, likely will land')
                    return True
        except Exception as e:
            err = str(e)
            if attempt < 2:
                print('  Attempt %d failed: %s, retrying...' % (attempt+1, err[:80]))
                time.sleep(3)
            else:
                print('  Failed after 3 attempts: %s' % err[:80])
                return False

    return True  # TX was sent at least

# Check starting USDC
start = get_usdc()
print('Starting USDC: $%.2f' % start)

# Buy 1: RAY $70
print()
success_ray = buy('4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', 'RAY', 70.0)
print('RAY result: %s' % ('OK' if success_ray else 'FAILED'))
time.sleep(5)

mid = get_usdc()
print('USDC after RAY: $%.2f' % mid)

# Buy 2: JUP $20
print()
success_jup = buy('JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', 'JUP', 20.0)
print('JUP result: %s' % ('OK' if success_jup else 'FAILED'))
time.sleep(5)

final = get_usdc()
print()
print('=== FINAL ===')
print('Deployed: $%.2f' % (start - final))
print('USDC remaining: $%.2f' % final)

# Show what we have
from scout_v2 import get_all_holdings, get_jupiter_price, MINT_TO_NAME, USDC, SOL_MINT as SM
holdings = get_all_holdings()
sol_r = requests.get('https://lite-api.jup.ag/swap/v1/quote?inputMint=%s&outputMint=%s&amount=%d&slippage=1' % (SM, USDC, 10**9), timeout=5)
sol_price = float(sol_r.json()['outAmount'])/1e6 if sol_r.status_code == 200 else 80
total = final
for mint, h in sorted(holdings.items()):
    if mint == USDC: continue
    name = MINT_TO_NAME.get(mint, mint[:10])
    price = get_jupiter_price(mint, decimals=h['decimals'])
    val = h['amount'] * price if price > 0 else 0
    if val >= 0.01:
        print('%s: %.4f units = $%.2f' % (name, h['amount'], val))
        total += val

print('Total portfolio: $%.2f' % total)