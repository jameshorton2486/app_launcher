"""
Project Dialog Component
Add/Edit project dialog with manual entry and drag-drop support
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
import uuid

# Try to import tkinterdnd2 for drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = None
    DND_FILES = None

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS


class ProjectDialog(ctk.CTkToplevel):
    """Dialog for adding or editing projects with manual entry and drag-drop modes"""
    
    def __init__(self, parent, config_manager, project=None, on_save=None, dropped_file=None):
        """
        Initialize project dialog
        
        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            project: Existing project dict (for edit mode) or None (for add mode)
            on_save: Callback when project is saved
            dropped_file: Path to dropped file/folder (for drag-drop mode)
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.project = project
        self.on_save = on_save
        self.result = None
        self.mode = "drag_drop" if dropped_file else ("edit" if project else "manual")
        self.dropped_file = dropped_file
        
        self.setup_window()
        self.setup_ui()
        
        # If dropped file, auto-detect values
        if dropped_file:
            self.auto_detect_from_file(dropped_file)
    
    def setup_window(self):
        """Configure dialog window"""
        title = "Edit Project" if self.project else ("Add Project (Drag & Drop)" if self.mode == "drag_drop" else "Add Project")
        self.title(title)
        self.geometry("650x750")
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Make modal
        if hasattr(self, 'master') and self.master:
            self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f'650x750+{x}+{y}')
    
    def setup_ui(self):
        """Set up the dialog UI"""
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = "Edit Project" if self.project else ("Add New Project (Drag & Drop)" if self.mode == "drag_drop" else "Add New Project")
        title_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=('Segoe UI', 18, 'bold'),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Drag & Drop Zone (only in add mode, not edit mode)
        if not self.project and self.mode != "drag_drop":
            self.setup_drag_drop_zone(main_frame)
        
        # Name field
        name_label = ctk.CTkLabel(main_frame, text="Name *", anchor='w', font=('Segoe UI', 11))
        name_label.pack(fill='x', pady=(0, 5))
        self.name_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.name_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.name_entry.insert(0, self.project.get('name', ''))
        
        # Path field
        path_label = ctk.CTkLabel(main_frame, text="Path *", anchor='w', font=('Segoe UI', 11))
        path_label.pack(fill='x', pady=(0, 5))
        path_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        path_frame.pack(fill='x', pady=(0, 15))
        self.path_entry = ctk.CTkEntry(path_frame, height=35, font=('Segoe UI', 11))
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        if self.project:
            self.path_entry.insert(0, self.project.get('path', ''))
        browse_path_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            width=80,
            height=35,
            command=lambda: self.browse_path(self.path_entry)
        )
        browse_path_btn.pack(side='right')
        
        # Launch Script field
        script_label = ctk.CTkLabel(main_frame, text="Launch Script *", anchor='w', font=('Segoe UI', 11))
        script_label.pack(fill='x', pady=(0, 5))
        script_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        script_frame.pack(fill='x', pady=(0, 15))
        self.script_entry = ctk.CTkEntry(script_frame, height=35, font=('Segoe UI', 11))
        self.script_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        if self.project:
            self.script_entry.insert(0, self.project.get('launch_script', ''))
        browse_script_btn = ctk.CTkButton(
            script_frame,
            text="Browse",
            width=80,
            height=35,
            command=lambda: self.browse_script(self.script_entry)
        )
        browse_script_btn.pack(side='right')
        
        # Launch Type
        type_label = ctk.CTkLabel(main_frame, text="Launch Type *", anchor='w', font=('Segoe UI', 11))
        type_label.pack(fill='x', pady=(0, 5))
        self.type_menu = ctk.CTkOptionMenu(
            main_frame,
            values=['python', 'npm', 'powershell', 'bat', 'exe'],
            height=35,
            font=('Segoe UI', 11)
        )
        self.type_menu.pack(fill='x', pady=(0, 15))
        if self.project:
            self.type_menu.set(self.project.get('launch_type', 'python'))
        else:
            self.type_menu.set('python')
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description", anchor='w', font=('Segoe UI', 11))
        desc_label.pack(fill='x', pady=(0, 5))
        self.desc_entry = ctk.CTkTextbox(main_frame, height=60, font=('Segoe UI', 11))
        self.desc_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.desc_entry.insert('1.0', self.project.get('description', ''))
        
        # Language
        lang_label = ctk.CTkLabel(main_frame, text="Language", anchor='w', font=('Segoe UI', 11))
        lang_label.pack(fill='x', pady=(0, 5))
        self.lang_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.lang_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.lang_entry.insert(0, self.project.get('language', ''))
        
        # GitHub URL
        github_label = ctk.CTkLabel(main_frame, text="GitHub URL", anchor='w', font=('Segoe UI', 11))
        github_label.pack(fill='x', pady=(0, 5))
        self.github_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.github_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.github_entry.insert(0, self.project.get('repo_url', ''))
        
        # Claude Project URL
        claude_label = ctk.CTkLabel(main_frame, text="Claude Project URL", anchor='w', font=('Segoe UI', 11))
        claude_label.pack(fill='x', pady=(0, 5))
        self.claude_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.claude_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.claude_entry.insert(0, self.project.get('claude_project_url', ''))
        
        # Icon
        icon_label = ctk.CTkLabel(main_frame, text="Icon (emoji)", anchor='w', font=('Segoe UI', 11))
        icon_label.pack(fill='x', pady=(0, 5))
        self.icon_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.icon_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            self.icon_entry.insert(0, self.project.get('icon', '📁'))
        else:
            self.icon_entry.insert(0, '📁')
        
        # File patterns
        patterns_label = ctk.CTkLabel(
            main_frame,
            text="File Patterns (comma-separated keywords for downloads matching)",
            anchor='w',
            font=('Segoe UI', 11)
        )
        patterns_label.pack(fill='x', pady=(0, 5))
        self.patterns_entry = ctk.CTkEntry(main_frame, height=35, font=('Segoe UI', 11))
        self.patterns_entry.pack(fill='x', pady=(0, 15))
        if self.project:
            patterns = self.project.get('file_patterns', [])
            self.patterns_entry.insert(0, ', '.join(patterns))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        button_frame.pack(fill='x', pady=(10, 0))
        
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
    
    def setup_drag_drop_zone(self, parent):
        """Set up drag and drop zone"""
        drop_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_secondary'],
            border_width=2,
            border_color=COLORS['border'],
            corner_radius=8
        )
        drop_frame.pack(fill='x', pady=(0, 20))
        
        drop_label = ctk.CTkLabel(
            drop_frame,
            text="📁 Drag & Drop File or Folder Here\n(.exe, .py, .ps1, .bat, .cmd, or folder)",
            font=('Segoe UI', 12),
            text_color=COLORS['text_secondary'],
            height=80
        )
        drop_label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Try to enable drag-and-drop if available
        if DND_AVAILABLE:
            try:
                drop_frame.drop_target_register(DND_FILES)
                drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            except:
                pass
        
        # Fallback: Click to browse
        def on_click(event):
            self.browse_file_or_folder()
        
        drop_frame.bind('<Button-1>', on_click)
        drop_label.bind('<Button-1>', on_click)
    
    def on_drop(self, event):
        """Handle file drop event"""
        if DND_AVAILABLE:
            files = self.tk.splitlist(event.data)
            if files:
                self.auto_detect_from_file(files[0])
    
    def browse_file_or_folder(self):
        """Browse for file or folder"""
        # First try folder
        directory = filedialog.askdirectory(title="Select Project Folder")
        if directory:
            self.auto_detect_from_file(directory)
            return
        
        # Then try file
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Supported", "*.exe;*.py;*.ps1;*.bat;*.cmd"),
                ("Executable", "*.exe"),
                ("Python", "*.py"),
                ("PowerShell", "*.ps1"),
                ("Batch", "*.bat;*.cmd"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.auto_detect_from_file(file_path)
    
    def auto_detect_from_file(self, file_path: str):
        """Auto-detect project values from dropped file/folder"""
        if not file_path or not os.path.exists(file_path):
            return
        
        # Determine if it's a file or folder
        is_file = os.path.isfile(file_path)
        is_dir = os.path.isdir(file_path)
        
        if not (is_file or is_dir):
            return
        
        # Auto-detect name from filename
        if is_file:
            name = os.path.splitext(os.path.basename(file_path))[0]
            path = os.path.dirname(file_path)
            script = os.path.basename(file_path)
        else:
            name = os.path.basename(file_path)
            path = file_path
            # Try to find common launch scripts
            script = self.find_launch_script(file_path)
        
        # Auto-detect launch type
        if is_file:
            ext = os.path.splitext(file_path)[1].lower()
            launch_type_map = {
                '.exe': 'exe',
                '.py': 'python',
                '.ps1': 'powershell',
                '.bat': 'bat',
                '.cmd': 'bat'
            }
            launch_type = launch_type_map.get(ext, 'python')
        else:
            # For folders, check for package.json (npm) or common Python files
            if os.path.exists(os.path.join(file_path, 'package.json')):
                launch_type = 'npm'
                script = 'run dev'  # Default npm command
            elif os.path.exists(os.path.join(file_path, 'main.py')):
                launch_type = 'python'
                script = 'main.py'
            elif os.path.exists(os.path.join(file_path, 'app.py')):
                launch_type = 'python'
                script = 'app.py'
            else:
                launch_type = 'python'
                script = script or 'main.py'
        
        # Auto-detect icon based on file type
        icon_map = {
            '.exe': '⚙️',
            '.py': '🐍',
            '.ps1': '💻',
            '.bat': '📜',
            '.cmd': '📜'
        }
        if is_file:
            ext = os.path.splitext(file_path)[1].lower()
            icon = icon_map.get(ext, '📁')
        else:
            icon = '📁'
        
        # Fill in the form
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, name)
        
        self.path_entry.delete(0, 'end')
        self.path_entry.insert(0, path)
        
        self.script_entry.delete(0, 'end')
        self.script_entry.insert(0, script)
        
        self.type_menu.set(launch_type)
        
        self.icon_entry.delete(0, 'end')
        self.icon_entry.insert(0, icon)
    
    def find_launch_script(self, folder_path: str) -> str:
        """Find a launch script in a folder"""
        common_scripts = [
            'main.py', 'app.py', 'run.py', 'start.py',
            'index.py', 'server.py', 'app.ps1', 'start.ps1',
            'run.bat', 'start.bat', 'launch.bat'
        ]
        
        for script in common_scripts:
            script_path = os.path.join(folder_path, script)
            if os.path.exists(script_path):
                return script
        
        return ''
    
    def browse_path(self, entry):
        """Browse for directory"""
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, 'end')
            entry.insert(0, directory)
    
    def browse_script(self, entry):
        """Browse for script file"""
        script = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[
                ("All Files", "*.*"),
                ("Python", "*.py"),
                ("PowerShell", "*.ps1"),
                ("Batch", "*.bat;*.cmd"),
                ("Executable", "*.exe")
            ]
        )
        if script:
            entry.delete(0, 'end')
            entry.insert(0, script)
    
    def validate(self):
        """
        Validate form data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check name
        name = self.name_entry.get().strip()
        if not name:
            return False, "Name is required"
        
        # Check for duplicate names
        projects = self.config_manager.load_projects()
        for p in projects:
            if p.get('id') != self.project.get('id') if self.project else None:
                if p.get('name', '').lower() == name.lower():
                    return False, f"Project with name '{name}' already exists"
        
        # Check path
        path = self.path_entry.get().strip()
        if not path:
            return False, "Path is required"
        
        if not os.path.isdir(path):
            return False, f"Path does not exist: {path}"
        
        # Check launch script
        script = self.script_entry.get().strip()
        if not script:
            return False, "Launch script is required"
        
        launch_type = self.type_menu.get()
        
        # For npm, script is a command (e.g., "run dev"), not a file
        if launch_type == 'npm':
            # Check if package.json exists
            package_json = os.path.join(path, 'package.json')
            if not os.path.exists(package_json):
                return False, f"package.json not found in {path}"
        else:
            # For other types, script should be a file
            script_path = os.path.join(path, script) if not os.path.isabs(script) else script
            if not os.path.exists(script_path):
                return False, f"Launch script does not exist: {script_path}"
        
        return True, ""
    
    def save(self):
        """Save project"""
        # Validate
        is_valid, error_msg = self.validate()
        if not is_valid:
            self.show_error(error_msg)
            return
        
        # Build project dict
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        script = self.script_entry.get().strip()
        
        project = {
            'id': self.project.get('id') if self.project else str(uuid.uuid4()),
            'name': name,
            'path': path,
            'launch_script': script,
            'launch_type': self.type_menu.get(),
            'description': self.desc_entry.get('1.0', 'end-1c').strip(),
            'language': self.lang_entry.get().strip(),
            'repo_url': self.github_entry.get().strip(),
            'claude_project_url': self.claude_entry.get().strip(),
            'icon': self.icon_entry.get().strip() or '📁',
            'favorite': self.project.get('favorite', False) if self.project else False,
            'file_patterns': [p.strip() for p in self.patterns_entry.get().split(',') if p.strip()]
        }
        
        self.result = project
        if self.on_save:
            self.on_save(project)
        self.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.destroy()
    
    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Validation Error", message)
