# Plugin System Roadmap (Design Only)

## 1. Definition
A plugin in this app is an extension that adds new tools, services, or tabs without modifying core files. The simplest model aligns with the existing JSON-driven tool registry: a plugin is either a tool definition JSON file, or a Python service module referenced by tool definitions, or a UI tab module.

## 2. Three Plugin Tiers
1. Tier 1 — Tool Plugins (JSON-only)
Add a tool entry in `config/tools.json` or a new JSON file under `plugins/tools/`.
The tool points to an existing service + method already in the app.
No code required.
Example: new external tool launcher or a cleanup shortcut.
2. Tier 2 — Service Plugins (Python module)
Drop a Python file into `plugins/services/`.
Expose methods that `tool_registry.py` can discover and call.
Return `(success: bool, message: str)` to match existing convention.
Example: custom backup utility or Docker manager.
3. Tier 3 — Tab Plugins (UI extension)
Provide a CustomTkinter frame in `plugins/tabs/`.
Registered as an additional sidebar tab below built-in tabs.
Access to `config_manager` and services only, no `app.py` internals.
Example: monitoring dashboard, notes panel.

## 3. What Plugins Must NEVER Touch
1. `src/app.py` internal state (window geometry, tab switching, tray)
2. `src/theme.py` tokens (plugins consume, never modify)
3. Other plugins' data or state
4. Settings that affect core app behavior
5. System tray icon or global hotkey registration

## 4. Directory Structure
```
plugins/
tools/
services/
tabs/
disabled/
```

## 5. Discovery Model
1. On startup, scan `plugins/` directories
2. Tier 1: merge JSON files into the tool registry
3. Tier 2: import service modules and register by conventional name
4. Tier 3: import tab modules and add to sidebar below built-ins
5. No hot-reloading; restart required after changes

## 6. Why This Is Not Implemented Yet
1. Current tool count (62) does not justify the complexity
2. JSON-driven registry already provides extensibility for power users
3. Plugin sandboxing and error isolation are hard problems to solve prematurely
4. The architecture should stabilize before exposing extension points

## 7. Trigger Conditions
1. Tool count exceeds ~100 and custom tools become common
2. Multiple users request the ability to add their own utilities
3. A new category of tools emerges that does not fit existing sections
