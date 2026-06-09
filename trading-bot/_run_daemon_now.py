import sys, os, io, subprocess, json, time
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')

# Run the actual daemon with a hard timeout
script = r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'
proc = subprocess.run(
    [sys.executable, script],
    capture_output=True, text=True, timeout=75,
    cwd=r'C:\Users\compj\.openclaw\workspace\trading-bot',
    encoding='utf-8', errors='replace'
)
print(proc.stdout)
if proc.stderr.strip():
    print("STDERR:", proc.stderr[:2000])
