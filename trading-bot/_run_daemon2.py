import subprocess, sys, json
import os
os.chdir(r'C:\Users\compj\.openclaw\workspace\trading-bot')
result = subprocess.run([sys.executable, 'daemon.py'], capture_output=True, text=True, timeout=240)
with open('_last_run_stdout.txt', 'w', encoding='utf-8') as f:
    f.write('=== STDOUT ===\n')
    f.write(result.stdout)
    f.write('\n=== STDERR ===\n')
    f.write(result.stderr[-3000:] if len(result.stderr) > 3000 else result.stderr)
    f.write(f'\n=== RC: {result.returncode} ===\n')
with open('trading-queue.json') as f:
    q = json.load(f)
with open('_last_run_stdout.txt', 'a', encoding='utf-8') as f:
    f.write(f'Pending: {len(q.get("pending",[]))}, Executed: {len(q.get("executed",[]))}\n')
