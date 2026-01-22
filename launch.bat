@echo off
REM James's Project Launcher - Launch Script
REM Launches the application without console window

cd /d "%~dp0"
pythonw "%~dp0main.py" %*
