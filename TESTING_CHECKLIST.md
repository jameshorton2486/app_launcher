# Testing Checklist

## Phase 6: Polish & Testing

### Core Functionality
- [ ] Application launches without errors
- [ ] All tabs load correctly (lazy loading works)
- [ ] Search bar filters projects correctly
- [ ] Status bar displays information correctly

### Projects Tab
- [ ] All projects display as cards
- [ ] Project cards show correct information (icon, name, description, git status)
- [ ] Launch button works for all project types (python, npm, powershell, bat, exe)
- [ ] Folder button opens project directory
- [ ] Terminal button opens PowerShell in project directory
- [ ] IDE dropdown opens projects in Cursor, VS Code, PyCharm
- [ ] Claude button opens Claude project URL (if configured)
- [ ] GitHub button opens repository URL (if configured)
- [ ] Favorite toggle works and persists
- [ ] Git status indicators show correctly (🟢 clean, 🟡 uncommitted, 🔴 needs pull)
- [ ] Git pull works from context menu
- [ ] Git push works from context menu
- [ ] Add project dialog works (all fields validate)
- [ ] Edit project dialog works
- [ ] Remove project works
- [ ] Search filters projects by name, description, language
- [ ] Sort options work (A-Z, Favorites First, Language)
- [ ] Git status polling works (updates every 60s)
- [ ] Refresh Git Status button works
- [ ] Git Pull All button works

### Downloads Tab
- [ ] Downloads tab loads (placeholder for Phase 3)

### Utilities Tab
- [ ] All utility buttons display correctly
- [ ] Empty Recycle Bin works
- [ ] Clear Temp Files works and shows MB freed
- [ ] Flush DNS works
- [ ] Clear Prefetch works (with admin elevation)
- [ ] Clear RAM Standby works
- [ ] Disk Cleanup launches
- [ ] Defrag/Optimize works
- [ ] Restart Explorer works
- [ ] Open CCleaner works (if path configured)
- [ ] Open Wise Memory works (if path configured)
- [ ] Reset MS Store works
- [ ] Reset TCP/IP works (with admin elevation)
- [ ] Release/Renew IP works
- [ ] Net Stats displays
- [ ] Clear Update Cache works (with admin elevation)
- [ ] Pause Updates works
- [ ] Visual feedback works (loading, success, error states)

### System Integration
- [ ] Tray icon appears on start
- [ ] Tray icon menu works (Open, Quick Launch, Utilities, Settings, Exit)
- [ ] Double-click tray icon restores window
- [ ] App minimizes to tray on close (when enabled)
- [ ] Global hotkey (Win+Shift+L) toggles window
- [ ] Startup with Windows works (when enabled)
- [ ] App starts minimized (when enabled)

### Settings Dialog
- [ ] Settings dialog opens from tray menu
- [ ] All checkboxes work (Start with Windows, Minimize to tray, Start minimized)
- [ ] Hotkey field displays current hotkey
- [ ] Path fields work (Downloads, Screenshots, External Tools)
- [ ] Browse buttons work for all path fields
- [ ] Theme mode dropdown works
- [ ] Color picker works for accent color
- [ ] Save button saves all settings
- [ ] Cancel button discards changes
- [ ] Settings persist after restart

### Error Handling
- [ ] Invalid project paths show error messages
- [ ] Missing external tools show appropriate messages
- [ ] Git operations handle errors gracefully
- [ ] File operations handle permission errors
- [ ] Network operations handle timeouts
- [ ] All errors are logged to logs/app.log
- [ ] No crashes occur during normal operation
- [ ] Status bar shows error messages

### Performance
- [ ] App starts quickly (< 3 seconds)
- [ ] Tabs load on demand (lazy loading)
- [ ] Git status polling doesn't block UI
- [ ] Long operations show progress/feedback
- [ ] No memory leaks after extended use (test for 1+ hour)
- [ ] UI remains responsive during operations

### Edge Cases
- [ ] App handles missing config files gracefully
- [ ] App handles corrupted JSON files gracefully
- [ ] App handles network disconnection during git operations
- [ ] App handles missing Python/Node executables
- [ ] App handles projects with invalid launch scripts
- [ ] App handles very long project names/descriptions
- [ ] App handles many projects (50+) without performance issues

### Documentation
- [ ] README.md is up to date
- [ ] All configuration options are documented
- [ ] Installation instructions are clear
- [ ] Troubleshooting section exists

## Notes
- Test on clean Windows 11 installation
- Test with and without admin privileges
- Test with various project types
- Test with missing external tools
- Monitor memory usage over time
- Check log files for errors
