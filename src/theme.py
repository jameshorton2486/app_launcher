"""
Theme system for App Launcher
Defines color palette and CustomTkinter theme configuration
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

# Premium dark theme colors with vibrant accents (fallback if config load fails)
DEFAULT_COLORS = {
    "bg_base": "#0f0f12",
    "bg_primary": "#16161a",
    "bg_secondary": "#1e1e24",
    "bg_tertiary": "#26262e",
    "bg_hover": "#2e2e38",
    "bg_active": "#36363f",
    "accent_primary": "#6366f1",
    "accent_secondary": "#818cf8",
    "accent_muted": "#4f46e5",
    "text_primary": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_tertiary": "#71717a",
    "text_inverse": "#09090b",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "border_subtle": "#27272a",
    "border_default": "#3f3f46",
    "border_strong": "#52525b",
    # Vibrant category colors
    "color_cleanup": "#10b981",  # Green
    "color_memory": "#3b82f6",   # Blue
    "color_network": "#8b5cf6",  # Purple
    "color_repair": "#f59e0b",   # Orange
    "color_privacy": "#ec4899",  # Pink
    "color_security": "#ef4444", # Red
    "color_external": "#06b6d4", # Cyan
    "color_optimization": "#f97316", # Orange-red
}

DEFAULT_SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "2xl": 32,
    "3xl": 48,
}

DEFAULT_TYPOGRAPHY = {
    "font_family": "Segoe UI",
    "size_xs": 11,
    "size_sm": 12,
    "size_base": 14,
    "size_lg": 16,
    "size_xl": 18,
    "size_2xl": 24,
    "size_3xl": 30,
}


def _load_design_system() -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parents[1]
    design_path = base_dir / "config" / "design_system.json"
    if not design_path.exists():
        return {
            "colors": DEFAULT_COLORS,
            "spacing": DEFAULT_SPACING,
            "typography": DEFAULT_TYPOGRAPHY,
        }

    try:
        with design_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("design_system.json must be a JSON object")
        return data
    except Exception:
        return {
            "colors": DEFAULT_COLORS,
            "spacing": DEFAULT_SPACING,
            "typography": DEFAULT_TYPOGRAPHY,
        }


_design_system = _load_design_system()

# Color palette (loaded from design system)
COLORS = {
    **DEFAULT_COLORS,
    **(_design_system.get("colors") or {}),
}

# Legacy aliases for existing UI usage
COLORS.setdefault("accent_success", COLORS.get("success"))
COLORS.setdefault("accent_warning", COLORS.get("warning"))
COLORS.setdefault("accent_danger", COLORS.get("error"))
COLORS.setdefault("text_muted", COLORS.get("text_tertiary"))
COLORS.setdefault("border", COLORS.get("border_default"))

# Typography tokens
FONTS = {
    "family": (_design_system.get("typography") or {}).get("font_family", DEFAULT_TYPOGRAPHY["font_family"]),
    "size_xs": (_design_system.get("typography") or {}).get("size_xs", DEFAULT_TYPOGRAPHY["size_xs"]),
    "size_sm": (_design_system.get("typography") or {}).get("size_sm", DEFAULT_TYPOGRAPHY["size_sm"]),
    "size_base": (_design_system.get("typography") or {}).get("size_base", DEFAULT_TYPOGRAPHY["size_base"]),
    "size_lg": (_design_system.get("typography") or {}).get("size_lg", DEFAULT_TYPOGRAPHY["size_lg"]),
    "size_xl": (_design_system.get("typography") or {}).get("size_xl", DEFAULT_TYPOGRAPHY["size_xl"]),
    "size_2xl": (_design_system.get("typography") or {}).get("size_2xl", DEFAULT_TYPOGRAPHY["size_2xl"]),
    "size_3xl": (_design_system.get("typography") or {}).get("size_3xl", DEFAULT_TYPOGRAPHY["size_3xl"]),
}

# Spacing tokens
SPACING = {
    **DEFAULT_SPACING,
    **(_design_system.get("spacing") or {}),
}


def get_hover_color(base_color: str) -> str:
    """Return a slightly lighter hover color for a given hex color."""
    if not isinstance(base_color, str) or not base_color.startswith("#") or len(base_color) != 7:
        return base_color

    def clamp(value: int) -> int:
        return max(0, min(255, value))

    r = int(base_color[1:3], 16)
    g = int(base_color[3:5], 16)
    b = int(base_color[5:7], 16)

    lighten = 18
    r = clamp(r + lighten)
    g = clamp(g + lighten)
    b = clamp(b + lighten)

    return f"#{r:02x}{g:02x}{b:02x}"


def create_styled_button(parent, **kwargs):
    """Create a CTkButton with consistent styling defaults."""
    import customtkinter as ctk

    defaults = {
        "fg_color": COLORS["accent_primary"],
        "hover_color": get_hover_color(COLORS["accent_primary"]),
        "text_color": COLORS["text_primary"],
        "corner_radius": 8,
        "font": (FONTS["family"], FONTS["size_base"], "bold"),
        "border_width": 0,
    }
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)

def apply_theme(app, mode=None, accent_color=None):
    """
    Apply theme to CustomTkinter app
    
    Args:
        app: CustomTkinter CTk instance
        mode: Theme mode ('dark', 'light', 'system') - if None, reads from config
        accent_color: Accent color hex string - if None, reads from config
    """
    import customtkinter as ctk
    
    # Get mode from config if not provided
    if mode is None:
        try:
            from src.config_manager import ConfigManager
            config = ConfigManager()
            mode = config.get_setting('theme.mode', 'dark')
        except:
            mode = 'dark'
    
    # Set appearance mode (system mode is supported by CustomTkinter)
    ctk.set_appearance_mode(mode)
    
    # Set default color theme
    ctk.set_default_color_theme("blue")
    
    # Configure custom colors
    # Note: CustomTkinter uses a different color system, so we'll apply these
    # through widget-specific configurations
    
    # If accent color is provided, we could apply it, but CustomTkinter's
    # color system is limited, so we'll keep using the default blue theme
    # and apply custom colors through widget configurations
