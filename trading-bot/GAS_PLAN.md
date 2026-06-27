# Gas Sustainability Plan

## The Problem
Every Jupiter v2 swap costs ~0.0005-0.001 SOL in priority fees. At 96 cycles/day (every 15min), even without actual trades, the bot burns SOL on balance checks and failed attempts. The old code only refilled SOL when it dropped below 0.001 — way too late.

## The Fix

### 1. Track gas budget as a % of portfolio
Instead of a fixed SOL target, set gas as a % of total portfolio value:
- **Gas reserve target:** 2% of portfolio value in SOL
- **Minimum floor:** 0.01 SOL (enough for ~20 swaps)
- **Maximum ceiling:** 0.05 SOL (no reason to hold more)

For a $50 portfolio: 2% = $1 = ~0.014 SOL. That's enough for ~20-30 swaps.

### 2. Refill early, refill small
- Trigger refill when SOL drops below **50% of target** (not when it hits 0.001)
- Refill only what's needed to reach target, capped at **5% of USDC per refill**
- This means frequent tiny refills instead of one big panic refill

### 3. Track gas spent per cycle
Log SOL balance before and after each executor run. If gas spent per cycle exceeds 0.001 SOL, flag it. This catches runaway fee issues early.

### 4. Kill the USDC→SOL refill loop
The `refill_usdc_from_sol` function sells SOL for USDC when USDC is low. But this costs gas too — it's a swap that burns SOL to get USDC, which then gets burned again to buy SOL. This creates a death spiral. **Remove it.** If USDC is low, the bot should just wait for a trade to close.

### 5. Cap daily gas spend
Hard limit: **0.01 SOL per day max on fees.** If the bot hits this, it pauses all trading until the next day. This prevents a runaway from draining the wallet.

## Implementation

### Changes to `executor_v2.py`:

```python
# Replace the SOL gas constants
SOL_TARGET_PCT = 0.02           # 2% of portfolio in SOL for gas
SOL_TARGET_FLOOR = 0.01         # minimum 0.01 SOL
SOL_TARGET_CEILING = 0.05       # never hold more than 0.05 SOL
SOL_REFILL_TRIGGER = 0.50       # refill when below 50% of target
SOL_REFILL_CAP_PCT = 0.05       # max 5% of USDC per refill
SOL_DAILY_BUDGET = 0.01         # max 0.01 SOL/day on fees
```

### Replace `ensure_sol_for_gas`:
```python
def ensure_sol_for_gas():
    sol_bal = get_sol_balance()
    sol_price = get_jupiter_price(SOL_MINT) or 170
    usdc_bal = get_usdc_balance()
    total_value = usdc_bal + (sol_bal * sol_price)
    
    # Calculate target
    target_sol = max(SOL_TARGET_FLOOR, min(SOL_TARGET_CEILING, total_value * SOL_TARGET_PCT / sol_price))
    
    # Check if we need refill
    if sol_bal >= target_sol * SOL_REFILL_TRIGGER:
        return False  # plenty of gas
    
    # Check daily budget
    daily_spent = get_daily_gas_spent()
    if daily_spent >= SOL_DAILY_BUDGET:
        print(f"[GAS] Daily budget reached ({daily_spent:.6f}/{SOL_DAILY_BUDGET} SOL) — pausing")
        return False
    
    # Calculate refill
    deficit = target_sol - sol_bal
    max_refill_usd = usdc_bal * SOL_REFILL_CAP_PCT
    refill_amount = min(deficit * sol_price, max_refill_usd)
    
    if refill_amount < 0.5:  # skip if less than $0.50
        return False
    
    success, msg = execute_buy_live(SOL_MINT, "SOL", refill_amount)
    if success:
        log_gas_refill(refill_amount)
    return success
```

### Remove `refill_usdc_from_sol` entirely
The bot should never sell gas for trading capital. If USDC is low, it waits.

### Add gas tracking
```python
GAS_LOG = "gas_tracker.json"

def log_gas_spent(cycle_start_sol, cycle_end_sol):
    spent = cycle_start_sol - cycle_end_sol
    if spent > 0:
        today = datetime.now().strftime("%Y-%m-%d")
        log = {}
        if os.path.exists(GAS_LOG):
            with open(GAS_LOG) as f:
                log = json.load(f)
        log.setdefault(today, 0)
        log[today] += spent
        with open(GAS_LOG, "w") as f:
            json.dump(log, f, indent=2)
        if spent > 0.001:
            print(f"[GAS WARNING] Cycle burned {spent:.6f} SOL — high!")
```

## Expected Outcome
- Gas reserve stays at ~$1-2 worth of SOL
- Daily gas burn capped at ~$0.70
- No more death spirals between SOL and USDC refills
- Bot pauses before it can drain itself
