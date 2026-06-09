import subprocess, time, sys
proc = subprocess.Popen(
    [r'C:\Python314\python.exe', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'],
    cwd=r'C:\Users\compj\.openclaw\workspace\trading-bot',
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NO_WINDOW
)
time.sleep(90)
proc.terminate()
time.sleep(2)
out = proc.stdout.read().decode('utf-8', errors='replace')
sys.stdout.write(out)
