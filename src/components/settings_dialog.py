"""
Settings Dialog Component
Comprehensive settings management UI
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, colorchooser
import os


from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog for application configuration"""
    
    def __init__(self, parent, config_manager, on_save=None):
        """
        Initialize settings dialog
        
        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            on_save: Callback when settings are saved
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.on_save = on_save
        self.settings = config_manager.settings.copy()
        self.result = None
        
        self.setup_window()
        self.setup_ui()
        self.bind("<Escape>", lambda e: self.destroy())
    
    def setup_window(self):
        """Configure dialog window"""
        self.title("Settings")
        self.geometry("700x800")
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f'700x800+{x}+{y}')
    
    def setup_ui(self):
        """Set up the settings UI"""
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # GENERAL Section
        self.create_section(main_frame, "GENERAL")
        
        # Start with Windows
        self.start_with_windows = ctk.BooleanVar(value=self.settings.get('window', {}).get('start_with_windows', False))
        ctk.CTkCheckBox(
            main_frame,
            text="Start with Windows",
            variable=self.start_with_windows,
            font=('Segoe UI', 11)
        ).pack(fill='x', pady=5)
        
        # Minimize to tray
        self.minimize_to_tray = ctk.BooleanVar(value=self.settings.get('window', {}).get('minimize_to_tray', True))
        ctk.CTkCheckBox(
            main_frame,
            text="Minimize to system tray on close",
            variable=self.minimize_to_tray,
            font=('Segoe UI', 11)
        ).pack(fill='x', pady=5)
        
        # Start minimized
        self.start_minimized = ctk.BooleanVar(value=self.settings.get('window', {}).get('start_minimized', False))
        ctk.CTkCheckBox(
            main_frame,
            text="Start minimized",
            variable=self.start_minimized,
            font=('Segoe UI', 11)
        ).pack(fill='x', pady=5)

        self.professional_mode = ctk.BooleanVar(value=self.settings.get('ui', {}).get('professional_mode', True))
        ctk.CTkCheckBox(
            main_frame,
            text="Professional Mode",
            variable=self.professional_mode,
            font=('Segoe UI', 11)
        ).pack(fill='x', pady=5)
        
        # HOTKEY Section
        self.create_section(main_frame, "HOTKEY")
        
        hotkey_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        hotkey_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(hotkey_frame, text="Global hotkey:", font=('Segoe UI', 11)).pack(side='left', padx=(0, 10))
        self.hotkey_entry = ctk.CTkEntry(hotkey_frame, width=200, font=('Segoe UI', 11))
        self.hotkey_entry.pack(side='left', padx=(0, 10))
        current_hotkey = self.settings.get('window', {}).get('global_hotkey', 'win+shift+l')
        # Format for display
        hotkey_display = current_hotkey.replace('+', ' + ').replace('windows', 'Win').replace('win', 'Win')
        self.hotkey_entry.insert(0, hotkey_display)
        self.hotkey_entry.configure(state='readonly')  # Make read-only, use button to change
        
        self.change_hotkey_btn = Button3D(
            hotkey_frame,
            text="Change Hotkey",
            width=120,
            height=32,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.change_hotkey
        )
        self.change_hotkey_btn.pack(side='left')
        
        # PATHS Section
        self.create_section(main_frame, "PATHS")
        
        # Downloads folder
        self.create_path_field(main_frame, "Downloads folder:", 'paths.downloads_folder')
        
        # Screenshots folder
        self.create_path_field(main_frame, "Screenshots folder:", 'paths.screenshots_folder', 
                              default='C:\\Users\\james\\Documents\\Screenshots')
        
        # EXTERNAL TOOLS Section
        self.create_section(main_frame, "EXTERNAL TOOLS")
        
        self.create_path_field(main_frame, "Cursor:", 'external_tools.cursor')
        self.create_path_field(main_frame, "VS Code:", 'external_tools.vscode')
        self.create_path_field(main_frame, "PyCharm:", 'external_tools.pycharm')
        
        # THEME Section
        self.create_section(main_frame, "THEME")
        
        # Theme mode
        theme_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        theme_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(theme_frame, text="Mode:", font=('Segoe UI', 11)).pack(side='left', padx=(0, 10))
        self.theme_mode = ctk.CTkOptionMenu(
            theme_frame,
            values=['dark', 'light', 'system'],
            width=150,
            font=('Segoe UI', 11)
        )
        self.theme_mode.pack(side='left')
        self.theme_mode.set(self.settings.get('theme', {}).get('mode', 'dark'))
        
        # Accent color
        color_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        color_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(color_frame, text="Accent Color:", font=('Segoe UI', 11)).pack(side='left', padx=(0, 10))
        
        self.color_preview = ctk.CTkFrame(
            color_frame,
            width=50,
            height=30,
            fg_color=self.settings.get('theme', {}).get('accent_color', COLORS['accent_primary'])
        )
        self.color_preview.pack(side='left', padx=(0, 10))
        
        self.accent_color = self.settings.get('theme', {}).get('accent_color', COLORS['accent_primary'])
        
        Button3D(
            color_frame,
            text="Pick",
            width=80,
            height=32,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.pick_color
        ).pack(side='left')
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        button_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = Button3D(
            button_frame,
            text="Cancel",
            width=120,
            height=35,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = Button3D(
            button_frame,
            text="Save",
            width=120,
            height=35,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=self.save
        )
        save_btn.pack(side='right')
    
    def create_section(self, parent, title):
        """Create a section header"""
        section_label = ctk.CTkLabel(
            parent,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        section_label.pack(fill='x', pady=(20, 10))
    
    def create_path_field(self, parent, label_text, setting_key, default=''):
        """Create a path input field with browse button"""
        path_frame = ctk.CTkFrame(parent, fg_color='transparent')
        path_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(path_frame, text=label_text, font=('Segoe UI', 11), width=150, anchor='w').pack(side='left', padx=(0, 10))
        
        # Get current value
        keys = setting_key.split('.')
        value = self.settings
        for key in keys:
            value = value.get(key, {})
        current_value = value if isinstance(value, str) else default
        
        entry = ctk.CTkEntry(path_frame, width=350, font=('Segoe UI', 11))
        entry.pack(side='left', padx=(0, 10))
        entry.insert(0, current_value)
        
        # Store reference for later retrieval
        if not hasattr(self, 'path_entries'):
            self.path_entries = {}
        self.path_entries[setting_key] = entry
        
        Button3D(
            path_frame,
            text="Browse",
            width=80,
            height=32,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=lambda: self.browse_path(entry)
        ).pack(side='left')
    
    def browse_path(self, entry):
        """Browse for directory or file"""
        current = entry.get()
        if os.path.isdir(current) if current else False:
            path = filedialog.askdirectory(initialdir=current)
        else:
            path = filedialog.askopenfilename(initialdir=os.path.dirname(current) if current else os.path.expanduser('~'))
        
        if path:
            entry.delete(0, 'end')
            entry.insert(0, path)
    
    def change_hotkey(self):
        """Open hotkey capture dialog"""
        from src.components.hotkey_capture_dialog import HotkeyCaptureDialog
        
        # Get current hotkey (remove formatting)
        current = self.hotkey_entry.get().replace(' + ', '+').replace('Win', 'win').replace(' ', '')
        dialog = HotkeyCaptureDialog(self, current)
        self.wait_window(dialog)
        
        if dialog.result:
            # Update the entry with the captured hotkey (formatted for display)
            self.hotkey_entry.configure(state='normal')
            self.hotkey_entry.delete(0, 'end')
            hotkey_display = dialog.result.replace('+', ' + ').replace('windows', 'Win').replace('win', 'Win')
            self.hotkey_entry.insert(0, hotkey_display)
            self.hotkey_entry.configure(state='readonly')
    
    def pick_color(self):
        """Pick accent color"""
        color = colorchooser.askcolor(initialcolor=self.accent_color)[1]
        if color:
            self.accent_color = color
            self.color_preview.configure(fg_color=color)
    
    def validate_paths(self) -> tuple[bool, str]:
        """
        Validate all path entries
        
        Returns:
            Tuple of (success, error_message)
        """
        errors = []
        
        # Validate paths (directories)
        directory_paths = [
            ('paths.downloads_folder', 'Downloads folder'),
            ('paths.screenshots_folder', 'Screenshots folder')
        ]
        
        for key, name in directory_paths:
            entry = self.path_entries.get(key)
            if entry:
                path = entry.get().strip()
                if path:  # Only validate if path is provided
                    if not os.path.exists(path):
                        errors.append(f"{name} path does not exist: {path}")
                    elif not os.path.isdir(path):
                        errors.append(f"{name} is not a directory: {path}")
        
        # Validate external tools (files)
        tool_paths = [
            ('external_tools.cursor', 'Cursor'),
            ('external_tools.vscode', 'VS Code'),
            ('external_tools.pycharm', 'PyCharm')
        ]
        
        for key, name in tool_paths:
            entry = self.path_entries.get(key)
            if entry:
                path = entry.get().strip()
                if path:  # Only validate if path is provided
                    if not os.path.exists(path):
                        errors.append(f"{name} path does not exist: {path}")
                    elif not os.path.isfile(path):
                        errors.append(f"{name} is not a file: {path}")
        
        if errors:
            return False, "\n".join(errors)
        return True, ""
    
    def save(self):
        """Save settings"""
        # Validate paths first
        valid, error_msg = self.validate_paths()
        if not valid:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{error_msg}")
            return
        
        # Update settings dict
        self.settings['window']['start_with_windows'] = self.start_with_windows.get()
        self.settings['window']['minimize_to_tray'] = self.minimize_to_tray.get()
        self.settings['window']['start_minimized'] = self.start_minimized.get()
        # Get hotkey (remove formatting for storage)
        hotkey_value = self.hotkey_entry.get().replace(' + ', '+').replace('Win', 'win').replace(' ', '').lower()
        self.settings['window']['global_hotkey'] = hotkey_value
        self.settings['theme']['mode'] = self.theme_mode.get()
        self.settings['theme']['accent_color'] = self.accent_color
        self.settings.setdefault('ui', {})
        self.settings['ui']['professional_mode'] = self.professional_mode.get()
        
        # Update paths
        for key, entry in getattr(self, 'path_entries', {}).items():
            keys = key.split('.')
            value = self.settings
            for k in keys[:-1]:
                if k not in value:
                    value[k] = {}
                value = value[k]
            value[keys[-1]] = entry.get()
        
        # Save to config
        self.config_manager.save_settings(self.settings)
        
        # Apply theme changes immediately
        try:
            from src.theme import apply_theme
            theme_mode = self.settings.get('theme', {}).get('mode', 'dark')
            accent_color = self.settings.get('theme', {}).get('accent_color', COLORS['accent_primary'])
            apply_theme(self.master, mode=theme_mode, accent_color=accent_color)
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("Theme Warning", f"Could not apply theme changes: {e}")
        
        if self.on_save:
            self.on_save(self.settings)
        
        self.result = self.settings
        self.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.destroy()
