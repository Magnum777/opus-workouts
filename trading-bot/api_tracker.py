import os, json, datetime

USAGE_FILE = os.path.join(os.path.dirname(__file__), "api_usage.json")

DEFAULT_USAGE = {
    "coingecko": {"calls": 0, "last_reset": None},
    "lunarcrush": {"calls": 0, "last_reset": None},
    "cryptopanic": {"calls": 0, "last_reset": None},
    "notion": {"calls": 0, "last_reset": None},
}

def _load_usage():
    if not os.path.exists(USAGE_FILE):
        # initialize file
        data = DEFAULT_USAGE.copy()
        now = datetime.datetime.utcnow().isoformat() + "Z"
        for v in data.values():
            v["last_reset"] = now
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data
    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_usage(data):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def track(api_name, reset_hours=1):
    """Increment call count for *api_name* and reset if *reset_hours* have passed.
    Returns the current call count after increment.
    """
    data = _load_usage()
    now = datetime.datetime.utcnow()
    entry = data.get(api_name)
    if not entry:
        entry = {"calls": 0, "last_reset": now.isoformat() + "Z"}
    # reset if needed
    last = datetime.datetime.fromisoformat(entry["last_reset"].replace("Z", ""))
    if (now - last).total_seconds() >= reset_hours * 3600:
        entry = {"calls": 0, "last_reset": now.isoformat() + "Z"}
    entry["calls"] += 1
    entry["last_reset"] = now.isoformat() + "Z"
    data[api_name] = entry
    _save_usage(data)
    return entry["calls"]

def usage():
    """Return the full usage dict (for reporting)."""
    return _load_usage()
