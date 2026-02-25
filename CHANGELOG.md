# Changelog

## [2.2.0] - 2026-02-25

### Changed
- Refactored `config/tools.json` through phases 0-9 for a cleaner, task-focused tool catalog.
- Reduced launcher-visible tools to 29 core actions across 7 sections.
- Simplified Maintenance and Optimization layouts to prioritize frequent workflows.

### Added
- Added plugin architecture support for external tools in the registry flow.
- Added packaging-safe resource path resolution to improve PyInstaller/runtime compatibility.
- Added subprocess launch path validation hardening for safer external command execution.

### Fixed
- Corrected registry integrity issues after refactor by validating IDs and section indexing.
- Trimmed optimization/performance tools to dev-focused controls only, removing redundant toggles.

### Tests
- Added regression tests for refactor toolset shape and performance section membership.

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
