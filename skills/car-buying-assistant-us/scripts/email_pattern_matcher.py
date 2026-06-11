#!/usr/bin/env python3
"""Guess staff email addresses from dealership domain + names from LinkedIn/staff pages."""
import argparse
import itertools


def generate_patterns(first: str, last: str, domain: str) -> list:
    """Generate common email patterns for a given name."""
    f = first.lower().strip()
    l = last.lower().strip()
    fi = f[0] if f else ""
    li = l[0] if l else ""

    patterns = [
        f"{f}.{l}@{domain}",
        f"{f}{l}@{domain}",
        f"{fi}{l}@{domain}",
        f"{f}_{l}@{domain}",
        f"{f}-{l}@{domain}",
        f"{fi}.{l}@{domain}",
        f"{f}{li}@{domain}",
        f"{f}@{domain}",
        f"{l}@{domain}",
        f"{fi}{li}@{domain}",
    ]

    # Handle compound last names (hyphenated or multi-word)
    if "-" in last or " " in last:
        l_compact = l.replace(" ", "").replace("-", "")
        li_compact = l_compact[0]
        patterns += [
            f"{f}.{l_compact}@{domain}",
            f"{fi}{l_compact}@{domain}",
        ]

    return patterns


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate probable staff email addresses from dealership domain + names."
    )
    parser.add_argument("--domain", required=True, help="Dealership email domain (e.g. danvadenchevrolet.com)")
    parser.add_argument(
        "--names",
        required=True,
        help='Comma-separated full names (e.g. "David Jung,Jonathan Rounds,Bill Bringhurst")',
    )
    parser.add_argument("--output", help="Optional output file for email list")
    args = parser.parse_args()

    domain = args.domain.lower().strip()
    if not domain.startswith("@"):
        domain = domain.lstrip("@")

    names_raw = [n.strip() for n in args.names.split(",") if n.strip()]
    results = []

    for full_name in names_raw:
        parts = full_name.split()
        if len(parts) >= 2:
            first = parts[0]
            last = " ".join(parts[1:])  # Handles multi-word last names
            emails = generate_patterns(first, last, domain)
            entry = {
                "full_name": full_name,
                "first": first,
                "last": last,
                "probable_emails": emails,
            }
            results.append(entry)
            print(f"\n{full_name}")
            for e in emails:
                print(f"  - {e}")
        else:
            print(f"  Skipping '{full_name}' — need at least first + last name")

    if args.output:
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved {len(results)} entries to {args.output}")


if __name__ == "__main__":
    main()
