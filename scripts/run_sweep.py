import subprocess, sys, time
p = subprocess.Popen([sys.executable, r'C:\Users\compj\.openclaw\workspace\scripts\gmail_spam_sweep_v2.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=120)
    print(out)
except subprocess.TimeoutExpired:
    p.kill()
    print("Script timed out after 120 seconds")
