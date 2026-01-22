# Implementation Prompts for Cursor AI

This document contains the exact prompts to give to Cursor AI to build the App Launcher application phase by phase.

---

## Prompt 1: Project Setup

Create a new Python project for a Windows desktop application called "App Launcher" using CustomTkinter.

**Project structure:**
```
app_launcher/
├── main.py
├── requirements.txt
├── config/
│   ├── settings.json
│   ├── projects.json
│   └── file_patterns.json
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config_manager.py
│   ├── theme.py
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── projects_tab.py
│   │   ├── downloads_tab.py
│   │   └── utilities_tab.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── project_card.py
│   │   ├── search_bar.py
│   │   ├── status_bar.py
│   │   └── file_item.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── git_service.py
│   │   ├── file_service.py
│   │   ├── process_service.py
│   │   └── cleanup_service.py
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       ├── helpers.py
│       └── system_tray.py
├── assets/
│   └── icons/
└── launch.bat
```

**Requirements:**
- customtkinter>=5.2.0
- pystray>=0.19.0
- Pillow>=10.0.0
- keyboard>=0.13.5
- watchdog>=3.0.0

Create the initial files with proper imports and docstrings. The theme should use a dark purple color scheme with these colors:
- bg_primary: #1a1a2e
- bg_secondary: #16213e
- accent_primary: #6c5ce7
- text_primary: #ffffff

The main window should be 900x650 pixels with a custom title "James's Project Launcher".

---

## Prompt 2: Phase 1 - Core Foundation

Implement Phase 1: Core Foundation for the App Launcher.

**Tasks:**
1. Complete `src/theme.py` with full color palette and `apply_theme()` function
2. Complete `src/config_manager.py` with:
   - JSON file loading/saving
   - Default value merging
   - File watching for external changes
   - Methods: `load_settings()`, `save_settings()`, `load_projects()`, `save_projects()`, `load_file_patterns()`
3. Complete `src/app.py` with:
   - CustomTkinter window setup
   - Tab view with 3 tabs: Projects, Downloads, Utilities
   - Search bar at top (functional, filters active tab)
   - Status bar at bottom (shows "Ready")
   - Window close handling (minimize to tray when enabled)
4. Create `src/components/search_bar.py` - Search bar component with filter callback
5. Create `src/components/status_bar.py` - Status bar with status, git, and system info sections
6. Create placeholder tabs in `src/tabs/` (Projects, Downloads, Utilities)
7. Create default configuration files in `config/`:
   - `settings.json` with window, theme, paths, external_tools
   - `projects.json` with sample projects array
   - `file_patterns.json` with file type patterns

**Deliverables:**
- App launches with themed window
- 3 empty tabs visible
- Search bar functional (no filtering yet)
- Status bar shows "Ready"
- Configuration files load correctly

---

## Prompt 3: Phase 2 - Projects Tab

Implement Phase 2: Projects Tab with full project management functionality.

**Tasks:**
1. Create `src/services/git_service.py` with:
   - `get_status()` - Returns git repository status
   - `pull()`, `push()` - Git operations
   - `get_current_branch()`, `get_last_commit()` - Git info
   - `clone()` - Clone repository
2. Create `src/services/process_service.py` with:
   - `launch_project()` - Launch projects (python, npm, powershell, bat, exe)
   - `open_folder()`, `open_terminal()` - File system operations
   - `open_in_ide()` - Open in Cursor, VS Code, PyCharm
   - `open_url()` - Open URLs in browser
3. Create `src/components/project_card.py` with:
   - Project card layout (icon, name, description, git status, actions)
   - Favorite star toggle
   - Git status indicator (🟢 clean, 🟡 uncommitted, 🔴 needs pull)
   - Action buttons: Launch, Folder, Terminal, IDE dropdown, Claude, GitHub
   - Right-click context menu
4. Create `src/components/project_dialog.py` with:
   - Add/Edit project dialog
   - All project fields (name, path, launch_script, launch_type, etc.)
   - Browse buttons for paths
   - Validation
5. Complete `src/tabs/projects_tab.py` with:
   - Quick actions bar (+ Add Project, Refresh Git Status, Git Pull All, Sort)
   - Grid layout (2 columns) for project cards
   - Search filtering
   - Add/Edit/Remove functionality
   - Git status polling (every 60 seconds)

**Deliverables:**
- Projects display as cards in grid
- All action buttons functional
- Git status updates automatically
- Add/Edit/Remove projects working
- Search filters projects
- Sort functionality works

---

## Prompt 4: Phase 4 - Utilities Tab

Implement Phase 4: Utilities Tab with system maintenance tools.

**Tasks:**
1. Create `src/services/cleanup_service.py` with all cleanup operations:
   - `empty_recycle_bin()`, `clear_temp_files()`, `flush_dns()`
   - `clear_prefetch()`, `clear_standby_ram()`
   - `run_disk_cleanup()`, `optimize_drive()`, `restart_explorer()`
   - `reset_network()`, `release_renew_ip()`, `get_network_stats()`
   - `clear_windows_update_cache()`, `pause_windows_updates()`
   - `reset_ms_store()`, `launch_ccleaner()`, `launch_wise_memory_cleaner()`
   - Admin elevation handling with `is_admin()` and `run_as_admin()`
