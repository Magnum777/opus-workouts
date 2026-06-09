import subprocess, sys, os, time, json
os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")
start = time.time()
proc = subprocess.Popen(
    [sys.executable, "daemon.py"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, encoding="utf-8", errors="replace"
)
try:
    stdout, _ = proc.communicate(timeout=85)
    elapsed = time.time() - start
    report = {"elapsed": round(elapsed, 1), "rc": proc.returncode, "output": stdout}
    with open("daemon_out.json", "w") as f:
        json.dump(report, f)
    print("COMPLETED", proc.returncode)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, _ = proc.communicate()
    report = {"elapsed": 85, "rc": -1, "output": stdout + "\n--- TIMEOUT ---"}
    with open("daemon_out.json", "w") as f:
        json.dump(report, f)
    print("TIMEOUT")
