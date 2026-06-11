#!/usr/bin/env python3
"""Generate OTD quote request email for car dealers."""
import argparse
import datetime


def generate_email(dealer: str, to: str, vehicle: str, color: str, package: str = "",
                   year: int = 2026, make: str = "Chevrolet", buyer_name: str = "",
                   buyer_phone: str = "", buyer_location: str = "", incentives: str = "") -> str:
    """Generate a professional OTD quote request email."""
    pkg_line = f" with the {package} package" if package else ""
    color_upcharge_note = ""
    if color and "pearl" in color.lower() or "tri" in color.lower():
        color_upcharge_note = "\n- Color upcharge (premium tri-coat)"
    elif color:
        color_upcharge_note = "\n- Color upcharge (if applicable)"

    incentive_block = ""
    if incentives and incentives.strip():
        incentive_block = f"\nI have the {incentives.strip()} available. Can this stack with other current offers?\n"

    body = f"""Hi,

I'm shopping for a {year} {make} {vehicle} in {color}{pkg_line}. I'm reaching out to several dealers for competitive out-the-door pricing.

Before I visit any showroom, I'd like your total out-the-door price on this exact vehicle including:

- Vehicle sale price{color_upcharge_note}
- Documentation fee
- Sales tax
- Title and registration fees
- Any dealer-installed add-ons or mandatory packages

Please also confirm:
- Do you currently have this trim/color in stock or inbound?
- What is your documentation fee?
- Are there any current manufacturer incentives or rebates applicable to the {vehicle}?
{incentive_block}
I'm pre-approved for financing but open to comparing your rate. I am not trading in a vehicle.

I intend to make a decision soon, so please reply with your best OTD number.

Thanks,
{buyer_name}
{buyer_phone}
{buyer_location}""".strip()

    return body


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dealer quote request email.")
    parser.add_argument("--dealer", required=True, help="Dealership name")
    parser.add_argument("--to", required=True, help="Recipient email")
    parser.add_argument("--vehicle", required=True, help="Vehicle model + trim (e.g. 'Traverse RS')")
    parser.add_argument("--color", default="", help="Exterior color")
    parser.add_argument("--package", default="", help="Package code (e.g. '1RS')")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--make", default="Chevrolet")
    parser.add_argument("--name", default="", help="Buyer name")
    parser.add_argument("--phone", default="", help="Buyer phone")
    parser.add_argument("--location", default="", help="Buyer city/state")
    parser.add_argument("--incentives", default="", help="Incentives the buyer qualifies for (text)")
    parser.add_argument("--incentives-file", default="", help="Path to file containing incentives text (avoids $ escaping issues)")
    parser.add_argument("--config", default="", help="Path to JSON config file with buyer details")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    # Load config file if provided
    config_data = {}
    if args.config:
        import json
        with open(args.config, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    # Resolve incentives from file, config, or CLI arg (precedence: file > config > CLI)
    incentives_text = args.incentives or ""
    if config_data.get("incentives"):
        incentives_text = config_data["incentives"]
    if args.incentives_file:
        with open(args.incentives_file, "r", encoding="utf-8") as f:
            incentives_text = f.read().strip()

    body = generate_email(
        dealer=args.dealer,
        to=args.to,
        vehicle=args.vehicle,
        color=args.color,
        package=args.package,
        year=args.year,
        make=args.make,
        buyer_name=config_data.get("name", args.name),
        buyer_phone=config_data.get("phone", args.phone),
        buyer_location=config_data.get("location", args.location),
        incentives=incentives_text,
    )

    full_email = f"To: {args.to}\nSubject: OTD Quote Request — {args.year} {args.make} {args.vehicle}, {args.color}\n\n{body}"

    print(full_email)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(full_email)
        print(f"\n\nSaved to {args.output}")


if __name__ == "__main__":
    main()
