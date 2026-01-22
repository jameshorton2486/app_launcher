# James's Project Launcher - User Guide

## What Is This Application?

**James's Project Launcher** is a centralized desktop application that helps you:

1. **Launch your development projects** with one click
2. **Organize downloaded files** by automatically matching them to your projects
3. **Run system maintenance utilities** quickly and easily
4. **Monitor Git repository status** across all your projects
5. **Access your projects** in IDEs, terminals, and file explorers instantly

Think of it as a **command center** for all your development work - everything you need in one place.

---

## Getting Started

### First Launch

1. **Run the application:**
   ```powershell
   cd C:\user\james\app_launcher\app_launcher
   py main.py
   ```

2. **Configure Settings:**
   - Click the **⚙️ (gear icon)** in the bottom-right of the status bar
   - Set up your paths:
     - Downloads folder (where your downloads are stored)
     - Screenshots folder (optional)
     - External tools (Cursor, VS Code, PyCharm, CCleaner, etc.)

3. **Add Your Projects:**
   - Go to the **Projects** tab
   - Click **[+ Add Project]**
   - Fill in your project details (see "Adding Projects" below)

---

## Main Features

### 🚀 Projects Tab

**What it does:** Manages and launches all your development projects.

**How to use:**

#### Viewing Projects
- All your projects appear as **cards** in a grid
- Each card shows:
  - Project name and description
  - Git status indicator (🟢 clean, 🟡 uncommitted changes, 🔴 needs attention)
  - Last commit time
  - Programming language

#### Launching a Project
- Click the **▶ Launch** button on any project card
- The app will run your project based on its type:
  - **Python projects**: Runs `python main.py` (or your specified script)
  - **Node.js projects**: Runs `npm run dev` (or your specified command)
  - **PowerShell scripts**: Executes the `.ps1` file
  - **Executables**: Launches the `.exe` file

#### Quick Actions on Projects
Each project card has buttons for:

- **📁 Folder**: Opens the project folder in Windows File Explorer
- **💻 Terminal**: Opens PowerShell in the project directory
- **🔧 IDE**: Dropdown menu to open in:
  - Cursor
  - VS Code
  - PyCharm
- **🤖 Claude**: Opens your Claude project URL in browser
- **🐙 GitHub**: Opens your GitHub repository in browser

#### Git Operations
- **Git Status**: Shows on each card (🟢🟡🔴)
- **Right-click** a project card → **Git Pull** or **Git Push**
- **🔄 Refresh**: Updates all project git statuses
- **Git Pull All**: Pulls latest changes for all projects at once

#### Adding a New Project

**Method 1: Manual Entry**
1. Click **[+ Add Project]** button
2. Fill in the form:
   - **Name**: Your project name
   - **Path**: Full path to project folder (use Browse button)
   - **Launch Script**: Script to run (e.g., `main.py`, `npm run dev`)
   - **Launch Type**: Select from dropdown (python, npm, powershell, exe, bat)
   - **GitHub URL**: Your repository URL (optional)
   - **Claude Project URL**: Your Claude project link (optional)
   - **Icon**: Emoji or icon for the project
   - **File Patterns**: Keywords to match files (for Downloads tab)
3. Click **Save**

**Method 2: Drag & Drop**
1. Drag a file (`.py`, `.ps1`, `.exe`, `.bat`) or folder onto the Projects tab
2. The app will auto-detect the name and path
3. Fill in remaining details in the dialog
4. Click **Save**

#### Editing/Removing Projects
- **Right-click** any project card → **Edit Project** or **Remove Project**

#### Searching and Sorting
- **Search bar**: Type to filter projects by name or description
- **Sort dropdown**: Sort by:
  - A-Z (alphabetical)
  - Favorites First
  - Language

---

### 📥 Downloads Tab

**What it does:** Helps you organize downloaded files by automatically matching them to your projects.

**How to use:**

#### Viewing Downloads
1. Click the **Downloads** tab
2. The app scans your Downloads folder and shows all files
3. Files are automatically:
   - **Categorized** (Code, Docs, Images, Archives, Unknown)
   - **Matched** to projects based on filename patterns

#### File Information
Each file shows:
- File icon (based on type)
- Filename
- File size
- Modified date
- **Suggested destination** (which project it matches)

