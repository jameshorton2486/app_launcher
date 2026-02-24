# Packaging Plan (PyInstaller)

This plan builds two Windows executables from the same repo:
- App Launcher (core)
- App Launcher Power Tools

## Prerequisites
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
   - `pip install pyinstaller`

## Build Commands (Windows)
Run from the repo root:

```powershell
pyinstaller --noconfirm --onefile --windowed `
  --name "App Launcher" `
  --icon "assets/icons/app_icon.ico" `
  --add-data "assets;assets" `
  --add-data "config;config" `
  app_launcher_main.py
```

```powershell
pyinstaller --noconfirm --onefile --windowed `
  --name "App Launcher Power Tools" `
  --icon "assets/icons/app_icon.ico" `
  --add-data "assets;assets" `
  --add-data "config;config" `
  app_launcher_tools_main.py
```

## Spec-Based Builds (Recommended)
Spec files are provided for reproducible builds:
- `app_launcher.spec`
- `app_launcher_tools.spec`

Build with:

```powershell
pyinstaller app_launcher.spec
```

```powershell
pyinstaller app_launcher_tools.spec
```

Notes:
- `--add-data` uses `;` as the separator on Windows.
- The `assets` and `config` folders must be included for icons and tool definitions.

## Output
Executables will be created in `dist/`:
- `dist/App Launcher.exe`
- `dist/App Launcher Power Tools.exe`

## Optional Improvements
1. Create a `build/` cleanup script to remove old artifacts.
2. Add a version resource (file version + product name).
3. Add a post-build step that copies `README.md` and `USER_GUIDE.md` into `dist/`.
