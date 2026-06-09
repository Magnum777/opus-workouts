@echo off
cd /d "C:\Users\compj\.openclaw\workspace"
"C:\ProgramData\chocolatey\bin\python3.14.exe" trading-bot\daemon.py > tradebot_output.txt 2> tradebot_error.txt
echo EXIT_CODE=%ERRORLEVEL%