#### Moving Files
**Single File:**
1. Select a destination from the dropdown (or leave as suggested)
2. Click **[Move]** button

**Multiple Files:**
1. Check the boxes next to files you want to move
2. Click **[Move Selected]** at the bottom
3. Files will be moved to their suggested destinations

**Custom Destination:**
- Select "Custom..." from the destination dropdown
- Choose a folder manually

#### Deleting Files
- **Single file**: Click **[❌]** button (confirmation required)
- **Multiple files**: Select files, click **[Delete Selected]** (confirmation required)

#### Filtering Files
- Use filter buttons: **[All]**, **[Code]**, **[Docs]**, **[Images]**, **[Archives]**, **[Unknown]**
- Use search bar to filter by filename

#### Special Handling
- **Screenshots**: Automatically suggested to go to Screenshots folder
- **Archives**: Can be sent to Archives folder or project folders
- **Duplicates**: Files with `(1)`, `(2)` in name are highlighted

---

### 🛠️ Utilities Tab

**What it does:** Provides quick access to system maintenance and cleanup tools.

**How to use:**

#### Quick Cleanup Section
- **🗑️ Empty Recycle Bin**: Clears all deleted files
- **🧹 Clear Temp Files**: Removes temporary files (shows MB freed)
- **🔄 Flush DNS**: Clears DNS cache
- **📁 Clear Prefetch**: Clears Windows prefetch (requires admin)

#### Memory & Performance Section
- **🧠 Clear RAM Standby**: Frees up standby memory
- **💾 Disk Cleanup**: Launches Windows Disk Cleanup tool
- **⚡ Defrag/Optimize**: Optimizes your drive
- **🔄 Restart Explorer**: Restarts Windows Explorer (fixes UI issues)

#### External Tools Section
- **🧽 Open CCleaner**: Launches CCleaner (if configured)
- **🧠 Open Wise Memory**: Launches Wise Memory Optimizer (if configured)
- **🏪 Reset MS Store**: Resets Microsoft Store cache

#### Network Section
- **🌐 Reset TCP/IP**: Resets network stack (requires admin)
- **🔌 Release/Renew IP**: Releases and renews your IP address
- **📶 Net Stats**: Shows network statistics

#### Windows Update Section
- **🗑️ Clear Update Cache**: Clears Windows Update cache (requires admin)
- **⏸️ Pause Updates**: Pauses Windows updates for 7 days
- **🏪 Reset MS Store**: Resets Microsoft Store

**Note:** Some utilities require administrator privileges. You'll see a UAC (User Account Control) prompt - click "Yes" to proceed.

---

## System Integration Features

### System Tray Icon

**What it does:** Keeps the app running in the background, accessible from the system tray.

**How to use:**
- **Left-click** tray icon: Restores/shows the window
- **Right-click** tray icon: Shows menu with:
  - **Open App Launcher**: Show window
  - **Quick Launch**: Submenu to launch projects directly
  - **Utilities**: Submenu for common utilities
  - **Settings**: Open settings dialog
  - **Exit**: Close the application

