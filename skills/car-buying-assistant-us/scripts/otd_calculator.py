#!/usr/bin/env python3
"""Calculate total Out-The-Door (OTD) price for any US ZIP code."""
import argparse
import json

# State tax rates (state-level only; many counties add local tax)
STATE_TAX_RATES = {
    "AL": 0.02, "AK": 0.0, "AZ": 0.056, "AR": 0.065, "CA": 0.0725,
    "CO": 0.029, "CT": 0.0635, "DE": 0.0, "FL": 0.06, "GA": 0.04,
    "HI": 0.04, "ID": 0.06, "IL": 0.0625, "IN": 0.07, "IA": 0.06,
    "KS": 0.065, "KY": 0.06, "LA": 0.0445, "ME": 0.055, "MD": 0.06,
    "MA": 0.0625, "MI": 0.06, "MN": 0.06875, "MS": 0.07, "MO": 0.04225,
    "MT": 0.0, "NE": 0.055, "NV": 0.0685, "NH": 0.0, "NJ": 0.06625,
    "NM": 0.05125, "NY": 0.04, "NC": 0.0475, "ND": 0.05, "OH": 0.0575,
    "OK": 0.045, "OR": 0.0, "PA": 0.06, "RI": 0.07, "SC": 0.06,
    "SD": 0.045, "TN": 0.07, "TX": 0.0625, "UT": 0.0595, "VT": 0.06,
    "VA": 0.043, "WA": 0.065, "WV": 0.06, "WI": 0.05, "WY": 0.04,
    "DC": 0.06,
}

# Average local tax add-on by state (rough; varies by county)
LOCAL_TAX_AVG = {
    "AL": 0.03, "AZ": 0.025, "AR": 0.015, "CA": 0.015, "CO": 0.045,
    "FL": 0.01, "GA": 0.03, "IL": 0.015, "IN": 0.0, "KS": 0.02,
    "LA": 0.05, "MD": 0.0, "MN": 0.005, "MO": 0.02, "MS": 0.01,
    "NC": 0.02, "NV": 0.015, "NM": 0.03, "NY": 0.045, "OK": 0.015,
    "SC": 0.01, "SD": 0.015, "TN": 0.025, "TX": 0.015, "UT": 0.01,
    "VA": 0.01, "WA": 0.025, "WI": 0.005, "WY": 0.01,
}

# Doc fees (typical range; no cap in many states)
DOC_FEE_RANGE = {
    "AL": (300, 600), "AK": (150, 300), "AZ": (300, 500), "AR": (150, 400),
    "CA": (85, 500), "CO": (300, 600), "CT": (400, 600), "DE": (300, 500),
    "FL": (0, 999), "GA": (250, 600), "HI": (300, 500), "ID": (100, 400),
    "IL": (200, 400), "IN": (200, 500), "IA": (100, 400), "KS": (200, 500),
    "KY": (200, 450), "LA": (200, 550), "ME": (200, 400), "MD": (300, 600),
    "MA": (300, 500), "MI": (200, 400), "MN": (100, 150), "MS": (200, 500),
    "MO": (200, 500), "MT": (100, 400), "NE": (200, 400), "NV": (150, 500),
    "NH": (300, 500), "NJ": (300, 600), "NM": (200, 450), "NY": (75, 400),
    "NC": (0, 999), "ND": (100, 400), "OH": (200, 500), "OK": (200, 400),
    "OR": (75, 400), "PA": (100, 500), "RI": (200, 400), "SC": (0, 500),
    "SD": (100, 300), "TN": (300, 600), "TX": (100, 500), "UT": (200, 500),
    "VT": (200, 400), "VA": (300, 600), "WA": (150, 300), "WV": (200, 400),
    "WI": (100, 300), "WY": (150, 400), "DC": (300, 600),
}

TITLE_FEE = {
    "AL": 18, "AK": 15, "AZ": 4, "AR": 10, "CA": 23,
    "CO": 7.2, "CT": 25, "DE": 35, "FL": 85.25, "GA": 18,
    "HI": 5, "ID": 14, "IL": 95, "IN": 15, "IA": 25,
    "KS": 10, "KY": 9, "LA": 68.5, "ME": 33, "MD": 100,
    "MA": 75, "MI": 15, "MN": 8.25, "MS": 9, "MO": 11,
    "MT": 12, "NE": 10, "NV": 29.25, "NH": 25, "NJ": 60,
    "NM": 5, "NY": 50, "NC": 56, "ND": 5, "OH": 15,
    "OK": 96, "OR": 98, "PA": 58, "RI": 52.5, "SC": 15,
    "SD": 10, "TN": 95, "TX": 33, "UT": 6, "VT": 35,
    "VA": 15, "WA": 15, "WV": 15, "WI": 164.5, "WY": 15,
    "DC": 26,
}

