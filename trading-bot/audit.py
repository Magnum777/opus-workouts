#!/usr/bin/env python3
"""Check token accounts and positions DB."""
import json, requests, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())

print("=== ON-CHAIN TOKENS ===")
sol = C.get_balance(WALLET.pubkey()).value / 1e9
print(f"Native SOL: {sol:.6f}")

# Token accounts via Helius
r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[WS,{},{'encoding':'jsonParsed'}]}, timeout=10).json()
all_accts = r.get("result", {}).get("value", [])
print(f"Token accounts found: {len(all_accts)}")
for a in all_accts:
    info = a["account"]["data"]["parsed"]["info"]
    mint = info.get("mint", "")
    amt = float(info.get("tokenAmount", {}).get("uiAmount", 0) or 0)
    print(f"  {mint[:25]:25s}: {amt}")

if not all_accts:
    print("  (trying with specific program filter)")
    for prog in ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                  "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"]:
        r2 = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[WS,{"programId":prog},{"encoding":"jsonParsed"}]}, timeout=10).json()
        accts2 = r2.get("result", {}).get("value", [])
        print(f"  {prog[:20]}: {len(accts2)} accounts")
        for a in accts2:
            info = a["account"]["data"]["parsed"]["info"]
            print(f"    {info['mint'][:25]}: {info['tokenAmount']['uiAmount']}")

# Also check scout's view
print(f"\n=== SCOUT get_all_holdings ===")
import scout_v2 as scout
holdings = scout.get_all_holdings()
print(f"Holdings from scout: {len(holdings)}")
for mint, h in holdings.items():
    name = scout.MINT_TO_NAME.get(mint, mint[:10])
    print(f"  {name:12s} ({mint[:12]}..): {h['amount']:.6f}")

print(f"\n=== DB POSITIONS ===")
db_path = os.path.join(os.path.dirname(__file__), "portfolio.db.json")
with open(db_path) as f:
    d = json.load(f)
positions = d.get("positions", [])
print(f"Positions in DB: {len(positions)}")
for p in positions:
    print(f"  {p.get('token','?'):12s} status={p.get('status','?')} "
          f"value=${p.get('current_value_usd',0):.2f} "
          f"cost=${p.get('cost_basis_usd',0):.2f} "
          f"pnl=${p.get('unrealized_pnl_usd',0):.2f}")

print(f"\n=== DB TRADES (last 5) ===")
trades = d.get("trades", [])
for t in trades[-5:]:
    print(f"  {t.get('token','?'):12s} {t.get('action','?'):5s} "
          f"pnl=${t.get('pnl_usd',0):.2f} "
          f"tx={str(t.get('tx_hash',''))[:20]}")

# Check corrupted PnL
print(f"\n=== ALL TRADES sorted by PnL ===")
for t in sorted(trades, key=lambda x: abs(x.get('pnl_usd',0)), reverse=True)[:5]:
    print(f"  {t.get('token','?'):12s} {t.get('action','?'):5s} "
          f"pnl=${t.get('pnl_usd',0):.2f} "
          f"tx={str(t.get('tx_hash',''))[:20]}")