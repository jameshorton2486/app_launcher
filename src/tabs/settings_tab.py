"""
Settings Tab
Full-page settings with collapsible sections and auto-save
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, colorchooser
import sys
import os
import json
from datetime import datetime
import webbrowser

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS
from src.config_manager import ConfigManager
from src.utils.constants import SETTINGS_FILE

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class CollapsibleSection(ctk.CTkFrame):
    """Collapsible settings section."""

    def __init__(self, parent, title: str, collapsed: bool = False):
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
            text=title,
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(side='left', fill='x', expand=True)

        arrow = ctk.CTkLabel(
            header,
            textvariable=self._arrow_text,
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_secondary']
        )
        arrow.pack(side='right')

        self.content = ctk.CTkFrame(self, fg_color='transparent')
        self.content.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        for widget in (header, title_label, arrow):
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


class SettingsTab(ctk.CTkScrollableFrame):
    """Settings tab for application configuration."""

    def __init__(self, parent, config_manager, on_save=None):
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )

        self.config_manager = config_manager
        self.on_save = on_save
        self.settings = config_manager.settings.copy()

        self._path_errors = {}
        self._save_timer = None

        self.setup_ui()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="Settings",
            font=('Segoe UI', 22, 'bold'),
            text_color=COLORS['text_primary']
        )
        title.pack(side='left')

        self.save_status = ctk.CTkLabel(
            header,
            text="",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        self.save_status.pack(side='right')

        self.sections_container = ctk.CTkFrame(self, fg_color='transparent')
        self.sections_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self._build_general_section()
        self._build_appearance_section()
        self._build_paths_section()
        self._build_developer_section()
        self._build_optimization_section()
        self._build_external_tools_section()
        self._build_about_section()

    def _build_general_section(self):
        section = CollapsibleSection(self.sections_container, "GENERAL")
        section.pack(fill='x', pady=12)

        self.start_with_windows = ctk.BooleanVar(value=self._get_setting('window.start_with_windows', False))
        self.start_minimized = ctk.BooleanVar(value=self._get_setting('window.start_minimized', False))
        self.minimize_to_tray = ctk.BooleanVar(value=self._get_setting('window.minimize_to_tray', True))
        self.check_updates = ctk.BooleanVar(value=self._get_setting('updates.check_on_start', True))

        self._add_checkbox(section.content, "Start with Windows", self.start_with_windows)
        self._add_checkbox(section.content, "Start Minimized", self.start_minimized)
        self._add_checkbox(section.content, "Minimize to Tray on Close", self.minimize_to_tray)
        self._add_checkbox(section.content, "Check for Updates on Start", self.check_updates)

        hotkey_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        hotkey_frame.pack(fill='x', pady=8)

        ctk.CTkLabel(hotkey_frame, text="Global Hotkey:", font=('Segoe UI', 12)).pack(side='left')
        self.hotkey_entry = ctk.CTkEntry(hotkey_frame, width=200, font=('Segoe UI', 12))
        self.hotkey_entry.pack(side='left', padx=(10, 10))
        current_hotkey = self._get_setting('window.global_hotkey', 'win+shift+l')
        self.hotkey_entry.insert(0, current_hotkey.replace('+', ' + ').replace('win', 'Win'))
        self.hotkey_entry.configure(state='readonly')

        ctk.CTkButton(
            hotkey_frame,
            text="Change",
            width=120,
            command=self.change_hotkey
        ).pack(side='left')

        self.start_with_windows.trace_add("write", lambda *_: self._queue_save())
        self.start_minimized.trace_add("write", lambda *_: self._queue_save())
        self.minimize_to_tray.trace_add("write", lambda *_: self._queue_save())
        self.check_updates.trace_add("write", lambda *_: self._queue_save())

    def _build_appearance_section(self):
        section = CollapsibleSection(self.sections_container, "APPEARANCE")
        section.pack(fill='x', pady=12)

        self.theme_mode = ctk.StringVar(value=self._get_setting('theme.mode', 'dark'))
        self.sidebar_style = ctk.StringVar(value=self._get_setting('appearance.sidebar_style', 'Expanded'))
        self.button_size = ctk.StringVar(value=self._get_setting('appearance.button_size', 'Medium'))
        self.show_descriptions = ctk.BooleanVar(value=self._get_setting('appearance.show_descriptions', True))
        self.compact_mode = ctk.BooleanVar(value=self._get_setting('appearance.compact_mode', False))
        self.font_size = ctk.IntVar(value=self._get_setting('appearance.font_size', 14))

        self._add_dropdown(section.content, "Theme Mode", self.theme_mode, ['dark', 'light', 'system'])
        self._add_dropdown(section.content, "Sidebar Style", self.sidebar_style, ['Expanded', 'Collapsed', 'Auto-hide'])
        self._add_dropdown(section.content, "Button Size", self.button_size, ['Small', 'Medium', 'Large'])
        self._add_checkbox(section.content, "Show Tool Descriptions", self.show_descriptions)
        self._add_checkbox(section.content, "Compact Mode", self.compact_mode)

        font_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        font_frame.pack(fill='x', pady=8)
        ctk.CTkLabel(font_frame, text="Font Size:", font=('Segoe UI', 12)).pack(side='left')
        font_slider = ctk.CTkSlider(
            font_frame,
            from_=12,
            to=18,
            number_of_steps=6,
            variable=self.font_size,
            command=lambda *_: self._queue_save()
        )
        font_slider.pack(fill='x', expand=True, padx=10)

        color_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        color_frame.pack(fill='x', pady=8)
        ctk.CTkLabel(color_frame, text="Accent Color:", font=('Segoe UI', 12)).pack(side='left')

        self.accent_color = self._get_setting('theme.accent_color', COLORS['accent_primary'])
        self.color_preview = ctk.CTkFrame(color_frame, width=50, height=28, fg_color=self.accent_color)
        self.color_preview.pack(side='left', padx=(10, 10))

        ctk.CTkButton(color_frame, text="Pick", width=80, command=self.pick_color).pack(side='left')

        self.theme_mode.trace_add("write", lambda *_: self._queue_save())
        self.sidebar_style.trace_add("write", lambda *_: self._queue_save())
        self.button_size.trace_add("write", lambda *_: self._queue_save())
        self.show_descriptions.trace_add("write", lambda *_: self._queue_save())
        self.compact_mode.trace_add("write", lambda *_: self._queue_save())
        self.font_size.trace_add("write", lambda *_: self._queue_save())

    def _build_paths_section(self):
        section = CollapsibleSection(self.sections_container, "PATHS")
        section.pack(fill='x', pady=12)

        self.paths_entries = {}

        self._add_path_field(section.content, "Downloads Folder", 'paths.downloads_folder')
        self._add_path_field(section.content, "Screenshots Folder", 'paths.screenshots_folder')
        self._add_path_field(section.content, "Projects Root", 'paths.projects_root')

    def _build_developer_section(self):
        section = CollapsibleSection(self.sections_container, "DEVELOPER")
        section.pack(fill='x', pady=12)

        self.default_ide = ctk.StringVar(value=self._get_setting('developer.default_ide', 'VS Code'))
        self.custom_ide_path = ctk.StringVar(value=self._get_setting('developer.custom_ide_path', ''))
        self.default_terminal = ctk.StringVar(value=self._get_setting('developer.default_terminal', 'Windows Terminal'))
        self.github_desktop_path = ctk.StringVar(value=self._get_setting('developer.github_desktop_path', ''))
        self.auto_git_fetch = ctk.BooleanVar(value=self._get_setting('developer.auto_git_fetch', False))
        self.git_refresh_interval = ctk.IntVar(value=self._get_setting('developer.git_refresh_interval', 60))

        self._add_dropdown(section.content, "Default IDE", self.default_ide, ['Cursor', 'VS Code', 'PyCharm', 'Custom'], on_change=self._toggle_custom_ide)
        self.custom_ide_frame = self._add_path_field(section.content, "Custom IDE Path", None, var=self.custom_ide_path)
        self._toggle_custom_ide(self.default_ide.get())

        self._add_dropdown(section.content, "Default Terminal", self.default_terminal, ['Windows Terminal', 'PowerShell', 'CMD'])

        self._add_path_field(section.content, "GitHub Desktop Path", None, var=self.github_desktop_path)
        self._add_checkbox(section.content, "Auto Git Fetch on Project Open", self.auto_git_fetch)

        interval_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        interval_frame.pack(fill='x', pady=8)
        ctk.CTkLabel(interval_frame, text="Git Status Refresh Interval (sec):", font=('Segoe UI', 12)).pack(side='left')
        interval_slider = ctk.CTkSlider(
            interval_frame,
            from_=30,
            to=300,
            number_of_steps=27,
            variable=self.git_refresh_interval,
            command=lambda *_: self._queue_save()
        )
        interval_slider.pack(fill='x', expand=True, padx=10)

        self.default_ide.trace_add("write", lambda *_: self._queue_save())
        self.custom_ide_path.trace_add("write", lambda *_: self._queue_save())
        self.default_terminal.trace_add("write", lambda *_: self._queue_save())
        self.github_desktop_path.trace_add("write", lambda *_: self._queue_save())
        self.auto_git_fetch.trace_add("write", lambda *_: self._queue_save())
        self.git_refresh_interval.trace_add("write", lambda *_: self._queue_save())

    def _build_optimization_section(self):
        section = CollapsibleSection(self.sections_container, "OPTIMIZATION")
        section.pack(fill='x', pady=12)

        self.show_security_warnings = ctk.BooleanVar(value=self._get_setting('optimization.show_security_warnings', True))
        self.confirm_service_changes = ctk.BooleanVar(value=self._get_setting('optimization.confirm_service_changes', True))
        self.log_system_changes = ctk.BooleanVar(value=self._get_setting('optimization.log_system_changes', False))
        self.show_hw_recommendations = ctk.BooleanVar(value=self._get_setting('optimization.show_hw_recommendations', True))

        self._add_checkbox(section.content, "Show Security Warnings", self.show_security_warnings)
        self._add_checkbox(section.content, "Confirm Service Changes", self.confirm_service_changes)
        self._add_checkbox(section.content, "Log All System Changes", self.log_system_changes)
        self._add_checkbox(section.content, "Show Hardware Recommendations", self.show_hw_recommendations)

        self.show_security_warnings.trace_add("write", lambda *_: self._queue_save())
        self.confirm_service_changes.trace_add("write", lambda *_: self._queue_save())
        self.log_system_changes.trace_add("write", lambda *_: self._queue_save())
        self.show_hw_recommendations.trace_add("write", lambda *_: self._queue_save())

    def _build_external_tools_section(self):
        section = CollapsibleSection(self.sections_container, "EXTERNAL TOOLS")
        section.pack(fill='x', pady=12)

        self.external_tools = {
            "CCleaner": ("external_tools.ccleaner", "https://www.ccleaner.com/ccleaner/download"),
            "BleachBit": ("external_tools.bleachbit", "https://www.bleachbit.org/download"),
            "Wise Memory": ("external_tools.wise_memory_cleaner", "https://www.wisecleaner.com/wise-memory-optimizer.html"),
            "TreeSize": ("external_tools.treesize", "https://www.jam-software.com/treesize_free"),
            "Everything": ("external_tools.everything", "https://www.voidtools.com/downloads/"),
            "BCUninstaller": ("external_tools.bcuninstaller", "https://www.bcuninstaller.com/"),
            "CrystalDiskInfo": ("external_tools.crystaldiskinfo", "https://crystalmark.info/en/download/"),
            "HWiNFO": ("external_tools.hwinfo", "https://www.hwinfo.com/download/"),
            "CPU-Z": ("external_tools.cpuz", "https://www.cpuid.com/softwares/cpu-z.html"),
            "Autoruns": ("external_tools.autoruns", "https://learn.microsoft.com/sysinternals/downloads/autoruns"),
            "Process Lasso": ("external_tools.process_lasso", "https://bitsum.com/processlasso/"),
            "O&O ShutUp10++": ("external_tools.shutup10", "https://www.oo-software.com/en/shutup10"),
        }

        for label, (key, url) in self.external_tools.items():
            frame = self._add_path_field(section.content, label, key)
            download_btn = ctk.CTkButton(
                frame,
                text="Download",
                width=90,
                height=28,
                fg_color=COLORS['bg_tertiary'],
                hover_color=COLORS['accent_secondary'],
                command=lambda link=url: webbrowser.open(link)
            )
            download_btn.pack(side='left', padx=(8, 0))

    def _build_about_section(self):
        section = CollapsibleSection(self.sections_container, "ABOUT")
        section.pack(fill='x', pady=12)

        info_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        info_frame.pack(fill='x', pady=8)

        ctk.CTkLabel(
            info_frame,
            text="App Launcher v2.0.0",
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary']
        ).pack(anchor='w')

        build_date = datetime.now().strftime("%B %d, %Y")
        ctk.CTkLabel(
            info_frame,
            text=f"Build Date: {build_date}",
            font=('Segoe UI', 11),
            text_color=COLORS['text_secondary']
        ).pack(anchor='w', pady=(4, 0))

        links_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        links_frame.pack(fill='x', pady=8)

        ctk.CTkButton(
            links_frame,
            text="GitHub Repo",
            width=120,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=lambda: webbrowser.open("https://github.com/jameshorton2486/app_launcher")
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            links_frame,
            text="Documentation",
            width=120,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=lambda: webbrowser.open("https://github.com/jameshorton2486/app_launcher")
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            links_frame,
            text="Report Issue",
            width=120,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=lambda: webbrowser.open("https://github.com/jameshorton2486/app_launcher/issues")
        ).pack(side='left')

        actions_frame = ctk.CTkFrame(section.content, fg_color='transparent')
        actions_frame.pack(fill='x', pady=10)

        ctk.CTkButton(
            actions_frame,
            text="Reset to Defaults",
            width=160,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            command=self.reset_to_defaults
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            actions_frame,
            text="Export Settings",
            width=140,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.export_settings
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            actions_frame,
            text="Import Settings",
            width=140,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.import_settings
        ).pack(side='left')

    def _add_checkbox(self, parent, label, variable):
        checkbox = ctk.CTkCheckBox(
            parent,
            text=label,
            variable=variable,
            font=('Segoe UI', 12),
            text_color=COLORS['text_primary']
        )
        checkbox.pack(fill='x', pady=5)

    def _add_dropdown(self, parent, label, variable, values, on_change=None):
        frame = ctk.CTkFrame(parent, fg_color='transparent')
        frame.pack(fill='x', pady=6)

        ctk.CTkLabel(frame, text=label, font=('Segoe UI', 12)).pack(side='left')
        dropdown = ctk.CTkOptionMenu(
            frame,
            values=values,
            variable=variable,
            width=200,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['bg_tertiary'],
            button_hover_color=COLORS['accent_secondary'],
            command=lambda value: (on_change(value) if on_change else None, self._queue_save())
        )
        dropdown.pack(side='right')

    def _add_path_field(self, parent, label_text, setting_key, var=None):
        frame = ctk.CTkFrame(parent, fg_color='transparent')
        frame.pack(fill='x', pady=6)

        ctk.CTkLabel(frame, text=label_text, font=('Segoe UI', 12)).pack(side='left')

        entry_var = var or tk.StringVar(value=self._get_setting(setting_key, ''))
        entry = ctk.CTkEntry(frame, width=360, textvariable=entry_var, font=('Segoe UI', 11))
        entry.pack(side='left', padx=(10, 10))

        ctk.CTkButton(
            frame,
            text="Browse",
            width=90,
            command=lambda: self.browse_path(entry_var, setting_key)
        ).pack(side='left')

        if setting_key:
            self.paths_entries[setting_key] = entry_var
            entry_var.trace_add("write", lambda *_: self._validate_path(setting_key, entry_var.get()))
            entry_var.trace_add("write", lambda *_: self._queue_save())

        return frame

    def browse_path(self, entry_var, setting_key):
        current = entry_var.get()
        if setting_key and 'external_tools' in setting_key:
            path = filedialog.askopenfilename(initialdir=os.path.dirname(current) if current else os.path.expanduser('~'))
        else:
            path = filedialog.askdirectory(initialdir=current if os.path.isdir(current) else os.path.expanduser('~'))
        if path:
            entry_var.set(path)

    def change_hotkey(self):
        from src.components.hotkey_capture_dialog import HotkeyCaptureDialog
        current = self.hotkey_entry.get().replace(' + ', '+').replace('Win', 'win').replace(' ', '')
        dialog = HotkeyCaptureDialog(self, current)
        self.wait_window(dialog)
        if dialog.result:
            hotkey_display = dialog.result.replace('+', ' + ').replace('windows', 'Win').replace('win', 'Win')
            self.hotkey_entry.configure(state='normal')
            self.hotkey_entry.delete(0, 'end')
            self.hotkey_entry.insert(0, hotkey_display)
            self.hotkey_entry.configure(state='readonly')
            self._queue_save()

    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.accent_color)[1]
        if color:
            self.accent_color = color
            self.color_preview.configure(fg_color=color)
            self._queue_save()

    def _toggle_custom_ide(self, value):
        if value == 'Custom':
            self.custom_ide_frame.pack(fill='x', pady=6)
        else:
            self.custom_ide_frame.pack_forget()

    def _validate_path(self, setting_key: str, path_value: str):
        if not setting_key:
            return
        valid = True
        if path_value:
            if 'external_tools' in setting_key:
                valid = os.path.isfile(path_value)
            else:
                valid = os.path.isdir(path_value)
        if not valid:
            self.save_status.configure(text=f"Invalid path: {setting_key}", text_color=COLORS['error'])
        else:
            self.save_status.configure(text="", text_color=COLORS['text_secondary'])
        return valid

    def _queue_save(self):
        if self._save_timer:
            self.after_cancel(self._save_timer)
        self._save_timer = self.after(400, self._save_settings)

    def _save_settings(self):
        if not self._validate_all_paths():
            return

        self._set_setting('window.start_with_windows', self.start_with_windows.get())
        self._set_setting('window.start_minimized', self.start_minimized.get())
        self._set_setting('window.minimize_to_tray', self.minimize_to_tray.get())
        self._set_setting('updates.check_on_start', self.check_updates.get())

        hotkey_value = self.hotkey_entry.get().replace(' + ', '+').replace('Win', 'win').replace(' ', '').lower()
        self._set_setting('window.global_hotkey', hotkey_value)

        self._set_setting('theme.mode', self.theme_mode.get())
        self._set_setting('theme.accent_color', self.accent_color)

        self._set_setting('appearance.sidebar_style', self.sidebar_style.get())
        self._set_setting('appearance.button_size', self.button_size.get())
        self._set_setting('appearance.show_descriptions', self.show_descriptions.get())
        self._set_setting('appearance.compact_mode', self.compact_mode.get())
        self._set_setting('appearance.font_size', self.font_size.get())

        for key, entry_var in self.paths_entries.items():
            self._set_setting(key, entry_var.get())

        self._set_setting('developer.default_ide', self.default_ide.get())
        self._set_setting('developer.custom_ide_path', self.custom_ide_path.get())
        self._set_setting('developer.default_terminal', self.default_terminal.get())
        self._set_setting('developer.github_desktop_path', self.github_desktop_path.get())
        self._set_setting('developer.auto_git_fetch', self.auto_git_fetch.get())
        self._set_setting('developer.git_refresh_interval', self.git_refresh_interval.get())

        self._set_setting('optimization.show_security_warnings', self.show_security_warnings.get())
        self._set_setting('optimization.confirm_service_changes', self.confirm_service_changes.get())
        self._set_setting('optimization.log_system_changes', self.log_system_changes.get())
        self._set_setting('optimization.show_hw_recommendations', self.show_hw_recommendations.get())

        try:
            self.config_manager.save_settings(self.settings)
            self.save_status.configure(text="Saved", text_color=COLORS['text_secondary'])
            if self.on_save:
                self.on_save(self.settings)
        except Exception as exc:
            logger.error(f"Settings save failed: {exc}")
            self.save_status.configure(text="Save failed", text_color=COLORS['error'])

    def _validate_all_paths(self) -> bool:
        for key, var in self.paths_entries.items():
            if not self._validate_path(key, var.get()):
                return False
        return True

    def reset_to_defaults(self):
        import tkinter.messagebox as messagebox
        confirm = messagebox.askyesno("Reset Settings", "Reset all settings to defaults?")
        if not confirm:
            return

        backup_dir = os.path.join(os.path.dirname(SETTINGS_FILE), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(SETTINGS_FILE):
            backup_path = os.path.join(backup_dir, f"settings_{timestamp}.json")
            os.replace(SETTINGS_FILE, backup_path)

        defaults = ConfigManager().load_settings()
        self.settings = defaults
        self.config_manager.save_settings(defaults)
        self._reload_from_settings()
        self.save_status.configure(text="Defaults restored", text_color=COLORS['text_secondary'])

    def export_settings(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.settings, handle, indent=2)
        self.save_status.configure(text="Settings exported", text_color=COLORS['text_secondary'])

    def import_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.settings = data
            self.config_manager.save_settings(self.settings)
            self._reload_from_settings()
            self.save_status.configure(text="Settings imported", text_color=COLORS['text_secondary'])
        except Exception as exc:
            logger.error(f"Import failed: {exc}")
            self.save_status.configure(text="Import failed", text_color=COLORS['error'])

    def _reload_from_settings(self):
        self.start_with_windows.set(self._get_setting('window.start_with_windows', False))
        self.start_minimized.set(self._get_setting('window.start_minimized', False))
        self.minimize_to_tray.set(self._get_setting('window.minimize_to_tray', True))
        self.check_updates.set(self._get_setting('updates.check_on_start', True))

        self.theme_mode.set(self._get_setting('theme.mode', 'dark'))
        self.sidebar_style.set(self._get_setting('appearance.sidebar_style', 'Expanded'))
        self.button_size.set(self._get_setting('appearance.button_size', 'Medium'))
        self.show_descriptions.set(self._get_setting('appearance.show_descriptions', True))
        self.compact_mode.set(self._get_setting('appearance.compact_mode', False))
        self.font_size.set(self._get_setting('appearance.font_size', 14))

        current_hotkey = self._get_setting('window.global_hotkey', 'win+shift+l')
        self.hotkey_entry.configure(state='normal')
        self.hotkey_entry.delete(0, 'end')
        self.hotkey_entry.insert(0, current_hotkey.replace('+', ' + ').replace('win', 'Win'))
        self.hotkey_entry.configure(state='readonly')

        self.accent_color = self._get_setting('theme.accent_color', COLORS['accent_primary'])
        self.color_preview.configure(fg_color=self.accent_color)

        for key, var in self.paths_entries.items():
            var.set(self._get_setting(key, ''))

        self.default_ide.set(self._get_setting('developer.default_ide', 'VS Code'))
        self.custom_ide_path.set(self._get_setting('developer.custom_ide_path', ''))
        self.default_terminal.set(self._get_setting('developer.default_terminal', 'Windows Terminal'))
        self.github_desktop_path.set(self._get_setting('developer.github_desktop_path', ''))
        self.auto_git_fetch.set(self._get_setting('developer.auto_git_fetch', False))
        self.git_refresh_interval.set(self._get_setting('developer.git_refresh_interval', 60))

        self.show_security_warnings.set(self._get_setting('optimization.show_security_warnings', True))
        self.confirm_service_changes.set(self._get_setting('optimization.confirm_service_changes', True))
        self.log_system_changes.set(self._get_setting('optimization.log_system_changes', False))
        self.show_hw_recommendations.set(self._get_setting('optimization.show_hw_recommendations', True))

    def _get_setting(self, key_path: str, default=None):
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _set_setting(self, key_path: str, value):
        keys = key_path.split('.')
        target = self.settings
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
