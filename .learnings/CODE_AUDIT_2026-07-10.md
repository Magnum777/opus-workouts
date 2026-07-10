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

## P0 — Hardcoded Secrets (CRITICAL)

### 1. scripts/cashflow_real.py
- **Violation:** Lines 7-8 — Hardcoded Plaid `clientId` and `secret` directly in source code
- **Risk:** API credentials committed to git history. Anyone with repo access sees production Plaid credentials.
- **Code:**
  ```python
  config = plaid.Configuration(
      host='https://production.plaid.com',
      api_key={'clientId': '6a50015a66e1a0000ebc49d7', 'secret': '6f6c820c251156fe033f1591a903ee'}
  )
  ```
- **Fix:** Load from `credentials/plaid.env` or env vars, like `scripts/plaid_finance.py` does.

### 2. scripts/monthly_expenses.py
- **Violation:** Lines 8-9 — Same hardcoded Plaid credentials as cashflow_real.py
- **Risk:** Same as above — production credentials in source.
- **Fix:** Same fix — use env/config file pattern.

### 3. content_publish.py
- **Violation:** Lines 8-15 — Hardcoded WordPress XML-RPC URLs, usernames, and **app passwords** in plain text
- **Risk:** WordPress admin credentials exposed. Sites can be compromised.
- **Code:**
  ```python
  SITES = {
      'aitoolalliance.com': {
          'url': 'https://aitoolalliance.com/xmlrpc.php',
          'user': 'aitoolalliance_u6cbhe',
          'pass': 'PXop SzVQ b6wX IAyr FSig 8ZfL'
      },
      'aibusinessinsider.org': {
          'url': 'https://aibusinessinsider.org/xmlrpc.php',
          'user': 'nova.cofounder@gmail.com',
          'pass': 'sDLx Ja22 YxcI QAok gu8u xRXI'
      }
  }
  ```
- **Fix:** Move to `credentials/wordpress.env` or env vars. Load at runtime.

### 4. scripts/sweep_all.py
- **Violation:** Lines 3-4 — Hardcoded env var names (not values, but poor practice for isolation context)
- **Risk:** Less severe but contributes to config sprawl. Isolated crons can't read Windows env vars per AGENTS.md.
- **Fix:** Use `.gmail_accounts.json` pattern like `gmail_spam_sweep_v2.py`.

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
