import subprocess, sys, threading, time

result = {'out': '', 'err': '', 'rc': -1}

def target():
    p = subprocess.Popen(
        [r'C:\ProgramData\chocolatey\bin\python3.14.exe', r'C:\Users\compj\.openclaw\workspace\trading-bot\daemon.py'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        out, err = p.communicate(timeout=110)
        result['out'] = out
        result['err'] = err
        result['rc'] = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate(timeout=10)
        result['out'] = out
        result['err'] = err
        result['rc'] = -9

t = threading.Thread(target=target)
t.start()
t.join(timeout=120)
if t.is_alive():
    print('TIMEOUT_CRITICAL')
else:
    print(result['out'] if result['out'] else '(empty stdout)')
    if result['err']:
        print('STDERR:', result['err'], file=sys.stderr)
    print('EXIT:', result['rc'])
