# Building App Launcher

## Prerequisites
- Python 3.10+ (tested on 3.11)
- pip (included with Python)
- Git (for GitPython functionality)
- Windows 10 or 11

## Development Setup
```bash
# Clone the repository
git clone https://github.com/jameshorton2486/app_launcher
cd app_launcher

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Run with debug logging
python main.py --debug
```

## Running the UI Checker
```bash
python scripts/ui_checker.py
```

This validates design token usage across the codebase and reports hardcoded colors, bare excepts, and other consistency issues.

## Building with PyInstaller

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build (one-directory mode, recommended)
```bash
pyinstaller --onedir --windowed --name AppLauncher ^
  --add-data "config/tools.json;config" ^
  --add-data "config/design_system.json;config" ^
  --add-data "config/file_patterns.json;config" ^
  --add-data "config/external_tool_paths.json;config" ^
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  --hidden-import PIL ^
  --hidden-import git ^
  main.py
```

### Output
The built application will be in `dist/AppLauncher/`.

### First Run After Build
On first launch, the app copies default config files (settings.json, projects.json, tool_usage.json) from the bundle into a writable `config/` directory next to the exe if they don't already exist.

### Known Packaging Notes
- `customtkinter` requires `--collect-all` to include its theme assets
- `pystray` requires `--hidden-import pystray._win32` for the Windows backend
- `GitPython` requires Git to be installed on the user's system (not bundled)
- Expected output size: ~80-120MB
- Windows Defender may flag unsigned executables — consider code signing for distribution
