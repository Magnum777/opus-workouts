#!/usr/bin/env python3
"""Decode VIN using NHTSA API. Falls back to basic VIN checksum validation."""
import argparse
import json
import urllib.request
import urllib.error


def decode_vin_nhtsa(vin: str) -> dict:
    """Query NHTSA vPIC API for VIN decode."""
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"NHTSA API failed: {e}", "vin": vin}

    result = {"vin": vin}
    for item in data.get("Results", []):
        var = item.get("Variable")
        val = item.get("Value")
        if var and val:
            result[var.replace(" ", "_").lower()] = val

    # Extract commonly used fields
    result["year"] = result.get("model_year")
    result["make"] = result.get("make")
    result["model"] = result.get("model")
    result["trim"] = result.get("trim")
    result["series"] = result.get("series")
    result["engine"] = result.get("engine_model")
    result["plant"] = result.get("plant_company_name") or result.get("plant_city")
    return result


def validate_vin_checksum(vin: str) -> bool:
    """Basic VIN checksum validation (positions 1-8, 10, 9=check digit)."""
    if len(vin) != 17:
        return False
    transliteration = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
        "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
        "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
    }
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    total = 0
    for i, ch in enumerate(vin.upper()):
        if ch.isdigit():
            val = int(ch)
        elif ch in transliteration:
            val = transliteration[ch]
        else:
            return False
        total += val * weights[i]
    check_digit = total % 11
    check_char = "X" if check_digit == 10 else str(check_digit)
    return vin[8].upper() == check_char


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode a VIN using NHTSA API.")
    parser.add_argument("--vin", required=True, help="17-character VIN")
    parser.add_argument("--output", help="Optional JSON output file path")
    args = parser.parse_args()

    vin = args.vin.strip().upper()
    if len(vin) != 17:
        raise SystemExit(f"Invalid VIN length: {len(vin)} (expected 17)")

    valid = validate_vin_checksum(vin)
    result = decode_vin_nhtsa(vin)
    result["checksum_valid"] = valid

    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
