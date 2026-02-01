"""
3D Button Component for App Launcher
Implements raised buttons with shadow effects and visual state feedback.
"""

import customtkinter as ctk
from typing import Optional, Tuple, Callable, Dict

# Add parent directory to path for imports
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.utils.theme_extended import ButtonColors
except ImportError:
    ButtonColors = type('ButtonColors', (), {
        'PRIMARY': '#1DB954',
        'SECONDARY': '#4b5563',
        'DANGER': '#ef4444',
        'WARNING': '#f59e0b',
        'INFO': '#3b82f6',
        'SUCCESS': '#22c55e',
        'PURPLE': '#8b5cf6',
        'TEAL': '#14b8a6',
    })


class Button3D(ctk.CTkFrame):
    """
    A CustomTkinter button with 3D raised appearance and shadow effect.

    Features:
        - Customizable button color with automatic shadow generation
        - Visual pressed/depressed state on click
        - Hover brightness adjustment
        - Automatic text color contrast calculation
    """

    def __init__(
        self,
        parent,
        text: str = "",
        icon: Optional[ctk.CTkImage] = None,
        bg_color: str = "#1DB954",
        text_color: Optional[str] = None,
        width: int = 140,
        height: int = 38,
        corner_radius: int = 8,
        command: Optional[Callable] = None,
        hover_brightness: float = 1.12,
        press_brightness: float = 0.88,
        shadow_offset: int = 3,
        font: Optional[Tuple] = None,
        state: str = "normal",
        **kwargs
    ):
        """
        Initialize Button3D.

        Args:
            parent: Parent widget
            text: Button label text
            icon: Optional CTkImage for button icon
            bg_color: Button face color (hex)
            text_color: Text color (auto-calculated if None)
            width: Button width in pixels
            height: Button height in pixels
            corner_radius: Border radius
            command: Callback function on click
            hover_brightness: Color multiplier on hover (>1 = lighter)
            press_brightness: Color multiplier on press (<1 = darker)
            shadow_offset: Shadow distance in pixels
            font: Font tuple (family, size, weight)
            state: "normal" or "disabled"
        """
        self._bg_color = bg_color
        self._text_color = text_color or self._calc_text_color(bg_color)
        self._width = width
        self._height = height
        self._corner_radius = corner_radius
        self._command = command
        self._hover_brightness = hover_brightness
        self._press_brightness = press_brightness
        self._shadow_offset = shadow_offset
        self._state = state
        self._is_hovered = False
        self._is_pressed = False

        self._hover_color = self._adjust_brightness(bg_color, hover_brightness)
        self._press_color = self._adjust_brightness(bg_color, press_brightness)
        self._disabled_color = self._desaturate(bg_color, 0.5)

        super().__init__(
            parent,
            fg_color="transparent",
            width=width + shadow_offset,
            height=height + shadow_offset,
            **kwargs
        )

        self._button = ctk.CTkButton(
            self,
            text=text,
            image=icon,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=bg_color,
            hover_color=self._hover_color,
            text_color=self._text_color,
            text_color_disabled=self._calc_text_color(self._disabled_color),
            font=font or ("Segoe UI", 13, "bold"),
            command=self._on_click,
            state=state
        )

        self._button.place(x=0, y=0)

        self._button.bind("<Enter>", self._on_enter)
        self._button.bind("<Leave>", self._on_leave)
        self._button.bind("<ButtonPress-1>", self._on_press)
        self._button.bind("<ButtonRelease-1>", self._on_release)

        self._update_shadow()

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color."""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    @staticmethod
    def _calc_luminance(hex_color: str) -> float:
        """Calculate relative luminance of a color."""
        r, g, b = Button3D._hex_to_rgb(hex_color)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255

    @staticmethod
    def _calc_text_color(bg_color: str) -> str:
        """Return white or black text based on background luminance."""
        return "#ffffff" if Button3D._calc_luminance(bg_color) < 0.5 else "#1a1a1a"

    @staticmethod
    def _adjust_brightness(hex_color: str, factor: float) -> str:
        """Adjust color brightness by factor (>1 = lighter, <1 = darker)."""
        r, g, b = Button3D._hex_to_rgb(hex_color)
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        return Button3D._rgb_to_hex((r, g, b))

    @staticmethod
    def _desaturate(hex_color: str, amount: float) -> str:
        """Reduce color saturation (0 = grayscale, 1 = original)."""
        r, g, b = Button3D._hex_to_rgb(hex_color)
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        r = int(r * amount + gray * (1 - amount))
        g = int(g * amount + gray * (1 - amount))
        b = int(b * amount + gray * (1 - amount))
        return Button3D._rgb_to_hex((r, g, b))

    def _update_shadow(self):
        """Update button position to simulate shadow/depth."""
        if self._state == "disabled":
            self._button.place(x=0, y=0)
        elif self._is_pressed:
            offset = self._shadow_offset
            self._button.place(x=offset, y=offset)
            self._button.configure(fg_color=self._press_color)
        else:
            self._button.place(x=0, y=0)
            if self._is_hovered:
                self._button.configure(fg_color=self._hover_color)
            else:
                self._button.configure(fg_color=self._bg_color)

    def _on_enter(self, event=None):
        if self._state == "normal":
            self._is_hovered = True
            self._update_shadow()

    def _on_leave(self, event=None):
        self._is_hovered = False
        self._is_pressed = False
        self._update_shadow()

    def _on_press(self, event=None):
        if self._state == "normal":
            self._is_pressed = True
            self._update_shadow()

    def _on_release(self, event=None):
        if self._state == "normal":
            self._is_pressed = False
            self._update_shadow()

    def _on_click(self):
        if self._command and self._state == "normal":
            self._command()

    def configure(self, **kwargs):
        """Configure button properties."""
        if "state" in kwargs:
            self._state = kwargs.pop("state")
            self._button.configure(state=self._state)
            self._update_shadow()

        if "text" in kwargs:
            self._button.configure(text=kwargs.pop("text"))

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "bg_color" in kwargs:
            self._bg_color = kwargs.pop("bg_color")
            self._hover_color = self._adjust_brightness(self._bg_color, self._hover_brightness)
            self._press_color = self._adjust_brightness(self._bg_color, self._press_brightness)
            self._button.configure(
                fg_color=self._bg_color,
                hover_color=self._hover_color
            )

        super().configure(**kwargs)

    def set_state(self, state: str):
        """Set button state ('normal' or 'disabled')."""
        self.configure(state=state)

    def invoke(self):
        """Programmatically invoke the button."""
        self._on_click()


BUTTON_COLORS = ButtonColors
