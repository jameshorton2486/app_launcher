@echo off
REM James's Project Launcher - Launch without console window
REM Uses virtual environment if available

cd /d "%~dp0"

REM Check if venv exists and use it
if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" "%~dp0main.py" %*
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" "%~dp0main.py" %*
) else (
    REM Fallback to system Python
    pythonw "%~dp0main.py" %*
)
