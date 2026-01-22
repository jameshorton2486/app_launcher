# Getting Started - Quick Setup Guide

## ✅ Your Project Location

**CORRECT Directory:**
```
C:\user\james\app_launcher\app_launcher\
```

**NOT This Directory:**
```
C:\Users\james\app_launcher\  (different location, may be empty)
```

---

## Step 1: Navigate to the Correct Directory

```powershell
cd C:\user\james\app_launcher\app_launcher
```

**Verify you're in the right place:**
```powershell
dir
```

You should see:
- `main.py`
- `requirements.txt`
- `src/` folder
- `config/` folder
- Documentation files

---

## Step 2: Install Dependencies

**Option A: Using requirements.txt (Recommended)**
```powershell
cd C:\user\james\app_launcher\app_launcher
py -m pip install -r requirements.txt
```

**Option B: Install individually (if requirements.txt has issues)**
```powershell
py -m pip install customtkinter pystray Pillow keyboard watchdog psutil GitPython win10toast
```

---

## Step 3: Run the Application

**From the correct directory:**
```powershell
cd C:\user\james\app_launcher\app_launcher
py main.py
```

**Or with options:**
```powershell
py main.py --minimized    # Start minimized to tray
py main.py --debug        # Enable debug logging
py main.py --version      # Check version
```

---

## Step 4: Verify It's Working

You should see:
1. ✅ Application window opens
2. ✅ Three tabs visible: Projects, Downloads, Utilities
3. ✅ Search bar at top
4. ✅ Status bar at bottom
4. ✅ System tray icon appears

---

## Troubleshooting

### "No module named 'src'"
**Problem:** Running from wrong directory  
**Solution:** Make sure you're in `C:\user\james\app_launcher\app_launcher\`

### "Could not open requirements file"
**Problem:** Wrong directory or encoding issue  
**Solution:** 
1. Navigate to correct directory
2. If still fails, use Option B above to install individually

### "CTkTabview has no tab named 'Projects'"
**Problem:** This was fixed - make sure you have latest code  
**Solution:** Pull latest from GitHub or verify `src/app.py` has `tabview.add()` calls

### Application won't start
**Check:**
1. Python version: `py --version` (needs 3.8+)
2. Dependencies installed: `py -m pip list | Select-String "customtkinter"`
3. Logs: Check `logs/app.log` for errors

---

## Quick Commands Reference

```powershell
# Navigate
cd C:\user\james\app_launcher\app_launcher

# Install dependencies
py -m pip install -r requirements.txt

# Run application
py main.py

# Check version
py main.py --version

# Run without console window
pythonw main.py

# Or use launch script
.\launch.bat
```

---

## What You Should See

When running successfully:
- ✅ Window title: "James's Project Launcher (v2.0)"
- ✅ Three tabs: Projects | Downloads | Utilities
- ✅ Search bar at top
- ✅ Status bar showing "Ready"
- ✅ System tray icon in taskbar

---

## Next Steps

1. **Configure Settings:**
   - Click ⚙️ icon in status bar
   - Set Downloads folder path
   - Configure external tools (Cursor, VS Code, etc.)

2. **Add Your Projects:**
   - Go to Projects tab
   - Click [+ Add Project]
   - Fill in your project details

3. **Read the User Guide:**
   - See `USER_GUIDE.md` for complete instructions

---

**Remember:** Always run from `C:\user\james\app_launcher\app_launcher\` (not `C:\Users\james\app_launcher\`)
