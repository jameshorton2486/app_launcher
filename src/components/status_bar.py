"""
Status Bar Component
Displays application status, git info, and system info.
Enhanced with modern spacing and visual hierarchy.
"""

import customtkinter as ctk
import sys
import os
import threading
import time

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

# Optional: use extended theme for spacing if available
try:
    from src.utils.theme_extended import SPACING
    _PADX, _PADY = 12, 6
    _HEIGHT = 34
except ImportError:
    _PADX, _PADY = 10, 5
    _HEIGHT = 30


class StatusBar(ctk.CTkFrame):
    """Status bar component at bottom of window"""
    
    def __init__(self, parent, on_settings_click=None, on_help_click=None, on_screenshot_click=None):
        """
        Initialize status bar

        Args:
            parent: Parent widget
            on_settings_click: Optional callback for settings button click
            on_help_click: Optional callback for help button click
            on_screenshot_click: Optional callback for screenshot button click
        """
        super().__init__(parent, fg_color=COLORS['bg_secondary'], corner_radius=0, height=_HEIGHT)
        self.pack_propagate(False)
        
        self.status_text = "Ready"
        self.git_status = ""
        self.system_info = ""
        self.on_settings_click = on_settings_click
        self.on_help_click = on_help_click
        self.on_screenshot_click = on_screenshot_click
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the status bar UI"""
        # Left: Status label
        # Status indicator dot (subtle)
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
        separator1 = ctk.CTkFrame(self, width=1, fg_color=COLORS['border'])
        separator1.pack(side='left', fill='y', padx=4, pady=4)
        
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
            status_type: Optional - "info", "success", "warning", "error" for indicator color
        """
        self.status_text = text
        self.status_label.configure(text=text)
        color_map = {
            "info": COLORS.get("info", "#3b82f6"),
            "success": COLORS.get("success", "#22c55e"),
            "warning": COLORS.get("warning", "#f59e0b"),
            "error": COLORS.get("error", "#ef4444"),
        }
        if hasattr(self, '_indicator'):
            self._indicator.configure(text_color=color_map.get(status_type, color_map["info"]))
    
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
        """Start monitoring RAM usage in background"""
        if not PSUTIL_AVAILABLE:
            self.ram_label.configure(text="RAM: N/A (install psutil)")
            return
        
        def monitor_ram():
            try:
                while True:
                    try:
                        ram_percent = psutil.virtual_memory().percent
                        self.after(0, lambda p=ram_percent: self.set_ram_usage(p))
                    except:
                        pass
                    time.sleep(5)  # Update every 5 seconds
            except:
                pass
        
        thread = threading.Thread(target=monitor_ram, daemon=True)
        thread.start()
    
    def update_all(self, status: str = None, git: str = None, system: str = None):
        """Update all status fields at once"""
        if status is not None:
            self.set_status(status)
        if git is not None:
            self.set_git_status(git)
        if system is not None:
            # System info is now RAM usage, handled separately
            pass
