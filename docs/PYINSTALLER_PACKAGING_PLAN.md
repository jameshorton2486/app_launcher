# PyInstaller Packaging Plan (Design Only)

## 1. Single Executable Strategy
Recommend `--onedir` for this app.
1. Faster startup (no temp extraction).
2. User-mutable config files can live next to the exe.
3. Easier debugging of packaging issues.
4. Tray icons and hotkey hooks are more reliable.

Recommended output structure:
```
dist/AppLauncher/
AppLauncher.exe
config/
settings.json
projects.json
tool_usage.json
_internal/
config/
logs/
```

## 2. Data File Handling
Read-only data files to bundle into `_internal/config/`:
1. `config/tools.json`
2. `config/design_system.json`
3. `config/file_patterns.json`
4. `config/external_tool_paths.json`

Mutable data files to create next to the exe at first run:
1. `config/settings.json`
2. `config/projects.json`
3. `config/tool_usage.json`

Logs:
1. Create `logs/` directory next to the exe at runtime.

## 3. Path Resolution Changes Required
Documented code pattern for `config_manager.py` and `main.py`:
```python
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR
```

## 4. Known Packaging Risks & Mitigations
1. pystray icon not showing
   - Bundle icon file explicitly, test `_win32` backend import.
2. keyboard library needs low-level hooks
   - Document that hotkeys require non-restricted paths.
3. customtkinter assets missing
   - Use `--collect-all customtkinter`.
4. GitPython cannot find git.exe
   - Document Git must be installed on the system.
5. win10toast DLL issues
   - Test on a clean Windows install; consider winotify later.
6. Large exe size
   - Expect 80–120 MB; use `--strip` and exclude unused stdlib.
7. UAC elevation per tool
   - Existing PowerShell elevation should work from packaged exe.
8. Antivirus false positives
   - Sign the exe; otherwise expect Defender warnings.

## 5. Build Commands (Reference Only)
```powershell
pyinstaller --onedir --windowed --name AppLauncher ^
  --icon assets/icon.ico ^
  --add-data "config/tools.json;config" ^
  --add-data "config/design_system.json;config" ^
  --add-data "config/file_patterns.json;config" ^
  --add-data "config/external_tool_paths.json;config" ^
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  --hidden-import PIL ^
  --hidden-import git ^
  --strip ^
  --exclude-module unittest ^
  --exclude-module email ^
  main.py
```

## 6. Debug vs Release Builds
1. Debug: add `--console` and keep full logging.
2. Release: use `--windowed` and set log level to WARNING.
3. Consider a `build.bat` script with `--debug` toggle.

## 7. Future Auto-Update Compatibility
1. Check a GitHub releases JSON endpoint on startup.
2. Download to a temp folder, prompt the user, replace on restart.
3. Do not implement now.
4. `--onedir` makes folder replacement straightforward.
