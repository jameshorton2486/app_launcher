# App Architecture Split Assessment

## 1. Current State Analysis
1. Shared dependencies: both daily and power features depend on `config_manager`, `theme`, `tool_registry`, logging, and tray integration.
2. Shared UI infrastructure: sidebar navigation, status bar, toast notifications, search bar, and command palette are shared across all tabs.
3. Coupling points: Dashboard SmartMonitor references maintenance tool states; Settings configures paths used by all tools; `tool_usage.json` tracks runs across all categories.
4. Startup cost: tabs are lazy-loaded; power tools do not slow startup unless opened.

## 2. Arguments For Splitting
1. Reduced attack surface: daily users do not need admin-capable tools loaded.
2. Cleaner mental model: launcher for daily work, toolkit for maintenance sessions.
3. Smaller memory footprint for the always-running tray app.
4. Independent update cycles: maintenance tools change more frequently.
5. Enterprise deployability: launcher could ship without admin tools.

## 3. Arguments Against Splitting
1. Shared config complexity: two apps reading the same settings and usage data can conflict.
2. Doubled maintenance burden: two apps, two installers, two update paths.
3. Lost integration: health monitor is most useful when it can recommend actions in-context.
4. User friction: switching apps for related tasks adds overhead.
5. Current scale does not justify a split (62 tools, ~14.9K LOC).

## 4. Recommendation
Recommendation: stay as a single app for now, but prepare for modular extraction.

Preparation steps:
1. Keep services stateless and free of UI references.
2. Maintain a clean tab → service boundary (tabs call services only).
3. Allow tool registry to load tools from multiple JSON files.
4. Document which services require admin elevation.

Trigger conditions to revisit:
1. Tool count exceeds ~150.
2. Tray app idle memory exceeds ~200 MB.
3. Enterprise customers request a stripped-down launcher.
4. Maintenance tools require a different update cadence.

## 5. Naming Guidance (If Split Happens)
Launcher:
1. Keep “App Launcher” — it is accurate and established.
2. Identity: light, fast, always-on project hub.

Toolkit candidates:
1. SystemForge — “Precision tools for Windows maintenance and optimization.”
2. MaintenanceKit — “Professional system maintenance, organized and safe.”
3. TuneUp Studio — “Hands-on control for Windows performance and privacy.”
4. OpsBench — “Your workbench for system operations.”
5. SysCommand — “Direct, powerful Windows administration.”

Recommended: SystemForge.
Reason: enterprise tone, concise, communicates deliberate, advanced tooling without gimmick.
