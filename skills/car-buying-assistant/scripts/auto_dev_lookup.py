#!/usr/bin/env python3
"""
auto_dev_lookup.py — Query auto.dev API for VIN decode and related vehicle data.

Starter plan: ~100 requests/day. Use --full sparingly (1 VIN = ~10 requests).

Usage:
    python auto_dev_lookup.py --vin WP0AF2A99KS165242
    python auto_dev_lookup.py --vin WP0AF2A99KS165242 --full --output data.json
    python auto_dev_lookup.py --vin WP0AF2A99KS165242 --specs --recalls --listings
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Starter plan API key for James
DEFAULT_API_KEY = "sk_ad_x0vn9TqrdvQxJ8Ceql8PWU3S"
BASE_URL = "https://api.auto.dev"


def api_request(endpoint: str, api_key: str, method: str = "GET", data=None) -> dict:
    """Make an auto.dev API request and return parsed JSON."""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode("utf-8")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err_json = json.loads(body)
            # Code may be at top level or nested under "error" key
            code = err_json.get("code") or (err_json.get("error") or {}).get("code", "")
            if code == "FEATURE_NOT_AVAILABLE":
                return {
                    "_error": True,
                    "_status": e.code,
                    "_code": "FEATURE_NOT_AVAILABLE",
                    "_message": err_json.get("message") or (err_json.get("error") or {}).get("message", "Payment required"),
                    "_requiredPlan": err_json.get("requiredPlan") or (err_json.get("error") or {}).get("requiredPlan"),
                    "_currentPlan": err_json.get("currentPlan") or (err_json.get("error") or {}).get("currentPlan"),
                }
            elif e.code == 404 and code == "VIN_NOT_FOUND":
                return {
                    "_error": True,
                    "_status": e.code,
                    "_code": "VIN_NOT_FOUND",
                    "_message": err_json.get("message") or (err_json.get("error") or {}).get("message", "No data found for this VIN"),
                }
        except Exception:
            pass
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        print(f"Response: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def vin_decode(vin: str, api_key: str) -> dict:
    """Decode a VIN. Returns the full API response."""
    return api_request(f"/vin/{vin}", api_key)


def fetch_related(vin_data: dict, endpoints: list[str], api_key: str) -> dict:
    """Fetch related data from discover links in the VIN response."""
    discover = vin_data.get("discover", {})
    results = {}

    for name in endpoints:
        # Match discover keys by endpoint name
        matched_url = None
        for key, url in discover.items():
            if name.lower() in key.lower() or name.lower() in url.lower():
                matched_url = url
                break

        if not matched_url:
            print(f"Warning: no discover link found for '{name}'", file=sys.stderr)
            continue

        try:
            path = matched_url.replace(BASE_URL, "")
            print(f"  -> {name}: {path}")
            resp = api_request(path, api_key)
            if resp.get("_error"):
                msg = resp.get("_message", "Unknown error")
                if resp.get("_requiredPlan"):
                    print(f"  X {name}: {msg} (requires {resp['_requiredPlan']} plan)")
                else:
                    print(f"  X {name}: {msg}")
                results[name] = resp
            else:
                results[name] = resp
        except Exception as e:
            print(f"  X {name} failed: {e}", file=sys.stderr)
            results[name] = {"error": str(e)}

    return results


def print_summary(vin_data: dict):
    """Print a human-readable summary of the VIN decode."""
    vehicle = vin_data.get("vehicle", {})
    print(f"\n{'='*50}")
    print(f"  VIN:          {vin_data.get('vin', 'N/A')}")
    print(f"  Valid:        {vin_data.get('vinValid', False)}")
    print(f"  Year:         {vehicle.get('year', 'N/A')}")
    print(f"  Make:         {vehicle.get('make', 'N/A')}")
    print(f"  Model:        {vehicle.get('model', 'N/A')}")
    print(f"  Trim:         {vin_data.get('trim', 'N/A')}")
    print(f"  Style:        {vin_data.get('style', 'N/A')}")
    print(f"  Engine:       {vin_data.get('engine', 'N/A')}")
    print(f"  Drive:        {vin_data.get('drive', 'N/A')}")
    print(f"  Transmission: {vin_data.get('transmission', 'N/A')}")
    print(f"  Type:         {vin_data.get('type', 'N/A')}")
    print(f"  Origin:       {vin_data.get('origin', 'N/A')}")
    print(f"{'='*50}\n")

    discover = vin_data.get("discover", {})
    if discover:
        print("Available lookups:")
        for name, url in discover.items():
            safe_name = name.encode("ascii", "ignore").decode("ascii").strip()
            print(f"  - {safe_name}: {url}")
        print()


def main():
    # Force UTF-8 for stdout on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="auto.dev VIN lookup helper")
    parser.add_argument("--vin", required=True, help="Vehicle VIN to decode")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="auto.dev API key")
    parser.add_argument("--output", help="Write full JSON to this file")
    parser.add_argument("--full", action="store_true", help="Fetch ALL related data (uses ~10 requests)")
    parser.add_argument("--specs", action="store_true", help="Fetch specifications")
    parser.add_argument("--build", action="store_true", help="Fetch OEM build data")
    parser.add_argument("--recalls", action="store_true", help="Fetch all recalls")
    parser.add_argument("--open-recalls", action="store_true", help="Fetch open recalls")
    parser.add_argument("--listings", action="store_true", help="Fetch marketplace listings")
    parser.add_argument("--photos", action="store_true", help="Fetch vehicle photos")
    parser.add_argument("--apr", action="store_true", help="Fetch interest rates")
    parser.add_argument("--payments", action="store_true", help="Fetch payment estimates")
    parser.add_argument("--taxes", action="store_true", help="Fetch taxes & fees")
    parser.add_argument("--tco", action="store_true", help="Fetch total cost of ownership")
    args = parser.parse_args()

    # Decode VIN first
    print(f"Decoding VIN: {args.vin}...")
    vin_data = vin_decode(args.vin, args.api_key)
    print_summary(vin_data)

    result = {"vin_decode": vin_data}

    # Build list of endpoints to fetch
    endpoints = []
    if args.full:
        endpoints = ["specs", "build", "recalls", "openrecalls", "listings", "photos", "apr", "payments", "taxes", "tco"]
    else:
        if args.specs: endpoints.append("specs")
        if args.build: endpoints.append("build")
        if args.recalls: endpoints.append("recalls")
        if args.open_recalls: endpoints.append("openrecalls")
        if args.listings: endpoints.append("listings")
        if args.photos: endpoints.append("photos")
        if args.apr: endpoints.append("apr")
        if args.payments: endpoints.append("payments")
        if args.taxes: endpoints.append("taxes")
        if args.tco: endpoints.append("tco")

    if endpoints:
        print(f"Fetching related data: {', '.join(endpoints)}...")
        related = fetch_related(vin_data, endpoints, args.api_key)
        result.update(related)

    # Write output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Wrote full results to: {out_path}")

    # Also print condensed JSON to stdout
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
