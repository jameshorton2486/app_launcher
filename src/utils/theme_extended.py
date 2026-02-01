"""
App Launcher Extended Theme System
Centralized color palette and styling constants for premium UI.
Complements src.theme (COLORS) - use THEME, SPACING, STYLES for new components.
"""

from dataclasses import dataclass
from typing import Dict


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


# Global theme instance
THEME = ThemeColors()


class Spacing:
    """Consistent spacing values based on 8px grid."""
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 20
    xxl: int = 24
    xxxl: int = 32


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
        """Elevated card container style."""
        return {
            "fg_color": THEME.bg_card,
            "corner_radius": 12,
            "border_width": 1,
            "border_color": THEME.border_default
        }

    @staticmethod
    def panel_frame() -> Dict:
        """Side panel or navigation style."""
        return {
            "fg_color": THEME.bg_panel,
            "corner_radius": 0,
            "border_width": 0
        }

    @staticmethod
    def input_field() -> Dict:
        """Text entry field style."""
        return {
            "fg_color": THEME.bg_input,
            "border_color": THEME.border_default,
            "border_width": 1,
            "corner_radius": 6,
            "text_color": THEME.text_primary,
            "placeholder_text_color": THEME.text_muted
        }

    @staticmethod
    def primary_button() -> Dict:
        """Primary action button base style."""
        return {
            "fg_color": THEME.primary,
            "hover_color": THEME.primary_hover,
            "text_color": "#ffffff",
            "corner_radius": 8
        }

    @staticmethod
    def secondary_button() -> Dict:
        """Secondary action button style."""
        return {
            "fg_color": THEME.secondary,
            "hover_color": THEME.secondary_hover,
            "text_color": THEME.text_primary,
            "corner_radius": 8
        }

    @staticmethod
    def danger_button() -> Dict:
        """Destructive action button style."""
        return {
            "fg_color": THEME.danger,
            "hover_color": THEME.danger_hover,
            "text_color": "#ffffff",
            "corner_radius": 8
        }


SPACING = Spacing()
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
