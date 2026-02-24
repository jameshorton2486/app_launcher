"""
Main Application Class
CustomTkinter application with tabbed interface
"""

import customtkinter as ctk
import os
import threading
import psutil
import tkinter as tk
from datetime import datetime
from pathlib import Path
import subprocess
import sys


from src.theme import COLORS, SPACING, apply_theme
from src.components.button_3d import Button3D, BUTTON_COLORS
from src.config_manager import ConfigManager
from src.components.search_bar import SearchBar
from src.components.status_bar import StatusBar
from src.components.toast import ToastManager
from src.components.command_palette import CommandPalette
from src.components.help_manual import HelpManual
from src.tabs.dashboard_tab import DashboardTab
from src.tabs.projects_tab import ProjectsTab
from src.tabs.downloads_tab import DownloadsTab
from src.tabs.optimization_tab import OptimizationTab
from src.tabs.maintenance_tab import MaintenanceTab
from src.tabs.settings_tab import SettingsTab
from src.services.process_service import ProcessService
from src.services.cleanup_service import CleanupService
from src.utils.system_tray import start_tray_icon
from src.utils.startup_manager import StartupManager
from src.utils.hotkey_manager import HotkeyManager
from src.utils.logger import logger

SIDEBAR_WIDTH_EXPANDED = 240
SIDEBAR_WIDTH_COLLAPSED = 72
SIDEBAR_ITEM_HEIGHT = 48  # Larger click targets


