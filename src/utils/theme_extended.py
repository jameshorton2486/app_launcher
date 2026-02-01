"""
App Launcher Design System — Single Source of Truth
Global design tokens for visuals. NO MAGIC NUMBERS.
Phase 1: Visual system foundation.
"""

from dataclasses import dataclass
from typing import Dict

# ═══════════════════════════════════════════════════════════════════
# GLOBAL DESIGN TOKENS (MANDATORY)
# ═══════════════════════════════════════════════════════════════════

# Theme colors — dict for easy access THEME["bg"], THEME["primary"]
THEME: Dict[str, str] = {
    "bg": "#0f1115",
    "panel": "#161a22",
    "card": "#1c2230",
    "border": "#2a3142",
    "text_primary": "#e6e9ef",
    "text_secondary": "#a0a6b8",
    "text_muted": "#6b7280",
    "primary": "#1DB954",
    "secondary": "#4b5563",
    "info": "#3b82f6",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
}

# Spacing scale — NO MAGIC NUMBERS. All padding/margins reference this.
SPACING: Dict[str, int] = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 20,
    "xl": 32,
}


@dataclass(frozen=True)
class ThemeColors:
    """Immutable color definitions for the application theme."""

    # BACKGROUNDS (Layered depth system)
    bg_darkest: str = "#0a0c10"
    bg_dark: str = "#0f1115"
    bg_panel: str = "#161a22"
    bg_card: str = "#1c2230"
    bg_card_hover: str = "#242b3d"
    bg_input: str = "#1a1f2e"

    # BORDERS & DIVIDERS
    border_subtle: str = "#1e2433"
    border_default: str = "#2a3142"
    border_strong: str = "#3d4663"
    border_focus: str = "#1DB954"

    # TEXT HIERARCHY
    text_primary: str = "#e6e9ef"
    text_secondary: str = "#a0a6b8"
    text_muted: str = "#6b7280"
    text_disabled: str = "#4b5563"

    # SEMANTIC COLORS (Actions & Status)
    primary: str = "#1DB954"
    primary_hover: str = "#1ed760"
    primary_pressed: str = "#169c46"

    secondary: str = "#4b5563"
    secondary_hover: str = "#6b7280"
    secondary_pressed: str = "#374151"

    info: str = "#3b82f6"
    info_hover: str = "#60a5fa"

    success: str = "#22c55e"
    success_hover: str = "#4ade80"

    warning: str = "#f59e0b"
    warning_hover: str = "#fbbf24"

    danger: str = "#ef4444"
    danger_hover: str = "#f87171"
    danger_pressed: str = "#dc2626"

    # SPECIAL PURPOSE
    accent_purple: str = "#8b5cf6"
    accent_teal: str = "#14b8a6"
    accent_pink: str = "#ec4899"

    shadow: str = "#000000"
    overlay: str = "#000000"


# THEME dict is canonical (above). ThemeColors kept for backward compatibility.
ThemeColorsInstance = ThemeColors()


class _SpacingProxy:
    """Spacing scale — attribute access: SPACING.lg, SPACING.xl."""
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 20
    xl: int = 32
    xxl: int = 32   # alias for xl
    xxxl: int = 40  # extra-large


class Typography:
    """Font configurations."""
    family: str = "Segoe UI"
    size_xs: int = 11
    size_sm: int = 12
    size_md: int = 13
    size_lg: int = 15
    size_xl: int = 18
    size_xxl: int = 24
    weight_normal: str = "normal"
    weight_medium: str = "bold"
    weight_bold: str = "bold"


class ComponentStyles:
    """Pre-configured style dictionaries for common components."""

    @staticmethod
    def card_frame() -> Dict:
        """Card style: fg_color=card, corner_radius=12, border."""
        return {
            "fg_color": THEME["card"],
            "corner_radius": 12,
            "border_width": 1,
            "border_color": THEME["border"]
        }

    @staticmethod
    def panel_frame() -> Dict:
        """Side panel or navigation style."""
        return {
            "fg_color": THEME["panel"],
            "corner_radius": 0,
            "border_width": 0
        }

    @staticmethod
    def input_field() -> Dict:
        """Text entry field style."""
        return {
            "fg_color": THEME["card"],
            "border_color": THEME["border"],
            "border_width": 1,
            "corner_radius": 6,
            "text_color": THEME["text_primary"],
            "placeholder_text_color": THEME["text_muted"]
        }

    @staticmethod
    def primary_button() -> Dict:
        """Primary action button base style."""
        return {
            "fg_color": THEME["primary"],
            "text_color": "#ffffff",
            "corner_radius": 8
        }

    @staticmethod
    def secondary_button() -> Dict:
        """Secondary action button style."""
        return {
            "fg_color": THEME["secondary"],
            "text_color": THEME["text_primary"],
            "corner_radius": 8
        }

    @staticmethod
    def danger_button() -> Dict:
        """Destructive action button style (isolated only)."""
        return {
            "fg_color": THEME["danger"],
            "text_color": "#ffffff",
            "corner_radius": 8
        }


# Attribute access: SPACING.lg, SPACING.xl (for existing code)
Spacing = _SpacingProxy()
SPACING = Spacing
TYPOGRAPHY = Typography()
STYLES = ComponentStyles()


class ButtonColors:
    """Predefined button color palette for Button3D."""
    PRIMARY = "#1DB954"
    SECONDARY = "#4b5563"
    DANGER = "#ef4444"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"
    SUCCESS = "#22c55e"
    PURPLE = "#8b5cf6"
    TEAL = "#14b8a6"
