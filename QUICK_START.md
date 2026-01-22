# Quick Start Guide

## 🚀 Getting Started

### First Time Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   - Run the application: `python main.py` or double-click `launch.bat`
   - Click the ⚙️ (gear) icon in the status bar to open Settings
   - Configure your paths:
     - Downloads folder
     - Screenshots folder
     - External tools (Cursor, VS Code, PyCharm, CCleaner, etc.)

3. **Add Your Projects**
   - Go to the **Projects** tab
   - Click **[+ Add Project]**
   - Fill in project details:
     - Name, Path, Launch Script
     - Launch Type (python, npm, powershell, etc.)
     - GitHub URL, Claude Project URL (optional)
   - Or drag & drop a file/folder onto the Projects tab

4. **Enable System Integration** (Optional)
   - In Settings, enable "Start with Windows"
   - Set global hotkey (default: Win+Shift+L)
   - Enable "Minimize to system tray on close"

## 📋 Common Tasks

### Launch a Project
- Click the **▶ Launch** button on any project card
- Or use the context menu (right-click) → Launch

### Open Project in IDE
- Click the **🔧 IDE** button → Select Cursor, VS Code, or PyCharm
- Or right-click → Open in [IDE]

### Check Git Status
- Git status indicators show on each project card:
  - 🟢 Clean (no changes)
  - 🟡 Uncommitted changes
  - 🔴 Needs pull/push
- Click **🔄 Refresh** to update all statuses
- Use **Git Pull All** to pull all repositories

### Organize Downloads
1. Go to **Downloads** tab
2. Files are automatically categorized and matched to projects
3. Select files and click **Move Selected** or **Delete**
4. Use filters to find specific file types

### Run Utilities
- Go to **Utilities** tab
- Click any utility button for one-click system maintenance
- Some utilities require admin rights (UAC prompt will appear)

### Quick Access
- **Win+Shift+L**: Toggle window visibility
- **System Tray**: Right-click icon for quick launch menu
- **Search Bar**: Type to filter projects/files

## ⌨️ Keyboard Shortcuts

- **Win+Shift+L**: Toggle window (customizable in Settings)
- **Ctrl+F**: Focus search bar (when in app)
- **Escape**: Close dialogs

## 🔧 Troubleshooting

### Application Won't Start
- Check Python version: `python --version` (needs 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check logs: `logs/app.log`

### Projects Won't Launch
- Verify project path exists
- Check launch script exists and is correct
- For npm projects, ensure Node.js is installed
- Check logs for detailed error messages

### Git Status Not Updating
- Verify project is a git repository
- Check network connection
- Click **🔄 Refresh** button manually
- Check logs for git errors

### Downloads Tab Empty
- Verify Downloads folder path in Settings
- Click **🔄 Refresh** button
- Check that folder exists and is accessible

### Utilities Require Admin
- Some utilities need administrator privileges
- UAC prompt will appear - click "Yes"
- If declined, operation will be cancelled

## 📁 File Locations

- **Config**: `config/settings.json`, `config/projects.json`
- **Logs**: `logs/app.log`
- **Launch Scripts**: `launch.bat`, `launch.ps1`

## 🎯 Next Steps

1. Add all your projects
2. Configure external tools
3. Set up system tray and hotkey
4. Enable "Start with Windows" for automatic startup
5. Customize theme (Dark/Light/System)

## 📚 More Information

- See `README.md` for full documentation
- See `FEATURE_VERIFICATION.md` for feature list
- See `tests/manual_test_checklist.md` for testing guide

---

**Need Help?** Check the logs in `logs/app.log` for detailed error messages.
