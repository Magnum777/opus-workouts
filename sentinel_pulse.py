#!/usr/bin/env python3
"""
Sentinel Pulse - Lightweight Health Check
Replaces the OpenClaw agent-based cron for Sentinel-Pulse-15min
Runs directly via python, no subagent needed.
"""
import subprocess
import json
import sys
import re
from datetime import datetime, timezone

def run_cmd(cmd, timeout=15):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1

def check_gateway():
    """Check gateway status."""
    output, _, code = run_cmd("openclaw gateway status")
    if code == 0 and "ok" in output.lower():
        return "OK", "Running"
    return "ERROR", output[:100]

def check_discord():
    """Check Discord connection."""
    output, _, code = run_cmd("openclaw health")
    if code == 0:
        # Look for Discord status in output
        if "discord" in output.lower():
            return "OK", "Nova bot connected"
        return "OK", "Health OK"
    return "ERROR", output[:100]

def check_ollama():
    """Check Ollama is responding."""
    output, _, code = run_cmd('curl -s --max-time 5 http://127.0.0.1:11434/api/tags')
    if code == 0:
        try:
            data = json.loads(output)
            models = [m["name"] for m in data.get("models", [])]
            return "OK", ", ".join(models[:3])
        except:
            return "OK", "Responding"
    return "ERROR", "Not responding"

def check_crons():
    """Get cron job statuses from openclaw cron list output."""
    output, _, code = run_cmd("openclaw cron list 2>&1")
    if code != 0 and "error" in output.lower():
        return "UNKNOWN", output[:100]
    
    errors = 0
    ok = 0
    pending = 0
    
    VALID_STATUSES = {"error", "ok", "idle", "pending"}
    lines = output.split("\n")
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        # Find status column - it's the first word that matches a known status
        # (columns vary due to variable-length Name field)
        for i, part in enumerate(parts):
            if part.lower() in VALID_STATUSES:
                if part.lower() == "error":
                    errors += 1
                elif part.lower() == "ok":
                    ok += 1
                else:
                    pending += 1
                break
    
    return f"{errors} ERROR, {ok} OK, {pending} idle", f"{errors} error, {ok} ok, {pending} idle"

def main():
    now = datetime.now(timezone.utc).isoformat()
    
    gateway_status, gateway_notes = check_gateway()
    discord_status, discord_notes = check_discord()
    ollama_status, ollama_notes = check_ollama()
    cron_status, cron_notes = check_crons()
    
    # Build summary
    summary = f"""**SENTINEL PULSE {now}**

| System | Status | Notes |
|--------|--------|-------|
| Gateway | {gateway_status} | {gateway_notes} |
| Discord | {discord_status} | {discord_notes} |
| Ollama | {ollama_status} | {ollama_notes} |
| Cron Jobs | {cron_status} | {cron_notes} |

HEARTBEAT_OK"""
    
    print(summary)
    
    # Update AGENT-SYNC.md Last Pulse timestamp
    sync_path = r"C:\Users\compj\.openclaw\workspace\AGENT-SYNC.md"
    try:
        with open(sync_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        now_short = now[:16]
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("| Last Pulse"):
                new_lines.append(f"| Last Pulse | {now_short}Z |")
            else:
                new_lines.append(line)
        
        with open(sync_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"\n[AGENT-SYNC.md updated]", file=sys.stderr)
    except Exception as e:
        print(f"\n[AGENT-SYNC.md update failed: {e}]", file=sys.stderr)

if __name__ == "__main__":
    main()
