# James's Project Launcher - PowerShell Launch Script
# Uses virtual environment if available

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainScript = Join-Path $scriptPath "main.py"

# Check for venv
$venvPython = Join-Path $scriptPath ".venv\Scripts\python.exe"
$venvPythonw = Join-Path $scriptPath ".venv\Scripts\pythonw.exe"

if (Test-Path $venvPythonw) {
    # Use venv pythonw (no console)
    Start-Process $venvPythonw -ArgumentList "`"$mainScript`"" -WindowStyle Hidden
} elseif (Test-Path $venvPython) {
    # Use venv python (with console)
    & $venvPython $mainScript
} else {
    # Fallback to system Python
    Start-Process pythonw -ArgumentList "`"$mainScript`"" -WindowStyle Hidden
}
