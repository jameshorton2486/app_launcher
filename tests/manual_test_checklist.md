# Manual Testing Checklist

## Pre-Testing Setup
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Verify Python version (3.8+)
- [ ] Check that logs directory exists or will be created
- [ ] Ensure test projects exist with git repositories
- [ ] Configure downloads folder in settings

---

## 1. Application Startup
- [ ] Application launches without errors
- [ ] Window appears at correct size and position
- [ ] Window icon is displayed (if available)
- [ ] Status bar shows "Ready"
- [ ] All tabs are accessible
- [ ] No errors in `logs/app.log`

### Startup with Windows
- [ ] Enable "Start with Windows" in settings
- [ ] Restart computer or log out/in
- [ ] Application starts automatically
- [ ] "Start minimized" option works correctly
- [ ] Disable "Start with Windows" and verify it doesn't start

---

## 2. Projects Tab

### Project Display
- [ ] Projects load from config
- [ ] Project cards display correctly (icon, name, description)
- [ ] Git status indicators show correctly (clean/dirty/behind/ahead)
- [ ] Last commit time displays correctly
- [ ] Favorite star toggles correctly
- [ ] Cards are arranged in 2-column grid
- [ ] Scrollable when many projects

### Project Actions
- [ ] Launch button works (Python, npm, PowerShell, .exe, .bat)
- [ ] Folder button opens in File Explorer
- [ ] Terminal button opens PowerShell in project directory
- [ ] IDE dropdown shows options (Cursor, VS Code, PyCharm)
- [ ] IDE buttons open correct IDE
- [ ] Claude button opens Claude project URL
- [ ] GitHub button opens GitHub URL

### Git Operations
- [ ] Git status updates automatically (every 60 seconds)
- [ ] Git Pull works from context menu
- [ ] Git Push works from context menu
- [ ] Git Status shows detailed information
- [ ] "Git Pull All" button works
- [ ] Git operations show progress/feedback
- [ ] Errors are handled gracefully (no git repo, network errors)

### Add/Edit Project
- [ ] "Add Project" button opens dialog
- [ ] Manual entry mode works
- [ ] Drag & drop mode works (.exe, .py, .ps1, .bat, .cmd, folders)
- [ ] Auto-detection fills form correctly
- [ ] Validation works (empty name, invalid path, duplicate name)
- [ ] Save button saves to config
- [ ] Edit from context menu pre-fills dialog
- [ ] Cancel button closes without saving

