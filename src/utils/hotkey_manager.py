"""
Hotkey Manager
Handles global hotkey registration and management
"""

import keyboard
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class HotkeyManager:
    """Manages global hotkey registration"""
    
    def __init__(self):
        """Initialize HotkeyManager"""
        self.current_hotkey = None
        self.current_callback = None
        self.registered = False
    
    def normalize_hotkey(self, hotkey_str: str) -> str:
        """
        Normalize hotkey string to keyboard library format
        
        Args:
            hotkey_str: Hotkey string (e.g., "win+shift+l")
            
        Returns:
            Normalized hotkey string (e.g., "windows+shift+l")
        """
        # Convert common variations to keyboard library format
        normalized = hotkey_str.lower().strip()
        
        # Replace common variations
        replacements = {
            'win': 'windows',
            'ctrl': 'ctrl',
            'alt': 'alt',
            'shift': 'shift',
            ' ': '+',  # Spaces to plus signs
            '++': '+'   # Remove double plus signs
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Clean up any double plus signs
        while '++' in normalized:
            normalized = normalized.replace('++', '+')
        
        # Remove leading/trailing plus signs
        normalized = normalized.strip('+')
        
        return normalized
    
    def format_hotkey_display(self, hotkey_str: str) -> str:
        """
        Format hotkey for display in UI
        
        Args:
            hotkey_str: Normalized hotkey string
            
        Returns:
            Formatted string for display
        """
        # Convert back to user-friendly format
        display = hotkey_str.replace('windows', 'Win')
        display = display.replace('+', ' + ')
        return display
    
    def register(self, hotkey_str: str, callback) -> tuple[bool, str]:
        """
        Register a global hotkey
        
        Args:
            hotkey_str: Hotkey string (e.g., "win+shift+l")
            callback: Function to call when hotkey is pressed
            
        Returns:
            Tuple of (success, message)
        """
        # Unregister existing hotkey if any
        if self.registered:
            self.unregister()
        
        try:
            # Normalize hotkey string
            normalized = self.normalize_hotkey(hotkey_str)
            
            # Try to register the hotkey
            keyboard.add_hotkey(normalized, callback)
            
            self.current_hotkey = normalized
            self.current_callback = callback
            self.registered = True
            
            logger.info(f"Hotkey registered: {normalized}")
            return True, f"Hotkey registered: {self.format_hotkey_display(normalized)}"
        
        except keyboard.HotkeyAlreadyRegisteredError:
            error_msg = f"Hotkey '{self.format_hotkey_display(normalized)}' is already registered by another application"
            logger.warning(error_msg)
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Failed to register hotkey: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def unregister(self):
        """Unregister the current hotkey"""
        if self.registered:
            try:
                # keyboard library doesn't have remove_hotkey for specific hotkeys
                # We need to unhook all and re-register if needed
                # For now, just unhook all (we'll re-register if needed)
                keyboard.unhook_all()
                logger.info(f"Hotkey unregistered: {self.current_hotkey}")
            except Exception as e:
                logger.warning(f"Error unregistering hotkey: {e}")
            
            self.current_hotkey = None
            self.current_callback = None
            self.registered = False
    
    def is_registered(self) -> bool:
        """Check if a hotkey is currently registered"""
        return self.registered
    
    def get_current_hotkey(self) -> str:
        """Get the current registered hotkey (normalized)"""
        return self.current_hotkey or ""
    
    def cleanup(self):
        """Clean up all hotkey registrations"""
        self.unregister()
        try:
            keyboard.unhook_all()
        except Exception as e:
            logger.debug(f"Error in hotkey cleanup: {e}")
