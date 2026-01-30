@echo off
REM James's Project Launcher - Simplified Launch Script
REM Uses virtual environment if available, falls back to system Python

cd /d "%~dp0"

REM Check if venv exists and use it
if exist ".venv\Scripts\python.exe" (
    echo [Using virtual environment]
    ".venv\Scripts\python.exe" "%~dp0main.py" %*
) else (
    echo [Using system Python]
    python "%~dp0main.py" %*
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to launch application
    echo Check logs/app.log for details
    pause
)
