"""Set re-buy cooldowns on coins we just dumped so bot doesn't re-enter them"""
import json, os
from datetime import datetime, timezone, timedelta

COOLDOWN_FILE = os.path.join(os.path.dirname(__file__), "rebuy_cooldowns.json")
COOLDOWN_HOURS = 48  # Keep them out for 2 days

dumped = {
    "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv": "PENGU",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
    "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE": "ORCA",
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R": "RAY",
    "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN": "TRUMP",
}

cooldowns = {}
now = datetime.now(timezone.utc)
for mint, token in dumped.items():
    cooldowns[mint] = {
        "token": token,
        "sold_at": now.isoformat(),
        "cooldown_until": (now + timedelta(hours=COOLDOWN_HOURS)).isoformat()
    }

json.dump(cooldowns, open(COOLDOWN_FILE, "w"), indent=2)
print(f"Set {len(dumped)} re-buy cooldowns ({COOLDOWN_HOURS}h each):")
for mint, entry in cooldowns.items():
    print(f"  {entry['token']:8s} -> {entry['cooldown_until'][:19]}")