import subprocess, time, sys, os
os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")
p = subprocess.Popen(
    [r"C:\ProgramData\chocolatey\bin\python3.14.exe", "daemon.py"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, encoding="utf-8", errors="replace"
)
t0 = time.time()
buf = []
while time.time() - t0 < 90:
    try:
        line = p.stdout.readline()
        if not line:
            if p.poll() is not None:
                break
            time.sleep(1)
            continue
        buf.append(line.rstrip())
        if "[CYCLE END]" in line:
            time.sleep(2)
            break
    except:
        break
p.terminate()
p.wait(timeout=5)
out = "\n".join(buf)
with open(r"C:\Users\compj\.openclaw\workspace\trading-bot\daemon_output.txt", "w", encoding="utf-8") as f:
    f.write(out)
with open(r"C:\Users\compj\.openclaw\workspace\trading-bot\daemon_exit.txt", "w") as f:
    f.write(str(p.returncode))
sys.stdout.write(out or "(no output)")
