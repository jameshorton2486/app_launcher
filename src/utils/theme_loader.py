"""
Theme Loader System
Supports multiple theme variants with hot-swapping capability.

Current: Single dark theme (default)
Future: dark, darker, light, custom, high-contrast
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json


@dataclass
class ThemeVariant:
    """Defines a complete theme variant."""
    name: str
    display_name: str
    colors: Dict[str, Any]
    is_dark: bool = True

    def get_color(self, *path: str, default: str = "#ff00ff") -> str:
        """
        Get nested color value.

        Example:
            theme.get_color("background", "card")
        """
        value: Any = self.colors
        for key in path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value if isinstance(value, str) else default


class ThemeLoader:
    """
    Manages theme loading, switching, and access.

    Usage:
        loader = ThemeLoader()
        loader.load_theme("dark")

        current = loader.current_theme
        bg_color = current.get_color("background", "card")
    """

    _instance: Optional["ThemeLoader"] = None

    BUILT_IN_THEMES: Dict[str, Dict[str, Any]] = {
        "dark": {
            "display_name": "Dark",
            "is_dark": True,
            "colors": {
                "background": {
                    "darkest": "#0a0c10",
                    "dark": "#0f1115",
                    "panel": "#161a22",
                    "card": "#1c2230",
                    "card_hover": "#242b3d",
                    "input": "#1a1f2e",
                    "elevated": "#252d3d",
                },
                "border": {
                    "subtle": "#1e2433",
                    "default": "#2a3142",
                    "strong": "#3d4663",
                    "focus": "#1DB954",
                },
                "text": {
                    "primary": "#e6e9ef",
                    "secondary": "#a0a6b8",
                    "muted": "#6b7280",
                    "disabled": "#4b5563",
                },
                "semantic": {
                    "primary": "#1DB954",
                    "primary_hover": "#1ed760",
                    "secondary": "#4b5563",
                    "info": "#3b82f6",
                    "success": "#22c55e",
                    "warning": "#f59e0b",
                    "danger": "#ef4444",
                },
            },
        },
        "darker": {
            "display_name": "Darker (OLED)",
            "is_dark": True,
            "colors": {
                "background": {
                    "darkest": "#000000",
                    "dark": "#050507",
                    "panel": "#0a0c10",
                    "card": "#0f1115",
                    "card_hover": "#161a22",
                    "input": "#0d0f14",
                    "elevated": "#161a22",
                },
                "border": {
                    "subtle": "#151921",
                    "default": "#1e2433",
                    "strong": "#2a3142",
                    "focus": "#1DB954",
                },
                "text": {
                    "primary": "#e6e9ef",
                    "secondary": "#9ca3af",
                    "muted": "#6b7280",
                    "disabled": "#4b5563",
                },
                "semantic": {
                    "primary": "#1DB954",
                    "primary_hover": "#1ed760",
                    "secondary": "#374151",
                    "info": "#3b82f6",
                    "success": "#22c55e",
                    "warning": "#f59e0b",
                    "danger": "#ef4444",
                },
            },
        },
        "light": {
            "display_name": "Light",
            "is_dark": False,
            "colors": {
                "background": {
                    "darkest": "#f8fafc",
                    "dark": "#f1f5f9",
                    "panel": "#e2e8f0",
                    "card": "#ffffff",
                    "card_hover": "#f8fafc",
                    "input": "#ffffff",
                    "elevated": "#ffffff",
                },
                "border": {
                    "subtle": "#e2e8f0",
                    "default": "#cbd5e1",
                    "strong": "#94a3b8",
                    "focus": "#16a34a",
                },
                "text": {
                    "primary": "#0f172a",
                    "secondary": "#475569",
                    "muted": "#64748b",
                    "disabled": "#94a3b8",
                },
                "semantic": {
                    "primary": "#16a34a",
                    "primary_hover": "#15803d",
                    "secondary": "#64748b",
                    "info": "#2563eb",
                    "success": "#16a34a",
                    "warning": "#d97706",
                    "danger": "#dc2626",
                },
            },
        },
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._themes: Dict[str, ThemeVariant] = {}
        self._current_theme_name: str = "dark"
        self._listeners: list = []

        for name, config in self.BUILT_IN_THEMES.items():
            self._themes[name] = ThemeVariant(
                name=name,
                display_name=config["display_name"],
                colors=config["colors"],
                is_dark=config["is_dark"],
            )

        self._initialized = True

    @property
    def current_theme(self) -> ThemeVariant:
        """Get the current active theme."""
        return self._themes[self._current_theme_name]

    @property
    def current_theme_name(self) -> str:
        """Get current theme name."""
        return self._current_theme_name

    @property
    def available_themes(self) -> list:
        """List available theme names."""
        return list(self._themes.keys())

    def load_theme(self, name: str) -> bool:
        """
        Switch to a different theme.

        Args:
            name: Theme name ("dark", "darker", "light", or custom)
        """
        if name not in self._themes:
            return False

        if name == self._current_theme_name:
            return True

        self._current_theme_name = name
        self._notify_listeners()
        return True

    def add_listener(self, callback):
        """Register callback for theme changes."""
        self._listeners.append(callback)

    def remove_listener(self, callback):
        """Unregister theme change callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        """Notify all listeners of theme change."""
        for callback in self._listeners:
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Theme listener error: {e}")

    def load_custom_theme(self, path: Path) -> bool:
        """
        Load a custom theme from JSON file.

        Args:
            path: Path to theme JSON file
        """
        try:
            with open(path, "r", encoding="utf-8") as handle:
                config = json.load(handle)

            name = config.get("name", path.stem)
            self._themes[name] = ThemeVariant(
                name=name,
                display_name=config.get("display_name", name.title()),
                colors=config.get("colors", {}),
                is_dark=config.get("is_dark", True),
            )
            return True
        except Exception as e:
            print(f"Failed to load theme: {e}")
            return False


THEME_LOADER = ThemeLoader()


def get_color(*path: str, default: str = "#ff00ff") -> str:
    """Get color from current theme."""
    return THEME_LOADER.current_theme.get_color(*path, default=default)


__all__ = [
    "ThemeLoader",
    "ThemeVariant",
    "THEME_LOADER",
    "get_color",
]
