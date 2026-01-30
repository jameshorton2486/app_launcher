"""
Utilities Tab
System utilities and tools
"""

import customtkinter as ctk
import sys
import os
import tkinter.messagebox as messagebox

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS
from src.services.cleanup_service import CleanupService
from src.components.utility_button import UtilityButton
from src.utils.tool_registry import ToolRegistry

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class UtilitiesTab(ctk.CTkScrollableFrame):
    """Utilities tab for system tools"""
    
    def __init__(self, parent, config_manager):
        """
        Initialize utilities tab
        
        Args:
            parent: Parent widget
            config_manager: ConfigManager instance
        """
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        
        self.config_manager = config_manager
        self.cleanup_service = CleanupService()
        self.tool_registry = ToolRegistry()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the utilities tab UI"""
        tools_config = self.config_manager.tools or {}
        services = {
            "cleanup_service": self.cleanup_service,
            "utilities_tab": self
        }
        context = {"config_manager": self.config_manager}
        self.tool_registry.register_from_config(tools_config, services, context)

        for section in tools_config.get("sections", []):
            buttons = []
            for tool in section.get("tools", []):
                tool_id = tool.get("id")
                handler = self.tool_registry.get_handler(tool_id)
                if not handler:
                    logger.warning(f"Tool handler missing for {tool_id}")
                    handler = lambda: (False, "Tool not configured")
                buttons.append((
                    tool.get("icon", ""),
                    tool.get("title", ""),
                    tool.get("subtitle", ""),
                    handler,
                    tool.get("tooltip", "")
                ))
            self.create_section(section.get("title", ""), buttons)
    
    def create_section(self, title: str, buttons: list):
        """
        Create a section with title and utility buttons
        
        Args:
            title: Section title
            buttons: List of (icon, title, subtitle, command, tooltip) tuples
        """
        # Section frame
        section_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=8)
        section_frame.pack(fill='x', padx=20, pady=15)
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title_label.pack(fill='x', padx=15, pady=(15, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Create buttons (80x80 as specified)
        for icon, btn_title, subtitle, command, tooltip in buttons:
            button = UtilityButton(
                buttons_frame,
                icon=icon,
                title=btn_title,
                subtitle=subtitle,
                command=command,
                tooltip=tooltip,
                width=80,
                height=80
            )
            button.pack(side='left', padx=10, pady=5)
    
    def show_network_stats(self):
        """Show network statistics in a message box"""
        success, stats = self.cleanup_service.get_network_stats()
        if success:
            # Show in a dialog (truncate if too long)
            display_stats = stats[:1000] if len(stats) > 1000 else stats
            if len(stats) > 1000:
                display_stats += "\n\n(Truncated - showing first 1000 characters)"
            messagebox.showinfo("Network Statistics", display_stats)
            return True, "Network stats displayed"
        else:
            return False, stats
