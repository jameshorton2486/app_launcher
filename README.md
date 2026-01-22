# James's Project Launcher (v2.0)

A modern, centralized hub for launching projects, managing files, running utilities, and integrating with development tools. Built with CustomTkinter for a beautiful, modern interface.

## Features

### 🚀 Projects Tab
- **Project Management**: Add, edit, and organize your development projects
- **Quick Launch**: Launch projects with one click (Python, Node.js, PowerShell, executables)
- **Git Integration**: Real-time git status, pull, push, and commit information
- **IDE Integration**: Quick access to Cursor, VS Code, and PyCharm
- **Project Cards**: Beautiful cards showing project info, git status, and last commit
- **Search & Filter**: Fast search with debouncing, sort by name, favorites, or language
- **Drag & Drop**: Add projects by dragging files/folders onto the tab

### 📥 Downloads Tab
- **File Organization**: Automatically scan and categorize downloaded files
- **Smart Categorization**: Code, Docs, Images, Archives, and Unknown files
- **Project Matching**: Suggests project destinations based on file patterns
- **Batch Operations**: Select multiple files for move/delete operations
- **Filtering**: Filter by category or search by filename
- **Lazy Loading**: Only scans when tab is activated for better performance

### 🛠️ Utilities Tab
- **Quick Cleanup**: Empty recycle bin, clear temp files, flush DNS
- **Memory & Performance**: Clear standby RAM, disk cleanup, optimize drives
- **Network Tools**: Reset network, release/renew IP, view network stats
- **Windows Update**: Clear update cache, pause updates, reset MS Store
- **External Tools**: Launch CCleaner, Wise Memory Cleaner
- **Admin Elevation**: Automatic UAC prompts for operations requiring admin rights

### ⚙️ System Integration
- **System Tray**: Minimize to tray, quick launch menu, utility shortcuts
- **Global Hotkey**: Toggle window with Win+Shift+L (customizable)
- **Start with Windows**: Automatic startup option with minimized mode
- **Window Persistence**: Remembers window position and size
- **Status Bar**: Real-time git status, RAM usage, and operation feedback

### 🎨 Settings
- **Comprehensive Configuration**: All settings in one dialog
- **Theme Support**: Dark, Light, and System theme modes
- **Path Management**: Configure downloads, screenshots, and external tools
- **Hotkey Customization**: Change global hotkey with interactive capture
- **Startup Options**: Control Windows startup and minimize behavior

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option 1: Direct Python**
```bash
python main.py
```

**Option 2: Without Console Window**
```bash
pythonw main.py
```

**Option 3: Using Launch Scripts**
- `launch.bat` - Launches without console window (recommended)
- `launch.ps1` - PowerShell script for launching
- `launch_no_console.bat` - Alternative batch file

## Configuration

Configuration files are stored in the `config/` directory:

- **`settings.json`**: Application settings (window, theme, paths, external tools, startup)
- **`projects.json`**: Project definitions with paths, launch scripts, and metadata
- **`file_patterns.json`**: File pattern matching rules for downloads categorization

### First-Time Setup

1. **Configure Downloads Folder**
   - Open Settings (⚙ button in status bar)
   - Set "Downloads folder" path
   - Set "Screenshots folder" path (optional)

2. **Add Projects**
   - Go to Projects tab
   - Click "+ Add Project"
   - Fill in project details or drag & drop a file/folder

3. **Configure External Tools** (optional)
   - Open Settings
   - Set paths for Cursor, VS Code, PyCharm, CCleaner, etc.

