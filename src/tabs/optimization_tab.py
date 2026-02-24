"""
Optimization Tab
Loads optimization tools from registry and displays collapsible sections
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import ctypes


from src.theme import COLORS
from src.theme import SPACING
from src.utils.tool_registry import ToolRegistry
from src.utils.constants import TOOLS_FILE
from src.components.utility_button import UtilityButton

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class CollapsibleSection(ctk.CTkFrame):
    """Collapsible section container for tool groups."""

    def __init__(self, parent, title: str, description: str = "", icon: str = "", collapsed: bool = False):
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['border_subtle']
        )

        self._collapsed = collapsed
        self._arrow_text = ctk.StringVar(value="▸" if collapsed else "▾")

        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=24, pady=(20, 6))

        title_label = ctk.CTkLabel(
            header,
            text=f"{icon} {title}".strip(),
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(side='left', fill='x', expand=True)

        arrow = ctk.CTkLabel(
            header,
            textvariable=self._arrow_text,
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_secondary']
        )
        arrow.pack(side='right')

        description_label = ctk.CTkLabel(
            self,
            text=description or "",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            anchor='w',
            wraplength=900,
            justify='left'
        )
        description_label.pack(fill='x', padx=24, pady=(0, 12))

        self.content = ctk.CTkFrame(self, fg_color='transparent')
        self.content.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        for widget in (header, title_label, arrow, description_label):
            widget.bind("<Button-1>", self.toggle)

        if self._collapsed:
            self.content.pack_forget()

    def toggle(self, event=None):
        self._collapsed = not self._collapsed
        self._arrow_text.set("▸" if self._collapsed else "▾")
        if self._collapsed:
            self.content.pack_forget()
        else:
            self.content.pack(fill='both', expand=True, padx=24, pady=(0, 20))


class OptimizationTab(ctk.CTkScrollableFrame):
    """Optimization tab for performance and system tuning tools."""

    def __init__(self, parent, config_manager):
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )

        self.config_manager = config_manager
        self.professional_mode = bool(self.config_manager.get_setting("ui.professional_mode", False))
        self.tool_registry = ToolRegistry()
        self.tool_registry.load_tools(TOOLS_FILE)

        self.setup_ui()

    def setup_ui(self):
        sections = self.tool_registry.get_sections_by_tab("optimization")

        if not sections:
            empty_label = ctk.CTkLabel(
                self,
                text="Unable to load optimization tools.\nCheck that config/tools.json is present and valid.",
                font=('Segoe UI', 14),
                text_color=COLORS['text_secondary'],
                anchor='w'
            )
            empty_label.pack(fill='x', padx=SPACING.get("xl", 24), pady=SPACING.get("xl", 24))
            return

        for section in sections:
            card = ctk.CTkFrame(self, fg_color=COLORS['border_default'], corner_radius=16)
            card.pack(fill='x', padx=SPACING.get("2xl", 32), pady=SPACING.get("md", 12))

            section_frame = CollapsibleSection(
                card,
                title=section.get("title", ""),
                description="" if self.professional_mode else section.get("description", ""),
                icon="" if self.professional_mode else section.get("icon", ""),
                collapsed=self.professional_mode
            )
            section_frame.pack(fill='both', expand=True, padx=0, pady=(0, 2))

            self._build_tools(section_frame.content, section.get("tools", []))

    def _build_tools(self, parent, tools):
        if not tools:
            return

        grid = ctk.CTkFrame(parent, fg_color='transparent')
        grid.pack(fill='both', expand=True)

        columns = 5
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1)

        for index, tool in enumerate(tools):
            tool = self.tool_registry.get_ui_tool(tool, professional_mode=self.professional_mode)
            tool_id = tool.get("id", "")
            icon = tool.get("icon", "")
            title = tool.get("title", "")
            tooltip = "" if self.professional_mode else tool.get("description", "")
            requires_restart = tool.get("requires_restart", False)

            handler = lambda tid=tool_id: self._execute_tool(tid)

            button = UtilityButton(
                grid,
                icon=icon,
                title=title,
                subtitle="",
                command=handler,
                tooltip=tooltip,
                width=90 if self.professional_mode else 100,
                height=86 if self.professional_mode else 100,
                requires_restart=requires_restart
            )

            row = index // columns
            col = index % columns
            button.grid(row=row, column=col, padx=8, pady=8)

    def _execute_tool(self, tool_id: str):
        if not self.tool_registry.get_tool_by_id(tool_id):
            logger.warning(f"Tool not found: {tool_id}")
            return False, "Tool not configured"

        tool = self.tool_registry.get_tool_by_id(tool_id) or {}
        if not self._confirm_admin_if_needed(tool):
            return False, "Cancelled"

        success, message = self.tool_registry.execute_tool(
            tool_id,
            self.config_manager,
            skip_confirmation=False
        )
        if not success:
            messagebox.showerror("Operation Failed", message)
        return success, message

    @staticmethod
    def _is_admin() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def _confirm_admin_if_needed(self, tool: dict) -> bool:
        if not tool.get("requires_admin"):
            return True
        if self._is_admin():
            return True

        return self._prompt_user("Admin Required", "This action may require administrator privileges. Continue?")

    def _prompt_user(self, title: str, message: str) -> bool:
        result = {"value": False}
        ready = threading.Event()

        def _ask():
            result["value"] = messagebox.askyesno(title, message)
            ready.set()

        self.after(0, _ask)
        ready.wait()
        return result["value"]
