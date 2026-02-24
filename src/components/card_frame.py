"""
Elevated Card Frame Component
Provides consistent card styling with subtle depth.
"""

import customtkinter as ctk
from typing import Optional

from src.theme import COLORS, SPACING, get_hover_color


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
        pad = SPACING.get("lg", 16)
        self._padding = padding if padding is not None else pad

        bg_card = COLORS.get("bg_card", COLORS.get("bg_secondary"))
        bg_panel = COLORS.get("bg_panel", COLORS.get("bg_secondary"))
        bg = bg_card if elevated else bg_panel
        hover_bg = COLORS.get("bg_card_hover", get_hover_color(bg_card)) if elevated else bg_card

        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border", COLORS.get("border_default")),
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
        sm = SPACING.get("sm", 8)
        xs = SPACING.get("xs", 4)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=self._padding, pady=(self._padding, sm))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        if icon:
            icon_label = ctk.CTkLabel(title_row, image=icon, text="")
            icon_label.pack(side="left", padx=(0, sm))

        title_label = ctk.CTkLabel(
            title_row,
            text=title,
            font=("Segoe UI", 15, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left")

        if subtitle:
            subtitle_label = ctk.CTkLabel(
                header,
                text=subtitle,
                font=("Segoe UI", 12),
                text_color=COLORS["text_secondary"]
            )
            subtitle_label.pack(anchor="w", pady=(xs, 0))

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
                fg_color=COLORS.get("border", COLORS.get("border_default")),
                height=1
            )
            sep.pack(fill="x", padx=self._padding)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=self._padding, pady=self._padding)
        return footer