4. **Set Global Hotkey** (optional)
   - Open Settings
   - Click "Change Hotkey" to customize

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Win + Shift + L` | Toggle window visibility (default, customizable) |
| `Ctrl + F` | Focus search bar (when in main window) |
| `Esc` | Clear search (when search bar focused) |

## Usage Guide

### Projects Tab

**Adding a Project:**
1. Click "+ Add Project" button
2. **Manual Entry**: Fill in name, path, launch script, etc.
3. **Drag & Drop**: Drag a file (.exe, .py, .ps1, .bat) or folder onto the tab
4. Click "Save"

**Launching Projects:**
- Click "▶ Launch" button on project card
- Or right-click → "Launch"

**Git Operations:**
- Git status updates automatically every 60 seconds
- Right-click project → "Git Pull" or "Git Push"
- Click git status indicator for detailed information

**IDE Integration:**
- Click IDE dropdown on project card
- Select Cursor, VS Code, or PyCharm
- Or right-click → "Open in IDE"

### Downloads Tab

**Scanning Files:**
- Files are automatically scanned when tab is first activated
- Click "Refresh" to rescan manually

**Filtering:**
- Click category buttons (All, Code, Docs, Images, Archives, Unknown)
- Use search bar to filter by filename
- Search is debounced (300ms delay)

**Moving Files:**
- Select files using checkboxes
- Click "Move Selected" and choose destination
- Or use individual file "Move" buttons with suggested destinations

**Deleting Files:**
- Select files and click "Delete Selected"
- Or use individual file "Delete" buttons
- Confirmation dialog appears before deletion

### Utilities Tab

**Running Utilities:**
- Click any utility button
- Visual feedback shows: Loading → Success/Error
- Some utilities require admin elevation (UAC prompt)

**Quick Cleanup:**
- Empty Recycle Bin
- Clear Temp Files
- Flush DNS
- Clear Prefetch

**Memory & Performance:**
- Clear Standby RAM (requires admin)
- Run Disk Cleanup (requires admin)
- Optimize Drive (requires admin)
- Restart Explorer

**Network Tools:**
- Reset Network (requires admin)
- Release/Renew IP (requires admin)
- View Network Stats

### System Tray

**Accessing Tray Menu:**
- Right-click tray icon
- Menu includes:
  - Open App Launcher
  - Quick Launch (all projects)
  - Utilities (quick access)
  - Settings
  - Exit

**Minimizing to Tray:**
- Click window close (X) button
- Window minimizes to tray (if enabled in settings)
- First minimize shows notification

**Restoring Window:**
- Left-click tray icon
- Or use global hotkey (Win+Shift+L)

### Settings Dialog

**Accessing Settings:**
- Click ⚙ button in status bar
- Or right-click tray icon → Settings

**General Settings:**
- ☑ Start with Windows
- ☑ Minimize to system tray on close
- ☑ Start minimized

**Hotkey:**
- View current hotkey
- Click "Change Hotkey" to customize
- Interactive hotkey capture dialog

**Paths:**
- Downloads folder
- Screenshots folder
- Browse buttons for easy selection

**External Tools:**
- CCleaner path
- Wise Memory Cleaner path
- Cursor, VS Code, PyCharm paths

**Theme:**
- Mode: Dark / Light / System
- Accent color picker with preview

## Project Structure

```
app_launcher/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── launch.bat                   # Launch script (no console)
├── launch.ps1                   # PowerShell launch script
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
│
├── config/                       # Configuration files
│   ├── settings.json            # Application settings
│   ├── projects.json            # Project definitions
│   └── file_patterns.json       # File pattern rules
│
├── src/                         # Source code
│   ├── app.py                   # Main application class
│   ├── config_manager.py        # Configuration management
│   ├── theme.py                 # Theme system
│   │
│   ├── tabs/                    # Tab implementations
│   │   ├── projects_tab.py      # Projects tab
│   │   ├── downloads_tab.py     # Downloads tab
│   │   └── utilities_tab.py    # Utilities tab
│   │
│   ├── components/              # UI components
│   │   ├── project_card.py      # Project card widget
│   │   ├── project_dialog.py    # Add/Edit project dialog
│   │   ├── file_item.py         # File item widget
│   │   ├── search_bar.py        # Search bar component
│   │   ├── status_bar.py        # Status bar component
│   │   ├── utility_button.py    # Utility button widget
│   │   ├── settings_dialog.py   # Settings dialog
│   │   └── hotkey_capture_dialog.py  # Hotkey capture
│   │
│   ├── services/                # Business logic
│   │   ├── git_service.py       # Git operations
│   │   ├── process_service.py   # Process launching
│   │   ├── file_service.py      # File operations
│   │   └── cleanup_service.py  # System utilities
│   │
│   └── utils/                   # Utilities
│       ├── logger.py            # Logging system
│       ├── system_tray.py        # System tray integration
│       ├── hotkey_manager.py    # Global hotkey management
│       ├── startup_manager.py   # Windows startup management
│       ├── validation.py        # Input validation
│       └── helpers.py           # Helper functions
│
├── logs/                        # Application logs
│   └── app.log                  # Main log file (rotates at 5MB)
│
└── tests/                       # Testing
    └── manual_test_checklist.md # Manual testing checklist
