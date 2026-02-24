"""
Maintenance Tab
Loads maintenance tools from registry and displays collapsible sections
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import ctypes


from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS
from src.theme import SPACING
from src.utils.tool_registry import ToolRegistry
from src.utils.constants import TOOLS_FILE
from src.components.utility_button import UtilityButton
from src.utils.quick_cleanup import QuickCleanupRunner
from src.services.cleanup_service import CleanupService

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class CollapsibleSection(ctk.CTkFrame):
    """Collapsible section container for tool groups with enhanced styling."""

    def __init__(self, parent, title: str, description: str = "", icon: str = "", collapsed: bool = False, section_id: str = ""):
        super().__init__(
            parent,
            fg_color='transparent',
            corner_radius=0
        )
        self._section_id = section_id

        self._collapsed = collapsed
        self._arrow_text = ctk.StringVar(value="▸" if collapsed else "▾")

        # Get category color
        category_colors = {
            "quick_cleanup": COLORS.get("color_cleanup", COLORS['success']),
            "memory_disk": COLORS.get("color_memory", COLORS['info']),
            "network": COLORS.get("color_network", COLORS['accent_primary']),
            "system_repair": COLORS.get("color_repair", COLORS['warning']),
            "privacy": COLORS.get("color_privacy", COLORS['accent_secondary']),
            "security": COLORS.get("color_security", COLORS['error']),
            "system_health": COLORS.get("color_external", COLORS['info']),
            "storage_files": COLORS.get("color_memory", COLORS['info']),
            "privacy_tools": COLORS.get("color_privacy", COLORS['accent_secondary']),
        }
        section_id = getattr(self, '_section_id', '')
        section_color = category_colors.get(section_id, COLORS['accent_primary'])
        
        # Enhanced header with colored accent
        header = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=14,
            border_width=2,
            border_color=section_color
        )
        header.pack(fill='x', padx=20, pady=(16, 12))

        # Icon with larger size
        icon_label = ctk.CTkLabel(
            header,
            text=icon or "⚙️",
            font=('Segoe UI', 28),
            text_color=section_color,
            anchor='w'
        )
        icon_label.pack(side='left', padx=(20, 12), pady=16)

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=('Segoe UI', 20, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(side='left', fill='x', expand=True, pady=16)

        arrow = ctk.CTkLabel(
            header,
            textvariable=self._arrow_text,
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_secondary']
        )
        arrow.pack(side='right')

        if description:
            description_label = ctk.CTkLabel(
                self,
                text=description,
                font=('Segoe UI', 13),
                text_color=COLORS['text_secondary'],
                anchor='w',
                wraplength=900,
                justify='left'
            )
            description_label.pack(fill='x', padx=20, pady=(0, 16))

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


class MaintenanceTab(ctk.CTkScrollableFrame):
    """Maintenance tab for cleanup and repair tools."""

    def __init__(self, parent, config_manager):
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )

        self.config_manager = config_manager
        self.cleanup_service = CleanupService()
        self.tool_registry = ToolRegistry()
        self.tool_registry.load_tools(TOOLS_FILE)

        self.setup_ui()

    def setup_ui(self):
        # Enhanced header with gradient effect
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=SPACING.get("2xl", 32), pady=(SPACING.get("3xl", 48), SPACING.get("xl", 24)))

        # Title section
        title_frame = ctk.CTkFrame(header, fg_color='transparent')
        title_frame.pack(fill='x', pady=(0, 16))

        # Title with gradient effect using multiple colors
        title_frame_inner = ctk.CTkFrame(title_frame, fg_color='transparent')
        title_frame_inner.pack(side='left', fill='x', expand=True)
        
        icon_label = ctk.CTkLabel(
            title_frame_inner,
            text="🛠️",
            font=('Segoe UI', 32),
            text_color=COLORS['accent_primary'],
            anchor='w'
        )
        icon_label.pack(side='left', padx=(0, 12))
        
        title = ctk.CTkLabel(
            title_frame_inner,
            text="System Maintenance",
            font=('Segoe UI', 32, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(side='left')

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Keep your system running smoothly with powerful maintenance tools",
            font=('Segoe UI', 13),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        subtitle.pack(fill='x', pady=(8, 0))

        # Action buttons row
        actions_frame = ctk.CTkFrame(header, fg_color='transparent')
        actions_frame.pack(fill='x', pady=(12, 0))

        quick_cleanup = Button3D(
            actions_frame,
            text="🚀 Run Quick Cleanup",
            width=240,
            height=44,
            bg_color=BUTTON_COLORS.SUCCESS,
            font=('Segoe UI', 14, 'bold'),
            command=self._run_quick_cleanup
        )
        quick_cleanup.pack(side='left', padx=(0, 12))
        
        info_btn = Button3D(
            actions_frame,
            text="ℹ️ Help",
            width=120,
            height=44,
            bg_color=BUTTON_COLORS.INFO,
            font=('Segoe UI', 13, 'bold'),
            command=lambda: self._show_help()
        )
        info_btn.pack(side='left')

        sections = self.tool_registry.get_sections_by_tab("maintenance")

        if not sections:
            empty_label = ctk.CTkLabel(
                self,
                text="Unable to load maintenance tools.\nCheck that config/tools.json is present and valid.",
                font=('Segoe UI', 14),
                text_color=COLORS['text_secondary'],
                anchor='w'
            )
            empty_label.pack(fill='x', padx=20, pady=20)
            return

        for section in sections:
            # Enhanced card with shadow effect
            card_container = ctk.CTkFrame(self, fg_color='transparent')
            card_container.pack(fill='x', padx=40, pady=16)
            
            # Shadow layer
            shadow = ctk.CTkFrame(
                card_container,
                fg_color=COLORS['bg_base'],
                corner_radius=20
            )
            shadow.pack(fill='both', expand=True, padx=(0, 0), pady=(0, 0))
            
            # Main card
            card = ctk.CTkFrame(
                shadow,
                fg_color=COLORS['bg_secondary'],
                corner_radius=18,
                border_width=1,
                border_color=COLORS['border_subtle']
            )
            card.pack(fill='both', expand=True, padx=2, pady=2)

            section_frame = CollapsibleSection(
                card,
                title=section.get("title", ""),
                description=section.get("description", ""),
                icon=section.get("icon", ""),
                collapsed=False,
                section_id=section.get("id", "")
            )
            section_frame._section_id = section.get("id", "")
            section_frame.content._section_id = section.get("id", "")
            section_frame.pack(fill='both', expand=True, padx=0, pady=(0, 2))

            self._build_tools(section_frame.content, section.get("tools", []))

    def _build_tools(self, parent, tools):
        if not tools:
            return

        # Enhanced grid with better spacing
        grid = ctk.CTkFrame(parent, fg_color='transparent')
        grid.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = 5
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="tool_col")

        # Category color mapping
        category_colors = {
            "quick_cleanup": COLORS.get("color_cleanup", COLORS['success']),
            "memory_disk": COLORS.get("color_memory", COLORS['info']),
            "network": COLORS.get("color_network", COLORS['accent_primary']),
            "system_repair": COLORS.get("color_repair", COLORS['warning']),
            "privacy": COLORS.get("color_privacy", COLORS['accent_secondary']),
            "security": COLORS.get("color_security", COLORS['error']),
            "system_health": COLORS.get("color_external", COLORS['info']),
            "storage_files": COLORS.get("color_memory", COLORS['info']),
            "privacy_tools": COLORS.get("color_privacy", COLORS['accent_secondary']),
        }
        
        # Get section color from parent section
        section_id = getattr(parent, '_section_id', '')
        section_color = category_colors.get(section_id, COLORS['accent_primary'])

        for index, tool in enumerate(tools):
            tool_id = tool.get("id", "")
            icon = tool.get("icon", "") or "⚙️"  # Default icon if missing
            title = tool.get("title", "")
            tooltip = tool.get("description", "")
            requires_admin = tool.get("requires_admin", False)
            requires_restart = tool.get("requires_restart", False)
            
            # Normalize icon size - use larger, more attractive icons
            icon = self._normalize_icon(icon)

            handler = lambda tid=tool_id: self._execute_tool(tid)

            button = UtilityButton(
                grid,
                icon=icon,
                title=title,
                subtitle="",
                command=handler,
                tooltip=tooltip,
                width=120,
                height=120,
                requires_admin=requires_admin,
                requires_restart=requires_restart,
                accent_color=section_color
            )

            row = index // columns
            col = index % columns
            button.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
    
    def _normalize_icon(self, icon: str) -> str:
        """Normalize icon to ensure consistent, attractive appearance"""
        # Map common icons to better alternatives
        icon_map = {
            "": "⚙️",
            "🧹": "✨",  # Sparkles for cleanup
            "🗑": "🗑️",  # Ensure full emoji
            "🔄": "🔄",
            "🌐": "🌐",
            "📁": "📂",
            "🧠": "🧠",
            "💾": "💾",
            "🔧": "🔧",
            "🛠": "🛠️",
            "💿": "💿",
            "🏪": "🏪",
            "⏸️": "⏸️",
        }
        return icon_map.get(icon, icon) if icon in icon_map else (icon or "⚙️")

    def _execute_tool(self, tool_id: str):
        if tool_id == "network_stats":
            return self._show_network_stats()

        if not self.tool_registry.get_tool_by_id(tool_id):
            logger.warning(f"Tool not found: {tool_id}")
            return False, "Tool not configured"

        tool = self.tool_registry.get_tool_by_id(tool_id) or {}
        
        # Check and request admin elevation if needed
        if tool.get("requires_admin"):
            if not self._is_admin():
                # Request elevation
                from src.utils.admin_elevator import run_command_elevated
                # For now, we'll still use the existing method but show better messaging
                if not self._confirm_admin_if_needed(tool):
                    return False, "Administrator privileges required"
            else:
                # Already admin, proceed
                pass

        if tool_id in {"sfc_scan", "dism_repair"}:
            return self._run_with_progress(tool_id)

        success, message = self.tool_registry.execute_tool(tool_id, self.config_manager)
        if not success:
            messagebox.showerror("Operation Failed", message)
        return success, message

    def _run_quick_cleanup(self):
        runner = QuickCleanupRunner(self, self.config_manager, self.tool_registry)
        runner.start()

    def _show_network_stats(self):
        success, stats = self.cleanup_service.get_network_stats()
        if success:
            display_stats = stats[:1000] if len(stats) > 1000 else stats
            if len(stats) > 1000:
                display_stats += "\n\n(Truncated - showing first 1000 characters)"
            messagebox.showinfo("Network Statistics", display_stats)
            return True, "Network stats displayed"
        messagebox.showerror("Network Statistics", stats)
        return False, stats

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

    def _run_with_progress(self, tool_id: str):
        dialog_ready = threading.Event()
        dialog_container = {}

        def show_dialog():
            dialog = ctk.CTkToplevel(self)
            dialog.title("Working...")
            dialog.geometry("420x160")
            dialog.configure(fg_color=COLORS['bg_primary'])
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()

            label = ctk.CTkLabel(
                dialog,
                text="Operation in progress. This may take several minutes.",
                font=('Segoe UI', 12),
                text_color=COLORS['text_primary']
            )
            label.pack(pady=(20, 10))

            progress = ctk.CTkProgressBar(
                dialog,
                height=8,
                corner_radius=8,
                fg_color=COLORS['bg_tertiary'],
                progress_color=COLORS['accent_primary']
            )
            progress.pack(fill='x', padx=24, pady=(0, 20))
            progress.configure(mode="indeterminate")
            progress.start()

            dialog_container["dialog"] = dialog
            dialog_container["progress"] = progress
            dialog_ready.set()

        self.after(0, show_dialog)
        dialog_ready.wait()

        success, message = self.tool_registry.execute_tool(tool_id, self.config_manager)

        def close_dialog():
            dialog = dialog_container.get("dialog")
            if dialog:
                dialog.destroy()

        self.after(0, close_dialog)

        if not success:
            messagebox.showerror("Operation Failed", message)
        return success, message

    def _prompt_user(self, title: str, message: str) -> bool:
        result = {"value": False}
        ready = threading.Event()

        def _ask():
            result["value"] = messagebox.askyesno(title, message)
            ready.set()

        self.after(0, _ask)
        ready.wait()
        return result["value"]
    
    def _show_help(self):
        """Show help dialog for maintenance tools"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Maintenance Tools Help")
        dialog.geometry("600x400")
        dialog.configure(fg_color=COLORS['bg_primary'])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        header = ctk.CTkLabel(
            dialog,
            text="🛠️ Maintenance Tools Guide",
            font=('Segoe UI', 20, 'bold'),
            text_color=COLORS['text_primary']
        )
        header.pack(pady=(20, 10))
        
        help_text = (
            "Quick Cleanup: Fast, safe operations you can run daily\n"
            "Memory & Disk: Deep cleaning and optimization\n"
            "Network: Network-related maintenance\n"
            "System Repair: Advanced repair tools (may take time)\n"
            "Privacy: Privacy and data protection tools\n"
            "System Health: Stability and startup diagnostics\n"
            "Storage & Files: Disk analysis and file search\n\n"
            "🔒 = Requires Administrator privileges\n"
            "Tools are color-coded by category for easy identification."
        )
        
        body = ctk.CTkLabel(
            dialog,
            text=help_text,
            font=('Segoe UI', 13),
            text_color=COLORS['text_secondary'],
            justify='left',
            anchor='w'
        )
        body.pack(fill='both', expand=True, padx=30, pady=10)
        
        Button3D(
            dialog,
            text="Close",
            width=120,
            height=36,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=dialog.destroy
        ).pack(pady=20)
