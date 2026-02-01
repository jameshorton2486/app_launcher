"""
Elevated Card Frame Component
Provides consistent card styling with subtle depth.
"""

import customtkinter as ctk
from typing import Optional

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.utils.theme_extended import THEME, SPACING
except ImportError:
    THEME = type('THEME', (), {
        'bg_card': '#1c2230', 'bg_panel': '#161a22', 'bg_card_hover': '#242b3d',
        'border_default': '#2a3142', 'border_subtle': '#1e2433',
        'text_primary': '#e6e9ef', 'text_secondary': '#a0a6b8',
    })()
    SPACING = type('SPACING', (), {'xs': 4, 'sm': 8, 'lg': 16})()


class CardFrame(ctk.CTkFrame):
    """
    An elevated card container with consistent styling.

    Features:
        - Subtle border for depth perception
        - Consistent corner radius
        - Hover state option
        - Header/content layout helpers
    """

    def __init__(
        self,
        parent,
        hover_effect: bool = False,
        elevated: bool = True,
        padding: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize CardFrame.

        Args:
            parent: Parent widget
            hover_effect: Enable hover color change
            elevated: Use elevated (lighter) background
            padding: Internal padding (uses SPACING.lg if None)
        """
        self._hover_effect = hover_effect
        self._elevated = elevated
        self._padding = padding if padding is not None else SPACING.lg

        bg = THEME.bg_card if elevated else THEME.bg_panel
        hover_bg = THEME.bg_card_hover if elevated else THEME.bg_card

        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=12,
            border_width=1,
            border_color=THEME.border_default,
            **kwargs
        )

        self._bg_color = bg
        self._hover_bg = hover_bg

        if hover_effect:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        self.configure(fg_color=self._hover_bg)

    def _on_leave(self, event=None):
        self.configure(fg_color=self._bg_color)

    def add_header(
        self,
        title: str,
        subtitle: Optional[str] = None,
        icon: Optional[ctk.CTkImage] = None
    ) -> ctk.CTkFrame:
        """
        Add a header section to the card.

        Returns the header frame for additional customization.
        """
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=self._padding, pady=(self._padding, SPACING.sm))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        if icon:
            icon_label = ctk.CTkLabel(title_row, image=icon, text="")
            icon_label.pack(side="left", padx=(0, SPACING.sm))

        title_label = ctk.CTkLabel(
            title_row,
            text=title,
            font=("Segoe UI", 15, "bold"),
            text_color=THEME.text_primary
        )
        title_label.pack(side="left")

        if subtitle:
            subtitle_label = ctk.CTkLabel(
                header,
                text=subtitle,
                font=("Segoe UI", 12),
                text_color=THEME.text_secondary
            )
            subtitle_label.pack(anchor="w", pady=(SPACING.xs, 0))

        return header

    def add_content(self) -> ctk.CTkFrame:
        """
        Add a content section to the card.

        Returns the content frame for adding widgets.
        """
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self._padding, pady=(0, self._padding))
        return content

    def add_footer(self, separator: bool = True) -> ctk.CTkFrame:
        """
        Add a footer section to the card.

        Args:
            separator: Show top border separator

        Returns the footer frame.
        """
        if separator:
            sep = ctk.CTkFrame(
                self,
                fg_color=THEME.border_subtle,
                height=1
            )
            sep.pack(fill="x", padx=self._padding)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=self._padding, pady=self._padding)
        return footer
