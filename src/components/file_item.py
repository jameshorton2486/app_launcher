"""
File Item Component
Displays individual file information in downloads tab
"""

import customtkinter as ctk
import sys
import os
import tkinter as tk

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS


class FileItem(ctk.CTkFrame):
    """Component for displaying a file in the downloads list"""
    
    # Icon mapping for file types
    ICONS = {
        'Code': '💻',
        'Docs': '📄',
        'Images': '🖼️',
        'Archives': '📦',
        'Unknown': '📁'
    }
    
    def __init__(self, parent, file_info: dict, file_service, config_manager, on_select=None, on_move=None, on_delete=None):
        """
        Initialize file item
        
        Args:
            parent: Parent widget
            file_info: File dictionary with name, path, size, modified, category, suggested_project
            file_service: FileService instance
            config_manager: ConfigManager instance
            on_select: Callback when checkbox is toggled (file_info, selected)
            on_move: Callback when move button is clicked (file_info, destination)
            on_delete: Callback when delete button is clicked (file_info)
        """
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=4,
            border_width=1,
            border_color=COLORS['border']
        )
        
        self.file_info = file_info
        self.file_service = file_service
        self.config_manager = config_manager
        self.on_select = on_select
        self.on_move = on_move
        self.on_delete = on_delete
        self.selected = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the file item UI"""
        # Main horizontal frame
        main_frame = ctk.CTkFrame(self, fg_color='transparent')
        main_frame.pack(fill='x', padx=10, pady=8)
        
        # Checkbox
        self.checkbox = ctk.CTkCheckBox(
            main_frame,
            text="",
            width=20,
            height=20,
            command=self.toggle_select
        )
        self.checkbox.pack(side='left', padx=(0, 10))
        
        # File icon
        icon_text = self.ICONS.get(self.file_info.get('category', 'Unknown'), '📁')
        icon_label = ctk.CTkLabel(
            main_frame,
            text=icon_text,
            font=('Segoe UI', 16),
            width=30
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        # Filename (truncated)
        filename = self.file_info.get('name', 'Unknown')
        max_length = 40
        display_name = filename if len(filename) <= max_length else filename[:max_length-3] + '...'
        
        self.name_label = ctk.CTkLabel(
            main_frame,
            text=display_name,
            font=('Segoe UI', 11),
            text_color=COLORS['text_primary'],
            anchor='w',
            width=200
        )
        self.name_label.pack(side='left', padx=(0, 10))
        
        # Tooltip for full filename
        if len(filename) > max_length:
            self._create_tooltip(self.name_label, filename)
        
        # File size
        size = self.file_service.format_file_size(self.file_info.get('size', 0))
        size_label = ctk.CTkLabel(
            main_frame,
            text=size,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            width=80
        )
        size_label.pack(side='left', padx=(0, 10))
        
        # Modified date
        modified = self.file_info.get('modified')
        if modified:
            date_str = self.file_service.format_date(modified)
        else:
            date_str = "Unknown"
        
        date_label = ctk.CTkLabel(
            main_frame,
            text=date_str,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary'],
            width=100
        )
        date_label.pack(side='left', padx=(0, 10))
        
        # Suggested destination dropdown
        self.dest_menu = self._create_destination_menu(main_frame)
        self.dest_menu.pack(side='left', padx=(0, 10))
        
        # Move button
        move_btn = ctk.CTkButton(
            main_frame,
            text="Move",
            width=70,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            command=self.handle_move
        )
        move_btn.pack(side='left', padx=(0, 5))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            main_frame,
            text="Delete",
            width=70,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['accent_danger'],
            hover_color='#cc0000',
            command=self.handle_delete
        )
        delete_btn.pack(side='left')
    
    def _create_destination_menu(self, parent) -> ctk.CTkOptionMenu:
        """Create destination dropdown menu"""
        # Get projects
        projects = self.config_manager.load_projects()
        
        # Build menu values
        values = ['Select destination...']
        
        # Add suggested project if available
        suggested = self.file_info.get('suggested_project')
        if suggested:
            for project in projects:
                project_id = project.get('id') or project.get('name', '')
                if project_id == suggested:
                    values.append(f"📁 {project.get('name', 'Project')}")
                    break
        
        # Add all projects
        for project in projects:
            project_name = project.get('name', 'Unknown')
            project_id = project.get('id') or project_name
            if not suggested or project_id != suggested:
                values.append(f"📁 {project_name}")
        
        # Add special destinations
        values.append("📸 Screenshots")
        values.append("📦 Archives")
        values.append("➕ Custom...")
        
        menu = ctk.CTkOptionMenu(
            parent,
            values=values,
            width=150,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['bg_tertiary'],
            button_hover_color=COLORS['accent_secondary']
        )
        menu.set(values[0])
        
        return menu
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=text,
                background=COLORS['bg_secondary'],
                foreground=COLORS['text_primary'],
                relief='solid',
                borderwidth=1,
                font=('Segoe UI', 9),
                padx=5,
                pady=3
            )
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def toggle_select(self):
        """Toggle selection state"""
        self.selected = self.checkbox.get()
        if self.on_select:
            self.on_select(self.file_info, self.selected)
    
    def set_selected(self, selected: bool):
        """Set selection state programmatically"""
        self.selected = selected
        self.checkbox.select() if selected else self.checkbox.deselect()
    
    def handle_move(self):
        """Handle move button click"""
        destination = self.dest_menu.get()
        
        if destination == 'Select destination...':
            return
        
        if destination == '➕ Custom...':
            # Open folder dialog
            from tkinter import filedialog
            dest_folder = filedialog.askdirectory(title="Select Destination Folder")
            if not dest_folder:
                return
            destination = dest_folder
        elif destination == '📸 Screenshots':
            screenshots_folder = self.config_manager.get_setting('screenshots_folder', '')
            if not screenshots_folder:
                # Show error
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Screenshots folder not configured in settings")
                return
            destination = screenshots_folder
        elif destination == '📦 Archives':
            # Use downloads folder/Archives
            downloads_folder = self.config_manager.get_setting('downloads_folder', '')
            if downloads_folder:
                destination = os.path.join(downloads_folder, 'Archives')
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Downloads folder not configured")
                return
        else:
            # Extract project name
            project_name = destination.replace('📁 ', '')
            projects = self.config_manager.load_projects()
            for project in projects:
                if project.get('name') == project_name:
                    destination = project.get('path', '')
                    break
        
        if self.on_move:
            self.on_move(self.file_info, destination)
    
    def handle_delete(self):
        """Handle delete button click"""
        if self.on_delete:
            self.on_delete(self.file_info)
