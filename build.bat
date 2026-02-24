@echo off
setlocal enabledelayedexpansion

rem Usage: build.bat [--debug]
set MODE=release
if /I "%1"=="--debug" set MODE=debug

set NAME=AppLauncher
set ICON=assets\icon.ico

if /I "%MODE%"=="debug" (
  set WINDOWED=--console
) else (
  set WINDOWED=--windowed
)

pyinstaller --onedir %WINDOWED% --name %NAME% ^
  --icon %ICON% ^
  --add-data "config\tools.json;config" ^
  --add-data "config\design_system.json;config" ^
  --add-data "config\file_patterns.json;config" ^
  --add-data "config\external_tool_paths.json;config" ^
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  --hidden-import PIL ^
  --hidden-import git ^
  main.py

endlocal
