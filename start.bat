@echo off
REM Start CR Process Automation on Windows (Waitress WSGI server).
REM
REM   start.bat                         bind 0.0.0.0:8000
REM   start.bat --host 127.0.0.1        behind nginx on the same machine
REM   start.bat --port 9000 --threads 16
REM
setlocal EnableExtensions
cd /d "%~dp0"

set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe"  set "PY=venv\Scripts\python.exe"

"%PY%" wsgi_app.py --migrate --collectstatic %*
exit /b %ERRORLEVEL%
