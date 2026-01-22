# James's Project Launcher - PowerShell Launch Script
# Launches the application without console window

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainScript = Join-Path $scriptPath "main.py"

Start-Process pythonw -ArgumentList "`"$mainScript`"" -WindowStyle Hidden
