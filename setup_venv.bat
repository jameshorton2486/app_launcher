@echo off
REM Setup Virtual Environment for App Launcher
REM Creates .venv and installs all dependencies

cd /d "%~dp0"

echo ========================================
echo App Launcher - Virtual Environment Setup
echo ========================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [2/4] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

echo.
echo [3/4] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying installation...
".venv\Scripts\python.exe" -c "import customtkinter; print('[OK] All dependencies installed successfully')"
if errorlevel 1 (
    echo [ERROR] Installation verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now launch the app with:
echo   - launch.bat (with console)
echo   - launch_no_console.bat (no console)
echo   - .venv\Scripts\python.exe main.py
echo.
pause
