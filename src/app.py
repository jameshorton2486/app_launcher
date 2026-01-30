"""
Main Application Class
CustomTkinter application with tabbed interface
"""

import customtkinter as ctk
import sys
import os
import threading
import psutil

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS, apply_theme
from src.config_manager import ConfigManager
from src.components.search_bar import SearchBar
from src.components.status_bar import StatusBar
from src.components.command_palette import CommandPalette
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
SIDEBAR_ITEM_HEIGHT = 44


class SidebarNavItem(ctk.CTkFrame):
    """Sidebar navigation item with hover and active states."""

    def __init__(self, parent, label: str, icon: str, command):
        super().__init__(parent, fg_color='transparent', corner_radius=8, height=SIDEBAR_ITEM_HEIGHT)
        self.label_text = label
        self.icon = icon
        self.command = command
        self._active = False
        self._collapsed = False

        self.pack_propagate(False)

        self.left_border = ctk.CTkFrame(self, width=3, fg_color='transparent', corner_radius=0)
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
        self.label.pack(fill='both', expand=True, padx=16)

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
            self.left_border.configure(fg_color=COLORS['accent_primary'])
            self.content.configure(fg_color='transparent')
            self.label.configure(text_color=COLORS['text_primary'])
        else:
            self.left_border.configure(fg_color='transparent')
            self.content.configure(fg_color='transparent')
            self.label.configure(text_color=COLORS['text_secondary'])

    def set_collapsed(self, collapsed: bool):
        self._collapsed = collapsed
        self.label.configure(text=self._format_label())

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
    
    def __init__(self):
        super().__init__()
        
        try:
            # Initialize config manager
            self.config_manager = ConfigManager()
            
            # Load settings
            self.settings = self.config_manager.settings
            
            # Initialize services
            self.process_service = ProcessService()
            self.cleanup_service = CleanupService()
            self.hotkey_manager = HotkeyManager()
            
            # Tray icon
            self.tray_icon = None
            self._first_minimize = True  # Track first minimize for notification
            
            # Tab instances (will be created in setup_ui)
            self.projects_tab = None
            self.downloads_tab = None
            self.optimization_tab = None
            self.maintenance_tab = None
            
            # Apply theme (read from config)
            theme_mode = self.config_manager.get_setting('theme.mode', 'dark')
            accent_color = self.config_manager.get_setting('theme.accent_color', '#6c5ce7')
            apply_theme(self, mode=theme_mode, accent_color=accent_color)
            
            # Configure window
            self.setup_window()
            
            # Setup UI
            self.setup_ui()
            
            # Setup system integration
            self.setup_system_integration()
            
            # Bind close event
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
    
    def setup_window(self):
        """Configure main window with position/size persistence"""
        width = self.config_manager.get_setting('window.width', 900)
        height = self.config_manager.get_setting('window.height', 650)
        
        self.title("James's Project Launcher (v2.0)")
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
        except:
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
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Status bar at bottom
        self.status_bar = StatusBar(self.content_container, on_settings_click=self.open_settings)
        self.status_bar.pack(fill='x', side='bottom', padx=0, pady=0)

        self._sidebar_expanded = True
        self._nav_items = {}
        self._current_view = None

        self._build_sidebar()
        self._build_views()
        self.show_view("Dashboard")

        # Command palette bindings
        self.bind_all("<Control-k>", lambda e: self.open_command_palette())
        self.bind_all("<Control-p>", lambda e: self.open_command_palette())

        # Update status
        self.status_bar.set_status("Ready")

        # Start git status monitoring for status bar
        self.start_git_status_monitoring()

    def _build_sidebar(self):
        header_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        header_frame.pack(fill='x', padx=12, pady=(12, 8))

        self.sidebar_title = ctk.CTkLabel(
            header_frame,
            text="App Launcher",
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        self.sidebar_title.pack(side='left', fill='x', expand=True)

        self.sidebar_toggle = ctk.CTkButton(
            header_frame,
            text="☰",
            width=32,
            height=28,
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['bg_hover'],
            command=self.toggle_sidebar
        )
        self.sidebar_toggle.pack(side='right')

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        nav_frame.pack(fill='both', expand=True, padx=8, pady=8)

        nav_items = [
            ("Dashboard", "🏠"),
            ("Projects", "🚀"),
            ("Optimization", ""),
            ("Maintenance", "🛠"),
            ("Settings", ""),
        ]

        for name, icon in nav_items:
            item = SidebarNavItem(
                nav_frame,
                label=name,
                icon=icon,
                command=lambda n=name: self.show_view(n)
            )
            item.pack(fill='x', pady=2)
            self._nav_items[name] = item

        footer_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_primary'], corner_radius=0)
        footer_frame.pack(fill='x', side='bottom', padx=12, pady=12)

        self.ram_label = ctk.CTkLabel(
            footer_frame,
            text="RAM: --%",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        self.ram_label.pack(fill='x')

        self.version_label = ctk.CTkLabel(
            footer_frame,
            text="v2.0.0",
            font=('Segoe UI', 10),
            text_color=COLORS['text_tertiary'],
            anchor='w'
        )
        self.version_label.pack(fill='x', pady=(6, 0))

        self.after(1000, self._update_ram_usage)

    def _build_views(self):
        self.views = {}

        dashboard_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.dashboard_tab = DashboardTab(
            dashboard_view,
            self.config_manager,
            process_service=self.process_service,
            status_bar=self.status_bar,
            on_open_downloads=lambda: self.show_view("Downloads")
        )
        self.dashboard_tab.pack(fill='both', expand=True)
        self._dashboard_initialized = True

        downloads_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.downloads_tab = DownloadsTab(
            downloads_view,
            self.config_manager,
            status_bar=self.status_bar
        )
        self.downloads_tab.pack(fill='both', expand=True)

        projects_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.projects_tab = ProjectsTab(projects_view, self.config_manager)
        self.projects_tab.pack(fill='both', expand=True)

        optimization_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.optimization_tab = OptimizationTab(optimization_view, self.config_manager)
        self.optimization_tab.pack(fill='both', expand=True)

        maintenance_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.maintenance_tab = MaintenanceTab(maintenance_view, self.config_manager)
        self.maintenance_tab.pack(fill='both', expand=True)

        settings_view = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.settings_tab = SettingsTab(settings_view, self.config_manager, on_save=self.on_settings_saved)
        self.settings_tab.pack(fill='both', expand=True, padx=10, pady=10)

        self.views = {
            "Dashboard": dashboard_view,
            "Downloads": downloads_view,
            "Projects": projects_view,
            "Optimization": optimization_view,
            "Maintenance": maintenance_view,
            "Settings": settings_view,
        }

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

        self.sidebar_title.configure(text="App Launcher" if self._sidebar_expanded else "AL")

        for item in self._nav_items.values():
            item.set_collapsed(not self._sidebar_expanded)

    def _update_ram_usage(self):
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
            self.show_view("Settings")
        except Exception as e:
            logger.error(f"Error opening settings: {e}", exc_info=True)
            self.status_bar.set_status("Error opening settings")

    def open_command_palette(self):
        """Open command palette modal"""
        try:
            CommandPalette(self, self.config_manager)
        except Exception as e:
            logger.error(f"Error opening command palette: {e}", exc_info=True)
    
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
            # Start system tray icon
            try:
                self.tray_icon = start_tray_icon(
                    self,
                    self.config_manager,
                    self.process_service,
                    self.cleanup_service,
                    on_settings=self.open_settings
                )
                logger.info("System tray icon started")
            except Exception as e:
                logger.warning(f"Failed to start tray icon: {e}")
            
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
            logger.error(f"Error in system integration: {e}", exc_info=True)
        
        # Optional: Start file watcher for downloads
        # Uncomment to enable:
        # from src.utils.file_watcher import FileWatcher
        # downloads_path = self.config_manager.get_setting('paths.downloads_folder', '')
        # if downloads_path:
        #     projects = self.config_manager.load_projects()
        #     self.file_watcher = FileWatcher(downloads_path, projects)
        #     self.file_watcher.start()
    
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
                from src.services.git_service import GitService
                git_service = GitService()
                projects = self.config_manager.load_projects()
                
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
                    self.status_bar.set_git_status("")
            except Exception as e:
                logger.debug(f"Error checking git status: {e}")
        
        def monitor():
            import time
            while True:
                time.sleep(30)  # Check every 30 seconds
                try:
                    self.after(0, check_git_status)
                except:
                    pass
        
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
        # Stop tray icon first
        if self.tray_icon:
            try:
                self.tray_icon.stop()
                # Give it a moment to stop
                import time
                time.sleep(0.1)
            except Exception as e:
                logger.debug(f"Error stopping tray icon: {e}")
        
        # Shutdown config manager
        try:
            self.config_manager.shutdown()
        except Exception as e:
            logger.debug(f"Error shutting down config manager: {e}")
        
        # Unregister hotkey
        try:
            self.hotkey_manager.cleanup()
        except Exception as e:
            logger.debug(f"Error cleaning up hotkey manager: {e}")
        
        # Destroy window
        try:
            self.destroy()
        except Exception as e:
            logger.debug(f"Error destroying window: {e}")
    
    def run(self):
        """Start the application"""
        self.mainloop()
