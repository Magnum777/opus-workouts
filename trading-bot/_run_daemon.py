import subprocess, sys, datetime, json, os

start = datetime.datetime.now()

# Run the daemon
proc = subprocess.Popen(
    [r'C:\ProgramData\chocolatey\bin\python3.14.exe', '-u', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=r'C:\Users\compj\.openclaw\workspace\trading-bot'
)

TIMEOUT = 90
try:
    stdout, stderr = proc.communicate(timeout=TIMEOUT)
    elapsed = (datetime.datetime.now() - start).total_seconds()
    print(f'=== DAEMON COMPLETED in {elapsed:.1f}s ===')
    print(stdout)
    if stderr.strip():
        print('=== STDERR ===')
        print(stderr)
except subprocess.TimeoutExpired:
    elapsed = (datetime.datetime.now() - start).total_seconds()
    print(f'=== TIMEOUT after {elapsed:.1f}s ===')
    out, err = proc.communicate(timeout=5)
    if out:
        print(out[-3000:] if len(out) > 3000 else out)
    if err:
        print('=== STDERR (last 2000) ===')
        print(err[-2000:])
    proc.kill()
