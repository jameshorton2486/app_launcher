@echo off
REM James's Project Launcher - Installer Script
REM Optional installer for creating shortcuts and enabling startup

echo ========================================
echo James's Project Launcher - Installer
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "APP_NAME=James's Project Launcher"
set "APP_DIR=%SCRIPT_DIR%"
set "MAIN_SCRIPT=%APP_DIR%main.py"

REM Check if main.py exists
if not exist "%MAIN_SCRIPT%" (
    echo Error: main.py not found in %APP_DIR%
    pause
    exit /b 1
)

echo Installing %APP_NAME%...
echo.

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "SHORTCUT_PATH=%START_MENU%\%APP_NAME%.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '\"%MAIN_SCRIPT%\"'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Description = '%APP_NAME%'; $Shortcut.Save()"

if %errorLevel% equ 0 (
    echo [OK] Start Menu shortcut created
) else (
    echo [ERROR] Failed to create Start Menu shortcut
)

REM Create Desktop shortcut
echo Creating Desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "DESKTOP_SHORTCUT=%DESKTOP%\%APP_NAME%.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '\"%MAIN_SCRIPT%\"'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Description = '%APP_NAME%'; $Shortcut.Save()"

if %errorLevel% equ 0 (
    echo [OK] Desktop shortcut created
) else (
    echo [ERROR] Failed to create Desktop shortcut
)

REM Ask about startup
echo.
set /p ENABLE_STARTUP="Enable 'Start with Windows'? (Y/N): "
if /i "%ENABLE_STARTUP%"=="Y" (
    echo Enabling startup with Windows...
    pythonw "%MAIN_SCRIPT%" --enable-startup
    if %errorLevel% equ 0 (
        echo [OK] Startup enabled
    ) else (
        echo [WARNING] Could not enable startup automatically
        echo You can enable it manually in Settings
    )
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Shortcuts created:
echo   - Start Menu: %SHORTCUT_PATH%
echo   - Desktop: %DESKTOP_SHORTCUT%
echo.
echo You can now launch the application from:
echo   - Start Menu
echo   - Desktop shortcut
echo   - Or run: launch.bat
echo.
pause
