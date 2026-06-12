import subprocess, sys, os, time
os.chdir(r'C:\Users\compj\.openclaw\workspace\trading-bot')
proc = subprocess.Popen(
    [r'C:\ProgramData\chocolatey\bin\python3.14.exe', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
t0 = time.time()
try:
    stdout, stderr = proc.communicate(timeout=300)
    elapsed = time.time() - t0
    out = stdout.decode('utf-8', errors='replace')
    print(f'EXIT_CODE:{proc.returncode} ELAPSED:{elapsed:.0f}s')
    if out.strip():
        print(out, end='')
    if stderr:
        print('STDERR:', stderr.decode('utf-8', errors='replace'), end='')
except subprocess.TimeoutExpired:
    print(f'TIMEOUT at {time.time()-t0:.0f}s')
    proc.kill()
