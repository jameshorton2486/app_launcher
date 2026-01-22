"""
Hotkey Capture Dialog
Dialog for capturing global hotkey combinations
"""

import customtkinter as ctk
import keyboard
import sys
import os
import threading
import time

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class HotkeyCaptureDialog(ctk.CTkToplevel):
    """Dialog for capturing a hotkey combination"""
    
    def __init__(self, parent, current_hotkey=""):
        """
        Initialize hotkey capture dialog
        
        Args:
            parent: Parent window
            current_hotkey: Current hotkey string
        """
        super().__init__(parent)
        
        self.result = None
        self.captured_keys = []
        self.capturing = False
        self.current_hotkey = current_hotkey
        
        self.setup_window()
        self.setup_ui()
        self.start_capture()
    
    def setup_window(self):
        """Configure dialog window"""
        self.title("Capture Hotkey")
        self.geometry("500x200")
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f'500x200+{x}+{y}')
        
        # Make window stay on top
        self.attributes('-topmost', True)
        
        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def setup_ui(self):
        """Set up the dialog UI"""
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_frame,
            text="Press the key combination you want to use as the global hotkey:",
            font=('Segoe UI', 11),
            text_color=COLORS['text_primary']
        )
        instructions.pack(pady=(0, 10))
        
        # Current hotkey display
        current_label = ctk.CTkLabel(
            main_frame,
            text=f"Current: {self.current_hotkey}",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        current_label.pack(pady=(0, 10))
        
        # Captured keys display
        self.capture_label = ctk.CTkLabel(
            main_frame,
            text="Press keys...",
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['accent_primary'],
            height=40
        )
        self.capture_label.pack(pady=10, fill='x')
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        button_frame.pack(fill='x', pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            height=32,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_danger'],
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            width=100,
            height=32,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            command=self.save,
            state='disabled'
        )
        self.save_btn.pack(side='right')
    
    def start_capture(self):
        """Start capturing key combinations"""
        self.capturing = True
        self.captured_keys = []
        self.pressed_modifiers = set()
        self.last_key_time = 0
        
        def on_press(event):
            if not self.capturing:
                return
            
            try:
                key_name = event.name.lower()
                
                # Map common key names
                key_mapping = {
                    'left ctrl': 'ctrl',
                    'right ctrl': 'ctrl',
                    'left alt': 'alt',
                    'right alt': 'alt',
                    'left shift': 'shift',
                    'right shift': 'shift',
                    'left windows': 'windows',
                    'right windows': 'windows',
                    'left win': 'windows',
                    'right win': 'windows'
                }
                
                key_name = key_mapping.get(key_name, key_name)
                
                # Check if it's a modifier
                modifiers = ['ctrl', 'alt', 'shift', 'windows']
                is_modifier = key_name in modifiers
                
                if is_modifier:
                    self.pressed_modifiers.add(key_name)
                    self.after(0, lambda: self.update_capture_display_live())
                else:
                    # Regular key pressed - complete the combination
                    # Skip very short keys that might be accidental
                    if key_name and len(key_name) > 1:  # Skip single character keys that might be typos
                        # Combine modifiers with the key
                        combo = sorted(list(self.pressed_modifiers)) + [key_name]
                        self.captured_keys = combo
                        self.capturing = False
                        if hasattr(self, 'hook'):
                            keyboard.unhook(self.hook)
                        self.after(0, self.update_capture_display)
            except Exception as e:
                logger.debug(f"Error in hotkey capture: {e}")
        
        # Hook keyboard events
        try:
            self.hook = keyboard.hook(on_press)
        except Exception as e:
            logger.error(f"Failed to hook keyboard: {e}")
            self.capturing = False
            self.capture_label.configure(
                text="Failed to start capture",
                text_color=COLORS['accent_danger']
            )
    
    def update_capture_display_live(self):
        """Update display while capturing (shows modifiers being held)"""
        if self.pressed_modifiers:
            mods_display = '+'.join(sorted(self.pressed_modifiers)).replace('windows', 'win')
            self.capture_label.configure(
                text=f"Press keys... ({mods_display} + ?)",
                text_color=COLORS['accent_warning']
            )
        else:
            self.capture_label.configure(
                text="Press keys...",
                text_color=COLORS['accent_primary']
            )
    
    def update_capture_display(self):
        """Update the capture display with captured keys"""
        if self.captured_keys:
            # Format the hotkey string
            hotkey_str = '+'.join(sorted([k for k in self.captured_keys if k in ['ctrl', 'alt', 'shift', 'windows']]) + 
                                 [k for k in self.captured_keys if k not in ['ctrl', 'alt', 'shift', 'windows']])
            # Convert windows back to win for display
            hotkey_display = hotkey_str.replace('windows', 'win')
            
            self.capture_label.configure(
                text=f"Captured: {hotkey_display}",
                text_color=COLORS['accent_success']
            )
            self.save_btn.configure(state='normal')
        else:
            self.capture_label.configure(
                text="No keys captured",
                text_color=COLORS['accent_danger']
            )
            self.save_btn.configure(state='disabled')
    
    def save(self):
        """Save the captured hotkey"""
        if self.captured_keys:
            # Format hotkey string (convert windows to win for storage)
            # Sort modifiers first, then the main key
            modifiers = sorted([k for k in self.captured_keys if k in ['ctrl', 'alt', 'shift', 'windows']])
            main_key = [k for k in self.captured_keys if k not in ['ctrl', 'alt', 'shift', 'windows']]
            hotkey_str = '+'.join(modifiers + main_key).replace('windows', 'win')
            self.result = hotkey_str
            if hasattr(self, 'hook'):
                keyboard.unhook(self.hook)
            self.destroy()
        else:
            self.cancel()
    
    def cancel(self):
        """Cancel hotkey capture"""
        self.capturing = False
        if hasattr(self, 'hook'):
            try:
                keyboard.unhook(self.hook)
            except:
                pass
        self.result = None
        self.destroy()
