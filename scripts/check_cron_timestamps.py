#!/usr/bin/env python3
"""Check that nightly crons left correct timestamps in logs."""
import subprocess, re, json, datetime

def get_cron_list():
    out = subprocess.check_output(["openclaw", "cron", "list"], text=True, errors="ignore")
    ids = re.findall(r"([a-f0-9-]{36})\s+", out)
    return ids

def get_runs(cron_id: str):
    try:
        out = subprocess.check_output(["openclaw", "cron", "runs", cron_id], text=True, errors="ignore")
    except subprocess.CalledProcessError:
        return []
    runs = []
    for line in out.splitlines():
        m = re.search(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s+(\w+)", line)
        if m:
            runs.append({"time": m.group(1), "status": m.group(2)})
    return runs

if __name__ == "__main__":
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Cron checkpoint scan for {yesterday}\n")
    for cid in get_cron_list()[:10]:  # limit output
        runs = get_runs(cid)
        for r in runs:
            if yesterday in r["time"]:
                icon = "✅" if r["status"].lower() == "success" else "❌"
                print(f"{icon} {cid[:8]}... @ {r['time']} — {r['status']}")
