# Nova's Trading Bot - Complete Playbook

**Created:** February 23, 2026  
**By:** Nova 🦝  
**Purpose:** AI Agent with crypto wallet for autonomous trading

---

## The Vision

Give Nova her own crypto wallet so she can:
- Make predictions on Polymarket
- Earn money from bets
- Pay for her own compute costs
- Become self-funding!

This is the future Nate Jones described - AI agents with their own money.

---

## What We Need

| Item | Cost | Notes |
|------|------|-------|
| Coinbase Developer Account | Free | Sign up at cdp.coinbase.com |
| CDP API Key | Free | Generate in developer portal |
| Polymarket Account | Free | Sign up at polymarket.com |
| Starting Capital | $50-100 | Your investment |
| Computer to run bot | $0 | Can run on existing PC or future Mini PC |

---

## Step 1: Get Coinbase CDP API Key

### 1.1 Create Coinbase Developer Account
1. Go to https://cdp.coinbase.com
2. Sign up for free
3. Verify email

### 1.2 Create API Key
1. In CDP dashboard, go to "API Keys"
2. Click "Create API Key"
3. Name it "Nova-Trading-Bot"
4. Scopes needed:
   - `wallet:read`
   - `wallet:write`
   - `addresses:read`
   - `addresses:write`
5. **Save the Key ID and Key Secret** - you'll only see it once!

### 1.3 Get Wallet Secret (Optional)
- For existing wallets, you can import a wallet secret
- Or let the agent create a new wallet

---

## Step 2: Set Up Python Environment

### 2.1 Install Python
```bash
# Check if Python is installed
python --version

# If not, download from python.org
```

### 2.2 Install Required Packages
```bash
pip install coinbase-agentkit
pip install polygon-market-client
pip install python-dotenv
```

---

## Step 3: Create Trading Bot Script

### 3.1 Basic Agent Setup
```python
import os
from dotenv import load_dotenv
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpEvmWalletProvider,
    CdpEvmWalletProviderConfig,
)

# Load environment variables
load_dotenv()

# Configure wallet
wallet_provider = CdpEvmWalletProvider(
    CdpEvmWalletProviderConfig(
        api_key_id=os.getenv("CDP_API_KEY_ID"),
        api_key_secret=os.getenv("CDP_API_KEY_SECRET"),
        wallet_secret=os.getenv("CDP_WALLET_SECRET"),  # Optional
        network_id="base-sepolia",  # Testnet first!
    )
)

# Create AgentKit instance
agentkit = AgentKit(
    AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            # Add action providers
        ],
    )
)

print(f"Wallet address: {wallet_provider.get_address()}")
```

### 3.2 Add Polymarket Integration
```python
from polymarket import Polymarket

# Initialize Polymarket client
pm = Polymarket(
    api_key=os.getenv("POLYMARKET_API_KEY"),
    api_secret=os.getenv("POLYMARKET_API_SECRET")
)

# Get market data
markets = pm.get_markets(category="politics")
for market in markets:
    print(f"{market.question}: {market.price}")
```

### 3.3 Basic Trading Logic
```python
def make_trade(market_question, prediction, amount):
    """
    Make a trade on Polymarket
    """
    # Get the market
    market = pm.get_market(question=market_question)
    
    # Place order
    if prediction == "yes":
        outcome = "Yes"
    else:
        outcome = "No"
    
    order = pm.place_order(
        market_id=market.id,
        outcome=outcome,
        amount=amount,  # In USDC
    )
    
    return order

# Example usage
result = make_trade(
    market_question="Will BTC hit $100k in 2025?",
    prediction="yes",
    amount=10  # $10
)
print(f"Trade placed: {result}")
```

---

## Step 4: Add AI Intelligence

### 4.1 Research Before Trading
```python
import requests

def research_topic(topic):
    """
    Use web search to research a topic before making a prediction
    """
    # This would integrate with your AI research tools
    # For now, simple example:
    
    search_url = f"https://api.search.com/v1/search?q={topic}"
    response = requests.get(search_url)
    
    # Analyze results and return summary
    return analyze_search_results(response.json())

def analyze_search_results(results):
    """
    Analyze search results to make a prediction
    """
    # Use your AI to analyze
    # This is where Nova's research abilities come in!
    
    sentiment = analyze_sentiment(results)
    return sentiment
```

### 4.2 Decision Making
```python
async def should_trade(market, research_data):
    """
    Decide whether to make a trade based on research
    """
    confidence = research_data["confidence"]
    potential_return = market["current_price"]
    
    # Only trade if confident and good odds
    if confidence > 0.7 and potential_return > 2.0:
        return True
    return False
```

---

## Step 5: Run the Bot

### 5.1 Test Mode (Use Testnet First!)
```python
# Always start with testnet!
NETWORK_ID = "base-sepolia"  # Testnet
# After testing:
# NETWORK_ID = "base"  # Mainnet
```

### 5.2 Start Trading
```bash
python nova_trading_bot.py
```

---

## Step 6: Connect to Notion (Tax Tracking)

We already have a trading journal in Notion!

After each trade, log it:
```python
def log_trade_to_notion(trade_result, market, amount):
    """
    Log trade to Notion for tax tracking
    """
    # Use Notion API to create a log entry
    # Already set up at: https://notion.so/31035eadc48d81c787b2f9b70d9c91b5
    pass
```

---

## Complete Code Structure

```
nova-trading-bot/
├── .env                 # API keys
├── nova_trader.py       # Main bot
├── strategies/
│   └── research_strategy.py
├── utils/
│   ├── polymarket_api.py
│   ├── research.py
│   └── logging.py
├── notebooks/
│   └── analysis.ipynb
└── README.md
```

---

## Important Notes

### Security
- Never share API keys
- Use environment variables, never hardcode
- Start with testnet (Sepolia)
- Set spending limits

### Legal/Taxes
- All trades under Layered Media LLC
- Log every trade in Notion
- Keep records for tax purposes

### Start Small
- Start with $10-50
- Only trade when confident
- Don't risk more than you can afford to lose

---

## Resources

- Coinbase AgentKit: https://github.com/coinbase/agentkit
- Coinbase Docs: https://docs.cdp.coinbase.com/
- Polymarket Agents: https://github.com/Polymarket/agents
- Polymarket API: https://docs.polymarket.com/
- Nate Jones AI Stack: https://publicservicesalliance.org/2025/11/10/nate-b-joness-personal-ai-stack/

---

## The Goal

1. **Week 1:** Get testnet working
2. **Week 2:** Make first test trade
3. **Week 3:** Add research logic
4. **Week 4:** Go live with real money
5. **Ongoing:** Refine strategies, track profits

---

*Built by Nova - AI Assistant* 🦝

Let's make some money!
