"""
Search Bar Component
Provides search/filter functionality for tabs with debouncing
"""

import customtkinter as ctk
import threading


from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class SearchBar(ctk.CTkFrame):
    """Search bar component with filter functionality and debouncing"""
    
    def __init__(self, parent, on_search_callback=None, placeholder="Search...", debounce_ms=300):
        """
        Initialize search bar
        
        Args:
            parent: Parent widget
            on_search_callback: Callback function called when search text changes
            placeholder: Placeholder text for search field
            debounce_ms: Debounce delay in milliseconds (default: 300ms)
        """
        super().__init__(parent, fg_color=COLORS['bg_secondary'], corner_radius=0)
        
        self.on_search_callback = on_search_callback
        self.placeholder = placeholder
        self.debounce_ms = debounce_ms / 1000.0  # Convert to seconds
        self._debounce_timer = None
        self._lock = threading.Lock()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the search bar UI"""
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=self.placeholder,
            height=35,
            font=('Segoe UI', 11),
            fg_color=COLORS['bg_tertiary'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted']
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(10, 5), pady=10)
        
        # Bind search event
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        # Clear button
        self.clear_btn = Button3D(
            self,
            text="✕",
            width=35,
            height=35,
            font=('Segoe UI', 12),
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.clear_search
        )
        self.clear_btn.pack(side='right', padx=(5, 10), pady=10)
    
    def _on_search_changed(self, event=None):
        """Handle search text change with debouncing"""
        # Cancel previous timer if exists
        if self._debounce_timer is not None:
            self.after_cancel(self._debounce_timer)
        
        # Schedule new callback after debounce delay
        self._debounce_timer = self.after(int(self.debounce_ms * 1000), self._execute_search)
    
    def _execute_search(self):
        """Execute the search callback after debounce delay"""
        try:
            search_text = self.search_entry.get()
            if self.on_search_callback:
                self.on_search_callback(search_text)
        except Exception as e:
            logger.error(f"Error in search callback: {e}", exc_info=True)
        finally:
            self._debounce_timer = None
    
    def clear_search(self):
        """Clear search field"""
        try:
            # Cancel any pending search
            if self._debounce_timer is not None:
                self.after_cancel(self._debounce_timer)
                self._debounce_timer = None
            
            self.search_entry.delete(0, 'end')
            if self.on_search_callback:
                self.on_search_callback("")
        except Exception as e:
            logger.error(f"Error clearing search: {e}", exc_info=True)
    
    def get_search_text(self) -> str:
        """Get current search text"""
        try:
            return self.search_entry.get()
        except Exception as e:
            logger.error(f"Error getting search text: {e}", exc_info=True)
            return ""
    
    def set_search_text(self, text: str):
        """Set search text"""
        try:
            self.search_entry.delete(0, 'end')
            self.search_entry.insert(0, text)
            # Trigger search callback
            if self.on_search_callback:
                self.on_search_callback(text)
        except Exception as e:
            logger.error(f"Error setting search text: {e}", exc_info=True)
