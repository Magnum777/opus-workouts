@echo off
cd /d C:\Users\compj\.openclaw\workspace\trading-bot
set outfile=daemon_batch_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log
set errfile=daemon_batch_err.log
echo Starting at %DATE% %TIME%
"C:\ProgramData\chocolatey\bin\python3.14.exe" daemon.py > %outfile% 2> %errfile%
echo Exit code: %ERRORLEVEL%
echo Output file: %outfile%
