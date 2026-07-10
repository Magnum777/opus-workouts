# Coding Guidelines for Nova

Adapted from Stack Overflow's "Building shared coding guidelines for AI (and people too)" (March 2026).
These rules apply to ALL code Nova writes: Python scripts, shell commands, Node.js tools, Discord bots, web scrapers, financial utilities, and automation pipelines.

---

## 1. Philosophy

- **Be explicit, not implicit.** If a human engineer would need to infer intent, spell it out.
- **Prefer boring over clever.** Simple solutions beat clever ones. Clever code breaks.
- **Fail well.** Every script must handle errors gracefully and log what happened.
- **AI loves patterns.** Provide examples of both CORRECT and INCORRECT code. Nova learns from the contrast.

---

## 2. Language & Stack

| Context | Primary Language | Supporting Tools |
|---------|------------------|------------------|
| Automation scripts | Python 3.11+ | `requests`, `json`, `pathlib`, `logging` |
| Discord bots / API calls | Shell (pwsh/bash) + `curl` | Discord API v10 |
| Web scraping | Python | `playwright`, `requests`, `BeautifulSoup` |
| Data processing | Python | `pandas` (if needed), standard library preferred |
| Financial tools | Python / shell | CSV parsing, simple math, no heavy deps |
| Config edits | Python `json` module or direct file I/O | Never use regex for JSON |

**Rule:** Do not introduce new languages or frameworks without checking with Opus first.

---

## 3. Naming Conventions

### Variables & Functions
- Use `snake_case` for Python variables and functions.
- Use `camelCase` for JavaScript / Node.js.
- Use `SCREAMING_SNAKE_CASE` for constants and environment variable names.
- Names must describe WHAT, not HOW. `process_csv` is better than `do_thing`.

**CORRECT:**
```python
user_email = "opus@example.com"
MAX_RETRY_COUNT = 3

def fetch_discord_channel_messages(channel_id: str, limit: int = 100) -> list:
    """Fetch recent messages from a Discord channel."""
```

**INCORRECT:**
```python
x = "opus@example.com"  # what is x?
max = 3  # max what? shadows built-in?
def do_stuff(a, b):  # meaningless
```

### Files
- Python scripts: `snake_case.py` — e.g., `gmail_spam_sweep.py`, `discover_patterns.py`
- Shell scripts: `kebab-case.sh` or `snake_case.sh`
- Config files: `kebab-case.json`, `SCREAMING-config.env`
- Documentation: `UPPERCASE.md` for important docs (AGENTS.md, MEMORY.md, TOOLS.md)

---

## 4. Error Handling

Every script that makes network calls, reads files, or runs shell commands MUST handle failures.

**CORRECT:**
```python
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_url(url: str) -> dict:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out: {url}")
        return {}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} for {url}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return {}
```

**INCORRECT:**
```python
response = requests.get(url)  # No timeout
return response.json()  # Will crash on 404, 500, timeout, bad JSON
```

**Shell script CORRECT:**
```bash
if ! response=$(curl -s -f -H "Authorization: Bot $TOKEN" "$URL"); then
    echo "error: API call failed" >&2
    exit 1
fi
```

**Shell script INCORRECT:**
```bash
response=$(curl -s -H "Authorization: Bot $TOKEN" "$URL")  # -f missing, silent failure
```

---

## 5. Logging vs Print

- Use Python `logging` module for all scripts, not `print()`.
- Use `logger.info()` for normal operations.
- Use `logger.warning()` for recoverable issues.
- Use `logger.error()` for failures that need attention.
- Use `print()` ONLY for CLI tools where human-readable output is the product.

**CORRECT:**
```python
logger.info(f"Processed {count} transactions")
logger.warning(f"Rate limited, retrying in {delay}s")
logger.error(f"Failed to parse CSV: {e}")
```

**INCORRECT:**
```python
print(f"Processed {count} transactions")  # pollutes logs, no levels
print("something went wrong")  # not actionable
```

---

## 6. File & Path Handling

- Use `pathlib.Path` for all file paths in Python. No raw string concatenation.
- Use `C:\Users\compj\.openclaw\workspace` as the workspace root. Never hardcode other paths.
- Always check if a file exists before reading, but handle the case gracefully.

**CORRECT:**
```python
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
data_dir = WORKSPACE / "finance" / "data"
csv_file = data_dir / "transactions_2026-07.csv"

if not csv_file.exists():
    logger.warning(f"File not found: {csv_file}")
    return []
```

**INCORRECT:**
```python
# Hardcoded, fragile, Windows-specific slashes mixed
path = "C:\\Users\\compj\\.openclaw\\workspace\\finance\\data\\" + filename
```

---

## 7. Configuration & Secrets

- NEVER hardcode API keys, tokens, or passwords in source code.
- Use environment variables or `.env` files (never committed to git).
- Reference secrets by env var name in code, not by value.

**CORRECT:**
```python
import os

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
```

**INCORRECT (NEVER DO THIS):**
```python
DISCORD_BOT_TOKEN = "MTg4MzQ5NDU2Nzg5MDEyMzQ1Njc.abc123.xyz789"
```

---

## 8. Comments & Documentation

- Every Python module gets a module docstring explaining its purpose.
- Every public function gets a docstring with args, returns, and raises.
- Comments explain WHY, not WHAT. The code should say what.
- Keep comments current. Stale comments are worse than no comments.

**CORRECT:**
```python
def calculate_take_home(gross_pay: float, tax_rate: float = 0.22) -> float:
    """Calculate estimated take-home pay after federal withholding.

    Args:
        gross_pay: Semi-monthly gross salary
        tax_rate: Estimated effective tax rate (default 22%)

    Returns:
        Estimated take-home amount

    Note:
        This is a simplification. Actual taxes include state, FICA, etc.
    """
    return gross_pay * (1 - tax_rate)
```

