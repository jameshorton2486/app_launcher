"""
Quick Cleanup Runner
Runs a sequence of cleanup tools with progress UI.
"""

from __future__ import annotations

import threading
from typing import List, Tuple
import re

import customtkinter as ctk

from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS
from src.utils.tool_registry import ToolRegistry
from src.utils.tool_usage import ToolUsageStore
from src.utils.constants import TOOLS_FILE

try:
    from src.components.toast import ToastManager
except Exception:
    ToastManager = None


class QuickCleanupRunner:
    """Run a sequence of cleanup tools with progress feedback."""

    TOOL_SEQUENCE: List[Tuple[str, str]] = [
        ("empty_recycle_bin", "Empty Recycle Bin"),
        ("clear_temp_files", "Clear Temp Files"),
        ("clear_browser_cache", "Clear Browser Cache"),
        ("flush_dns", "Flush DNS"),
        ("clear_ram_standby", "Clear RAM Standby"),
    ]

    def __init__(self, parent, config_manager, tool_registry: ToolRegistry):
        self.parent = parent
        self.config_manager = config_manager
        self.tool_registry = tool_registry
        self.usage_store = ToolUsageStore()

        self._cancelled = False
        self._dialog = None
        self._rows = {}
        self._progress = None
        self._total_label = None

    def start(self):
        self._show_dialog()
        thread = threading.Thread(target=self._run_sequence, daemon=True)
        thread.start()

    def _show_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Quick Cleanup")
        dialog.geometry("520x360")
        dialog.configure(fg_color=COLORS['bg_primary'])
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        self._dialog = dialog

        title = ctk.CTkLabel(
            dialog,
            text="🚀 Quick Cleanup in Progress",
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_primary']
        )
        title.pack(pady=(16, 10))

        list_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_secondary'], corner_radius=12)
        list_frame.pack(fill='x', padx=16, pady=(0, 12))

        for tool_id, label in self.TOOL_SEQUENCE:
            row = ctk.CTkFrame(list_frame, fg_color='transparent')
            row.pack(fill='x', padx=12, pady=6)
            name_label = ctk.CTkLabel(
                row,
                text=label,
                font=('Segoe UI', 12, 'bold'),
                text_color=COLORS['text_primary'],
                anchor='w'
            )
            name_label.pack(side='left')
            status_label = ctk.CTkLabel(
                row,
                text="Pending",
                font=('Segoe UI', 11),
                text_color=COLORS['text_secondary'],
                anchor='e'
            )
            status_label.pack(side='right')
            self._rows[tool_id] = status_label

        self._progress = ctk.CTkProgressBar(
            dialog,
            height=8,
            corner_radius=8,
            fg_color=COLORS['bg_tertiary'],
            progress_color=COLORS['accent_primary']
        )
        self._progress.pack(fill='x', padx=20, pady=(0, 8))
        self._progress.set(0)

        self._total_label = ctk.CTkLabel(
            dialog,
            text="Total space freed: 0.0 GB",
            font=('Segoe UI', 11),
            text_color=COLORS['text_secondary']
        )
        self._total_label.pack(pady=(0, 6))

        cancel_btn = Button3D(
            dialog,
            text="Cancel",
            width=120,
            height=35,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self._cancel
        )
        cancel_btn.pack(pady=(0, 12))

    def _run_sequence(self):
        total_freed_mb = 0.0
        total_steps = len(self.TOOL_SEQUENCE)

        for index, (tool_id, _) in enumerate(self.TOOL_SEQUENCE, start=1):
            if self._cancelled:
                break

            self._update_row(tool_id, "Running...")
            success, message = self.tool_registry.execute_tool(tool_id, self.config_manager)
            if not success:
                self._update_row(tool_id, "Failed")
            else:
                self._update_row(tool_id, message)
            total_freed_mb += self._parse_freed_mb(message)

            if self._progress:
                self._progress.set(index / total_steps)

            if self._total_label:
                total_gb = total_freed_mb / 1024
                self._total_label.configure(text=f"Total space freed: {total_gb:.1f} GB")

        if not self._cancelled:
            self.usage_store.mark_full_cleanup()
            self._show_summary_toast(total_freed_mb)

        self._close_dialog()

    def _update_row(self, tool_id: str, message: str):
        if not self._dialog:
            return

        def _update():
            label = self._rows.get(tool_id)
            if label:
                label.configure(text=message)

        self._dialog.after(0, _update)

    def _close_dialog(self):
        if not self._dialog:
            return

        def _close():
            try:
                self._dialog.destroy()
            except Exception:
                pass

        self._dialog.after(0, _close)

    def _cancel(self):
        self._cancelled = True

    def _show_summary_toast(self, total_freed_mb: float):
        if not ToastManager:
            return
        if self.config_manager and not self.config_manager.get_setting('ui.show_toasts', True):
            return
        total_gb = total_freed_mb / 1024
        ToastManager.show_success(
            "Quick Cleanup complete!",
            f"Freed {total_gb:.1f} GB and optimized system memory."
        )

    @staticmethod
    def _parse_freed_mb(message: str) -> float:
        if not message:
            return 0.0
        match = re.search(r"([\d\.]+)\s*(GB|MB)", message, re.IGNORECASE)
        if not match:
            return 0.0
        value = float(match.group(1))
        unit = match.group(2).upper()
        return value * 1024 if unit == "GB" else value
