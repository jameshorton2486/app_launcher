# Changelog

## [2.1.0] - 2026-02-06

### Fixed
- Fixed Privacy tools (Telemetry, Activity History, Advertising ID, Cortana) failing due to incorrect service mapping in tools.json
- Replaced 24 bare `except:` clauses with specific exception types
- Fixed silent exception swallowing in 6 locations — added debug logging
- Added missing icons for 6 tools

### Improved
- Added cooldown enforcement to 8 additional long-running/one-time tools
- Enhanced input validation for window position/size in config loading
- Better error messages when external tools aren't found (includes download URL)
- Added confirmation dialogs for all high-risk tools
- Added restart-required visual indicators on tool buttons
- Added keyboard shortcut hints to sidebar navigation
- Cleaned up redundant sys.path manipulation from all modules

### Documentation
- Updated doc files with correct tool counts and tab counts
- Added CHANGELOG.md