**Minimize to Tray:**
- When you click the **X** button, the app minimizes to tray (doesn't close)
- First time: Shows a notification
- To actually exit: Right-click tray icon → **Exit**

### Global Hotkey

**What it does:** Quickly show/hide the launcher from anywhere.

**Default hotkey:** `Win + Shift + L`

**How to use:**
- Press `Win + Shift + L` to toggle the window visibility
- If hidden: Shows the window
- If visible: Hides to tray

**Change hotkey:**
1. Open **Settings** (⚙️ icon)
2. Go to **HOTKEY** section
3. Click **[Change]** button
4. Press your desired key combination
5. Click **Save**

### Start with Windows

**What it does:** Automatically starts the app when Windows boots.

**How to enable:**
1. Open **Settings** (⚙️ icon)
2. Check **"Start with Windows"**
3. Optionally check **"Start minimized"** to start in tray
4. Click **Save**

The app will now start automatically when you log in.

---

## Settings

### Opening Settings
- Click the **⚙️ (gear icon)** in the status bar (bottom-right)

### Settings Sections

#### GENERAL
- **☑ Start with Windows**: Launch app on Windows startup
- **☑ Minimize to system tray on close**: Hide instead of closing
- **☑ Start minimized**: Start in tray (only icon visible)

#### HOTKEY
- **Current hotkey**: Shows your current global hotkey
- **[Change]**: Click to set a new hotkey

#### PATHS
- **Downloads folder**: Where your downloads are stored
- **Screenshots folder**: Where screenshots should go
- **[Browse]**: Buttons to select folders

#### EXTERNAL TOOLS
Configure paths to:
- CCleaner
- Wise Memory Cleaner
- Cursor (IDE)
- VS Code (IDE)
- PyCharm (IDE)

#### THEME
- **Mode**: Choose Dark, Light, or System (follows Windows theme)
- **Accent Color**: Pick a color for buttons and highlights

---

## Keyboard Shortcuts

- **Win + Shift + L**: Toggle window visibility (global hotkey, customizable)
- **Escape**: Close dialogs
- **Ctrl + F**: Focus search bar (when in app)

---

## Status Bar

The bottom status bar shows:

- **Left**: Current status message (e.g., "Ready", "Scanning downloads...")
- **Center**: Git summary (e.g., "3 repos need attention")
- **Right**: RAM usage percentage
- **Far Right**: ⚙️ Settings button

---

## Tips & Best Practices

### Project Management
1. **Use descriptive names** for projects
2. **Set file patterns** when adding projects - this helps the Downloads tab match files
3. **Keep GitHub URLs updated** for quick access
4. **Use favorites** (⭐) to mark important projects

### Downloads Organization
1. **Review suggestions** before moving files - the app is smart but not perfect
2. **Use filters** to find specific file types quickly
3. **Batch operations** save time when organizing many files
4. **Check duplicates** - the app highlights files with `(1)`, `(2)` in names

### System Utilities
1. **Run cleanup regularly** - especially "Clear Temp Files" and "Empty Recycle Bin"
2. **Use "Clear RAM Standby"** if your computer feels slow
3. **"Restart Explorer"** fixes many Windows UI glitches
4. **Admin utilities** will prompt for permission - this is normal

### Performance
- The app uses **lazy loading** - Downloads tab only scans when you open it
- Git status updates **every 60 seconds** automatically
- Search is **debounced** - waits 300ms after you stop typing

---

## Troubleshooting

### Application Won't Start
- **Check Python version**: Need Python 3.8 or higher
- **Install dependencies**: Run `py -m pip install -r requirements.txt`
- **Check logs**: Look in `logs/app.log` for error details

### Projects Won't Launch
- **Verify project path exists**
- **Check launch script** is correct
- **For npm projects**: Ensure Node.js is installed
- **Check logs**: `logs/app.log` has detailed error messages

### Git Status Not Updating
- **Verify project is a git repository**
- **Check network connection**
- **Click 🔄 Refresh** button manually
- **Check logs** for git errors

### Downloads Tab Empty
- **Verify Downloads folder path** in Settings
- **Click 🔄 Refresh** button
- **Check folder exists** and is accessible

### Utilities Require Admin
- Some utilities need administrator privileges
- **UAC prompt will appear** - click "Yes"
- If you decline, the operation will be cancelled

### Window Won't Show
- **Check system tray** - app might be minimized
- **Press Win + Shift + L** to toggle visibility
- **Right-click tray icon** → "Open App Launcher"

---

## File Locations

- **Config files**: `config/settings.json`, `config/projects.json`
- **Logs**: `logs/app.log` (rotates when over 5MB)
- **Launch scripts**: `launch.bat`, `launch.ps1`

---

## What Makes This Different?

Unlike other launchers, this app:

1. **Understands your projects** - Knows what type they are and how to launch them
2. **Organizes downloads automatically** - Matches files to projects intelligently
3. **Monitors Git status** - Shows repository status across all projects
4. **System integration** - Tray icon, global hotkey, startup options
5. **All-in-one** - Projects, file management, and system utilities in one place

---

## Need Help?

1. **Check logs**: `logs/app.log` has detailed information
2. **Review this guide**: Most questions are answered here
3. **Check README.md**: Technical details and installation info
4. **Test checklist**: See `tests/manual_test_checklist.md` for feature verification

---

**Enjoy your streamlined development workflow! 🚀**
