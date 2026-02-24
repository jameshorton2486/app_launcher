# UI Acceptance Checklist

## 1. Token Compliance
1. All colors use `COLORS["key"]`; no hex literals except `#ffffff` and `#000000`.
2. All font sizes use `FONTS["size_*"]`; no raw integer font sizes.
3. All spacing uses `SPACING["key"]` or multiples of 4.
4. All `corner_radius` values are one of 0, 4, 6, 8, 12.
5. `fg_color` on frames/buttons uses a named `COLORS` key, never a raw hex.
6. Hover colors use `get_hover_color()` from `src/theme.py`.
7. No imports from `src/utils/theme_extended.py`.

## 2. Layout & Hierarchy
1. Primary actions use `COLORS["accent_primary"]`; secondary use `COLORS["secondary"]`; destructive use `COLORS["error"]`.
2. Only one primary action is visible per view or dialog.
3. Section headers use `FONTS["size_xl"]` or `FONTS["size_2xl"]`; body text uses `FONTS["size_base"]`; captions use `FONTS["size_sm"]` or `FONTS["size_xs"]`.
4. Content padding: outer frame uses `SPACING["xl"]`, inner sections use `SPACING["md"]` or `SPACING["lg"]`.
5. Scrollable content uses `CTkScrollableFrame`.
6. Dialogs/modals are centered on the parent window.

## 3. Controls & Interaction
1. Every clickable element has a visible hover state.
2. Buttons for long operations (>1s) show loading or disable themselves.
3. Destructive actions show a confirmation dialog.
4. Text entry fields include placeholder text.
5. Disabled controls are visually distinct via `COLORS["text_disabled"]` or `state="disabled"`.
6. Admin-required tools display a shield icon or `[Admin]` badge before click.

## 4. Feedback & Status
1. Every tool execution shows feedback: toast, status bar, or inline message.
2. Error messages include the failure reason and a next step.
3. Success messages are concise and auto-dismiss via toast (3s default).
4. Progress indicators appear for operations >2 seconds.
5. Status bar shows the most recent operation result.

## 5. Accessibility & Readability
1. Text contrast meets WCAG AA (example: `COLORS["text_primary"]` on `COLORS["bg_primary"]`).
2. No information is conveyed by color alone; include icon or text.
3. All interactive elements are reachable by Tab in dialogs.
4. Font sizes never go below `FONTS["size_xs"]` (11px).
5. Emoji icons are supplementary; every button has a text label.

## 6. Consistency
1. New tool buttons use `UtilityButton`.
2. New cards/panels use `CardFrame` or match its `corner_radius=12`, `border_width=1`, `border_color=COLORS["border_default"]`.
3. Toast notifications use `ToastManager`.
4. New tabs inherit from `CTkFrame`, accept `parent` and `config_manager`, and implement `refresh()`.
