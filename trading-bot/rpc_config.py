'''
RPC Configuration - single source of truth for Solana RPC URLs.
Auto-falls back to public RPC if Helius is unresponsive.
'''
import os
import requests

HELIUS_RPC = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")
PUBLIC_RPC = 'https://api.mainnet-beta.solana.com'

_ACTIVE_RPC = HELIUS_RPC
_CHECKED = False

def get_rpc():
    global _ACTIVE_RPC, _CHECKED
    if not _CHECKED:
        _CHECKED = True
        try:
            r = requests.post(
                HELIUS_RPC,
                json={"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if r.status_code == 200 and "result" in r.json():
                _ACTIVE_RPC = HELIUS_RPC
                print(f"[RPC] Using Helius: {HELIUS_RPC[:60]}...")
            else:
                print(f"[RPC] Helius responded but unexpected: {r.status_code} {r.text[:100]}")
                _ACTIVE_RPC = PUBLIC_RPC
                print(f"[RPC] Falling back to public RPC: {PUBLIC_RPC}")
        except Exception as e:
            print(f"[RPC] Helius failed: {e}")
            _ACTIVE_RPC = PUBLIC_RPC
            print(f"[RPC] Falling back to public RPC: {PUBLIC_RPC}")
    return _ACTIVE_RPC

def set_rpc(url):
    global _ACTIVE_RPC, _CHECKED
    _ACTIVE_RPC = url
    _CHECKED = True

def force_refresh():
    global _CHECKED
    _CHECKED = False