### Search and Filter
- [ ] Search bar filters projects by name
- [ ] Search is debounced (doesn't trigger on every keystroke)
- [ ] Clear button clears search
- [ ] Sort dropdown works (Name, Last Modified, Language)
- [ ] Refresh button reloads projects

### Context Menu
- [ ] Right-click on card shows menu
- [ ] All menu items work correctly
- [ ] Menu closes on selection

---

## 3. Downloads Tab

### File Display
- [ ] Downloads folder path displays correctly
- [ ] Files are scanned and displayed
- [ ] File icons show correctly by category
- [ ] File size displays correctly
- [ ] Modified date displays correctly
- [ ] Files are categorized correctly (Code, Docs, Images, Archives, Unknown)

### Lazy Loading
- [ ] Downloads tab doesn't scan until activated
- [ ] First activation shows "Loading downloads..."
- [ ] Files load correctly on first activation

### Filtering
- [ ] Category filters work (All, Code, Docs, Images, Archives, Unknown)
- [ ] Search bar filters files by name
- [ ] Search is debounced
- [ ] Multiple filters work together

### File Operations
- [ ] Select All selects all visible files
- [ ] Deselect All clears selection
- [ ] Individual file checkboxes work
- [ ] Selected count updates correctly
- [ ] Move button shows suggested destinations
- [ ] Move operation works correctly
- [ ] Delete button shows confirmation dialog
- [ ] Delete operation works correctly
- [ ] Progress indicators show during operations
- [ ] Errors are handled gracefully

### File Item Actions
- [ ] Individual Move button works
- [ ] Individual Delete button works with confirmation
- [ ] Destination dropdown shows project suggestions
- [ ] Custom destination option works

---

## 4. Utilities Tab

### Quick Cleanup
- [ ] Empty Recycle Bin works (with admin elevation)
- [ ] Clear Temp Files works
- [ ] Flush DNS works
- [ ] Clear Prefetch works
- [ ] All show loading spinners
- [ ] All show success/error feedback

### Memory & Performance
- [ ] Clear Standby RAM works (with admin)
- [ ] Run Disk Cleanup works (with admin)
- [ ] Optimize Drive works (with admin)
- [ ] Restart Explorer works

### External Tools
- [ ] CCleaner launches (if path configured)
- [ ] Wise Memory Cleaner launches (if path configured)
- [ ] Error shown if tool not found

### Network
- [ ] Reset Network works (with admin)
- [ ] Release/Renew IP works (with admin)
- [ ] Network Stats displays correctly

### Windows Update
- [ ] Clear Windows Update Cache works (with admin)
- [ ] Pause Windows Updates works (with admin)
- [ ] Reset MS Store works

### Admin Elevation
- [ ] UAC prompt appears when needed
- [ ] Operations work after elevation
- [ ] Error shown if elevation declined

---

## 5. Settings Dialog

### General Settings
- [ ] "Start with Windows" checkbox works
- [ ] "Minimize to tray" checkbox works
- [ ] "Start minimized" checkbox works
- [ ] Settings save correctly

### Hotkey
- [ ] Current hotkey displays correctly
- [ ] "Change Hotkey" button opens capture dialog
- [ ] Hotkey capture works
- [ ] New hotkey registers correctly
- [ ] Hotkey works after change
- [ ] Error shown if hotkey conflict

### Paths
- [ ] Downloads folder browse works
- [ ] Screenshots folder browse works
- [ ] Paths save correctly
- [ ] Path validation works (shows errors for invalid paths)

### External Tools
- [ ] All tool path browse buttons work
- [ ] Paths save correctly
- [ ] Path validation works

### Theme
- [ ] Mode dropdown works (Dark, Light, System)
- [ ] Theme applies immediately on save
- [ ] Accent color picker works
- [ ] Color preview updates
- [ ] Theme persists after restart

### Save/Cancel
- [ ] Save button validates and saves
- [ ] Cancel button discards changes
- [ ] Error messages show for validation failures

---

## 6. System Integration

### System Tray
- [ ] Tray icon appears on startup
- [ ] Left-click restores window
- [ ] Right-click shows menu
- [ ] Quick Launch submenu shows projects
- [ ] Utilities submenu shows utilities
- [ ] Settings opens settings dialog
- [ ] Exit closes application
- [ ] Window close minimizes to tray
- [ ] First minimize shows notification (if enabled)

### Global Hotkey
- [ ] Default hotkey (Win+Shift+L) works
- [ ] Hotkey toggles window visibility
- [ ] Hotkey works when window minimized
- [ ] Hotkey works when window hidden
- [ ] Hotkey cleanup on exit

### Window Management
- [ ] Window position saves on move
- [ ] Window size saves on resize
- [ ] Window state restores on startup
- [ ] Minimize to tray works
- [ ] Restore from tray works

---

## 7. Error Handling

### File Operations
- [ ] Missing files handled gracefully
- [ ] Permission errors show user-friendly messages
- [ ] Network errors handled (git operations)
- [ ] Invalid paths show error messages
- [ ] All errors logged to `logs/app.log`

### Process Operations
- [ ] Missing executables show error
- [ ] Failed launches show error
- [ ] Invalid commands show error
- [ ] All errors logged

### Git Operations
- [ ] Not a git repo handled
- [ ] Network errors handled
- [ ] Authentication errors handled
- [ ] All errors logged

### UI Responsiveness
- [ ] Long operations don't freeze UI
- [ ] Progress indicators show
- [ ] Status bar updates during operations
- [ ] Background threads work correctly

---

## 8. Performance

### Startup
- [ ] Application starts quickly (< 3 seconds)
- [ ] No unnecessary operations on startup
- [ ] Downloads tab lazy loads correctly

### Operations
- [ ] Git status polling doesn't block UI
- [ ] File scanning doesn't block UI
- [ ] Search is debounced (no lag)
- [ ] Large file lists scroll smoothly

### Memory
- [ ] No memory leaks (check over time)
- [ ] RAM usage reasonable (< 200MB typical)

---

## 9. Logging

### Log File
- [ ] Log file created in `logs/app.log`
- [ ] Logs include timestamp, level, module, message
- [ ] Log rotation works (when > 5MB)
- [ ] Old logs kept (3 backups)

### Log Levels
- [ ] DEBUG logs detailed information
- [ ] INFO logs important events
- [ ] WARNING logs potential issues
- [ ] ERROR logs errors with stack traces
- [ ] CRITICAL logs fatal errors

### Console Output
- [ ] Warnings and errors shown in console
- [ ] Debug messages not shown in console

---

## 10. Edge Cases

### Empty States
- [ ] No projects shows empty state
- [ ] No downloads shows empty state
- [ ] Empty search shows all items

### Invalid Data
- [ ] Invalid config files handled
- [ ] Missing config files handled
- [ ] Corrupted data handled

### Network Issues
- [ ] Offline git operations handled
- [ ] Slow network handled
- [ ] Timeout errors handled

### Permissions
- [ ] Read-only files handled
- [ ] Protected folders handled
- [ ] Admin operations handled

---

## 11. Cross-Feature Testing

### Search Integration
- [ ] Search works in Projects tab
- [ ] Search works in Downloads tab
- [ ] Search clears when switching tabs

### Status Bar
- [ ] Status updates for all operations
- [ ] Git status shows in status bar
- [ ] RAM usage updates
- [ ] Settings button works

### Theme Consistency
- [ ] All components use theme colors
- [ ] Theme changes apply everywhere
- [ ] Dark/Light/System modes work

---

## 12. Regression Testing

### Previous Features
- [ ] All features from previous prompts still work
- [ ] No breaking changes
- [ ] Backward compatibility maintained

### Configuration
- [ ] Settings persist after restart
- [ ] Projects persist after restart
- [ ] Window state persists

---

## Known Issues / Notes

Document any issues found during testing:

1. 
2. 
3. 

---

## Test Environment

- **OS**: Windows 10/11
- **Python Version**: 
- **Date**: 
- **Tester**: 

---

## Test Results Summary

- **Total Tests**: 
- **Passed**: 
- **Failed**: 
- **Skipped**: 
- **Pass Rate**: %

**Overall Status**: [ ] Pass [ ] Fail [ ] Needs Work
