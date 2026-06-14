import subprocess, sys, threading, time
import signal, os

class TimeoutError(Exception):
    pass

logpath = r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon_quick_1111_output.txt'
proc = subprocess.Popen(
    [r'C:\ProgramData\chocolatey\bin\python3.14.exe', '-u', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
)

lines = []
def reader():
    for line in proc.stdout:
        lines.append(line)
        print(line, end='', flush=True)

t = threading.Thread(target=reader, daemon=True)
t.start()
start = time.time()
while True:
    ret = proc.poll()
    if ret is not None:
        break
    if time.time() - start > 120:
        proc.kill()
        lines.append(f'\n[KILLED after 120s timeout]\n')
        break
    time.sleep(0.5)

with open(logpath, 'w') as f:
    f.writelines(lines)
print(f'Done. {len(lines)} lines written.')
