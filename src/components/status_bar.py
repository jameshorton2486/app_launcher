"""
Status Bar Component
Displays application status, git info, and system info.
Enhanced with color-coded states and visual hierarchy.
"""

import customtkinter as ctk
import sys
import os
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

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS

# Design tokens for status bar
try:
    from src.utils.theme_extended import THEME, SPACING
    _BG = THEME.get("panel", COLORS.get("bg_secondary", "#161a22"))
    _BORDER = THEME.get("border", COLORS.get("border", "#2a3142"))
    _PADX = getattr(SPACING, 'md', 12)
    _PADY = getattr(SPACING, 'sm', 8)
    _HEIGHT = 40  # Vertical padding — visually separated
except ImportError:
    _BG = COLORS.get("bg_secondary", "#1e1e24")
    _BORDER = COLORS.get("border", "#3f3f46")
    _PADX, _PADY = 12, 8
    _HEIGHT = 38


class StatusType(Enum):
    """Status types with associated colors and indicators."""
    READY = ("ready", "#6b7280", "●")
    INFO = ("info", "#3b82f6", "●")
    SUCCESS = ("success", "#22c55e", "●")
    WARNING = ("warning", "#f59e0b", "●")
    ERROR = ("error", "#ef4444", "●")
    LOADING = ("loading", "#a0a6b8", "◌")


class StatusBar(ctk.CTkFrame):
    """Status bar — vertical padding, visual separation, muted severity colors."""
    
    def __init__(self, parent, on_settings_click=None, on_help_click=None, on_screenshot_click=None):
        super().__init__(parent, fg_color=_BG, corner_radius=0, height=_HEIGHT, border_width=0)
        self.pack_propagate(False)
        
        self.status_text = "Ready"
        self.git_status = ""
        self.system_info = ""
        self.on_settings_click = on_settings_click
        self.on_help_click = on_help_click
        self.on_screenshot_click = on_screenshot_click
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
            self.screenshot_btn = ctk.CTkButton(
                self,
                text="📷",
                width=30,
                height=25,
                font=('Segoe UI', 12),
                fg_color='transparent',
                hover_color=COLORS['bg_tertiary'],
                command=self._on_screenshot_click
            )
            self.screenshot_btn.pack(side='right', padx=(4, 0), pady=4)
            separator_screenshot = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
            separator_screenshot.pack(side='right', fill='y', padx=4, pady=4)

        # Right: Help button
        self.help_btn = ctk.CTkButton(
            self,
            text="?",
            width=30,
            height=25,
            font=('Segoe UI', 12),
            fg_color='transparent',
            hover_color=COLORS['bg_tertiary'],
            command=self._on_help_click
        )
        self.help_btn.pack(side='right', padx=(4, 0), pady=4)

        # Separator before help
        separator_help = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
        separator_help.pack(side='right', fill='y', padx=4, pady=4)

        # Right: Settings button (gear icon)
        self.settings_btn = ctk.CTkButton(
            self,
            text="⚙",
            width=30,
            height=25,
            font=('Segoe UI', 12),
            fg_color='transparent',
            hover_color=COLORS['bg_tertiary'],
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
                "info": COLORS.get("info", "#3b82f6"),
                "success": COLORS.get("success", "#22c55e"),
                "warning": COLORS.get("warning", "#f59e0b"),
                "error": COLORS.get("error", "#ef4444"),
                "ready": COLORS.get("text_tertiary", "#6b7280"),
                "loading": COLORS.get("text_secondary", "#a0a6b8"),
            }
            color = color_map.get(status_type, color_map["info"])
        if hasattr(self, '_indicator'):
            self._indicator.configure(text_color=color)
    
    def set_git_status(self, text: str):
        """Set git status text"""
        self.git_status = text
        if text:
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
        except:
            pass
    
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
                    except Exception:
                        pass
                    time.sleep(5)
            except Exception:
                pass
        
        def poll_ram_queue():
            try:
                while True:
                    try:
                        p = ram_queue.get_nowait()
                        self.set_ram_usage(p)
                    except queue.Empty:
                        break
            except Exception:
                pass
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