class SidebarNavItem(ctk.CTkFrame):
    """Sidebar navigation item with hover and active states."""

    def __init__(self, parent, label: str, icon: str, command, show_indicator: bool = False, shortcut: str = ""):
        super().__init__(parent, fg_color='transparent', corner_radius=10, height=SIDEBAR_ITEM_HEIGHT)
        self.label_text = label
        self.icon = icon
        self.command = command
        self._active = False
        self._collapsed = False
        self._show_indicator = show_indicator
        self.shortcut_text = shortcut

        self.pack_propagate(False)

        self.left_border = ctk.CTkFrame(self, width=4, fg_color='transparent', corner_radius=0)
        self.left_border.pack(side='left', fill='y')

        self.content = ctk.CTkFrame(self, fg_color='transparent', corner_radius=8)
        self.content.pack(side='left', fill='both', expand=True)

        self.label = ctk.CTkLabel(
            self.content,
            text=self._format_label(),
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        self.label.pack(side='left', fill='both', expand=True, padx=20)

        self.shortcut_label = ctk.CTkLabel(
            self.content,
            text=self._format_shortcut(),
            font=('Segoe UI', 9),
            text_color=COLORS['text_tertiary'],
            anchor='e'
        )
        self.shortcut_label.pack(side='right', padx=(0, 8))

        self.indicator = ctk.CTkLabel(
            self.content,
            text="●" if self._show_indicator else "",
            font=('Segoe UI', 10, 'bold'),
            text_color=COLORS['success'],
            anchor='e'
        )
        self.indicator.pack(side='right', padx=12)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        for widget in (self.left_border, self.content, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _format_label(self) -> str:
        if self._collapsed:
            if self.icon:
                return self.icon
            return self.label_text[:1]
        if self.icon:
            return f"{self.icon}  {self.label_text}"
        return self.label_text

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.left_border.configure(fg_color=COLORS['accent_primary'], width=4)
            self.content.configure(fg_color=COLORS['bg_hover'])
            self.label.configure(text_color=COLORS['text_primary'], font=('Segoe UI', 12, 'bold'))
        else:
            self.left_border.configure(fg_color='transparent', width=4)
            self.content.configure(fg_color='transparent')
            self.label.configure(text_color=COLORS['text_secondary'], font=('Segoe UI', 12, 'bold'))

    def set_collapsed(self, collapsed: bool):
        self._collapsed = collapsed
        self.label.configure(text=self._format_label())
        self.shortcut_label.configure(text=self._format_shortcut())

    def _format_shortcut(self) -> str:
        if self._collapsed:
            return ""
        return self.shortcut_text or ""

    def set_indicator(self, level: str):
        if not self._show_indicator:
            return
        color_map = {
            "green": COLORS['success'],
            "yellow": COLORS['warning'],
            "red": COLORS['error']
        }
        self.indicator.configure(text_color=color_map.get(level, COLORS['success']))

    def _on_enter(self, event=None):
        if not self._active:
            self.content.configure(fg_color=COLORS['bg_hover'])

    def _on_leave(self, event=None):
        if not self._active:
            self.content.configure(fg_color='transparent')

    def _on_click(self, event=None):
        if callable(self.command):
            self.command()


class AppLauncher(ctk.CTk):
    """Main application window"""
    
    def __init__(self, enabled_tabs=None, show_power_tools_button: bool = False,
                 power_tools_command=None, dashboard_read_only: bool = False,
                 validate_tools_on_startup: bool = False, window_title: str | None = None,
                 sidebar_title: str | None = None, show_app_selector: bool | None = None):
        super().__init__()
        
        try:
            self._all_tabs = ["Dashboard", "Projects", "Downloads", "Maintenance", "Optimization", "Settings"]
            if enabled_tabs:
                self._enabled_tabs = [t for t in self._all_tabs if t in enabled_tabs]
            else:
                self._enabled_tabs = list(self._all_tabs)

            self._show_power_tools_button = show_power_tools_button
            self._power_tools_command = power_tools_command
            self._dashboard_read_only = dashboard_read_only
            self._validate_tools_on_startup = validate_tools_on_startup
            self._window_title = window_title
            self._sidebar_title_text = sidebar_title or "App Launcher"
            self._sidebar_title_short = "".join(
                word[0] for word in self._sidebar_title_text.split() if word
            ) or "AL"
            self._show_app_selector = show_app_selector
            self._app_selector_open = False

            # Initialize config manager
            self.config_manager = ConfigManager()
            
            # Load settings
            self.settings = self.config_manager.settings

            if self._show_app_selector is None:
                self._show_app_selector = self.config_manager.get_setting('ui.show_app_selector', True)
            
            # Initialize services
            self.process_service = ProcessService()
            self.cleanup_service = CleanupService()
            self.hotkey_manager = HotkeyManager()
            
            # Tray icon
            self.tray_icon = None
            self._first_minimize = True  # Track first minimize for notification
            self._is_shutting_down = False
            
            # Tab instances (will be created in setup_ui)
            self.projects_tab = None
            self.downloads_tab = None
            self.optimization_tab = None
            self.maintenance_tab = None
            
            # Apply theme (read from config)
            theme_mode = self.config_manager.get_setting('theme.mode', 'dark')
            accent_color = self.config_manager.get_setting('theme.accent_color', COLORS.get('accent_primary'))
            apply_theme(self, mode=theme_mode, accent_color=accent_color)
            
            # Configure window
            self.setup_window()
            
            # Setup UI
            self.setup_ui()
            
            # Setup system integration
            self.setup_system_integration()

            if self._validate_tools_on_startup:
                self._run_tool_self_check()
            
            # Bind close event
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print("[INFO] Application initialized successfully")
            logger.info("Application initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize application: {e}")
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
    
    def setup_window(self):
        """Configure main window with position/size persistence"""
        try:
            width = self.config_manager.get_setting('window.width', 900)
            height = self.config_manager.get_setting('window.height', 650)
            
            self.title(self._window_title or "James's Project Launcher (v2.0)")
            self.minsize(700, 500)
            
            # Set window background
            self.configure(fg_color=COLORS['bg_primary'])
            
            # Try to load saved window position
            saved_x = self.config_manager.get_setting('window.x', None)
            saved_y = self.config_manager.get_setting('window.y', None)
            
            if saved_x is not None and saved_y is not None:
                # Restore saved position
                self.geometry(f"{width}x{height}+{saved_x}+{saved_y}")
                # Verify window is on screen
                self.update_idletasks()
                if self._is_window_on_screen():
                    logger.debug(f"Restored window position: {saved_x}, {saved_y}")
                else:
                    # Position is off-screen, center instead
                    self.center_window()
            else:
                # No saved position, center on screen
                self.geometry(f"{width}x{height}")
                self.center_window()
            
            # Set window icon if available
            self._set_window_icon()
            
            # Save window position/size on move/resize
            self.bind('<Configure>', self._on_window_configure)
            logger.debug("Window setup complete")
        except Exception as e:
            logger.error(f"Error in setup_window: {e}", exc_info=True)
            print(f"[ERROR] Window setup failed: {e}")
            raise
    
    def _is_window_on_screen(self) -> bool:
        """Check if window is visible on any screen"""
        try:
            x = self.winfo_x()
            y = self.winfo_y()
            width = self.winfo_width()
            height = self.winfo_height()
            
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # Check if any part of window is on screen
            return (x + width > 0 and x < screen_width and
                    y + height > 0 and y < screen_height)
        except Exception as e:
            logger.debug(f"Could not check window position: {e}")
            return False
    
    def _on_window_configure(self, event=None):
        """Save window position and size when changed"""
        if event and event.widget == self:
            try:
                # Only save if window is not minimized
                if self.state() != 'iconic':
                    x = self.winfo_x()
                    y = self.winfo_y()
                    width = self.winfo_width()
                    height = self.winfo_height()
                    
                    # Update settings
                    settings = self.config_manager.settings
                    settings['window']['x'] = x
                    settings['window']['y'] = y
                    settings['window']['width'] = width
                    settings['window']['height'] = height
                    
                    # Save to file (debounced - only save after user stops resizing)
                    if hasattr(self, '_save_window_timer'):
                        self.after_cancel(self._save_window_timer)
                    self._save_window_timer = self.after(1000, self._save_window_settings)
            except Exception as e:
                logger.debug(f"Error saving window position: {e}")
    
    def _save_window_settings(self):
        """Save window settings to config"""
        try:
            if self._is_shutting_down:
                return
            self.config_manager.save_settings(self.config_manager.settings)
        except Exception as e:
            logger.warning(f"Failed to save window settings: {e}")
    
    def _set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    'assets', 'icons', 'app_icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                logger.debug("Window icon set")
        except Exception as e:
            logger.debug(f"Could not set window icon: {e}")
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width() or 900
        height = self.winfo_height() or 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Set up the main UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.main_container.pack(fill='both', expand=True)

        # Sidebar + content layout
        self.layout_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.layout_frame.pack(fill='both', expand=True)

        self.sidebar = ctk.CTkFrame(self.layout_frame, fg_color=COLORS['bg_primary'], corner_radius=0, width=SIDEBAR_WIDTH_EXPANDED)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        self.content_container = ctk.CTkFrame(self.layout_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.content_container.pack(side='left', fill='both', expand=True)

        # Search bar at top of content
        self.search_bar = SearchBar(
            self.content_container,
            on_search_callback=self.on_search
        )
        self.search_bar.pack(fill='x', padx=0, pady=0)

        # Content frame
        self.content_frame = ctk.CTkFrame(self.content_container, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.content_frame.pack(fill='both', expand=True, padx=40, pady=32)

        # Status bar at bottom
        self.status_bar = StatusBar(
            self.content_container,
            on_settings_click=self.open_settings if "Settings" in self._enabled_tabs else None,
            on_help_click=self.show_shortcuts_help,
            on_screenshot_click=self.capture_screenshot,
            show_settings="Settings" in self._enabled_tabs
        )
        self.status_bar.pack(fill='x', side='bottom', padx=0, pady=0)

        self._sidebar_expanded = True
        self._nav_items = {}
        self._current_view = None
        self._startup_health_notified = False

        self._build_sidebar()
        self._build_views()
        self._build_menu()
        self._bind_shortcuts()

        initial_view = "Dashboard" if "Dashboard" in self._enabled_tabs else (self._enabled_tabs[0] if self._enabled_tabs else None)
        if initial_view:
            self.show_view(initial_view)
        ToastManager.set_root(self)

        # Update status
        self.status_bar.set_status("Ready")

        # Start git status monitoring for status bar
        self.start_git_status_monitoring()

        if self._show_app_selector:
            self.after(250, self._show_app_selector_dialog)

    def _build_sidebar(self):
        _pad = SPACING.get("md", 12)
        header_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        header_frame.pack(fill='x', padx=_pad, pady=(_pad, _pad))

        self.sidebar_title = ctk.CTkLabel(
            header_frame,
            text=self._sidebar_title_text,
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        self.sidebar_title.pack(side='left', fill='x', expand=True)

        self.sidebar_toggle = Button3D(
            header_frame,
            text="☰",
            width=32,
            height=28,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.toggle_sidebar
        )
        self.sidebar_toggle.pack(side='right')

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        nav_frame.pack(fill='both', expand=True, padx=_pad, pady=_pad)

        nav_items = [
            ("Dashboard", "🏠"),
            ("Projects", "🚀"),
            ("Downloads", "⬇️"),
            ("Maintenance", "🛠"),
            ("Optimization", "⚡"),
            ("Settings", "⚙"),
        ]
        shortcuts = self._get_tab_shortcuts()

        for name, icon in nav_items:
            if name not in self._enabled_tabs:
                continue
            shortcut = shortcuts.get(name, "")
            item = SidebarNavItem(
                nav_frame,
                label=name,
                icon=icon,
                command=lambda n=name: self.show_view(n),
                show_indicator=(name == "Dashboard"),
                shortcut=shortcut
            )
            item.pack(fill='x', pady=4)
            self._nav_items[name] = item

        footer_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        footer_frame.pack(fill='x', side='bottom', padx=_pad, pady=_pad)

        footer_top = ctk.CTkFrame(footer_frame, fg_color='transparent')
        footer_top.pack(fill='x')

        self.ram_label = ctk.CTkLabel(
            footer_top,
            text="RAM: --%",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        self.ram_label.pack(side='left', fill='x', expand=True)

        shortcuts_btn = Button3D(
            footer_top,
            text="?",
            width=28,
            height=24,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.show_shortcuts_help
        )
        shortcuts_btn.pack(side='right')

        self.version_label = ctk.CTkLabel(
            footer_frame,
            text="v2.0.0",
            font=('Segoe UI', 10),
            text_color=COLORS['text_tertiary'],
            anchor='w'
        )
        self.version_label.pack(fill='x', pady=(6, 0))

        help_btn = Button3D(
            footer_frame,
            text="📖 Help Manual",
            height=28,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.open_help_manual
        )
        help_btn.pack(fill='x', pady=(10, 0))

        if self._show_power_tools_button:
            power_tools_btn = Button3D(
                footer_frame,
                text="🧰 Open Power Tools",
                height=32,
                bg_color=BUTTON_COLORS.SECONDARY,
                command=self._open_power_tools
            )
            power_tools_btn.pack(fill='x', pady=(10, 0))

        self.after(1000, self._update_ram_usage)

    def _build_views(self):
        self.views = {}

        if "Dashboard" in self._enabled_tabs:
            dashboard_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.dashboard_tab = DashboardTab(
                dashboard_view,
                self.config_manager,
                process_service=self.process_service,
                status_bar=self.status_bar,
                on_open_downloads=(lambda: self.show_view('Downloads')) if "Downloads" in self._enabled_tabs and not self._dashboard_read_only else None,
                on_health_update=self._handle_health_update,
                read_only=self._dashboard_read_only
            )
            self.dashboard_tab.pack(fill='both', expand=True)
            self.views["Dashboard"] = dashboard_view
            self._dashboard_initialized = True

        if "Downloads" in self._enabled_tabs:
            downloads_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.downloads_tab = DownloadsTab(
                downloads_view,
                self.config_manager,
                status_bar=self.status_bar
            )
            self.downloads_tab.pack(fill='both', expand=True)
            self.views["Downloads"] = downloads_view

        if "Projects" in self._enabled_tabs:
            projects_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.projects_tab = ProjectsTab(projects_view, self.config_manager)
            self.projects_tab.pack(fill='both', expand=True)
            self.views["Projects"] = projects_view

        if "Optimization" in self._enabled_tabs:
            optimization_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.optimization_tab = OptimizationTab(optimization_view, self.config_manager)
            self.optimization_tab.pack(fill='both', expand=True)
            self.views["Optimization"] = optimization_view

        if "Maintenance" in self._enabled_tabs:
            maintenance_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.maintenance_tab = MaintenanceTab(maintenance_view, self.config_manager)
            self.maintenance_tab.pack(fill='both', expand=True)
            self.views["Maintenance"] = maintenance_view

        if "Settings" in self._enabled_tabs:
            settings_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
            self.settings_tab = SettingsTab(settings_view, self.config_manager, on_save=self.on_settings_saved)
            self.settings_tab.pack(fill='both', expand=True)
            self.views["Settings"] = settings_view

    def show_view(self, view_name: str):
        if view_name not in self.views:
            logger.warning(f"View not found: {view_name}")
            return

        if self._current_view:
            self.views[self._current_view].pack_forget()

        self.views[view_name].pack(fill='both', expand=True)
        self._current_view = view_name

        for name, item in self._nav_items.items():
            item.set_active(name == view_name)

        if view_name == "Downloads" and self.downloads_tab and not getattr(self.downloads_tab, '_initialized', False):
            self.status_bar.set_status("Loading downloads...")
            self.after(0, self._initialize_downloads_tab)

    def toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        width = SIDEBAR_WIDTH_EXPANDED if self._sidebar_expanded else SIDEBAR_WIDTH_COLLAPSED
        self.sidebar.configure(width=width)
        self.sidebar.pack_propagate(False)

        self.sidebar_title.configure(
            text=self._sidebar_title_text if self._sidebar_expanded else self._sidebar_title_short
        )

        for item in self._nav_items.values():
            item.set_collapsed(not self._sidebar_expanded)

    def _update_ram_usage(self):
        if self._is_shutting_down:
            return
        try:
            ram_percent = psutil.virtual_memory().percent
            self.ram_label.configure(text=f"RAM: {ram_percent:.0f}%")
        except Exception:
            self.ram_label.configure(text="RAM: --%")
        self.after(5000, self._update_ram_usage)
    
    def on_tab_changed(self, tab_name):
        """Handle tab change event with lazy loading"""
        pass
    
    def _initialize_downloads_tab(self):
        """Initialize downloads tab (lazy loading)"""
        try:
            if self.downloads_tab and not getattr(self.downloads_tab, '_initialized', False):
                self.downloads_tab.refresh_files()
                self.downloads_tab._initialized = True
                self._dashboard_initialized = True
                self.status_bar.set_status("Downloads loaded")
        except Exception as e:
            logger.error(f"Error initializing downloads tab: {e}", exc_info=True)
            self.status_bar.set_status("Error loading downloads")
    
    def open_settings(self):
        """Open settings view"""
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
            self.show_view('Settings')
        except Exception as e:
            logger.error(f"Error opening settings: {e}", exc_info=True)
            self.status_bar.set_status("Error opening settings")

    def capture_screenshot(self):
        """Capture entire screen to file"""
        try:
            from PIL import ImageGrab
            
            # Get screenshots folder from settings
            screenshots_folder = self.config_manager.get_setting(
                'paths.screenshots_folder',
                os.path.join(os.path.expanduser('~'), 'Documents', 'Screenshots')
            )
            os.makedirs(screenshots_folder, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"app_launcher_{timestamp}.png"
            filepath = os.path.join(screenshots_folder, filename)
            
            # Capture full screen
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            self.status_bar.set_status(f"Screenshot saved: {filename}")
            if ToastManager:
                ToastManager.show_success("Screenshot", f"Saved to {filename}")
        except ImportError as e:
            msg = "Pillow required for screenshots (pip install Pillow)"
            logger.error(msg)
            self.status_bar.set_status("Screenshot failed")
            if ToastManager:
                ToastManager.show_error("Screenshot", msg)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}", exc_info=True)
            self.status_bar.set_status("Screenshot failed")
            if ToastManager:
                ToastManager.show_error("Screenshot", str(e))

    def open_command_palette(self):
        """Open command palette modal"""
        try:
            CommandPalette(self, self.config_manager, allowed_tabs=self._enabled_tabs)
        except Exception as e:
            logger.error(f"Error opening command palette: {e}", exc_info=True)

    def open_help_manual(self):
        """Open help manual modal"""
        try:
            HelpManual(self, allowed_tabs=self._enabled_tabs)
        except Exception as e:
            logger.error(f"Error opening help manual: {e}", exc_info=True)

    def show_shortcuts_help(self):
        """Show keyboard shortcuts dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("520x360")
        dialog.configure(fg_color=COLORS['bg_primary'])
        dialog.transient(self)
        dialog.grab_set()
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 520) // 2
        y = self.winfo_y() + (self.winfo_height() - 360) // 2
        dialog.geometry(f"520x360+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_primary'])
        frame.pack(fill='both', expand=True, padx=24, pady=24)

        title = ctk.CTkLabel(
            frame,
            text="Keyboard Shortcuts",
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor='w', pady=(0, 12))

        shortcuts = self._get_tab_shortcuts()
        navigation_lines = [f"{key:<11} {tab}" for tab, key in shortcuts.items()]
        if not navigation_lines:
            navigation_lines = ["(No tabs available)"]
        navigation_text = "\n".join(navigation_lines)

        body = (
            "Navigation\n"
            "Ctrl+1-6     Switch tabs\n"
            f"{navigation_text}\n"
            "Ctrl+K       Command Palette\n"
            "Escape       Close dialogs\n\n"
            "Actions\n"
            "Ctrl+R       Refresh\n"
            "F5           Refresh Dashboard\n"
            "Ctrl+F       Focus search\n"
            "F1           Help Manual\n"
            "Ctrl+Shift+S Capture screenshot\n\n"
            "Global\n"
            "Win+Shift+L  Show/Hide app"
        )
        ctk.CTkLabel(
            frame,
            text=body,
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            justify='left',
            anchor='w'
        ).pack(fill='x')

        Button3D(
            frame,
            text="Close",
            width=120,
            height=36,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=dialog.destroy
        ).pack(pady=20)

    def _get_tab_shortcuts(self) -> dict:
        shortcuts = {}
        tab_order = self._all_tabs
        for index, tab in enumerate(tab_order, start=1):
            if tab in self._enabled_tabs:
                shortcuts[tab] = f"Ctrl+{index}"
        return shortcuts

    def _bind_shortcuts(self):
        self.bind_all("<Control-k>", lambda event=None: self.open_command_palette())
        self.bind_all("<Control-K>", lambda event=None: self.open_command_palette())
        self.bind_all("<Control-f>", lambda event=None: self.focus_search())
        self.bind_all("<Control-F>", lambda event=None: self.focus_search())
        self.bind_all("<Control-r>", lambda event=None: self.refresh_current_view())
        self.bind_all("<Control-R>", lambda event=None: self.refresh_current_view())
        self.bind_all("<Control-Shift-s>", lambda event=None: self.capture_screenshot())
        self.bind_all("<Control-Shift-S>", lambda event=None: self.capture_screenshot())
        self.bind_all("<F5>", lambda event=None: self.refresh_dashboard())
        self.bind_all("<F1>", lambda event=None: self.open_help_manual())
        self.bind_all("<Escape>", lambda event=None: self.handle_escape())

        if "Dashboard" in self._enabled_tabs:
            self.bind_all("<Control-1>", lambda event=None: self.show_view('Dashboard'))
        if "Projects" in self._enabled_tabs:
            self.bind_all("<Control-2>", lambda event=None: self.show_view('Projects'))
        if "Downloads" in self._enabled_tabs:
            self.bind_all("<Control-3>", lambda event=None: self.show_view('Downloads'))
        if "Maintenance" in self._enabled_tabs:
            self.bind_all("<Control-4>", lambda event=None: self.show_view('Maintenance'))
        if "Optimization" in self._enabled_tabs:
            self.bind_all("<Control-5>", lambda event=None: self.show_view('Optimization'))
        if "Settings" in self._enabled_tabs:
            self.bind_all("<Control-6>", lambda event=None: self.show_view('Settings'))

    def _open_power_tools(self):
        try:
            if callable(self._power_tools_command):
                self._power_tools_command()
                return
            if isinstance(self._power_tools_command, (list, tuple)):
                subprocess.Popen(list(self._power_tools_command), cwd=str(Path.cwd()))
                return
            if isinstance(self._power_tools_command, str) and self._power_tools_command.strip():
                subprocess.Popen(self._power_tools_command, cwd=str(Path.cwd()), shell=True)
                return
            raise ValueError("Power tools launch command not configured")
        except Exception as e:
            logger.error(f"Failed to launch Power Tools: {e}", exc_info=True)
            if ToastManager:
                ToastManager.show_error("Power Tools", "Failed to launch Power Tools.")
            self.status_bar.set_status("Failed to launch Power Tools")

    def _run_tool_self_check(self):
        try:
            from src.utils.constants import TOOLS_FILE
            from src.utils.tool_registry import ToolRegistry
            registry = ToolRegistry()
            registry.load_tools(TOOLS_FILE)
            issues = registry.validate_tools(self.config_manager)
            if issues:
                logger.warning("Tool self-check found %s issues", len(issues))
            else:
                logger.info("Tool self-check passed")
        except Exception as e:
            logger.warning(f"Tool self-check failed: {e}", exc_info=True)

    def _show_app_selector_dialog(self):
        if self._app_selector_open:
            return
        self._app_selector_open = True

        dialog = ctk.CTkToplevel(self)
        dialog.title("Choose App")
        dialog.geometry("520x280")
        dialog.configure(fg_color=COLORS['bg_primary'])
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_primary'])
        frame.pack(fill='both', expand=True, padx=24, pady=24)

        title = ctk.CTkLabel(
            frame,
            text="Choose your workspace",
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor='w', pady=(0, 8))

        subtitle = ctk.CTkLabel(
            frame,
            text="Launch projects here, or open the Power Tools for advanced system actions.",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            justify='left',
            anchor='w',
            wraplength=440
        )
        subtitle.pack(anchor='w', pady=(0, 16))

        actions = ctk.CTkFrame(frame, fg_color='transparent')
        actions.pack(fill='x', pady=(8, 0))

        Button3D(
            actions,
            text="Continue in App Launcher",
            width=220,
            height=36,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=lambda: (dialog.destroy(), setattr(self, "_app_selector_open", False))
        ).pack(side='left', padx=(0, 12))

        Button3D(
            actions,
            text="Open Power Tools",
            width=180,
            height=36,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=lambda: (dialog.destroy(), setattr(self, "_app_selector_open", False), self._open_power_tools())
        ).pack(side='left')

        dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), setattr(self, "_app_selector_open", False)))

    def focus_search(self):
        try:
            self.search_bar.search_entry.focus_set()
        except Exception as e:
            logger.debug(f"Suppressed exception in focus_search: {e}")

    def refresh_dashboard(self):
        if hasattr(self, 'dashboard_tab') and self.dashboard_tab:
            try:
                self.dashboard_tab._refresh_system_stats()
            except Exception as e:
                logger.debug(f"Suppressed exception in refresh_dashboard: {e}")

    def refresh_current_view(self):
        if self._current_view == "Downloads" and self.downloads_tab:
            self.downloads_tab.refresh_files()
        elif self._current_view == "Projects" and self.projects_tab:
            self.projects_tab.refresh_all_git_status()
        elif self._current_view == "Dashboard":
            self.refresh_dashboard()

    def handle_escape(self):
        # Close command palette if open
        for widget in self.winfo_children():
            if isinstance(widget, CommandPalette):
                widget.close()
                return
    
    def on_settings_saved(self, settings):
        """Handle settings save"""
        try:
            # Reload settings
            self.settings = settings
            if hasattr(self, 'settings_tab') and self.settings_tab:
                self.settings_tab.settings = settings.copy()
            
            # Update startup if needed
            from src.utils.startup_manager import StartupManager
            start_with_windows = settings.get('window', {}).get('start_with_windows', False)
            start_minimized = settings.get('window', {}).get('start_minimized', False)
            startup_enabled = StartupManager.is_startup_enabled()
            
            if start_with_windows:
                # Enable startup with appropriate minimized flag
                # Always update to ensure correct flags are set
                if StartupManager.enable_startup(start_minimized):
                    logger.info(f"Startup enabled (minimized={start_minimized})")
                else:
                    logger.warning("Failed to enable startup")
            else:
                # Disable startup
                if startup_enabled:
                    if StartupManager.disable_startup():
                        logger.info("Startup disabled")
                    else:
                        logger.warning("Failed to disable startup")
            
            # Update hotkey if changed
            new_hotkey = settings.get('window', {}).get('global_hotkey', 'win+shift+l')
            current_hotkey = self.config_manager.get_setting('window.global_hotkey', 'win+shift+l')
            
            if new_hotkey != current_hotkey:
                # Unregister old hotkey
                self.hotkey_manager.unregister()
                
                # Register new hotkey
                success, message = self.hotkey_manager.register(new_hotkey, self.toggle_window)
                if success:
                    logger.info(f"Hotkey updated: {message}")
                    self.status_bar.set_status("Hotkey updated")
                else:
                    logger.warning(f"Failed to update hotkey: {message}")
                    self.status_bar.set_status(f"Hotkey error: {message}")
                    # Show error message
                    import tkinter.messagebox as msgbox
                    msgbox.showerror("Hotkey Error", message)
            
            logger.info("Settings saved successfully")
            self.status_bar.set_status("Settings saved")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            self.status_bar.set_status("Error saving settings")
    
    def setup_system_integration(self):
        """Set up system tray, hotkeys, and startup"""
        try:
            logger.debug("Setting up system integration...")
            suppress_warnings = self.config_manager.get_setting('ui.suppress_startup_warnings', True)
            StartupManager.set_suppress_errors(suppress_warnings)
            # Start system tray icon (delayed to ensure main loop is running)
            # Schedule tray icon start after main loop begins
            self.after(500, self._start_tray_icon_delayed)
            
            # Register global hotkey
            try:
                hotkey = self.config_manager.get_setting('window.global_hotkey', 'win+shift+l')
                success, message = self.hotkey_manager.register(hotkey, self.toggle_window)
                if success:
                    logger.info(f"Global hotkey registered: {message}")
                else:
                    logger.warning(f"Failed to register hotkey: {message}")
                    self.status_bar.set_status(f"Hotkey error: {message}")
            except Exception as e:
                logger.warning(f"Failed to register hotkey: {e}")
                self.status_bar.set_status(f"Hotkey error: {str(e)}")
            
            # Check startup setting
            start_with_windows = self.config_manager.get_setting('window.start_with_windows', False)
            start_minimized = self.config_manager.get_setting('window.start_minimized', False)
            startup_enabled = StartupManager.is_startup_enabled()
            
            if start_with_windows:
                # Enable startup with appropriate minimized flag
                if not startup_enabled:
                    if StartupManager.enable_startup(start_minimized):
                        logger.info(f"Startup enabled (minimized={start_minimized})")
                else:
                    # Update existing startup entry to ensure correct flags
                    StartupManager.enable_startup(start_minimized)
            elif not start_with_windows and startup_enabled:
                if StartupManager.disable_startup():
                    logger.info("Startup disabled")
            
            # Check if should start minimized (from command line or setting)
            # Note: Command line --minimized is handled in main.py
            # This handles the case where start_minimized setting is True
            if start_minimized and not hasattr(self, '_minimized_from_cli'):
                self.after(100, self.withdraw)
        except Exception as e:
            print(f"[ERROR] System integration failed: {e}")
            logger.error(f"Error in system integration: {e}", exc_info=True)

    
    def toggle_window(self):
        """Toggle window visibility (for hotkey)"""
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.deiconify()
            self.lift()
            self.focus_force()
    
    def start_git_status_monitoring(self):
        """Start monitoring git status for status bar summary"""
        def check_git_status():
            try:
                if self._is_shutting_down:
                    return
                from src.services.git_service import GitService
                git_service = GitService()
                projects = self.config_manager.load_projects()
                if not projects:
                    self.status_bar.set_git_status("No projects")
                    return

                repos_needing_attention = 0
                for project in projects:
                    repo_path = project.get('path', '')
                    if repo_path and os.path.exists(os.path.join(repo_path, '.git')):
                        status = git_service.get_status(repo_path)
                        if status.get('status_text') in ['uncommitted', 'behind', 'diverged']:
                            repos_needing_attention += 1
                
                if repos_needing_attention > 0:
                    self.status_bar.set_git_status(f"{repos_needing_attention} repos need attention")
                else:
                    self.status_bar.set_git_status("All clean")
            except Exception as e:
                logger.debug(f"Error checking git status: {e}")
        
        def monitor():
            import time
            while True:
                if self._is_shutting_down:
                    return
                time.sleep(30)  # Check every 30 seconds
                try:
                    self.after(0, check_git_status)
                except Exception as e:
                    logger.debug(f"Suppressed exception in git status scheduler: {e}")
        
        # Initial check
        self.after(2000, check_git_status)
        
        # Start background monitoring
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def on_search(self, search_text: str):
        """Handle search text changes - filters current tab's content"""
        try:
            current_view = self._current_view

            if current_view == "Projects" and self.projects_tab:
                self.projects_tab.filter_projects(search_text)
            elif current_view == "Downloads" and self.downloads_tab:
                self.downloads_tab.filter_by_search(search_text)
            elif current_view == "Maintenance" and self.maintenance_tab:
                if hasattr(self.maintenance_tab, 'filter_utilities'):
                    self.maintenance_tab.filter_utilities(search_text)
        except Exception as e:
            logger.error(f"Error in search: {e}", exc_info=True)
            self.status_bar.set_status("Search error")
    
    def on_closing(self):
        """Handle window close event"""
        # Check if minimize to tray is enabled
        minimize_to_tray = self.config_manager.get_setting('window.minimize_to_tray', True)
        
        if minimize_to_tray:
            # Minimize to tray
            self.withdraw()
            
            # Show notification on first minimize only
            if self._first_minimize:
                self._first_minimize = False
                self._show_minimize_notification()
        else:
            # Close application
            self.quit_app()
    
    def _show_minimize_notification(self):
        """Show notification when minimized to tray for the first time"""
        try:
            from src.utils.system_tray import show_notification
            show_notification(
                "App Launcher",
                "App Launcher minimized to tray. Click the tray icon to restore."
            )
        except Exception as e:
            logger.debug(f"Could not show minimize notification: {e}")
    
    def quit_app(self):
        """Quit the application completely"""
        print("[INFO] Shutting down application...")
        logger.info("Shutting down application...")
        self._is_shutting_down = True
        
        # Stop git status monitoring if active
        try:
            if self.projects_tab and hasattr(self.projects_tab, 'git_service'):
                self.projects_tab.git_service.stop_status_monitoring()
                logger.debug("Git monitoring stopped")
        except Exception as e:
            logger.warning(f"Error stopping git monitoring: {e}")
            print(f"[WARNING] Git monitoring: {e}")

        # Stop tray icon first
        if self.tray_icon:
            try:
                self.tray_icon.stop()
                import time
                time.sleep(0.1)
                logger.debug("Tray icon stopped")
            except Exception as e:
                logger.warning(f"Error stopping tray icon: {e}")
                print(f"[WARNING] Tray icon stop: {e}")
        
        # Shutdown config manager
        try:
            self.config_manager.shutdown()
            logger.debug("Config manager shutdown complete")
        except Exception as e:
            logger.warning(f"Error shutting down config manager: {e}")
            print(f"[WARNING] Config shutdown: {e}")
        
        # Unregister hotkey
        try:
            self.hotkey_manager.cleanup()
            logger.debug("Hotkey manager cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up hotkey manager: {e}")
            print(f"[WARNING] Hotkey cleanup: {e}")
        
        # Destroy window
        try:
            self.destroy()
            print("[INFO] Application shutdown complete")
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error destroying window: {e}")
            print(f"[ERROR] Window destroy: {e}")

    def _build_menu(self):
        try:
            menubar = tk.Menu(self)
            help_menu = tk.Menu(menubar, tearoff=0)
            help_menu.add_command(label="Tool Manual", command=self.open_help_manual)
            menubar.add_cascade(label="Help", menu=help_menu)
            self.configure(menu=menubar)
        except Exception as exc:
            logger.debug(f"Menu setup failed: {exc}")

    def _start_tray_icon_delayed(self):
        """Start tray icon after main loop is running"""
        try:
            logger.debug("Starting tray icon...")
            suppress_warnings = self.config_manager.get_setting('ui.suppress_startup_warnings', True)
            self.tray_icon = start_tray_icon(
                self,
                self.config_manager,
                self.process_service,
                self.cleanup_service,
                on_settings=self.open_settings,
                include_utilities=not self._dashboard_read_only,
                app_label=self._sidebar_title_text,
                tray_title=self._window_title or "James's Project Launcher"
            )
            if self.tray_icon:
                print("[INFO] System tray icon started")
                logger.info("System tray icon started")
            else:
                if suppress_warnings:
                    logger.debug("Tray icon not available")
                else:
                    print("[WARNING] Failed to start tray icon")
                    logger.warning("Failed to start tray icon")
        except Exception as e:
            suppress_warnings = self.config_manager.get_setting('ui.suppress_startup_warnings', True)
            print(f"[WARNING] Tray icon error: {e}")
            logger.warning(f"Failed to start tray icon: {e}", exc_info=True)
            if not suppress_warnings:
                logger.warning(f"Tray icon suppressed: {e}")
    
    def _handle_health_update(self, result: dict):
        attention = result.get("attention_count", 0)
        level = "green"
        if attention >= 3:
            level = "red"
        elif attention >= 1:
            level = "yellow"

        dashboard_item = self._nav_items.get('Dashboard')
        if dashboard_item:
            dashboard_item.set_indicator(level)

        if not self._startup_health_notified:
            enabled = self.config_manager.get_setting('ui.show_health_check_on_startup', True)
            if enabled and attention >= 3:
                try:
                    if ToastManager:
                        ToastManager.show_info(
                            "System health check",
                            f"{attention} items need attention. View Dashboard."
                        )
                except Exception as e:
                    logger.debug(f"Suppressed exception in health toast: {e}")
                self.after(200, lambda: self._show_health_notification(result))
            self._startup_health_notified = True

    def _show_health_notification(self, result: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title("System Health Check")
        dialog.geometry("520x260")
        dialog.configure(fg_color=COLORS['bg_primary'])
        dialog.transient(self)
        dialog.grab_set()

        header = ctk.CTkLabel(
            dialog,
            text="🩺 System Health Check",
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_primary']
        )
        header.pack(pady=(16, 8))

        body = ctk.CTkFrame(dialog, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=20)

        issues = []
        for metric in result.get("metrics", {}).values():
            if metric.get("status") in {"yellow", "red"}:
                label = metric.get("label", "")
                value = metric.get("value", "")
                issues.append(self._format_health_issue(label, value))

        message = f"Found {len(issues)} items that need attention:\n"
        message += "\n".join(f"• {issue}" for issue in issues[:3])

        ctk.CTkLabel(
            body,
            text=message,
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            justify='left',
            anchor='w'
        ).pack(fill='x')

        actions = ctk.CTkFrame(dialog, fg_color='transparent')
        actions.pack(fill='x', padx=20, pady=(10, 16))

        Button3D(
            actions,
            text="View Details",
            width=140,
            height=36,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=lambda: (dialog.destroy(), self.show_view('Dashboard'))
        ).pack(side='left')

        if not self._dashboard_read_only:
            Button3D(
                actions,
                text="Run Quick Cleanup",
                width=160,
                height=36,
                bg_color=BUTTON_COLORS.PRIMARY,
                command=lambda: (dialog.destroy(), self.dashboard_tab._run_quick_cleanup())
            ).pack(side='left', padx=8)

        Button3D(
            actions,
            text="Dismiss",
            width=120,
            height=36,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=dialog.destroy
        ).pack(side='right')
    
    def run(self):
        """Start the application"""
        self.mainloop()

    @staticmethod
    def _format_health_issue(label: str, value: str) -> str:
        label_lower = (label or "").lower()
        if "disk" in label_lower:
            return f"Disk space is low ({value})"
        if "temp" in label_lower:
            return f"Temp files are {value}"
        if "recycle" in label_lower:
            return f"Recycle Bin is {value}"
        if "uptime" in label_lower:
            return f"System uptime is {value}"
        if "cleanup" in label_lower:
            return f"{value} since last cleanup"
        if "ram" in label_lower:
            return f"RAM usage is {value}"
        if "dns" in label_lower:
            return f"DNS response is {value}"
        return f"{label}: {value}"