```

## Troubleshooting

### Application Won't Start

**Symptoms:** Application doesn't launch or crashes immediately

**Solutions:**
1. Check Python version: `python --version` (must be 3.8+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check logs: `logs/app.log` for error messages
4. Try running with console: `python main.py` to see errors
5. Verify all required files exist in `config/` directory

### Projects Won't Launch

**Symptoms:** Clicking "Launch" does nothing or shows error

**Solutions:**
1. Verify project path exists and is correct
2. Check launch script path is valid
3. Ensure required executables are in PATH:
   - Python: `python --version`
   - Node.js: `node --version`
   - Git: `git --version`
4. Check file permissions on project directory
5. Review logs for specific error messages
6. Try launching manually from command line to test

### Git Status Not Showing

**Symptoms:** Git status indicators show "?" or don't update

**Solutions:**
1. Verify project is a git repository (contains `.git` folder)
2. Check GitPython is installed: `pip install GitPython`
3. Verify git is installed and in PATH: `git --version`
4. Check repository paths are correct
5. Verify network connection for remote operations
6. Check logs for git operation errors

### Tray Icon Not Appearing

**Symptoms:** No tray icon visible in system tray

**Solutions:**
1. Check pystray and Pillow are installed: `pip install pystray Pillow`
2. Windows may hide tray icons - check notification area settings
3. Right-click taskbar → Taskbar settings → Select which icons appear
4. Check logs for tray icon initialization errors
5. Try restarting the application

### Hotkey Not Working

**Symptoms:** Global hotkey doesn't toggle window

**Solutions:**
1. Verify keyboard library is installed: `pip install keyboard`
2. Check hotkey is registered in Settings
3. Some antivirus software blocks global hotkeys - add exception
4. Try running as administrator
5. Check if another application is using the same hotkey
6. Try changing to a different hotkey combination

### Settings Not Saving

**Symptoms:** Settings changes don't persist after restart

**Solutions:**
1. Check write permissions on `config/` directory
2. Verify `config/settings.json` isn't open in another program
3. Check disk space available
4. Review logs for save errors
5. Try running as administrator
6. Manually check `config/settings.json` file format (valid JSON)

### Downloads Tab Not Loading

**Symptoms:** Downloads tab shows "Not configured" or empty

**Solutions:**
1. Configure downloads folder in Settings
2. Verify folder path exists and is accessible
3. Check folder permissions (read access required)
4. Click "Refresh" button to rescan
5. Check logs for scanning errors

### File Operations Fail

**Symptoms:** Move/delete operations show errors

**Solutions:**
1. Check file permissions (read/write access)
2. Verify destination folder exists and is writable
3. Ensure files aren't locked by another program
4. Check disk space available
5. Review logs for specific error messages
6. Try running as administrator for protected locations

## Logging

Application logs are stored in `logs/app.log` with automatic rotation:

- **Log Rotation**: Rotates when file exceeds 5MB
- **Backup Files**: Keeps 3 backup log files
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: Timestamp, module, function, line number, message

**Viewing Logs:**
```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View on Windows
type logs\app.log
```

## Performance Tips

1. **Lazy Loading**: Downloads tab only scans when activated
2. **Debounced Search**: Search input has 300ms delay to reduce filtering
3. **Git Caching**: Git status is cached and updated periodically
4. **Background Threading**: Long operations run in background threads
5. **Log Rotation**: Logs rotate automatically to prevent large files

## Development

### Running in Development Mode

```bash
# Run with console for debugging
python main.py

# Run with minimized flag
python main.py --minimized
```

### Testing

See `tests/manual_test_checklist.md` for comprehensive testing guide.

### Building Distribution

Currently, the application runs directly from source. For distribution:

1. Ensure all dependencies are listed in `requirements.txt`
2. Test on clean Python environment
3. Package with PyInstaller (optional):
   ```bash
   pip install pyinstaller
   pyinstaller --onefile --windowed --name "AppLauncher" main.py
   ```

## Dependencies

- **customtkinter** (>=5.2.0) - Modern UI framework
- **pystray** (>=0.19.5) - System tray integration
- **Pillow** (>=10.0.0) - Image processing for tray icon
- **keyboard** (>=0.13.5) - Global hotkey support
- **watchdog** (>=3.0.0) - File system monitoring (optional)
- **psutil** (>=5.9.0) - System information (RAM usage)
- **GitPython** (>=3.1.40) - Git operations
- **win10toast** (>=0.9) - Windows notifications (optional)

## License

Private project for personal use.

## Credits

Built with:
- **CustomTkinter** - Modern, beautiful UI framework
- **pystray** - Cross-platform system tray integration
- **keyboard** - Global hotkey registration
- **GitPython** - Pythonic git operations
- **Pillow** - Image processing

## Version History

- **v2.0** - Complete rewrite with CustomTkinter, all features implemented
- **v1.0** - Initial version

## Support

For issues or questions:
1. Check `logs/app.log` for error details
2. Review troubleshooting section above
3. Check `tests/manual_test_checklist.md` for feature verification

---

**Enjoy your streamlined development workflow! 🚀**
