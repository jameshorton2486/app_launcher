"""
Toast Notifications
"""

import customtkinter as ctk
import tkinter as tk

from src.theme import COLORS


class ToastManager:
    """Static toast notification manager."""

    _root = None
    _toasts = []

    @classmethod
    def set_root(cls, root):
        cls._root = root

    @classmethod
    def show_success(cls, title: str, message: str, duration: int = 3000):
        cls._show("success", title, message, duration)

    @classmethod
    def show_error(cls, title: str, message: str, duration: int = 3000):
        cls._show("error", title, message, duration)

    @classmethod
    def show_warning(cls, title: str, message: str, duration: int = 3000):
        cls._show("warning", title, message, duration)

    @classmethod
    def show_info(cls, title: str, message: str, duration: int = 3000):
        cls._show("info", title, message, duration)

    @classmethod
    def _show(cls, toast_type: str, title: str, message: str, duration: int):
        if not cls._root:
            return

        cls._root.after(0, lambda: cls._create_toast(toast_type, title, message, duration))

    @classmethod
    def _create_toast(cls, toast_type: str, title: str, message: str, duration: int):
        colors = {
            "success": (COLORS['success'], "✓"),
            "error": (COLORS['error'], "✗"),
            "warning": (COLORS['warning'], "⚠"),
            "info": (COLORS['accent_secondary'], "ℹ"),
        }
        accent, icon = colors.get(toast_type, (COLORS['accent_secondary'], "ℹ"))

        toast = ctk.CTkToplevel(cls._root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=COLORS['bg_secondary'])

        container = ctk.CTkFrame(
            toast,
            fg_color=COLORS['bg_secondary'],
            border_width=1,
            border_color=COLORS['border_subtle'],
            corner_radius=12
        )
        container.pack(fill='both', expand=True)

        header = ctk.CTkFrame(container, fg_color='transparent')
        header.pack(fill='x', padx=12, pady=(10, 4))

        icon_label = ctk.CTkLabel(
            header,
            text=icon,
            font=('Segoe UI', 14, 'bold'),
            text_color=accent,
            width=20
        )
        icon_label.pack(side='left')

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(side='left', padx=(6, 0), fill='x', expand=True)

        body = ctk.CTkLabel(
            container,
            text=message,
            font=('Segoe UI', 11),
            text_color=COLORS['text_secondary'],
            anchor='w',
            wraplength=260,
            justify='left'
        )
        body.pack(fill='x', padx=12, pady=(0, 10))

        toast.bind("<Button-1>", lambda e: cls._dismiss_toast(toast))
        for widget in (container, header, icon_label, title_label, body):
            widget.bind("<Button-1>", lambda e: cls._dismiss_toast(toast))

        cls._toasts.append(toast)
        cls._position_toasts()
        toast.after(duration, lambda: cls._dismiss_toast(toast))

    @classmethod
    def _dismiss_toast(cls, toast):
        try:
            if toast in cls._toasts:
                cls._toasts.remove(toast)
            toast.destroy()
            cls._position_toasts()
        except Exception:
            pass

    @classmethod
    def _position_toasts(cls):
        if not cls._root:
            return
        screen_width = cls._root.winfo_screenwidth()
        screen_height = cls._root.winfo_screenheight()

        padding = 20
        width = 300
        height = 90
        for index, toast in enumerate(cls._toasts):
            x = screen_width - width - padding
            y = screen_height - ((height + 10) * (index + 1)) - padding
            toast.geometry(f"{width}x{height}+{x}+{y}")
