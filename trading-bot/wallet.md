# Nova's Trading Wallet

## Wallet Details
- **Network:** Base (Ethereum L2)
- **Balance:** Check via RPC

## Private Key (KEEP SECRET!)
Stored in `trading-bot/.env` as `BASE_PRIVATE_KEY`. Never commit it.

## Setup Notes
- Created using web3.py (not Coinbase CDP due to SDK timeout issues)
- RPC: https://base.llamarpc.com
- Works!

## How to Add Funds
1. Go to Coinbase
2. Buy ETH
3. Send to this address (Base network)

## Trading Bot
Uses web3.py + direct RPC instead of Coinbase SDK.
