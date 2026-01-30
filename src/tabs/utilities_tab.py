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
            "cleanup": self.cleanup_service,
            "utilities_tab": self
        }
        context = {"config_manager": self.config_manager}
        self.tool_registry.register_from_config(tools_config, services, context)

        legacy_sections = [
            ("QUICK CLEANUP", [
                ("empty_recycle_bin", "🗑️", "Empty Recycle Bin", "",
                 lambda: self.cleanup_service.empty_recycle_bin(),
                 "Permanently delete all files in the Recycle Bin"),
                ("clear_temp_files", "🧹", "Clear Temp Files", "",
                 lambda: self.cleanup_service.clear_temp_files(),
                 "Delete temporary files from %temp% and Windows\\Temp"),
                ("flush_dns", "🔄", "Flush DNS", "",
                 lambda: self.cleanup_service.flush_dns(),
                 "Clear the DNS resolver cache"),
                ("clear_prefetch", "📁", "Clear Prefetch", "",
                 lambda: self.cleanup_service.clear_prefetch(),
                 "Clear Windows Prefetch folder (requires admin)"),
            ]),
            ("MEMORY & PERFORMANCE", [
                ("clear_standby_ram", "🧠", "Clear RAM Standby", "",
                 lambda: self.cleanup_service.clear_standby_ram(),
                 "Free up standby memory"),
                ("disk_cleanup", "💾", "Disk Cleanup", "",
                 lambda: self.cleanup_service.run_disk_cleanup(),
                 "Launch Windows Disk Cleanup tool"),
                ("defrag_optimize", "⚡", "Defrag/Optimize", "",
                 lambda: self.cleanup_service.optimize_drive("C:"),
                 "Optimize and defragment drive C:"),
                ("restart_explorer", "🔄", "Restart Explorer", "",
                 lambda: self.cleanup_service.restart_explorer(),
                 "Restart Windows Explorer process"),
            ]),
            ("EXTERNAL TOOLS", [
                ("open_ccleaner", "🧽", "Open CCleaner", "",
                 lambda: self.cleanup_service.launch_ccleaner(self.config_manager),
                 "Launch CCleaner (configure path in settings)"),
                ("open_wise_memory", "🧠", "Open Wise Memory", "",
                 lambda: self.cleanup_service.launch_wise_memory_cleaner(self.config_manager),
                 "Launch Wise Memory Cleaner (configure path in settings)"),
                ("reset_ms_store", "🏪", "Reset MS Store", "",
                 lambda: self.cleanup_service.reset_ms_store(),
                 "Reset Microsoft Store cache"),
            ]),
            ("NETWORK", [
                ("reset_tcpip", "🌐", "Reset TCP/IP", "",
                 lambda: self.cleanup_service.reset_network(),
                 "Reset network stack (requires admin, restart recommended)"),
                ("release_renew_ip", "🔌", "Release/Renew IP", "",
                 lambda: self.cleanup_service.release_renew_ip(),
                 "Release and renew IP address"),
                ("network_stats", "📶", "Network Stats", "",
                 lambda: self.show_network_stats(),
                 "Display network statistics"),
            ]),
            ("WINDOWS UPDATE", [
                ("clear_update_cache", "🗑️", "Clear Update Cache", "",
                 lambda: self.cleanup_service.clear_windows_update_cache(),
                 "Clear Windows Update cache (requires admin)"),
                ("pause_updates", "⏸️", "Pause Updates", "(7 days)",
                 lambda: self.cleanup_service.pause_windows_updates(7),
                 "Pause Windows Updates for 7 days"),
            ]),
        ]

        id_aliases = {
            "clear_standby_ram": "clear_ram_standby",
            "defrag_optimize": "optimize_drives",
            "open_ccleaner": "ccleaner",
            "open_wise_memory": "wise_memory"
        }
        force_legacy = {"defrag_optimize", "pause_updates", "network_stats", "open_ccleaner", "open_wise_memory"}

        for section_title, tools in legacy_sections:
            buttons = []
            for tool_id, icon, title, subtitle, legacy_handler, tooltip in tools:
                handler = legacy_handler
                if tool_id not in force_legacy:
                    handler = self.tool_registry.get_handler(tool_id)
                    if not handler:
                        alias_id = id_aliases.get(tool_id)
                        if alias_id:
                            handler = self.tool_registry.get_handler(alias_id)
                if not handler:
                    logger.warning(f"Tool handler missing for {tool_id}")
                    handler = legacy_handler

                buttons.append((icon, title, subtitle, handler, tooltip))
            self.create_section(section_title, buttons)
    
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
