import subprocess, sys, time
p = subprocess.Popen([r'C:\ProgramData\chocolatey\bin\python3.14.exe', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=r'C:\Users\compj\.openclaw\workspace\trading-bot')
try:
    stdout, _ = p.communicate(timeout=90)
    print(stdout.decode('utf-8', errors='replace'))
except subprocess.TimeoutExpired:
    p.kill()
    stdout, _ = p.communicate()
    print('[TIMEOUT] Daemon did not complete within 90s')
    if stdout:
        print(stdout.decode('utf-8', errors='replace'))
    # Fall back to last_run.log
    try:
        with open(r'C:\Users\compj\.openclaw\workspace\trading-bot\last_run.log', 'r') as f:
            print('--- LAST RUN LOG ---')
            print(f.read())
    except:
        print('Could not read last_run.log')
