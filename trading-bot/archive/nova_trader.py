"""
Nova's Trading Bot - Complete Edition
Features: Notion, Price Alerts, Portfolio, Strategies, Stop Loss, Take Profit, Daily Reports
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from web3 import Web3
from eth_account import Account
import requests
import time
import argparse
from api_tracker import track, usage

# Configuration
RPC_URL = "https://base.llamarpc.com"
WALLET_ADDRESS = "0x4d2049F1e4a1d34FF458944c13E4720d2BAbc6A8"
# PRIVATE_KEY is now read from the environment variable WALLET_PRIVATE_KEY for security

# Trading config
TRADE_SIZE_ETH = 0.001
TRADE_SIZE_USDC = 10  # $10 worth
NOTION_DB_ID = "31035ead-c48d-81c7-87b2-f9b70d9c91b5"

# USDC on Base (Wrapped USDC)
USDC_ADDRESS = "0x4ed4e862860bed51a9570b96d89af5e1b0efefed"  # Wrapped USDC on Base

# Initialize (handled inside NovaTrader class; removed global w3/account initialization)

class NovaTrader:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")
        if not self.private_key:
            raise EnvironmentError("WALLET_PRIVATE_KEY not set in environment")
        self.account = Account.from_key(self.private_key)
        self.wallet = self.account.address
        self.trades = []
        self.is_paper = False  # default to live trading; can be overridden with --paper flag
        self.portfolio = {}
        self.price_alerts = []
        self.strategy = "dca"  # dca, momentum, mean_reversion
        self.stop_loss_pct = 0.05  # 5%
        self.take_profit_pct = 0.10  # 10%

        
    # ============ CORE FUNCTIONS ============
    
    def get_balance(self):
        """Get ETH balance"""
        balance = self.w3.eth.get_balance(self.wallet)
        return float(self.w3.from_wei(balance, 'ether'))
    
    def get_usdc_balance(self):
        """Get USDC balance"""
        # Simplified - would need proper ERC-20 call
        return 0.0  # Would query USDC contract
    
    def get_eth_price(self):
        """Get ETH price in USD"""
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
                timeout=10
            )
            return resp.json()["ethereum"]["usd"]
        except:
            return 2500

    # -------------------------------------------------
    # 1️⃣  Helper: fetch price & candles from CoinGecko
    # -------------------------------------------------
    def fetch_price_and_ohlcv(self, days: int = 7, interval: str = "hourly"):
        """
        Returns:
            price (float)      – latest spot price USD
            candles (list)     – list of dicts {ts, open, high, low, close, vol}
        """
        track("coingecko")
        # 1️⃣ Current price (reuse existing call)
        price = self.get_eth_price()
        # 2️⃣ OHLCV candles (7‑day hourly)
        try:
            resp = requests.get(
                f"https://api.coingecko.com/api/v3/coins/ethereum/market_chart",
                params={"vs_currency": "usd", "days": days, "interval": interval},
                timeout=5,
            )
            data = resp.json()
            candles = []
            for entry in data.get("prices", []):
                ts_ms, p = entry
                candles.append({
                    "ts": int(ts_ms / 1000),
                    "open": p,
                    "high": p,
                    "low": p,
                    "close": p,
                    "vol": 0,
                })
            return price, candles
        except Exception:
            return price, []

    # -------------------------------------------------
    # 2️⃣  Helper: fetch sentiment from LunarCRUSH
    # -------------------------------------------------
    def fetch_lunarcrush_sentiment(self, symbol="ETH"):
        """Returns a sentiment score between -1 (bearish) and +1 (bullish)."""
        track("lunarcrush")
        api_key = os.getenv("LUNARCRUSH_API_KEY")
        if not api_key:
            return 0.0
        try:
            resp = requests.get(
                "https://api.lunarcrush.com/v2",
                params={"data": "assets", "key": api_key, "symbol": symbol},
                timeout=5,
            )
            data = resp.json()
            return float(data.get("data", [{}])[0].get("sentiment_score", 0.0))
        except Exception:
            return 0.0

    # -------------------------------------------------
    # 3️⃣  Helper: pull your Notion research entries
    # -------------------------------------------------
    def fetch_notion_research(self):
        """Returns a list of dicts from your Notion research DB."""
        track("notion")
        notion_key = os.getenv("NOTION_API_KEY")
        if not notion_key:
            return []
        url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
        headers = {
            "Authorization": f"Bearer {notion_key}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(url, headers=headers, json={"page_size": 20}, timeout=5)
            rows = resp.json().get("results", [])
            out = []
            for page in rows:
                props = page.get("properties", {})
                out.append({
                    "name": props.get("Name", {}).get("title", [{}])[0].get("plain_text", ""),
                    "sentiment": props.get("Sentiment", {}).get("select", {}).get("name", "Neutral"),
                    "confidence": props.get("Confidence", {}).get("number", 0),
                    "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                })
            return out
        except Exception:
            return []

    
    def fetch_crypto_panic_sentiment(self):
        """Fetch recent crypto‑news from CryptoPanic (public endpoint) and return a sentiment score in [-1, 1]."""
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {"public": "true"}
        try:
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            pos = 0
            neg = 0
            for item in data.get("results", [])[:20]:
                pos += item.get("positive_votes", 0)
                neg += item.get("negative_votes", 0)
            if pos + neg == 0:
                return 0.0
            return (pos - neg) / (pos + neg)
        except Exception:
            return 0.0



    def get_portfolio_value(self):
        """Get total portfolio value"""
        eth_balance = self.get_balance()
        usdc_balance = self.get_usdc_balance()
        eth_price = self.get_eth_price()
        
        return {
            "eth": eth_balance,
            "usdc": usdc_balance,
            "usd": (eth_balance * eth_price) + usdc_balance,
            "eth_price": eth_price
        }
    
    # ============ TRADING STRATEGIES ============
    
    def strategy_dca(self, price):
        """Dollar Cost Average - buy small amounts regularly"""
        return {
            "action": "buy",
            "amount": TRADE_SIZE_ETH,
            "reason": "DCA buy - regular investment"
        }
    
    def strategy_momentum(self, price, history):
        """Buy on momentum - price going up"""
        if len(history) < 2:
            return {"action": "hold", "amount": 0, "reason": "Need more data"}
        
        if history[-1] > history[-2]:
            return {
                "action": "buy",
                "amount": TRADE_SIZE_ETH,
                "reason": "Momentum bullish"
            }
        return {"action": "hold", "amount": 0, "reason": "Momentum bearish"}
    
    def strategy_mean_reversion(self, price, history):
        """Buy when price is below average"""
        if len(history) < 10:
            return {"action": "hold", "amount": 0, "reason": "Need more data"}
        
        avg = sum(history) / len(history)
        if price < avg * 0.95:
            return {
                "action": "buy",
                "amount": TRADE_SIZE_ETH,
                "reason": f"Price ${price:.2f} below avg ${avg:.2f}"
            }
        return {"action": "hold", "amount": 0, "reason": "Price near average"}
    
    # ============ RISK MANAGEMENT ============
    
    def check_stop_loss(self, entry_price, current_price):
        """Check if stop loss triggered"""
        loss_pct = (current_price - entry_price) / entry_price
        if loss_pct <= -self.stop_loss_pct:
            return True, "STOP LOSS"
        return False, None
    
    def check_take_profit(self, entry_price, current_price):
        """Check if take profit triggered"""
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct >= self.take_profit_pct:
            return True, "TAKE PROFIT"
        return False, None
    
    # ============ PRICE ALERTS ============
    
    def add_alert(self, target_price, direction, message=""):
        """Add a price alert"""
        alert = {
            "target": target_price,
            "direction": direction,  # "above" or "below"
            "message": message,
            "created": datetime.now().isoformat(),
            "triggered": False
        }
        self.price_alerts.append(alert)
        return alert
    
    def check_alerts(self, current_price):
        """Check if any alerts triggered"""
        triggered = []
        for alert in self.price_alerts:
            if alert["triggered"]:
                continue
            
            if alert["direction"] == "above" and current_price >= alert["target"]:
                alert["triggered"] = True
                triggered.append(alert)
            elif alert["direction"] == "below" and current_price <= alert["target"]:
                alert["triggered"] = True
                triggered.append(alert)
        
        return triggered
    
    # ============ NOTION INTEGRATION ============
    
    def log_to_notion(self, trade_data):
        """Log trade to Notion (simulated)"""
        # In production, use Notion API
        print(f"[NOTION] Trade logged: {trade_data}")
        return {"status": "logged", "data": trade_data}
    
    def log_to_file(self, trade_data):
        """Log to local file"""
        filename = "trading-bot/trades.json"
        os.makedirs("trading-bot", exist_ok=True)
        
        # Load existing
        trades = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                trades = json.load(f)
        
        trades.append(trade_data)
        
        with open(filename, 'w') as f:
            json.dump(trades, f, indent=2)
        
        return {"status": "saved", "file": filename}
    
    # ============ TRADING ============
    
    def execute_trade(self, action, amount, price, reason=""):
        """Execute a trade"""
        if self.is_paper:
            result = {
                "status": "paper",
                "action": action,
                "amount": amount,
                "price": price,
                "value": amount * price,
                "reason": reason
            }
        else:
            # Live trade: simple ETH transfer to a placeholder address (replace with actual DEX call)
            target_address = os.getenv("TRADE_TARGET_ADDRESS", "0x1111111111111111111111111111111111111111")
            tx = {
                "to": target_address,
                "value": self.w3.toWei(amount, "ether"),
                "gas": 21000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.wallet),
                "chainId": self.w3.eth.chain_id,
            }
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            try:
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                status = "success" if receipt.status == 1 else "failed"
            except Exception as e:
                tx_hash = None
                receipt = None
                status = f"error: {e}"
            result = {
                "status": "live",
                "action": action,
                "amount": amount,
                "price": price,
                "value": amount * price,
                "reason": reason,
                "tx_hash": tx_hash.hex() if tx_hash else None,
                "tx_status": status,
                "receipt": receipt,
            }
        # Always log
        self.log_to_file(result)
        return result
    
    # ============ ANALYSIS ============
    
    async def analyze_and_trade(self):
        """Main analysis and trading logic – now research‑augmented."""
        # ---- 5.1 Pull market data (price + recent candles) ----
        price, candles = self.fetch_price_and_ohlcv(days=7, interval="hourly")
        portfolio = self.get_portfolio_value()
        
        # ---- 5.2 Pull research signals ----
        sentiment_score = self.fetch_lunarcrush_sentiment()
        notion_rows = self.fetch_notion_research()
        
        # Compute a weighted Notion sentiment (simple avg of confidence‑adjusted scores)
        notion_score = 0.0
        total_conf = 0.0
        for row in notion_rows:
            val = {"Bullish": 1, "Neutral": 0, "Bearish": -1}.get(row.get("sentiment"), 0)
            conf = (row.get("confidence") or 0) / 100.0
            notion_score += val * conf
            total_conf += conf
        if total_conf:
            notion_score /= total_conf
        else:
            notion_score = 0.0
        # Pull crypto‑panic news sentiment as an additional research signal
        crypto_score = self.fetch_crypto_panic_sentiment()
        
        # ---- 5.3 Combine signals ----
        # Simple price trend from candles (last two closes)
        price_trend = 0.0
        if len(candles) >= 2:
            price_trend = (candles[-1]["close"] - candles[-2]["close"]) / candles[-2]["close"]
        
        # Weighted sum: 50 % price trend, 30 % market sentiment, 20 % Notion research
        combined_score = (0.5 * price_trend) + (0.25 * sentiment_score) + (0.15 * notion_score) + (0.1 * crypto_score)
        
        # ---- 5.4 Decision logic ----
        # If a forced sell flag is present, execute a sell regardless of the composite score.
        if getattr(self, "FORCE_SELL", False):
            signal = {"action": "sell", "amount": TRADE_SIZE_ETH, "reason": "Force‑sell (pump)"}
        elif getattr(self, "FORCE_BUY", False):
            signal = {"action": "buy", "amount": TRADE_SIZE_ETH, "reason": "Force‑buy approved by user"}
        elif combined_score > 0.02 and portfolio["eth"] > TRADE_SIZE_ETH:
            signal = {"action": "buy", "amount": TRADE_SIZE_ETH, "reason": "Research‑augmented BUY"}
        elif combined_score < -0.02 and portfolio["eth"] > 0:
            signal = {"action": "sell", "amount": TRADE_SIZE_ETH, "reason": "Research‑augmented SELL"}
        else:
            signal = {"action": "hold", "amount": 0, "reason": "Neutral composite signal"}
        
        # ---- 5.5 Execute trade (paper mode) ----
        if signal["action"] == "buy":
            result = self.execute_trade("buy", signal["amount"], price, signal["reason"])
        elif signal["action"] == "sell":
            result = self.execute_trade("sell", signal["amount"], price, signal["reason"])
        else:
            result = {"action": "hold", "reason": signal.get("reason", "No signal")}
        
        # ---- 5.6 Log enriched data ----
        enriched = {
            "timestamp": datetime.utcnow().isoformat(),
            "price_usd": price,
            "price_trend": price_trend,
            "coingecko_sentiment": sentiment_score,
            "notion_score": notion_score,
            "combined_score": combined_score,
            "signal": signal,
            "trade": result,
            "alerts": self.check_alerts(price),
            "portfolio_usd": portfolio["usd"],
        }
        self.log_to_file(enriched)
        self.log_to_notion(enriched)
        
        return enriched
    
    # ============ DAILY REPORT ============
    
    def daily_report(self):
        """Generate daily report"""
        portfolio = self.get_portfolio_value()
        
        report = {
            "date": datetime.now().isoformat(),
            "portfolio": portfolio,
            "trades_today": len([t for t in self.trades if 
                t.get("date", "").startswith(datetime.now().strftime("%Y-%m-%d"))]),
            "alerts": len(self.price_alerts),
            "alerts_triggered": len([a for a in self.price_alerts if a["triggered"]]),
            "strategy": self.strategy,
            "mode": "paper" if self.is_paper else "live"
        }
        
        return report


async def main():
    bot = NovaTrader()
    # Apply forced flags from environment variables
    if os.getenv("FORCE_BUY", "false").lower() == "true":
        bot.FORCE_BUY = True
    if os.getenv("FORCE_SELL", "false").lower() == "true":
        bot.FORCE_SELL = True
    
    print("=" * 60)
    print("Nova's Trading Bot - Complete Edition")
    print("=" * 60)
    
    # Portfolio (quiet mode – only printed if a trade occurs)
    portfolio = bot.get_portfolio_value()
    # Strategy info – printed only on trade
    # Test alerts – set up silently
    bot.add_alert(2000, "above", "Take some profit")
    bot.add_alert(1800, "below", "Buy more")
    # Run analysis
    result = await bot.analyze_and_trade()
    trade_action = result['signal']['action']
    if trade_action != "hold":
        # Print detailed info only when a trade is executed
        print("\nPortfolio:")
        print(f"   ETH: {portfolio['eth']:.4f}")
        print(f"   USDC: ${portfolio['usdc']:.2f}")
        print(f"   Total USD: ${portfolio['usd']:.2f}")
        print(f"   ETH Price: ${portfolio['eth_price']:.2f}")
        print(f"\nStrategy: {bot.strategy.upper()}")
        print(f"   Stop Loss: {bot.stop_loss_pct*100}%")
        print(f"   Take Profit: {bot.take_profit_pct*100}%")
        print(f"\nPrice Alerts: {len(bot.price_alerts)}")
        print("\nRunning analysis...")
        print(f"   Signal: {result['signal']['action']}")
        print(f"   Reason: {result['signal'].get('reason', 'N/A')}")
        print(f"   Trade: {result['trade']}")
        # Daily report (brief)
        report = bot.daily_report()
        print("\nDaily Report:")
        print(f"   Trades today: {report['trades_today']}")
        print(f"   Mode: {report['mode']}")
    else:
        # No trade – remain silent (only logs are written)
        pass
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
