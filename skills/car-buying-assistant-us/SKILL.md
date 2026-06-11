---
name: Car Buying Assistant US
slug: car-buying-assistant-us
version: 1.0.0
description: "Help car buyers in the US research, compare, and negotiate on new/used vehicles. Covers state-specific OTD pricing, VIN decoding, dealer email outreach, and negotiation scripts. Geared for dealers who expose inventory online; never sends money or payment details."
metadata:
  openclaw:
    emoji: "🚙"
    requires:
      bins: []
    os: ["darwin", "linux", "win32"]
    configPaths:
      - "~/.openclaw/workspace/car-search/"
---

# Car Buying Assistant US

A fork of [car-buying-assistant](https://clawhub.ai/justintsmith/car-buying-assistant) rebuilt for the US market. Adds state tax/fee calculations, VIN decoding, dealer email pattern matching, and negotiation templates.

## What This Skill Does

- **VIN Decoder** — Extract year/make/model/trim from a VIN using NHTSA API
- **OTD Calculator** — Compute total out-the-door price for any US state (sales tax, doc fees, title, registration). Includes disclaimer that rates are state averages; verify with dealer.
- **Dealer Email Matcher** — Guess staff emails from LinkedIn profiles + known dealership domain patterns
- **Email Templates** — Generate negotiation-ready OTD quote request emails
- **Call Scripts** — Generate phone scripts with dealer numbers, talking points, and fee benchmarks
- **Listing Comparison** — Normalize and compare candidates with red-flag detection

## What This Skill Does NOT Do

- Does not send money or process payments
- Does not submit credit applications
- Does not log into dealer portals or social media
- Does not guarantee vehicle condition or history
- Does not send emails/messages automatically — drafts only, user sends

## File Layout

Sessions are stored under `~/.openclaw/workspace/car-search/`:

```
sessions/
  YYYY-MM-DD-<slug>/
    criteria.md         # search criteria
    listings.json       # candidate vehicles
    listings.normalized.json
    comparison.md       # ranked comparison + red flags
    negotiation.md      # draft emails + call scripts
    otd_breakdowns.json # state-by-state OTD estimates
    notes.md            # scratchpad
archive/
  ...                   # older sessions
```

## Workflow

### 1. Clarify Criteria
Record answers in `criteria.md`:
- Budget (cash / financed)
- Use case (commute, family, towing, etc.)
- Location / search radius
- Body type, powertrain preference
- Must-have features (AWD, CarPlay, third row, etc.)
- Deal-breakers (max miles, no salvage, specific years to avoid)

### 2. Gather Listings
Sources (public pages only):
- Dealer inventory sites (DealerInspire, DealerOn, CDK, etc.)
- Cars.com, Edmunds, TrueCar, CarMax, Autotrader.com
- Manufacturer build-your-own tools for MSRP/config
- Reddit/forums for model reliability and common issues

Extract per candidate:
- `vin`, `year_make_model_trim`, `msrp_or_list_price`, `color`
- `location`, `seller_name`, `seller_phone`, `seller_website`
- `inventory_status` (in stock, in transit, factory order)
- `url`, `notes`

Store in `listings.json`. Run `normalize_listings.py` to standardize keys.

### 3. Decode VINs
Run `vin_decoder.py` on each VIN to populate:
- Year, make, model, trim, engine, drivetrain, plant
- Verify listing accuracy (some dealers mislabel trim levels)

### 4. Calculate OTD Pricing
Run `otd_calculator.py` with:
- ZIP code (determines state + county tax rates)
- Vehicle price (MSRP or negotiated)
- Trade-in value (reduces taxable amount in most states)
- Optional doc fee cap override

**Important:** Output includes a disclaimer — tax rates are state averages. Actual rates vary by county/city. Always verify the total with the dealer before signing.

Outputs state-specific totals:
- Sales tax (state + local rates)
- Documentation fee
- Title fee
- Registration fee
- Total OTD

### 5. Find Dealer Emails
For dealers without public email contacts:
- Search LinkedIn for sales manager / GSM names
- Run `email_pattern_matcher.py` with dealership domain + staff names
- Generates probable email addresses (pattern-based guesses, not verified)

### 6. Draft Outreach
- `email_template_generator.py` — outputs OTD quote request email for each dealer
- `call_script_generator.py` — outputs phone script with talking points

User reviews drafts and sends themselves.

### 7. Compare & Decide
Fill `comparison.md` with:
- Side-by-side candidate table
- Model-specific research (common issues, recall history, owner feedback)
- Red flags (mislabeled trim, suspicious pricing, mandatory add-ons)
- Clear recommendation: Buy / Shortlist / Keep Looking

## Scripts

### `scripts/vin_decoder.py`
Query NHTSA API for VIN decode. Falls back to basic VIN checksum validation.

Usage:
```bash
python vin_decoder.py --vin 1GNERLKS8TJ262544
```

### `scripts/otd_calculator.py`
Compute total OTD price for any US ZIP code.

Usage:
```bash
python otd_calculator.py --zip 31093 --price 55400 --trade 0
```

### `scripts/email_pattern_matcher.py`
Guess staff emails from names + dealership domain.

Usage:
```bash
python email_pattern_matcher.py --domain danvadenchevrolet.com \
  --names "David Jung,Jonathan Rounds"
```

### `scripts/email_template_generator.py`
Generate OTD quote request email given dealer info + vehicle spec.

Supports CLI args or a JSON config file for complex values (e.g. incentives with `$` signs).

**CLI usage:**
```bash
python email_template_generator.py --dealer "Dan Vaden Chevrolet" \
  --to "djung@danvadenchevrolet.com" --vehicle "2026 Traverse RS" \
  --color "Iridescent Pearl Tricoat" --package "1RS" --output quote_email.txt
```

**Config file usage** (recommended when incentives contain `$`):
```bash
python email_template_generator.py --dealer "Dan Vaden Chevrolet" \
  --to "djung@danvadenchevrolet.com" --vehicle "Traverse RS" \
  --config buyer_config.json --output quote_email.txt
```

`buyer_config.json`:
```json
{
  "name": "James Henderson",
  "phone": "256-490-8625",
  "location": "Warner Robins, GA",
  "incentives": "GM Educator Appreciation Program ($500 — wife is a teacher)"
}
```

### `scripts/call_script_generator.py`
Generate a printable call sheet.

Supports CLI args or a JSON config file for buyer details and incentives.

**CLI usage:**
```bash
python call_script_generator.py --dealers dealers.json \
  --target target_vehicle.json --output call_sheet.md
```

**Config file usage** (recommended for complex incentives):
```bash
python call_script_generator.py --dealers dealers.json \
  --target target_vehicle.json --config buyer_config.json \
  --output call_sheet.md
```

`target_vehicle.json`:
```json
{
  "year": 2026,
  "make": "Chevrolet",
  "model": "Traverse",
  "trim": "RS",
  "color": "Iridescent Pearl Tricoat",
  "package": "1RS",
  "budget": 60000,
  "msrp": 55400
}
```

### `scripts/normalize_listings.py`
Ensures `listings.json` has consistent keys. Passes through extras.

## Safety & Boundaries

1. **Never send money.** No payment initiation.
2. **Never share payment/identity details.** No SSN, credit card, banking info on any site.
3. **No automated logins.** Public listings and URLs only.
4. **Always ask before contacting dealers.** Draft emails/messages, user confirms before sending.
5. **Treat all data as approximate.** Encourage inspections and history reports.

## License

MIT-0 — fork freely.

## Credits

Forked from [car-buying-assistant](https://clawhub.ai/justintsmith/car-buying-assistant) by justintsmith (Ontario/Canada market).
US-market additions by Nova / Layered Media LLC.