**INCORRECT:**
```python
def calc_pay(g, t=0.22):
    # calculate pay
    return g * (1 - t)
```

---

## 9. Code Layout & Formatting

- Python: Follow PEP 8. 4 spaces for indentation. 88-100 character line length.
- Shell: 2-space indentation for readability. Keep pipelines readable.
- JSON: 2-space indentation. Sort keys alphabetically when generating.
- No trailing whitespace. One newline at end of file.

**CORRECT (Python):**
```python
def process_transactions(
    csv_path: Path,
    output_dir: Path,
    date_format: str = "%Y-%m-%d"
) -> int:
    """Process a transactions CSV and write categorized output."""
    count = 0
    # ... logic ...
    return count
```

**INCORRECT (Python):**
```python
def process_transactions(csv_path,output_dir,date_format="%Y-%m-%d"):
  count=0  # 2 spaces (inconsistent), no spaces after commas
  return count
```

---

## 10. Testing Patterns

- Every script that processes data should have a "dry run" mode.
- Use `--dry-run` or `DRY_RUN=1` env var to preview changes without applying.
- Validate inputs before processing. Fail fast with clear messages.

**CORRECT:**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
args = parser.parse_args()

if args.dry_run:
    logger.info("DRY RUN: Would update %d records", len(records))
else:
    apply_updates(records)
```

---

## 11. External API Calls

- Always set timeouts (default 30s, lower for simple GETs).
- Always handle rate limits (429 status). Respect `Retry-After` headers.
- Always validate response structure before accessing nested fields.
- Log the endpoint (not full URL with tokens) and status code.

**CORRECT:**
```python
def call_discord_api(endpoint: str, payload: dict = None) -> dict:
    url = f"https://discord.com/api/v10{endpoint}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            logger.warning(f"Rate limited, waiting {retry_after}s")
            time.sleep(retry_after)
            return call_discord_api(endpoint, payload)
        response.raise_for_status()
        return response.json() if response.content else {}
    except Exception as e:
        logger.error(f"Discord API error: {e}")
        return {}
```

---

## 12. Data Processing

- Never mutate input data in place. Return new structures.
- Use type hints for function signatures.
- Validate data types and ranges before calculations.
- Round financial calculations to 2 decimal places using `Decimal` or `round(x, 2)`.

**CORRECT:**
```python
from decimal import Decimal, ROUND_HALF_UP

def calculate_apr_earnings(principal: Decimal, apy: Decimal, months: int) -> Decimal:
    """Calculate earnings on a principal over N months at given APY."""
    if principal < 0 or apy < 0 or months < 0:
        raise ValueError("All inputs must be non-negative")
    
    monthly_rate = apy / Decimal("12")
    earnings = principal * monthly_rate * Decimal(str(months))
    return earnings.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**INCORRECT:**
```python
def calc_earnings(p, r, m):
    return p * (r/12) * m  # floating point, no validation, no rounding
```

---

## 13. Version Control

- Every script change gets a clear commit message.
- Use `git add -p` for granular commits when possible.
- Never commit secrets, tokens, or `.env` files.
- Include a `README.md` in every project folder explaining what it does.

**Commit message format:**
```
[type]: [short description] ([context])

[type] = feat | fix | refactor | docs | test | spam | finance | trade
Example: "feat: add monthly fee audit report generator (finance)"
Example: "fix: handle missing CSV columns in spending analyzer (finance)"
Example: "spam: auto-add 3 discovered signatures (2026-07-09)"
```

---

## 14. Agents.md Integration

- These guidelines supplement `AGENTS.md`, not replace it.
- When writing code for a specific domain (finance, trading, Discord), check that domain's `AGENTS.md` first.
- Log pattern violations in `.learnings/ERRORS.md` so future Nova iterations improve.

---

## 15. Gold Standard Example

Below is a complete, guideline-compliant script that demonstrates all rules above:

```python
#!/usr/bin/env python3
"""Discord channel permission checker.

Validates that Nova has proper permissions in configured channels.
Run with --dry-run to preview without making changes.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DISCORD_API_BASE = "https://discord.com/api/v10"
REQUIRED_PERMISSIONS = {"VIEW_CHANNEL", "SEND_MESSAGES", "READ_MESSAGE_HISTORY"}


def get_bot_token() -> str:
    """Retrieve Discord bot token from environment."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        sys.exit(1)
    return token


def fetch_channel(channel_id: str, token: str) -> dict:
    """Fetch channel data from Discord API."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}"
    headers = {"Authorization": f"Bot {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch channel {channel_id}: {e}")
        return {}


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check Discord channel permissions")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()
    
    token = get_bot_token()
    channel_id = "1524864332478021802"
    
    logger.info(f"Checking channel {channel_id} (dry_run={args.dry_run})")
    
    channel_data = fetch_channel(channel_id, token)
    if not channel_data:
        logger.error("Channel not found or no access")
        return 1
    
    logger.info(f"Channel name: {channel_data.get('name')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 16. Feedback Loop

When Nova violates these guidelines:
1. Opus corrects the code or calls out the issue.
2. Nova logs the specific violation in `.learnings/ERRORS.md`.
3. Nova updates this file if the guideline was unclear or missing.

**Format for ERRORS.md entry:**
```markdown
## YYYY-MM-DD — [Category]
- **Violation:** [What happened]
- **File:** [Path]
- **Guideline:** [Which section above]
- **Fix:** [What should have been done]
- **Learned:** [Pattern to remember]
```

---

*Last updated: 2026-07-10*
*Source: Stack Overflow Blog — "Building shared coding guidelines for AI (and people too)"*
*Applies to: All Nova code across all projects*
