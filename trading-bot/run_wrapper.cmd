@echo off
"C:\ProgramData\chocolatey\bin\python3.14.exe" "C:\Users\compj\.openclaw\workspace\trading-bot\run_executor.py" > "%TEMP%\executor_out.txt" 2>&1
type "%TEMP%\executor_out.txt"
del "%TEMP%\executor_out.txt"
