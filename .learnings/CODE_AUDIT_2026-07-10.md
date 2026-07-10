# Retroactive Code Audit Report

Date: 2026-07-10
Auditor: Nova (self-audit against CODING.md)
Scope: All Python and shell scripts in workspace + scripts/ directory

---

## Summary

**P0 (Critical — Fix Immediately):** 4 files with hardcoded secrets
**P1 (High — Fix Soon):** 7+ files with no logging, bare excepts, missing type hints
**P2 (Medium — Fix When Touched):** 5+ files with missing docstrings, hardcoded paths, no dry-run

---

## P0 — Hardcoded Secrets (CRITICAL) — FIXED 2026-07-10

All secrets moved to local SQLite vault (`scripts/credentials/vault.db`).
Scripts updated to use `vault_helper.get_credential()` instead of hardcoded values.

### ✅ scripts/cashflow_real.py — FIXED
- ~~Lines 7-8 — Hardcoded Plaid `clientId` and `secret`~~
- Now uses `vault_helper.get_credential('plaid', 'client_id')` / `get_credential('plaid', 'secret')`

### ✅ scripts/monthly_expenses.py — FIXED
- ~~Same hardcoded Plaid credentials~~
- Same fix as above

### ✅ content_publish.py — FIXED
- ~~Lines 8-15 — Hardcoded WordPress XML-RPC URLs, usernames, app passwords~~
- Now uses `vault_helper.get_credential()` for all WordPress credentials

### ✅ scripts/sweep_all.py — FIXED
- ~~Lines 3-4 — Hardcoded env var names~~
- Now uses vault for Gmail credentials

### Also Fixed (not in original audit):
- `daily_publish.py` — WordPress credentials moved to vault
- `scripts/publish_aibusiness.py` — WordPress credentials moved to vault
- `scripts/publish_wordpress_batch.py` — WordPress credentials moved to vault
- `scripts/add_menu_item.py` — WordPress credentials moved to vault
- `scripts/check_markdown_posts.py` — WordPress credentials moved to vault
- `scripts/check_menus.py` — WordPress credentials moved to vault
- `scripts/disable_comments.py` — WordPress credentials moved to vault
- `scripts/disable_default_comments.py` — WordPress credentials moved to vault
- `scripts/find_marketplace_post.py` — WordPress credentials moved to vault
- `scripts/fix_aicofounder_posts.py` — WordPress credentials moved to vault
- `scripts/fix_br_lists.py` — WordPress credentials moved to vault
- `scripts/fix_dup_titles.py` — WordPress credentials moved to vault
- `scripts/publish_product_page.py` — WordPress credentials moved to vault
- `scripts/publish_products_page.py` — WordPress credentials moved to vault
- `scripts/verify_post_369.py` — WordPress credentials moved to vault
- `scripts/all_inflows.py` — Plaid credentials moved to vault
- `scripts/check_all.py` — Plaid credentials moved to vault
- `scripts/check_credit.py` — Plaid credentials moved to vault
- `scripts/check_liabilities.py` — Plaid credentials moved to vault
- `scripts/check_tokens.py` — Plaid credentials moved to vault
- `scripts/expense_snapshot.py` — Plaid credentials moved to vault
- `scripts/hard_numbers.py` — Plaid credentials moved to vault
- `scripts/real_monthly_burn.py` — Plaid credentials moved to vault
- `scripts/six_month_overview.py` — Plaid credentials moved to vault
- `scripts/test_acct_type.py` — Plaid credentials moved to vault
- `scripts/test_networth.py` — Plaid credentials moved to vault
- `scripts/test_prod.py` — Plaid credentials moved to vault
- `scripts/update_consent.py` — Plaid credentials moved to vault
- `scripts/variable_spending.py` — Plaid credentials moved to vault

### Files Created:
- `scripts/credential_vault.py` — SQLite vault CLI for storing/retrieving credentials
- `scripts/vault_helper.py` — Runtime helper: `get_credential(service, key) -> str`
- `.gitignore` — `scripts/credentials/vault.db` excluded from version control

**Status: ✅ COMPLETE — No hardcoded secrets remain in Python source**

---

## P1 — No Logging (using print())

### scripts/gmail_spam_sweep_v2.py
- **Violation:** Uses `print()` for all output. No `logging` module.
- **Impact:** Can't set log levels. Output mixes with tool results. Can't redirect logs properly.
- **Count:** ~15 print statements
- **Fix:** Replace with `logging.info()`, `logging.warning()`, `logging.error()`

### scripts/discover_spam_patterns.py
- **Violation:** Same — `print()` throughout, no `logging`.
- **Count:** ~20 print statements
- **Fix:** Same as above.

### scripts/cashflow_real.py
- **Violation:** Uses `print()` exclusively for formatted output. No `logging`.
- **Code:**
  ```python
  print("=" * 70)
  print("REAL CASH FLOW (90 Days)")
  print(f"Total Income:            ${income_total:>12,.2f}")
  ```
