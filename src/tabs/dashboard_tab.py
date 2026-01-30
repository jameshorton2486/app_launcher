"""
Dashboard Tab
Home screen with system overview and quick actions
"""

import customtkinter as ctk
import sys
import os
import threading
import platform
from datetime import datetime, timedelta

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS
from src.utils.constants import TOOLS_FILE
from src.utils.tool_registry import ToolRegistry
from src.services.cleanup_service import CleanupService
from src.services.process_service import ProcessService
from src.services.git_service import GitService

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

try:
    import psutil
except Exception:
    psutil = None


class DashboardTab(ctk.CTkScrollableFrame):
    """Dashboard tab for system overview and quick actions."""

    def __init__(self, parent, config_manager, process_service=None, status_bar=None, on_open_downloads=None):
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )

        self.config_manager = config_manager
        self.status_bar = status_bar
        self.on_open_downloads = on_open_downloads
        self.process_service = process_service or ProcessService()
        self.cleanup_service = CleanupService()
        self.git_service = GitService()

        self.tool_registry = ToolRegistry()
        self.tool_registry.load_tools(TOOLS_FILE)

        self._system_widgets = {}
        self._project_rows = []

        self.setup_ui()
        self._refresh_system_stats()

    def setup_ui(self):
        """Build dashboard layout."""
        # Welcome section
        welcome_frame = ctk.CTkFrame(self, fg_color='transparent')
        welcome_frame.pack(fill='x', padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to App Launcher",
            font=('Segoe UI', 22, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(fill='x')

        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Your centralized hub for launching projects, optimizing Windows performance, and maintaining your system.",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            anchor='w',
            wraplength=900
        )
        subtitle.pack(fill='x', pady=(6, 0))

        if self.on_open_downloads:
            open_downloads = ctk.CTkButton(
                welcome_frame,
                text="Open Downloads Manager",
                width=200,
                height=32,
                fg_color=COLORS['bg_tertiary'],
                hover_color=COLORS['bg_hover'],
                command=self.on_open_downloads
            )
            open_downloads.pack(anchor='w', pady=(10, 0))

        # Cards grid
        grid_frame = ctk.CTkFrame(self, fg_color='transparent')
        grid_frame.pack(fill='x', padx=20, pady=(10, 0))
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        system_card = self._create_card(grid_frame, "System Overview")
        system_card.grid(row=0, column=0, padx=(0, 10), pady=10, sticky='nsew')
        self._build_system_overview(system_card)

        actions_card = self._create_card(grid_frame, "Quick Actions")
        actions_card.grid(row=0, column=1, padx=(10, 0), pady=10, sticky='nsew')
        self._build_quick_actions(actions_card)

        projects_card = self._create_card(self, "Recent Projects")
        projects_card.pack(fill='x', padx=20, pady=10)
        self._build_recent_projects(projects_card)

    def _create_card(self, parent, title: str):
        shadow = ctk.CTkFrame(parent, fg_color=COLORS['border_default'], corner_radius=16)
        card = ctk.CTkFrame(
            shadow,
            fg_color=COLORS['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['border_subtle']
        )
        card.pack(fill='both', expand=True, padx=0, pady=(0, 2))

        header = ctk.CTkLabel(
            card,
            text=title,
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        header.pack(fill='x', padx=24, pady=(20, 10))

        content = ctk.CTkFrame(card, fg_color='transparent')
        content.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        shadow.content = content
        return shadow

    def _build_system_overview(self, card):
        content = card.content

        self._system_widgets['ram'] = self._build_stat_row(content, "RAM")
        self._system_widgets['cpu'] = self._build_stat_row(content, "CPU")
        self._system_widgets['disk'] = self._build_stat_row(content, "Disk C")

        self._system_widgets['windows'] = self._build_info_row(content, "Windows")
        self._system_widgets['uptime'] = self._build_info_row(content, "Uptime")

    def _build_stat_row(self, parent, label):
        row = ctk.CTkFrame(parent, fg_color='transparent')
        row.pack(fill='x', pady=(0, 12))

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            width=80,
            anchor='w'
        )
        label_widget.pack(side='left')

        value_label = ctk.CTkLabel(
            row,
            text="--",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            anchor='e'
        )
        value_label.pack(side='right')

        progress = ctk.CTkProgressBar(
            row,
            height=8,
            corner_radius=8,
            fg_color=COLORS['bg_tertiary'],
            progress_color=COLORS['accent_primary']
        )
        progress.pack(fill='x', padx=(0, 12))
        progress.set(0)

        return {"value": value_label, "progress": progress}

    def _build_info_row(self, parent, label):
        row = ctk.CTkFrame(parent, fg_color='transparent')
        row.pack(fill='x', pady=(0, 8))

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            width=80,
            anchor='w'
        )
        label_widget.pack(side='left')

        value_label = ctk.CTkLabel(
            row,
            text="--",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        value_label.pack(side='left', padx=(10, 0))
        return value_label

    def _build_quick_actions(self, card):
        content = card.content

        grid = ctk.CTkFrame(content, fg_color='transparent')
        grid.pack(fill='both', expand=True)

        actions = [
            ("🧹", "Clear Temp", lambda: self._run_tool("clear_temp_files")),
            ("🔄", "Flush DNS", lambda: self._run_tool("flush_dns")),
            ("🗑️", "Empty Recycle Bin", lambda: self._run_tool("empty_recycle_bin")),
            ("🔄", "Restart Explorer", lambda: self._run_tool("restart_explorer")),
            ("🐙", "GitHub Desktop", self._launch_github_desktop),
            ("🧠", "Clear RAM", lambda: self._run_tool("clear_ram_standby")),
            ("💾", "Disk Cleanup", lambda: self._run_tool("disk_cleanup")),
            ("📶", "Network Stats", self._show_network_stats),
        ]

        for index, (icon, label, handler) in enumerate(actions):
            row = index // 4
            col = index % 4
            btn = self._create_action_button(grid, icon, label, handler)
            btn.grid(row=row, column=col, padx=8, pady=8)

    def _create_action_button(self, parent, icon, label, handler):
        button = ctk.CTkButton(
            parent,
            text=f"{icon}\n{label}",
            width=100,
            height=100,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            font=('Segoe UI', 11, 'bold'),
            command=lambda: self._run_in_thread(handler)
        )
        button.configure(corner_radius=12)
        return button

    def _build_recent_projects(self, card):
        content = card.content
        projects = self.config_manager.load_projects()
        recent = projects[-5:] if len(projects) >= 5 else projects

        if not recent:
            empty_label = ctk.CTkLabel(
                content,
                text="No recent projects found.",
                font=('Segoe UI', 12),
                text_color=COLORS['text_secondary'],
                anchor='w'
            )
            empty_label.pack(fill='x')
            return

        for project in reversed(recent):
            row = self._create_project_row(content, project)
            row.pack(fill='x', pady=6)
            self._project_rows.append(row)

    def _create_project_row(self, parent, project):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_tertiary'], corner_radius=12)

        name = project.get('name', 'Unknown')
        language = project.get('language', '').lower()
        language_icon = self._get_language_icon(language)

        name_label = ctk.CTkLabel(
            row,
            text=f"{language_icon}  {name}",
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        name_label.pack(side='left', padx=12, pady=10, expand=True, fill='x')

        status = self._get_git_status(project.get('path', ''))
        status_label = ctk.CTkLabel(
            row,
            text=status['label'],
            font=('Segoe UI', 10, 'bold'),
            text_color=status['color'],
            anchor='e'
        )
        status_label.pack(side='right', padx=12)

        row.bind("<Button-1>", lambda e, p=project: self._launch_project(p))
        name_label.bind("<Button-1>", lambda e, p=project: self._launch_project(p))
        status_label.bind("<Button-1>", lambda e, p=project: self._launch_project(p))
        return row

    def _get_git_status(self, path):
        try:
            if not path or not os.path.exists(os.path.join(path, '.git')):
                return {"label": "No Git", "color": COLORS['text_tertiary']}
            status = self.git_service.get_status(path)
            status_text = status.get('status_text', 'clean')
            if status_text == 'clean':
                return {"label": "Clean", "color": COLORS['success']}
            if status_text in {'uncommitted', 'diverged'}:
                return {"label": "Changes", "color": COLORS['warning']}
            if status_text == 'behind':
                return {"label": "Behind", "color": COLORS['warning']}
            return {"label": "Unknown", "color": COLORS['text_tertiary']}
        except Exception as exc:
            logger.debug(f"Git status error: {exc}")
            return {"label": "Unknown", "color": COLORS['text_tertiary']}

    @staticmethod
    def _get_language_icon(language):
        mapping = {
            "python": "🐍",
            "typescript": "🟦",
            "javascript": "🟨",
            "powershell": "⚡",
            "c#": "🟪",
            "csharp": "🟪",
            "go": "🟦",
        }
        return mapping.get(language, "📁")

    def _launch_project(self, project):
        if not project:
            return
        success, message = self.process_service.launch_project(project)
        if self.status_bar:
            self.status_bar.set_status(message)
        if not success:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Launch Failed", message)

    def _run_tool(self, tool_id):
        if not self.tool_registry.get_tool_by_id(tool_id):
            logger.warning(f"Tool not found: {tool_id}")
            return
        success, message = self.tool_registry.execute_tool(tool_id, self.config_manager)
        if self.status_bar:
            self.status_bar.set_status(message)
        if not success:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Action Failed", message)

    def _show_network_stats(self):
        success, stats = self.cleanup_service.get_network_stats()
        if success:
            display_stats = stats[:1000] if len(stats) > 1000 else stats
            if len(stats) > 1000:
                display_stats += "\n\n(Truncated - showing first 1000 characters)"
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Network Statistics", display_stats)
        else:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Network Statistics", stats)

    def _launch_github_desktop(self):
        path = self._resolve_external_tool("github_desktop")
        if not path:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("GitHub Desktop", "GitHub Desktop path not configured.")
            return
        try:
            os.startfile(path)
            if self.status_bar:
                self.status_bar.set_status("GitHub Desktop launched")
        except Exception as exc:
            import tkinter.messagebox as messagebox
            messagebox.showerror("GitHub Desktop", f"Failed to launch: {exc}")

    def _resolve_external_tool(self, key):
        settings_path = self.config_manager.get_setting(f'external_tools.{key}', '')
        if settings_path and os.path.exists(settings_path):
            return settings_path

        candidates = []
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "external_tool_paths.json")
            if os.path.exists(config_path):
                import json
                with open(config_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                candidates = data.get(key, [])
        except Exception:
            candidates = []

        for candidate in candidates:
            expanded = os.path.expandvars(candidate)
            if os.path.exists(expanded):
                return expanded
        return ""

    def _run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def _refresh_system_stats(self):
        if not psutil:
            self._set_system_stat("ram", "--", 0)
            self._set_system_stat("cpu", "--", 0)
            self._set_system_stat("disk", "--", 0)
            self._system_widgets['windows'].configure(text=platform.platform())
            self._system_widgets['uptime'].configure(text="--")
            return

        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            ram_text = f"{used_gb:.1f} / {total_gb:.1f} GB"
            self._set_system_stat("ram", ram_text, mem.percent / 100)

            cpu_percent = psutil.cpu_percent(interval=0.3)
            self._set_system_stat("cpu", f"{cpu_percent:.0f}%", cpu_percent / 100)

            disk = psutil.disk_usage("C:\\")
            used_disk = disk.used / (1024 ** 3)
            free_disk = disk.free / (1024 ** 3)
            disk_text = f"{used_disk:.1f} GB used / {free_disk:.1f} GB free"
            self._set_system_stat("disk", disk_text, disk.percent / 100)

            self._system_widgets['windows'].configure(text=platform.platform())

            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            uptime_text = self._format_uptime(uptime)
            self._system_widgets['uptime'].configure(text=uptime_text)
        except Exception as exc:
            logger.debug(f"System stats error: {exc}")

        self.after(5000, self._refresh_system_stats)

    def _set_system_stat(self, key, value, progress):
        widget = self._system_widgets.get(key)
        if not widget:
            return
        widget["value"].configure(text=value)
        widget["progress"].set(progress)

    @staticmethod
    def _format_uptime(delta: timedelta) -> str:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