2. Create `src/components/utility_button.py` with:
   - Icon, title, subtitle
   - Visual feedback (loading, success, error states)
   - Hover effects
   - Status messages
3. Complete `src/tabs/utilities_tab.py` with organized sections:
   - Quick Cleanup (4 buttons)
   - Memory & Performance (4 buttons)
   - External Tools (3 buttons)
   - Network (3 buttons)
   - Windows Update (2 buttons)

**Deliverables:**
- All utility buttons functional
- Visual feedback during and after operations
- Admin elevation handled gracefully
- External tools launch correctly

---

## Prompt 5: Phase 5 - System Integration

Implement Phase 5: System Integration with tray icon, hotkeys, and startup.

**Tasks:**
1. Complete `src/utils/system_tray.py` with:
   - System tray icon creation using pystray
   - Menu structure: Open, Quick Launch submenu, Utilities submenu, Settings, Exit
   - Double-click to restore window
   - Integration with app instance
2. Create `src/utils/startup_manager.py` with:
   - `enable_startup()` - Add to Windows startup registry
   - `disable_startup()` - Remove from registry
   - `check_startup_enabled()` - Check current status
3. Update `src/app.py` to:
   - Start tray icon on initialization
   - Register global hotkey (Win+Shift+L) using keyboard library
   - Handle startup settings
   - Minimize to tray on close
   - Toggle window visibility with hotkey
4. Optional: Create `src/utils/file_watcher.py` for Downloads folder monitoring

**Deliverables:**
- Tray icon appears on start
- App minimizes to tray on close
- Tray menu fully functional
- Global hotkey works
- Startup toggle in settings

---

## Prompt 6: Phase 6 - Polish & Testing

Implement Phase 6: Polish & Testing with error handling, settings dialog, and optimizations.

**Tasks:**
1. Create `src/components/settings_dialog.py` with:
   - General section (checkboxes for startup options)
   - Hotkey section (hotkey input and change button)
   - Paths section (Downloads, Screenshots with browse buttons)
   - External Tools section (all tool paths with browse buttons)
   - Theme section (mode dropdown, color picker)
   - Save/Cancel buttons
2. Create `src/utils/logger.py` with:
   - File logging to `logs/app.log`
   - Console logging for warnings/errors
   - Proper log levels and formatting
3. Add error handling throughout:
   - Wrap file/process operations in try-except
   - Show user-friendly error messages in status bar
   - Log all errors to file
   - Never crash silently
4. Performance optimizations:
   - Lazy load tabs (only render when tab activated)
   - Cache git status (refresh on interval)
   - Use threading for long operations
   - Show progress indicators
5. Integrate settings dialog with tray menu
6. Update all services to use logger

**Deliverables:**
- Settings dialog functional
- All error cases handled
- Smooth performance
- No crashes
- Comprehensive logging

---

## Usage Instructions

1. Start with **Prompt 1** to set up the project structure
2. Proceed through prompts 2-6 in order
3. Test after each phase using the deliverables checklist
4. **Commit to GitHub after each prompt** (see Git Workflow below)
5. Refer to `TESTING_CHECKLIST.md` for comprehensive testing
6. Check `logs/app.log` for any errors

## Git Workflow

After completing each prompt, commit your changes to GitHub:

### After Prompt 1: Project Setup
```bash
git add .
git commit -m "Phase 1: Project setup - Initial structure and dependencies"
git push origin main
```

### After Prompt 2: Phase 1 - Core Foundation
```bash
git add .
git commit -m "Phase 1: Core Foundation - Theme, config manager, UI skeleton"
git push origin main
```

### After Prompt 3: Phase 2 - Projects Tab
```bash
git add .
git commit -m "Phase 2: Projects Tab - Project cards, git integration, actions"
git push origin main
```

### After Prompt 4: Phase 4 - Utilities Tab
```bash
git add .
git commit -m "Phase 4: Utilities Tab - System maintenance tools"
git push origin main
```

### After Prompt 5: Phase 5 - System Integration
```bash
git add .
git commit -m "Phase 5: System Integration - Tray icon, hotkeys, startup"
git push origin main
```

### After Prompt 6: Phase 6 - Polish & Testing
```bash
git add .
git commit -m "Phase 6: Polish & Testing - Settings dialog, error handling, optimizations"
git push origin main
```

### Optional: Tag Releases
After completing all phases, create a release tag:
```bash
git tag -a v2.0.0 -m "App Launcher v2.0 - Complete implementation"
git push origin v2.0.0
```

## Notes

- All prompts assume you're working in the `app_launcher/` directory
- Configuration files should be created with sensible defaults
- Error handling should be added from the start
- Use the existing codebase as reference if rebuilding
- **Always commit working code** - don't commit broken/incomplete implementations
- Test before committing to ensure deliverables are met