- **Fix:** Keep print for the formatted report (it's the product), but add `logging` for operational info.

### scripts/monthly_expenses.py
- **Violation:** Same — `print()` for all output.
- **Fix:** Same as cashflow_real.py.

### scripts/sweep_all.py
- **Violation:** `print()` for all output, no `logging`.
- **Fix:** Add `logging` module.

### scripts/backup-finance-to-nas.py
- **Violation:** `print()` for status messages. No `logging`.
- **Fix:** Add `logging` module.

### content_publish.py
- **Violation:** No logging at all. Silent failures on publish.
- **Fix:** Add `logging` for publish attempts and failures.

---

## P1 — Bare/Empty Exception Handling

### scripts/gmail_spam_sweep_v2.py
- **Violation:** Multiple `except: pass` blocks
- **Code:**
  ```python
  try:
      with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
          config = json.load(f)
      return config.get(email_addr, "").strip().replace(" ", "")
  except Exception:
      return ""
  ```
  ```python
  except: pass  # in message processing loops
  ```
- **Fix:** Log the exception before returning/continuing. `logger.warning("Config load failed: %s", e)`

### scripts/discover_spam_patterns.py
- **Violation:** `except: pass` / `except Exception: pass` in multiple places
- **Fix:** Log exceptions, don't silently swallow.

### scripts/sweep_all.py
- **Violation:** `except: pass` in mail processing loop
- **Fix:** Log the exception.

### scripts/nova_finance_dashboard.py
- **Violation:** Line ~88 — `except: pass` when fetching liabilities
- **Code:**
  ```python
  try:
      liab_resp = client.liabilities_get(...)
      # ... process ...
  except:
      pass
  ```
- **Fix:** `logger.warning("Liabilities fetch failed for %s: %s", bank_name, e)`

---

## P1 — Missing Type Hints

### Affected files:
- `scripts/gmail_spam_sweep_v2.py` — No type hints anywhere
- `scripts/discover_spam_patterns.py` — No type hints
- `scripts/cashflow_real.py` — No type hints
- `scripts/monthly_expenses.py` — No type hints
- `scripts/sweep_all.py` — No type hints
- `content_publish.py` — No type hints
- `scripts/browser_retry.py` — Has some type hints (Callable, Any, Optional) — **COMPLIANT**

---

## P2 — Missing Module Docstrings

### Affected files:
- `scripts/sweep_all.py` — No docstring. What does this do vs gmail_spam_sweep_v2.py?
- `scripts/cashflow_real.py` — No docstring explaining the Plaid connection and analysis logic.
- `restart-gateway.ps1` — No comments at all. Dangerous script with no explanation.
- `run_daemon.ps1` — No comments. Hardcoded paths with no context.

---

## P2 — Hardcoded Paths

### scripts/backup-finance-to-nas.py
- **Violation:** Line 15 — Hardcoded Windows path as string
- **Code:**
  ```python
  LOCAL_DIR = Path("C:/Users/compj/.openclaw/workspace")
  ```
- **Fix:** Use workspace constant from AGENTS.md or derive from `__file__`.

### content_publish.py
- **Violation:** Hardcoded content HTML embedded in Python source (150+ lines of HTML in triple-quoted strings)
- **Fix:** Move content to separate `.md` or `.html` files, load at runtime.

---

## P2 — No Dry-Run Mode

### Affected files:
- `scripts/discover_spam_patterns.py` — Modifies `gmail_spam_sweep_v2.py` in place. No preview.
- `scripts/backup-finance-to-nas.py` — Copies files to NAS. No preview.
- `content_publish.py` — Publishes to WordPress immediately. No preview.
- `restart-gateway.ps1` — Kills processes. No confirmation or dry-run.

---

## P2 — Shell Script Issues

### restart-gateway.ps1
- **Violation:** `-ErrorAction SilentlyContinue` swallows ALL errors
- **Code:**
  ```powershell
  Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  ```
- **Risk:** If the gateway fails to restart, you won't know. Errors are silently discarded.
- **Fix:** Remove `-ErrorAction SilentlyContinue`, add proper error handling and logging.

### run_daemon.ps1
- **Violation:** Hardcoded Python path (`C:\ProgramData\chocolatey\bin\python3.14.exe`)
- **Violation:** No error handling. Daemon could fail silently.
- **Fix:** Use `python3` from PATH or check version. Add error handling.

---

## Files That Are Mostly Compliant

### scripts/plaid_finance.py
- ✅ Module docstring with usage example
- ✅ Uses `argparse` for CLI
- ✅ Uses `pathlib.Path` for paths
- ✅ Loads credentials from env file
- ⚠️ No `logging` module (uses `print()`)
- ⚠️ No type hints

### scripts/nova_finance_dashboard.py
- ✅ Module docstring
- ✅ Uses `pathlib.Path`
- ⚠️ `except: pass` on liabilities fetch
- ⚠️ No `logging` module
- ⚠️ No type hints

### scripts/browser_retry.py
- ✅ Module docstring
- ✅ Uses type hints (`Callable`, `Any`, `Optional`)
- ✅ Has class structure
- ⚠️ Uses `print()` instead of `logging`

---

## Recommended Priority Order

**Fix in this order:**

1. **P0 — Rotate secrets immediately** (cashflow_real.py, monthly_expenses.py, content_publish.py)
   - Change Plaid secret, WordPress app passwords
   - Move credentials to env files
   
2. **P1 — Add logging** (gmail_spam_sweep_v2.py, discover_spam_patterns.py, sweep_all.py)
   - Replace `print()` with `logging`
   - Add bare-except fixes
   
3. **P1 — Fix bare excepts** (all affected files)
   - Log before swallowing
   
4. **P2 — Add docstrings** (sweep_all.py, cashflow_real.py, ps1 files)
   
5. **P2 — Add dry-run flags** (discover_spam_patterns.py, content_publish.py)

---

*Report generated: 2026-07-10*
*Next audit: After fixes applied*
