#!/usr/bin/env python3
"""
Iris Multi-Account Wrapper
Runs the Iris email triage on all 4 Gmail accounts and produces a combined report.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Force UTF-8 on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ACCOUNTS_FILE = r"C:\Users\compj\.openclaw\workspace\scripts\.gmail_accounts.json"
IRIS_SCRIPT = r"C:\Users\compj\.openclaw\workspace\skills\iris\iris.py"
REPORT_DIR = r"C:\Users\compj\.openclaw\workspace\output"

WHITELIST = {"paypal.com", "chase.com", "tiktok.com"}


def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_iris(email, password):
    env = os.environ.copy()
    env["GMAIL_ADDRESS"] = email
    env["GMAIL_APP_PASSWORD"] = password
    env["SCAN_COUNT"] = "30"
    # Fix Rich/Windows console crashes in subprocess
    env["PYTHONIOENCODING"] = "utf-8"
    env["RICH_NO_COLOR"] = "1"
    env["RICH_FORCE_COLOR"] = "0"
    env["NO_COLOR"] = "1"
    # Don't generate per-account markdown reports
    env["IRIS_NO_REPORT"] = "1"

    result = subprocess.run(
        [sys.executable, IRIS_SCRIPT],
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return result.stdout, result.stderr, result.returncode


def parse_iris_output(stdout):
    """Parse the Rich console output to extract counts and top emails."""
    lines = stdout.splitlines()
    summary = {
        "scanned": 0,
        "actionable": 0,
        "noise": 0,
        "replied": 0,
        "high_priority": 0,
        "top_emails": [],
    }

    for line in lines:
        line = line.strip()
        if "Priority Inbox" in line:
            # "📬 Priority Inbox — 3 actionable emails"
            parts = line.split("—")
            if len(parts) > 1:
                try:
                    count = int(parts[1].split()[0].strip())
                    summary["actionable"] = count
                except ValueError:
                    pass
        elif "Scanned:" in line:
            # Rich table summary line
            # "Scanned:    30 emails"
            m = line.split()
            for i, word in enumerate(m):
                if word == "Scanned:" and i + 1 < len(m):
                    try:
                        summary["scanned"] = int(m[i + 1])
                    except ValueError:
                        pass
                elif word == "Actionable:" and i + 1 < len(m):
                    try:
                        summary["actionable"] = int(m[i + 1])
                    except ValueError:
                        pass
                elif word == "Noise:" and i + 1 < len(m):
                    try:
                        summary["noise"] = int(m[i + 1])
                    except ValueError:
                        pass
                elif "replied" in word.lower() and i + 1 < len(m):
                    try:
                        summary["replied"] = int(m[i + 1])
                    except ValueError:
                        pass
                elif "priority" in word.lower() and "70" in word and i + 1 < len(m):
                    try:
                        summary["high_priority"] = int(m[i + 1])
                    except ValueError:
                        pass

        # Parse table rows — look for urgency score + sender
        if line.startswith("|") and not line.startswith("|----"):
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c]
            if len(cells) >= 4:
                try:
                    score = int(cells[0])
                    sender = cells[1]
                    subject = cells[2]
                    age = cells[3]
                    if score >= 50:
                        summary["top_emails"].append({
                            "score": score,
                            "sender": sender,
                            "subject": subject,
                            "age": age,
                        })
                except (ValueError, IndexError):
                    pass

    return summary


def build_report(results):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# 🦝 Iris — All Accounts Digest — {date_str}\n")

    total_scanned = 0
    total_actionable = 0
    total_noise = 0
    total_high = 0

    for email, data in results.items():
        out = data["stdout"]
        summary = parse_iris_output(out)
        total_scanned += summary["scanned"]
        total_actionable += summary["actionable"]
        total_noise += summary["noise"]
        total_high += summary["high_priority"]

        lines.append(f"\n## {email}\n")
        lines.append(f"- **Scanned:** {summary['scanned']}  **Actionable:** {summary['actionable']}  **Noise:** {summary['noise']}")
        lines.append(f"- **High priority (70+):** {summary['high_priority']}")

        if data["returncode"] != 0:
            lines.append(f"- ⚠️ **Error:** non-zero exit code {data['returncode']}")
            if data["stderr"]:
                lines.append(f"```\n{data['stderr'][:500]}\n```")

        if summary["top_emails"]:
            lines.append("\n**Flagged emails:**")
            for e in summary["top_emails"][:5]:
                lines.append(f"- [{e['score']}] {e['sender']} — *{e['subject']}* ({e['age']})")
        elif summary["actionable"] == 0:
            lines.append("\n✅ Clean — nothing flagged.")

    lines.insert(2, f"\n**Totals:** {total_scanned} scanned | {total_actionable} actionable | {total_noise} noise | {total_high} high priority\n")

    report_text = "\n".join(lines)
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, f"iris_digest_{date_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text, report_path


def main():
    try:
        accounts = load_accounts()
    except Exception as e:
        print(f"ERROR: Failed to load accounts: {e}", file=sys.stderr)
        sys.exit(1)

    results = {}
    for email, password in accounts.items():
        try:
            stdout, stderr, rc = run_iris(email, password)
            results[email] = {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": rc,
            }
        except subprocess.TimeoutExpired:
            results[email] = {
                "stdout": "",
                "stderr": "TIMEOUT after 180s",
                "returncode": -1,
            }
        except Exception as e:
            results[email] = {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    report_text, report_path = build_report(results)
    print(report_text)
    print(f"\n✅ Report saved to: {report_path}")

    # Return exit code 0 if at least one account succeeded
    if any(r["returncode"] == 0 for r in results.values()):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