REGISTRATION_FEE = {
    "AL": 23, "AK": 100, "AZ": 8, "AR": 30, "CA": 65,
    "CO": 10, "CT": 80, "DE": 40, "FL": 225, "GA": 20,
    "HI": 45, "ID": 45, "IL": 101, "IN": 21.35, "IA": 50,
    "KS": 40, "KY": 21, "LA": 20, "ME": 35, "MD": 135,
    "MA": 60, "MI": 5, "MN": 35, "MS": 15, "MO": 29,
    "MT": 12, "NE": 15, "NV": 33, "NH": 40, "NJ": 60,
    "NM": 30, "NY": 50, "NC": 38.75, "ND": 5, "OH": 34.5,
    "OK": 96, "OR": 112, "PA": 39, "RI": 30, "SC": 40,
    "SD": 36, "TN": 26.5, "TX": 51.75, "UT": 44, "VT": 47,
    "VA": 40.75, "WA": 30, "WV": 30, "WI": 85, "WY": 30,
    "DC": 72,
}


def zip_to_state(zip_code: str) -> str:
    """Rough mapping of ZIP code to state."""
    z = int(zip_code[:3])
    if 300 <= z <= 319:
        return "GA"
    if 320 <= z <= 349:
        return "FL"
    if z >= 980:
        return "WA"
    if 500 <= z <= 528:
        return "IA"
    if 600 <= z <= 699:
        return "IL"
    if 700 <= z <= 714:
        return "LA"
    if 750 <= z <= 799:
        return "TX"
    if 850 <= z <= 865:
        return "AZ"
    if 870 <= z <= 884:
        return "NM"
    if 900 <= z <= 961:
        return "CA"
    if 100 <= z <= 149:
        return "NY"
    if 150 <= z <= 196:
        return "PA"
    if 200 <= z <= 205:
        return "DC"
    if 206 <= z <= 219:
        return "MD"
    if 220 <= z <= 246:
        return "VA"
    if 247 <= z <= 268:
        return "WV"
    if 270 <= z <= 289:
        return "NC"
    if 290 <= z <= 299:
        return "SC"
    if 350 <= z <= 369:
        return "AL"
    if 370 <= z <= 385:
        return "TN"
    if 386 <= z <= 397:
        return "MS"
    if 400 <= z <= 427:
        return "KY"
    if 430 <= z <= 458:
        return "OH"
    if 460 <= z <= 479:
        return "IN"
    if 480 <= z <= 499:
        return "MI"
    if 530 <= z <= 549:
        return "WI"
    if 550 <= z <= 567:
        return "MN"
    if 570 <= z <= 577:
        return "SD"
    if 580 <= z <= 588:
        return "ND"
    if 590 <= z <= 599:
        return "MT"
    if 680 <= z <= 693:
        return "NE"
    if 700 <= z <= 714:
        return "LA"
    if 716 <= z <= 729:
        return "AR"
    if 730 <= z <= 749:
        return "OK"
    if 800 <= z <= 816:
        return "CO"
    if 820 <= z <= 831:
        return "WY"
    if 832 <= z <= 838:
        return "ID"
    if 840 <= z <= 847:
        return "UT"
    if 889 <= z <= 898:
        return "NV"
    return "UNKNOWN"


def calculate_otd(state: str, price: float, trade_in: float = 0.0, doc_fee: float = None) -> dict:
    """Calculate OTD breakdown for a given state."""
    taxable_base = max(price - trade_in, 0)
    state_tax_rate = STATE_TAX_RATES.get(state, 0.06)
    local_tax_rate = LOCAL_TAX_AVG.get(state, 0.0)
    total_tax_rate = state_tax_rate + local_tax_rate

    tax_amount = taxable_base * total_tax_rate

    if doc_fee is None:
        low, high = DOC_FEE_RANGE.get(state, (250, 600))
        doc_fee = (low + high) / 2

    title = TITLE_FEE.get(state, 50)
    registration = REGISTRATION_FEE.get(state, 50)

    total = price + tax_amount + doc_fee + title + registration

    return {
        "state": state,
        "vehicle_price": round(price, 2),
        "trade_in": round(trade_in, 2),
        "taxable_base": round(taxable_base, 2),
        "state_tax_rate": state_tax_rate,
        "local_tax_rate": local_tax_rate,
        "total_tax_rate": round(total_tax_rate, 4),
        "tax_amount": round(tax_amount, 2),
        "doc_fee": round(doc_fee, 2),
        "title_fee": title,
        "registration_fee": registration,
        "total_otd": round(total, 2),
        "disclaimer": "ESTIMATE — tax rates vary by county/city. Confirm actual tax and fees with dealer or DMV before purchasing.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate OTD price for a US ZIP code.")
    parser.add_argument("--zip", required=True, help="ZIP code (5 digits)")
    parser.add_argument("--price", type=float, required=True, help="Vehicle sale price")
    parser.add_argument("--trade", type=float, default=0.0, help="Trade-in value")
    parser.add_argument("--doc", type=float, help="Override doc fee")
    parser.add_argument("--output", help="JSON output file")
    args = parser.parse_args()

    if len(args.zip) != 5 or not args.zip.isdigit():
        raise SystemExit("ZIP code must be 5 digits")

    state = zip_to_state(args.zip)
    if state == "UNKNOWN":
        print(f"Warning: Could not determine state for ZIP {args.zip}. Using default CA rates.")
        state = "CA"

    result = calculate_otd(state, args.price, args.trade, args.doc)
    result["zip_code"] = args.zip

    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
