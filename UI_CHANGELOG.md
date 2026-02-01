# UI Overhaul Changelog (v2.1)

## New Components

| Component | Description |
|-----------|-------------|
| **Button3D** | Raised buttons with shadow, hover brightening, press “push” effect, auto text contrast, disabled desaturation. |
| **CardFrame** | Elevated card container: `fg_color=THEME["card"]`, `corner_radius=12`, border; optional hover; `add_header` / `add_content` / `add_footer`. |
| **StatusBar** | Color-coded status: `StatusType` enum (READY, INFO, SUCCESS, WARNING, ERROR, LOADING); `set_ready()`, `set_success()`, `set_error()`, `set_warning()`, `set_loading()`. |

## Design System

- **Tokens**: `config/design_system.json` — background, border, text, semantic, accent colors; spacing (xs–xxxl); typography (family, size, weight); corner_radius; elevation.
- **Runtime**: `src/utils/theme_extended.py` — `THEME` dict, `SPACING` (attribute + dict), `ButtonColors`, `ComponentStyles`.
- **Usage**: Replace magic numbers with `SPACING.lg`, `THEME["card"]`; primary actions use `Button3D` with `BUTTON_COLORS.PRIMARY` etc.

## Visual Improvements

- Premium dark palette (Spotify/Discord-inspired).
- Clear hierarchy: titles → body → muted; status bar severity colors.
- Navigation: larger click targets (48px), active tab highlight, consistent padding.
- Empty states: muted copy + CTA on Projects, Downloads, Dashboard, Maintenance, Optimization.
- Loading: `UtilityButton` spinner + status text; status bar `set_loading()`; no double-run on tools.

## Fixes

- **Pystray**: All tray `MenuItem` callbacks use factory functions `(icon, item) -> None`; no lambdas; queue-based callbacks for Tkinter thread safety.
- **Git status callback**: Project list uses closure over queue only (no `self` in background thread).
- **Status bar RAM**: RAM updates via queue + main-thread polling (no `after()` from worker thread).

## Phase 3 Optional Improvements

- **Animation timing**: `src/utils/animation.py` — `TIMING`, `EASING`, `HoverDebouncer`, `delayed_call`, `cancel_delayed_call`. Button3D uses `HoverDebouncer` for hover flicker prevention.
- **Button3D replacements**: Maintenance (Run Quick Cleanup, Help, Close), Downloads (Move Selected, Delete Selected), App (health dialog buttons, shortcuts Close), Dashboard (Scan, Run Now).
- **UI checker**: `scripts/ui_checker.py` — run `python scripts/ui_checker.py` to validate design system compliance (hardcoded colors, CTkButton candidates, required components).

## Verification Checklist

- [x] App launches without tray/thread errors
- [x] All 74 tools and shortcuts (Ctrl+1–5, Ctrl+K, F1) work
- [x] Button3D used for primary actions in tabs and dialogs
- [x] Cards and spacing use design tokens
- [x] Status bar supports Ready / Success / Error / Warning / Loading
