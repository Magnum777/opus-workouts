#!/usr/bin/env python3
"""Generate a printable dealer call sheet with phone numbers and talking points."""
import argparse
import json
import datetime


CALL_SCRIPT_TEMPLATE = """# Dealer Call Sheet — {date}

## Target Vehicle
{year} {make} {model} {trim}
Color: {color}
Package: {package}
Budget: ${budget:,.0f}

## Call Objectives
- Get total OTD price (sale price + tax + doc fee + title + reg + add-ons)
- Confirm stock / inbound status
- Identify doc fee and any mandatory add-ons
- Stack available incentives (educator, military, Costco, etc.)

## Opening Script
"Hi, I was looking at your inventory online but didn't see the exact trim I'm after. Do you have any {year} {make} {model} {trim} in {color}{package_text} in stock or inbound?"

## If They Have It
"Great. Before I drive in, I need your total out-the-door price on that exact vehicle. Can you give me a breakdown of:

- Vehicle sale price
- Color upcharge — {color} is a premium color{extra_color_note}
- Documentation fee
- Sales tax
- Title and registration fees
- Any dealer-installed add-ons or mandatory packages

What's your best OTD number?"

## Negotiation Prompts
- "I have {incentives_display}. Does that stack with other current offers?"
- "I'm not trading anything in, and I'm pre-approved for financing, but I'll compare your rate."
- "I'm talking to a few dealers today — what's the number that gets me to pick up the keys this week?"

## Questions to Ask Every Dealer
- What is your documentation fee? (Benchmark: ${doc_low}-${doc_high})
- Do you add any mandatory dealer packages (VIN etch, paint protection, etc.)?
- How long is this price good for?
- If it's in transit, when does it arrive?

## If They Don't Have It
"Do you have any {model} {trim} in other colors right now, or do you have one inbound? What about the next trim down/up?"

## If They Push You to Come In
"I appreciate that, but I'm comparing multiple dealers today. Give me your best OTD number over the phone and I'll decide which lot to visit. If the number is right, I'm a same-day buyer."

## Closing
"What's the name and direct number of the person I'm speaking with? I'll call back to confirm if this moves forward."

---

## Dealers to Call

| # | Dealer | City | Phone | Hours | Notes |
|---|--------|------|-------|-------|-------|
"""


def generate_call_sheet(dealers: list, target: dict, incentives: str, doc_range: tuple) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    year = target.get("year", 2026)
    make = target.get("make", "")
    model = target.get("model", "")
    trim = target.get("trim", "")
    color = target.get("color", "")
    package = target.get("package", "")
    budget = target.get("budget", 0)

    package_text = f" with the {package} package" if package else ""
    extra_color_note = " (typically ~$495-$995 upcharge)" if color and ("pearl" in color.lower() or "tri" in color.lower()) else ""

    # Handle empty or missing incentives gracefully
    incentives_display = incentives or "available incentives"
    if incentives_display.strip() == "":
        incentives_display = "available incentives"

    md = CALL_SCRIPT_TEMPLATE.format(
        date=now,
        year=year,
        make=make,
        model=model,
        trim=trim,
        color=color,
        package_text=package_text,
        package=package,
        budget=budget,
        incentives=incentives or "available incentives",
        incentives_display=incentives_display,
        extra_color_note=extra_color_note,
        doc_low=doc_range[0],
        doc_high=doc_range[1],
    )

    for i, d in enumerate(dealers, 1):
        md += f"| {i} | {d.get('name','')} | {d.get('city','')} | {d.get('phone','')} | {d.get('hours','')} | {d.get('notes','')} |\n"

    md += f"""
---

## After-Call Notes

Use this space to record quotes:

| Dealer | Person | OTD Quote | Doc Fee | Add-ons | Stock Status | Notes |
|--------|--------|-----------|---------|---------|--------------|-------|
"""
    for _ in dealers:
        md += "| | | | | | | |\n"

    md += f"""
## Key Benchmarks
- MSRP: ${target.get('msrp', 0):,.0f}
- Target OTD: ${budget:,.0f}
- State doc fee range: ${doc_range[0]}-{doc_range[1]}
- Typical premium color upcharge: $495-$995

Prepared {now}
"""
    return md


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a dealer call sheet.")
    parser.add_argument("--dealers", required=True, help="JSON file with dealer array")
    parser.add_argument("--target", required=True, help="JSON file with target vehicle spec")
    parser.add_argument("--incentives", default="", help="Incentives text")
    parser.add_argument("--incentives-file", default="", help="Path to file containing incentives text")
    parser.add_argument("--config", default="", help="Path to JSON config file with buyer details (may include incentives)")
    parser.add_argument("--doc-low", type=int, default=250)
    parser.add_argument("--doc-high", type=int, default=600)
    parser.add_argument("--output", default="call_sheet.md")
    args = parser.parse_args()

    with open(args.dealers, "r", encoding="utf-8") as f:
        dealers = json.load(f)
    with open(args.target, "r", encoding="utf-8") as f:
        target = json.load(f)

    # Resolve incentives from file, config, or CLI arg
    incentives_text = args.incentives or ""
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        if config_data.get("incentives"):
            incentives_text = config_data["incentives"]
    if args.incentives_file:
        with open(args.incentives_file, "r", encoding="utf-8") as f:
            incentives_text = f.read().strip()

    md = generate_call_sheet(dealers, target, incentives_text, (args.doc_low, args.doc_high))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Call sheet written to {args.output}")


if __name__ == "__main__":
    main()
