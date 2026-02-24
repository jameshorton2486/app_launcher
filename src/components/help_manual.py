"""
Help Manual Component
Comprehensive manual showing all tools with descriptions and usage metadata.
"""

from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from typing import List, Dict, Any

from src.theme import COLORS
from src.utils.constants import TOOLS_FILE
from src.utils.tool_registry import ToolRegistry
from src.utils.tool_usage import ToolUsageStore


class HelpManual(ctk.CTkToplevel):
    """
    Comprehensive help manual showing all tools with descriptions.
    Features alphabetical and category-based views.
    """

    def __init__(self, parent, allowed_tabs: List[str] | None = None):
        super().__init__(parent)

        config_manager = getattr(parent, "config_manager", None)
        self.professional_mode = bool(
            config_manager.get_setting("ui.professional_mode", False)
        ) if config_manager else False

        self.tool_registry = ToolRegistry()
        self.tool_registry.load_tools(TOOLS_FILE)
        self.usage_store = ToolUsageStore()
        self.allowed_tabs = [tab.lower() for tab in allowed_tabs] if allowed_tabs else None

        self.all_tools: List[Dict[str, Any]] = self._load_tools()
        self.filtered_tools: List[Dict[str, Any]] = list(self.all_tools)

        self._setup_window(parent)
        self._build_ui()
        self._render_tools()

    def _setup_window(self, parent):
        self.title("App Launcher Help Manual")
        self.geometry("800x600")
        self.configure(fg_color=COLORS['bg_primary'])
        self.transient(parent)
        self.grab_set()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=20, pady=(16, 10))

        title = ctk.CTkLabel(
            header,
            text="App Launcher Help Manual",
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(side='left')

        controls = ctk.CTkFrame(self, fg_color='transparent')
        controls.pack(fill='x', padx=20, pady=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            controls,
            textvariable=self.search_var,
            placeholder_text="Search tools...",
            width=320,
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_subtle']
        )
        search_entry.pack(side='left')
        self.search_var.trace_add("write", lambda *_: self._on_search())

        view_label = ctk.CTkLabel(
            controls,
            text="View:",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary']
        )
        view_label.pack(side='left', padx=(16, 6))

        self.view_mode = tk.StringVar(value="Alphabetical")
        self.view_selector = ctk.CTkSegmentedButton(
            controls,
            values=["Alphabetical", "Category"],
            variable=self.view_mode,
            command=lambda _: self._render_tools()
        )
        self.view_selector.pack(side='left')

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color='transparent',
            corner_radius=0
        )
        self.list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def _load_tools(self) -> List[Dict[str, Any]]:
        tools: List[Dict[str, Any]] = []
        sections = self.tool_registry._sections if hasattr(self.tool_registry, '_sections') else []
        for section in sections:
            section_title = section.get("title", "Uncategorized")
            tab = str(section.get("tab", "")).strip().lower()
            for tool in section.get("tools", []):
                if self.allowed_tabs and tab not in self.allowed_tabs:
                    continue
                tool_entry = dict(tool)
                tool_entry.setdefault("category", section_title.title())
                tool_entry.setdefault("section_title", section_title)
                tools.append(tool_entry)
        return tools

    def _on_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.filtered_tools = list(self.all_tools)
        else:
            self.filtered_tools = [
                tool for tool in self.all_tools
                if self._tool_matches_query(tool, query)
            ]
        self._render_tools()

    def _render_tools(self):
        for child in self.list_frame.winfo_children():
            child.destroy()

        if not self.filtered_tools:
            empty = ctk.CTkLabel(
                self.list_frame,
                text="No results found.",
                font=('Segoe UI', 12),
                text_color=COLORS['text_secondary']
            )
            empty.pack(pady=20)
            return

        mode = self.view_mode.get()
        if mode == "Category":
            self._render_by_category()
        else:
            self._render_alphabetical()

    def _render_alphabetical(self):
        sorted_tools = sorted(self.filtered_tools, key=lambda t: t.get("title", "").lower())
        for tool in sorted_tools:
            self._add_tool_entry(self.list_frame, tool)

    def _render_by_category(self):
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for tool in self.filtered_tools:
            category = tool.get("category") or tool.get("section_title") or "Uncategorized"
            grouped.setdefault(category, []).append(tool)

        for category in sorted(grouped.keys()):
            header = ctk.CTkLabel(
                self.list_frame,
                text=category,
                font=('Segoe UI', 14, 'bold'),
                text_color=COLORS['text_primary'],
                anchor='w'
            )
            header.pack(fill='x', pady=(12, 4))
            for tool in sorted(grouped[category], key=lambda t: t.get("title", "").lower()):
                self._add_tool_entry(self.list_frame, tool)

    def _add_tool_entry(self, parent, tool: Dict[str, Any]):
        tool = self.tool_registry.get_ui_tool(tool, professional_mode=self.professional_mode)
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border_subtle']
        )
        card.pack(fill='x', pady=8)

        header = ctk.CTkFrame(card, fg_color='transparent')
        header.pack(fill='x', padx=16, pady=(14, 6))

        icon = "" if self.professional_mode else tool.get("icon", "•")
        title = tool.get("title", "Untitled")
        ctk.CTkLabel(
            header,
            text=f"{icon}  {title}".strip(),
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        ).pack(side='left', fill='x', expand=True)

        if not self.professional_mode:
            badge = ctk.CTkLabel(
                header,
                text=self._format_risk_label(tool),
                font=('Segoe UI', 10, 'bold'),
                text_color=self._risk_color(tool),
                anchor='e'
            )
            badge.pack(side='right')

        if not self.professional_mode:
            description = tool.get("detailed_description") or tool.get("description", "")
            desc_label = ctk.CTkLabel(
                card,
                text=description,
                font=('Segoe UI', 12),
                text_color=COLORS['text_secondary'],
                anchor='w',
                justify='left',
                wraplength=720
            )
            desc_label.pack(fill='x', padx=16, pady=(0, 8))

        info_frame = ctk.CTkFrame(card, fg_color='transparent')
        info_frame.pack(fill='x', padx=16, pady=(0, 10))

        category = tool.get("category") or tool.get("section_title", "Uncategorized")
        requirements = self._format_requirements(tool)
        frequency = self._format_frequency(tool)
        last_run = self._format_last_run(tool)

        info_text = (
            f"Category: {category}\n"
            f"Requires: {requirements}\n"
            f"Frequency: {frequency} (last run: {last_run})"
        )
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=('Segoe UI', 11),
            text_color=COLORS['text_secondary'],
            anchor='w',
            justify='left'
        ).pack(fill='x')

        notes = tool.get("notes") or tool.get("warning")
        when_to_use = tool.get("when_to_use")
        if (notes or when_to_use) and not self.professional_mode:
            note_frame = ctk.CTkFrame(card, fg_color='transparent')
            note_frame.pack(fill='x', padx=16, pady=(0, 14))

            note_text_parts = []
            if notes:
                note_text_parts.append(f"Note: {notes}")
            if when_to_use:
                note_text_parts.append(f"When to use: {when_to_use}")
            note_text = "\n".join(note_text_parts)

            ctk.CTkLabel(
                note_frame,
                text=note_text,
                font=('Segoe UI', 10),
                text_color=COLORS['text_tertiary'],
                anchor='w',
                justify='left',
                wraplength=720
            ).pack(fill='x')

    @staticmethod
    def _tool_matches_query(tool: Dict[str, Any], query: str) -> bool:
        haystack = " ".join([
            str(tool.get("title", "")),
            str(tool.get("description", "")),
            str(tool.get("detailed_description", "")),
            str(tool.get("category", "")),
        ]).lower()
        if query in haystack:
            return True
        for tag in tool.get("tags", []):
            if query in str(tag).lower():
                return True
        return False

    @staticmethod
    def _format_risk_label(tool: Dict[str, Any]) -> str:
        risk = (tool.get("risk_level") or "safe").lower()
        if risk == "high":
            return "High Risk - Security"
        if risk == "medium":
            return "Medium Risk"
        if risk == "low":
            return "Low Risk"
        return "Safe"

    @staticmethod
    def _risk_color(tool: Dict[str, Any]) -> str:
        risk = (tool.get("risk_level") or "safe").lower()
        if risk == "high":
            return COLORS['error']
        if risk == "medium":
            return COLORS['warning']
        if risk == "low":
            return COLORS['accent_secondary']
        return COLORS['success']

    @staticmethod
    def _format_requirements(tool: Dict[str, Any]) -> str:
        requirements = []
        if tool.get("requires_admin"):
            requirements.append("Administrator")
        if tool.get("requires_restart"):
            requirements.append("Restart")
        if not requirements:
            return "None"
        return ", ".join(requirements)

    def _format_last_run(self, tool: Dict[str, Any]) -> str:
        tool_id = tool.get("id")
        if not tool_id:
            return "Never"
        last_run = self.usage_store.get_last_run(tool_id)
        if not last_run:
            return "Never"
        try:
            last_dt = datetime.fromisoformat(last_run)
            delta = datetime.utcnow() - last_dt
            days = max(0, delta.days)
            return f"{days} days ago"
        except Exception:
            return "Unknown"

    @staticmethod
    def _format_frequency(tool: Dict[str, Any]) -> str:
        value = (tool.get("recommended_frequency") or "as_needed").lower()
        mapping = {
            "daily": "Daily",
            "weekly": "Weekly",
            "monthly": "Once per month",
            "quarterly": "Quarterly",
            "once": "One-time",
            "as_needed": "As needed"
        }
        return mapping.get(value, value.title())
