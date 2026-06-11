import subprocess, sys, os

os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")
result = subprocess.run(
    [r"C:\ProgramData\chocolatey\bin\python3.14.exe", "daemon.py"],
    capture_output=True, text=True, timeout=180
)
print("STDOUT:", result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
print("STDERR:", result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
print("RC:", result.returncode)
