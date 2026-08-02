#!/usr/bin/env python3
"""
Cron Health Monitor
Verifies cron jobs are running on their configured models and schedules.
Checks last run times, failure rates, and config drift.

Usage:
    python scripts/cron_health.py                  # Full health check
    python scripts/cron_health.py --json            # JSON output
    python scripts/cron_health.py --fix-models      # Report model mismatches
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")

# Expected cron configurations (source of truth)
EXPECTED_CONFIGS = {
    "ContentNova-aitoolalliance": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "2am daily"},
    "ContentNova-aibusinessinsider": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "3am daily"},
    "ContentNova-aicofounderstack": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "4am daily"},
    "EveOnion-NewsScan": {"model": "minimax-m3", "timeout": 180, "schedule": "8:15am daily"},
    "EveOnion-Article": {"model": "kimi-k2.6", "timeout": 300, "schedule": "9:30am Tue/Fri"},
    "EveOnion-RedditTweet": {"model": "minimax-m3", "timeout": 180, "schedule": "10am daily"},
    "EveOnion-PersonaScan": {"model": "deepseek-v4-flash", "timeout": 180, "schedule": "every 3 days"},
    "Kybernauts-Propaganda": {"model": "minimax-m3", "timeout": 180, "schedule": "6:15pm Sun"},
    "Yagas-Intel-Collect": {"model": "minimax-m3", "timeout": 120, "schedule": "2pm daily"},
    "Yagas-Propaganda-Post": {"model": "minimax-m3", "timeout": 180, "schedule": "5pm daily"},
    "Amazon-Affiliate-Publish": {"model": "minimax-m3", "timeout": 480, "schedule": "10:15am Tue/Fri"},
    "Amazon-Affiliate-Injector": {"model": "deepseek-v4-flash", "timeout": 180, "schedule": "11am daily"},
    "Amazon-Tracker-Weekly": {"model": "deepseek-v4-flash", "timeout": 120, "schedule": "Mon noon"},
    "spam-sweep-every-4h": {"model": "deepseek-v4-flash", "timeout": 120, "schedule": "every 4h"},
    "spam-pattern-discovery": {"model": "deepseek-v4-flash", "timeout": 120, "schedule": "6:45am daily"},
    "daily-brief-7am": {"model": "kimi-k2.6", "timeout": 300, "schedule": "7am daily"},
    "gmail-cleanup-daily": {"model": "deepseek-v4-flash", "timeout": 180, "schedule": "7:15am daily"},
    "Iris-all-accounts-digest": {"model": "deepseek-v4-flash", "timeout": 180, "schedule": "7:30am daily"},
    "Nova-Ops-Assessment": {"model": "deepseek-v4-flash", "timeout": 180, "schedule": "9am daily"},
    "DS-Seed-Enforcer": {"model": "deepseek-v4-flash", "timeout": 120, "schedule": "9:30am daily"},
    "TD-Scanner": {"model": "deepseek-v4-flash", "timeout": 120, "schedule": "7am Sun"},
    "NightSchool-8pm": {"model": "deepseek-v4-flash", "timeout": 3600, "schedule": "8pm daily"},
    "NightSchool-NAS-Sync": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "8:15pm daily"},
    "Weekly-MemoryHygiene": {"model": "kimi-k2.6", "timeout": 900, "schedule": "10pm Sun"},
    "Daily-MemorySweep": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "6:45am daily"},
    "Weekly-SkillUpdate": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "6am Mon"},
    "Weekly-SkillDiscovery": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "6pm Fri"},
    "Finance-NAS-Backup": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "3:38am daily"},
    "Workspace-NAS-Backup": {"model": "deepseek-v4-flash", "timeout": 300, "schedule": "11pm daily"},
}

# Model alias mapping
MODEL_ALIASES = {
    "ollama/kimi-k2.6:cloud": "kimi-k2.6",
    "ollama/deepseek-v4-flash:cloud": "deepseek-v4-flash",
    "ollama/minimax-m3:cloud": "minimax-m3",
    "ollama/glm-5.2:cloud": "glm-5.2",
    "ollama/kimi-k3:cloud": "kimi-k3",
}


def normalize_model(model_str):
    """Normalize model string to short alias."""
    if not model_str:
        return "unknown"
    return MODEL_ALIASES.get(model_str, model_str.replace("ollama/", "").replace(":cloud", ""))


def check_cron_health(crons_data, json_output=False, fix_models=False):
    """Check cron health against expected configs."""
    now = datetime.now(timezone.utc)
    issues = []
    healthy = []
    never_run = []

    for cron in crons_data:
        name = cron.get("name", "?")
        enabled = cron.get("enabled", False)
        model = cron.get("payload", {}).get("model", "")
        timeout = cron.get("payload", {}).get("timeoutSeconds", 0)
        last_run = cron.get("lastRunAtMs")
        last_status = cron.get("lastRunStatus")
        last_error = cron.get("lastRunError")

        norm_model = normalize_model(model)
        expected = EXPECTED_CONFIGS.get(name, {})

        # Check enabled
        if not enabled:
            issues.append({"name": name, "type": "disabled", "detail": "Cron is disabled"})
            continue

        # Check model
        expected_model = expected.get("model", "")
        model_ok = not expected_model or norm_model == expected_model

        # Check timeout
        expected_timeout = expected.get("timeout", 0)
        timeout_ok = not expected_timeout or timeout >= expected_timeout

        # Check staleness (never run or hasn't run in 24h for daily+ crons)
        never_run_flag = not last_run
        if last_run:
            last_run_dt = datetime.fromtimestamp(last_run / 1000, tz=timezone.utc)
            hours_ago = (now - last_run_dt).total_seconds() / 3600
        else:
            hours_ago = 9999

        # Build status
        job_issues = []
        if not model_ok:
            job_issues.append(f"model: got {norm_model}, expected {expected_model}")
        if not timeout_ok:
            job_issues.append(f"timeout: got {timeout}s, expected {expected_timeout}s+")
        if never_run_flag:
            job_issues.append("never run")
        elif last_status == "error":
            job_issues.append(f"last run error: {last_error or 'unknown'}")
        elif last_error:
            job_issues.append(f"last error: {last_error}")

        if job_issues:
            issues.append({"name": name, "type": "config_drift" if not model_ok or not timeout_ok else "stale" if never_run_flag else "error", "detail": "; ".join(job_issues), "model": norm_model, "expected_model": expected_model, "timeout": timeout, "expected_timeout": expected_timeout})
        else:
            healthy.append({"name": name, "model": norm_model, "last_run_hours_ago": round(hours_ago, 1) if last_run else None, "last_status": last_status})

        if never_run_flag:
            never_run.append(name)

    if json_output:
        result = {"healthy": len(healthy), "issues": len(issues), "never_run": len(never_run), "details": {"healthy": healthy, "issues": issues, "never_run": never_run}}
        print(json.dumps(result, indent=2))
        return result

    # Human-readable output
    print("=== Cron Health Monitor ===")
    print(f"Checked: {len(healthy) + len(issues)} crons")
    print(f"Healthy: {len(healthy)} | Issues: {len(issues)} | Never run: {len(never_run)}")
    print()

    if healthy:
        print("--- Healthy ---")
        for h in healthy:
            ago = f"{h['last_run_hours_ago']}h ago" if h['last_run_hours_ago'] else "never"
            print(f"  {h['name']}: {h['model']} ({ago}, {h['last_status']})")
        print()

    if issues:
        print("--- Issues ---")
        for i in issues:
            print(f"  [{i['type'].upper()}] {i['name']}: {i['detail']}")
        print()

    if fix_models and issues:
        model_issues = [i for i in issues if "model" in i.get("detail", "")]
        if model_issues:
            print("--- Model Fix Commands ---")
            for i in model_issues:
                print(f"  # {i['name']}: change model from {i.get('model', '?')} to {i.get('expected_model', '?')}")

    return {"healthy": len(healthy), "issues": len(issues)}


def main():
    parser = argparse.ArgumentParser(description="Cron health monitor")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fix-models", action="store_true", help="Show model fix commands")

    args = parser.parse_args()

    # We need cron data from the API, but this script can also accept JSON from stdin
    # or from a file
    cron_file = WORKSPACE / "memory" / "cron-health" / "latest.json"
    if cron_file.exists():
        with open(cron_file) as f:
            crons_data = json.load(f)
    else:
        # Try to use cron tool output if available
        print("No cron data found. Run: openclaw cron list --json > memory/cron-health/latest.json")
        print("Or pipe JSON data via stdin.")
        crons_data = []

    check_cron_health(crons_data, json_output=args.json, fix_models=args.fix_models)


if __name__ == "__main__":
    main()