# App Launcher - Quick Start Guide

## 🚀 Simplest Way to Launch

### Option 1: One-Click Launch (Recommended)
Double-click **`launch.bat`** - That's it!

### Option 2: No Console Window
Double-click **`launch_no_console.bat`** - Runs silently in background

### Option 3: PowerShell
Right-click **`launch.ps1`** → Run with PowerShell

## 📦 First Time Setup

If this is your first time running the app:

1. **Run setup script** (one time only):
   ```
   setup_venv.bat
   ```
   This will:
   - Create a virtual environment (`.venv`)
   - Install all dependencies
   - Verify everything works

2. **Then launch normally**:
   ```
   launch.bat
   ```

## 🔧 How It Works

The launch scripts automatically:
- ✅ Use virtual environment (`.venv`) if it exists
- ✅ Fall back to system Python if venv not found
- ✅ Handle all paths correctly
- ✅ Show errors if something goes wrong

## 🎯 Direct Python Launch

If you prefer to run Python directly:

**With virtual environment:**
```bash
.venv\Scripts\python.exe main.py
```

**With system Python:**
```bash
python main.py
```

## ⚙️ Command Line Options

```bash
python main.py              # Normal start
python main.py --minimized  # Start minimized to tray
python main.py --debug      # Enable debug logging
```

## 🐛 Troubleshooting

### "Python not found"
- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Make sure "Add Python to PATH" is checked during installation

### "Module not found"
- Run `setup_venv.bat` to install dependencies
- Or manually: `pip install -r requirements.txt`

### "Virtual environment not working"
- Delete `.venv` folder
- Run `setup_venv.bat` again

## 📝 Notes

- The app uses a **virtual environment** (`.venv`) to keep dependencies isolated
- Launch scripts automatically detect and use the venv
- No need to activate the venv manually
- All dependencies are listed in `requirements.txt`

---

**That's it!** Just double-click `launch.bat` and you're good to go! 🎉
