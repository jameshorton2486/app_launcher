"""
Command Palette Component
Quick access to tools via searchable modal
"""

import customtkinter as ctk
import tkinter as tk
import difflib
from typing import List, Dict

from src.theme import COLORS
from src.utils.tool_registry import ToolRegistry
from src.utils.constants import TOOLS_FILE


class CommandPalette(ctk.CTkToplevel):
    """Command palette modal for tool search and execution."""

    recent_tools: List[str] = []

    def __init__(self, parent, config_manager):
        super().__init__(parent)

        self.parent = parent
        self.config_manager = config_manager
        self.tool_registry = ToolRegistry()
        self.tool_registry.load_tools(TOOLS_FILE)
        self.results: List[Dict] = []
        self.selected_index = 0

        self._setup_window()
        self._build_ui()
        self._load_results("")

    def _setup_window(self):
        self.title("Command Palette")
        self.geometry("800x500")
        self.configure(fg_color=COLORS['bg_base'])
        self.attributes("-topmost", True)
        self.grab_set()

        # Dim background
        try:
            self.attributes("-alpha", 0.97)
        except Exception:
            pass

        self.bind("<Escape>", lambda e: self.close())

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'], corner_radius=16)
        container.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            container,
            textvariable=self.search_var,
            font=('Segoe UI', 14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_subtle']
        )
        self.search_entry.pack(fill='x', padx=16, pady=(16, 10))
        self.search_entry.focus_set()
        self.search_var.trace_add("write", lambda *_: self._on_search())

        self.results_frame = ctk.CTkScrollableFrame(
            container,
            fg_color='transparent',
            corner_radius=0,
            height=320
        )
        self.results_frame.pack(fill='both', expand=True, padx=8, pady=(0, 10))

        self.bind("<Up>", lambda e: self._move_selection(-1))
        self.bind("<Down>", lambda e: self._move_selection(1))
        self.bind("<Return>", lambda e: self._execute_selected())

    def _on_search(self):
        query = self.search_var.get().strip()
        self._load_results(query)

    def _load_results(self, query: str):
        for child in self.results_frame.winfo_children():
            child.destroy()

        if not query:
            self.results = [self.tool_registry.get_tool_by_id(tid) for tid in self.recent_tools]
            self.results = [item for item in self.results if item]
            if not self.results:
                self.results = self.tool_registry.search_tools("")
        else:
            self.results = self._fuzzy_search(query)

        self.selected_index = 0
        for idx, tool in enumerate(self.results[:30]):
            self._add_result_row(tool, idx)

        self._highlight_selected()

    def _fuzzy_search(self, query: str) -> List[Dict]:
        candidates = self.tool_registry.search_tools("")
        scored = []
        for tool in candidates:
            text = f"{tool.get('title', '')} {tool.get('description', '')} {' '.join(tool.get('tags', []))}".lower()
            score = difflib.SequenceMatcher(None, query.lower(), text).ratio()
            if query.lower() in text:
                score += 0.5
            scored.append((score, tool))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [tool for score, tool in scored if score > 0.2]

    def _add_result_row(self, tool: Dict, index: int):
        row = ctk.CTkFrame(self.results_frame, fg_color='transparent', corner_radius=8)
        row.pack(fill='x', padx=8, pady=4)

        icon = tool.get("icon", "•")
        title = tool.get("title", "Untitled")
        section = tool.get("section_title", tool.get("section", ""))
        description = tool.get("description", "")

        icon_label = ctk.CTkLabel(
            row,
            text=icon,
            font=('Segoe UI', 16),
            width=32
        )
        icon_label.pack(side='left', padx=(10, 8))

        text_frame = ctk.CTkFrame(row, fg_color='transparent')
        text_frame.pack(side='left', fill='x', expand=True)

        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(fill='x')

        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        desc_label.pack(fill='x')

        section_label = ctk.CTkLabel(
            row,
            text=section,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        section_label.pack(side='right', padx=10)

        row.bind("<Button-1>", lambda e, i=index: self._execute_selected(i))
        for widget in row.winfo_children():
            widget.bind("<Button-1>", lambda e, i=index: self._execute_selected(i))

    def _highlight_selected(self):
        for idx, row in enumerate(self.results_frame.winfo_children()):
            if idx == self.selected_index:
                row.configure(fg_color=COLORS['bg_hover'])
            else:
                row.configure(fg_color='transparent')

    def _move_selection(self, delta: int):
        if not self.results:
            return
        self.selected_index = max(0, min(self.selected_index + delta, len(self.results) - 1))
        self._highlight_selected()

    def _execute_selected(self, index: int | None = None):
        if not self.results:
            return
        idx = index if index is not None else self.selected_index
        if idx < 0 or idx >= len(self.results):
            return
        tool = self.results[idx]
        tool_id = tool.get("id")
        if tool_id:
            self.tool_registry.execute_tool(tool_id, self.config_manager)
            self._add_recent(tool_id)
        self.close()

    def _add_recent(self, tool_id: str):
        if tool_id in self.recent_tools:
            self.recent_tools.remove(tool_id)
        self.recent_tools.insert(0, tool_id)
        self.recent_tools = self.recent_tools[:10]

    def close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
