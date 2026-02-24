"""
Status Bar Component
Displays application status, git info, and system info.
Enhanced with color-coded states and visual hierarchy.
"""

import customtkinter as ctk
import threading
import time
import queue
from enum import Enum

# Try to import psutil, but don't fail if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# Design tokens for status bar
from src.theme import SPACING

_BG = COLORS.get("bg_panel", COLORS["bg_secondary"])
_BORDER = COLORS.get("border", COLORS.get("border_default", COLORS["border_default"]))
_PADX = SPACING.get("md", 12)
_PADY = SPACING.get("sm", 8)
_HEIGHT = 40  # Vertical padding — visually separated


class StatusType(Enum):
    """Status types with associated colors and indicators."""
    READY = ("ready", COLORS["text_tertiary"], "●")
    INFO = ("info", COLORS["info"], "●")
    SUCCESS = ("success", COLORS["success"], "●")
    WARNING = ("warning", COLORS["warning"], "●")
    ERROR = ("error", COLORS["error"], "●")
    LOADING = ("loading", COLORS["text_secondary"], "◌")


class StatusBar(ctk.CTkFrame):
    """Status bar — vertical padding, visual separation, muted severity colors."""
    
    def __init__(self, parent, on_settings_click=None, on_help_click=None, on_screenshot_click=None,
                 show_settings: bool = True, show_help: bool = True):
        super().__init__(parent, fg_color=_BG, corner_radius=0, height=_HEIGHT, border_width=0)
        self.pack_propagate(False)
        
        self.status_text = "Ready"
        self.git_status = ""
        self.system_info = ""
        self.on_settings_click = on_settings_click
        self.on_help_click = on_help_click
        self.on_screenshot_click = on_screenshot_click
        self.show_settings = show_settings
        self.show_help = show_help
        self._ram_queue = queue.Queue()  # Thread-safe: worker puts, main thread polls
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the status bar UI"""
        # Top border — visual separation from content
        top_sep = ctk.CTkFrame(self, height=1, fg_color=_BORDER)
        top_sep.pack(fill='x', side='top')
        
        # Left: Status indicator dot (subtle)
        self._indicator = ctk.CTkLabel(
            self,
            text="●",
            font=('Segoe UI', 8),
            text_color=COLORS['success'],
            width=16
        )
        self._indicator.pack(side='left', padx=(_PADX, 2), pady=_PADY)
        
        self.status_label = ctk.CTkLabel(
            self,
            text=self.status_text,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=(0, _PADX), pady=_PADY)
        
        # Separator
        separator1 = ctk.CTkFrame(self, width=1, fg_color=_BORDER)
        separator1.pack(side='left', fill='y', padx=4, pady=6)
        
        # Center: Git status label
        self.git_label = ctk.CTkLabel(
            self,
            text="",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='w'
        )
        self.git_label.pack(side='left', padx=_PADX, pady=_PADY, expand=True)
        
        # Separator
        separator2 = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
        separator2.pack(side='left', fill='y', padx=5, pady=5)
        
        # Right: Screenshot button (capture full screen)
        if self.on_screenshot_click:
            self.screenshot_btn = Button3D(
                self,
                text="📷",
                width=30,
                height=25,
                font=('Segoe UI', 12),
                bg_color=BUTTON_COLORS.SECONDARY,
                command=self._on_screenshot_click
            )
            self.screenshot_btn.pack(side='right', padx=(4, 0), pady=4)
            separator_screenshot = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
            separator_screenshot.pack(side='right', fill='y', padx=4, pady=4)

        if self.show_help:
            # Right: Help button
            self.help_btn = Button3D(
                self,
                text="?",
                width=30,
                height=25,
                font=('Segoe UI', 12),
                bg_color=BUTTON_COLORS.SECONDARY,
                command=self._on_help_click
            )
            self.help_btn.pack(side='right', padx=(4, 0), pady=4)

            # Separator before help
            separator_help = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
            separator_help.pack(side='right', fill='y', padx=4, pady=4)

        if self.show_settings:
            # Right: Settings button (gear icon)
            self.settings_btn = Button3D(
                self,
                text="⚙",
                width=30,
                height=25,
                font=('Segoe UI', 12),
                bg_color=BUTTON_COLORS.SECONDARY,
                command=self._on_settings_click
            )
            self.settings_btn.pack(side='right', padx=(4, 4), pady=4)

            # Separator before settings
            separator3 = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
            separator3.pack(side='right', fill='y', padx=4, pady=4)
        
        # Right: RAM usage label
        self.ram_label = ctk.CTkLabel(
            self,
            text="RAM: --%",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            anchor='e'
        )
        self.ram_label.pack(side='right', padx=_PADX, pady=_PADY)
        
        # Start RAM monitoring
        self.start_ram_monitoring()
    
    def _on_settings_click(self):
        """Handle settings button click"""
        if self.on_settings_click:
            self.on_settings_click()
        else:
            # Fallback: try to find parent window with open_settings method
            widget = self
            while widget:
                if hasattr(widget, 'open_settings'):
                    widget.open_settings()
                    return
                widget = widget.master

    def _on_help_click(self):
        if self.on_help_click:
            self.on_help_click()

    def _on_screenshot_click(self):
        """Handle screenshot button click"""
        if self.on_screenshot_click:
            self.on_screenshot_click()
    
    def set_status(self, text: str, status_type: str = "info"):
        """
        Set main status text.
        
        Args:
            text: Status message
            status_type: "info", "success", "warning", "error", or StatusType enum
        """
        self.status_text = text
        self.status_label.configure(text=text)
        if isinstance(status_type, StatusType):
            _, color, _ = status_type.value
        else:
            color_map = {
                "info": COLORS["info"],
                "success": COLORS["success"],
                "warning": COLORS["warning"],
                "error": COLORS["error"],
                "ready": COLORS["text_tertiary"],
                "loading": COLORS["text_secondary"],
            }
            color = color_map.get(status_type, color_map["info"])
        if hasattr(self, '_indicator'):
            self._indicator.configure(text_color=color)
    
    def set_git_status(self, text: str):
        """Set git status text"""
        self.git_status = text
        if text:
            if text.strip().lower() == "no projects":
                self.git_label.configure(text="No projects")
            else:
                self.git_label.configure(text=f"Git: {text}")
        else:
            self.git_label.configure(text="")
    
    def set_system_info(self, text: str):
        """Set system info text (deprecated - use set_ram_usage instead)"""
        # Keep for backward compatibility
        pass
    
    def set_ram_usage(self, percentage: float):
        """Set RAM usage percentage"""
        try:
            self.ram_label.configure(text=f"RAM: {percentage:.0f}%")
        except Exception as e:
            logger.debug(f"Suppressed exception in set_ram_usage: {e}")
    
    def start_ram_monitoring(self):
        """Start monitoring RAM usage in background (queue-based, main-thread safe)"""
        if not PSUTIL_AVAILABLE:
            self.ram_label.configure(text="RAM: N/A (install psutil)")
            return
        
        ram_queue = self._ram_queue
        
        def monitor_ram():
            try:
                while True:
                    try:
                        ram_percent = psutil.virtual_memory().percent
                        ram_queue.put(ram_percent)
                    except Exception as e:
                        logger.debug(f"Suppressed exception in RAM monitor: {e}")
                    time.sleep(5)
            except Exception as e:
                logger.debug(f"Suppressed exception in RAM monitor loop: {e}")
        
        def poll_ram_queue():
            try:
                while True:
                    try:
                        p = ram_queue.get_nowait()
                        self.set_ram_usage(p)
                    except queue.Empty:
                        break
            except Exception as e:
                logger.debug(f"Suppressed exception in RAM poller: {e}")
            if self.winfo_exists():
                self.after(1000, poll_ram_queue)
        
        threading.Thread(target=monitor_ram, daemon=True).start()
        self.after(2000, poll_ram_queue)
    
    def set_loading(self, message: str = "Processing..."):
        """Show loading / busy indication."""
        self.set_status(message, StatusType.LOADING)
        if hasattr(self, '_indicator'):
            self._indicator.configure(text="◌")

    def clear_loading(self):
        """Clear loading state, restore normal indicator."""
        if hasattr(self, '_indicator'):
            self._indicator.configure(text="●")
        self.set_ready()

    def set_ready(self):
        """Reset to ready state."""
        self.set_status("Ready", StatusType.READY)

    def set_success(self, message: str):
        """Show success state."""
        self.set_status(message, StatusType.SUCCESS)

    def set_error(self, message: str):
        """Show error state."""
        self.set_status(message, StatusType.ERROR)

    def set_warning(self, message: str):
        """Show warning state."""
        self.set_status(message, StatusType.WARNING)

    def update_all(self, status: str = None, git: str = None, system: str = None):
        """Update all status fields at once"""
        if status is not None:
            self.set_status(status)
        if git is not None:
            self.set_git_status(git)
        if system is not None:
            pass
