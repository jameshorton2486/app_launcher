@echo off
REM Quick sanity check - verifies environment and imports
REM Run this to test if everything is set up correctly

cd /d "%~dp0"

echo ========================================
echo App Launcher - Sanity Check
echo ========================================
echo.

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Run setup_venv.bat first.
    pause
    exit /b 1
)

echo [1/3] Checking Python...
".venv\Scripts\python.exe" --version
if errorlevel 1 (
    echo [ERROR] Python not working in venv
    pause
    exit /b 1
)
echo [OK] Python is working
echo.

echo [2/3] Checking dependencies...
".venv\Scripts\python.exe" -c "import customtkinter, psutil, pystray; print('[OK] Core dependencies found')"
if errorlevel 1 (
    echo [ERROR] Missing dependencies
    echo Run: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [3/3] Testing imports...
".venv\Scripts\python.exe" -c "from src.utils.tool_registry import ToolRegistry; from src.app import AppLauncher; print('[OK] All imports successful')"
if errorlevel 1 (
    echo [ERROR] Import test failed
    echo Check logs/app.log for details
    pause
    exit /b 1
)
echo [OK] All imports working
echo.
echo [4/4] Testing app initialization...
".venv\Scripts\python.exe" -c "from src.app import AppLauncher; app = AppLauncher(); print('[OK] App can be created')"
if errorlevel 1 (
    echo [ERROR] App initialization failed
    echo Check logs/app.log for details
    pause
    exit /b 1
)
echo [OK] App initialization successful
echo.

echo ========================================
echo [SUCCESS] Everything looks good!
echo ========================================
echo.
echo You can now launch with:
echo   - launch.bat
echo   - launch_no_console.bat
echo.
pause
