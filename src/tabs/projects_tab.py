"""
Projects Tab
Displays and manages project cards
"""

import customtkinter as ctk
import os
import threading
import queue
import time
from typing import Dict


from src.theme import COLORS, FONTS
from src.components.button_3d import Button3D, BUTTON_COLORS
from src.services.git_service import GitService
from src.services.process_service import ProcessService
from src.components.project_card import ProjectCard
from src.components.project_dialog import ProjectDialog

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ProjectsTab(ctk.CTkFrame):
    """Projects tab with project cards"""
    
    def __init__(self, parent, config_manager):
        """
        Initialize projects tab
        
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
        self.projects = []
        self.filtered_projects = []
        self.search_text = ""
        self.sort_mode = "name"  # name, favorite, language
        
        # Services
        self.git_service = GitService()
        self.process_service = ProcessService()
        
        # UI components
        self.cards_frame = None
        self.cards = []
        self._git_update_queue = queue.Queue()
        self._git_update_polling = False
        
        self.setup_ui()
        self.load_projects()
        
        # Start git status polling
        self._start_git_update_polling()
        self.start_git_polling()
    
    def setup_ui(self):
        """Set up the projects tab UI"""
        # Quick actions bar
        actions_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=0)
        actions_frame.pack(fill='x', padx=0, pady=0)
        
        # Add project button
        add_btn = Button3D(
            actions_frame,
            text="+ Add Project",
            width=130,
            height=34,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=self.add_project
        )
        add_btn.pack(side='left', padx=12, pady=10)
        
        # Refresh git status button
        refresh_btn = Button3D(
            actions_frame,
            text="Refresh Git Status",
            width=160,
            height=34,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.refresh_all_git_status
        )
        refresh_btn.pack(side='left', padx=6, pady=10)
        
        # Git pull all button
        pull_all_btn = Button3D(
            actions_frame,
            text="Git Pull All",
            width=120,
            height=34,
            bg_color=BUTTON_COLORS.INFO,
            command=self.pull_all_projects
        )
        pull_all_btn.pack(side='left', padx=6, pady=10)
        
        # Sort dropdown
        sort_label = ctk.CTkLabel(
            actions_frame,
            text="Sort:",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        sort_label.pack(side='right', padx=(0, 5), pady=8)
        
        self.sort_menu = ctk.CTkOptionMenu(
            actions_frame,
            values=['A-Z', 'Favorites First', 'Language'],
            width=120,
            height=32,
            font=('Segoe UI', 10),
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['bg_tertiary'],
            button_hover_color=COLORS['accent_secondary'],
            command=self.change_sort
        )
        self.sort_menu.set('A-Z')
        self.sort_menu.pack(side='right', padx=(0, 10), pady=8)
        
        # Scrollable frame for project cards
        scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        scrollable_frame.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        # Grid frame for cards
        self.cards_frame = ctk.CTkFrame(scrollable_frame, fg_color='transparent')
        self.cards_frame.pack(fill='both', expand=True)

        # Set up drag and drop on the tab
        self.setup_drag_drop()

        # Debug console panel
        self._build_debug_console()
    
    def load_projects(self):
        """Load projects from config"""
        self.projects = self.config_manager.load_projects()
        self.filtered_projects = self.projects.copy()
        self.apply_sort()
        self.refresh_display()
        
        # Restart monitoring with updated project list
        if hasattr(self.git_service, '_monitoring') and self.git_service._monitoring:
            self.git_service.stop_status_monitoring()
            self.git_service.start_status_monitoring(self.projects, interval=60)
    
    def apply_sort(self):
        """Apply current sort mode"""
        if self.sort_mode == "favorite":
            self.filtered_projects.sort(key=lambda p: (not p.get('favorite', False), p.get('name', '').lower()))
        elif self.sort_mode == "language":
            self.filtered_projects.sort(key=lambda p: (p.get('language', '').lower(), p.get('name', '').lower()))
        else:  # name
            self.filtered_projects.sort(key=lambda p: p.get('name', '').lower())
    
    def change_sort(self, choice):
        """Change sort mode"""
        sort_map = {
            'A-Z': 'name',
            'Favorites First': 'favorite',
            'Language': 'language'
        }
        self.sort_mode = sort_map.get(choice, 'name')
        self.apply_sort()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the project display"""
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        
        if not self.filtered_projects:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.cards_frame,
                text="No projects found.\nClick '+ Add Project' to get started.",
                font=(FONTS['family'], FONTS['size_lg']),
                text_color=COLORS['text_secondary']
            )
            empty_label.pack(expand=True, pady=50)
            return
        
        # Create cards in grid layout (2 columns)
        row = 0
        col = 0
        max_cols = 2
        
        for project in self.filtered_projects:
            card = ProjectCard(
                self.cards_frame,
                project,
                self.config_manager,
                self.git_service,
                self.process_service,
                on_edit=self.edit_project,
                on_remove=self.remove_project,
                output_callback=self.append_console
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            self.cards.append(card)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            self.cards_frame.grid_columnconfigure(i, weight=1)
    
    def filter_projects(self, search_text: str):
        """Filter projects based on search text"""
        self.search_text = search_text.lower()
        if not search_text:
            self.filtered_projects = self.projects.copy()
        else:
            self.filtered_projects = [
                p for p in self.projects
                if search_text in p.get('name', '').lower() or
                   search_text in p.get('description', '').lower() or
                   search_text in p.get('language', '').lower()
            ]
        self.apply_sort()
        self.refresh_display()
    
    def add_project(self, dropped_file=None):
        """Open add project dialog
        
        Args:
            dropped_file: Optional path to dropped file/folder for drag-drop mode
        """
        dialog = ProjectDialog(
            self.master,
            self.config_manager,
            on_save=self.save_project,
            dropped_file=dropped_file
        )
        dialog.wait_window()
    
    def edit_project(self, project):
        """Open edit project dialog"""
        dialog = ProjectDialog(self.master, self.config_manager, project=project, on_save=self.save_project)
        dialog.wait_window()
    
    def save_project(self, project):
        """Save project to config"""
        projects = self.config_manager.load_projects()
        
        # Check if editing existing project
        existing_index = None
        for i, p in enumerate(projects):
            if p.get('id') == project.get('id'):
                existing_index = i
                break
        
        if existing_index is not None:
            projects[existing_index] = project
        else:
            projects.append(project)
        
        self.config_manager.save_projects(projects)
        self.load_projects()
    
    def remove_project(self, project):
        """Remove project from config"""
        projects = self.config_manager.load_projects()
        projects = [p for p in projects if p.get('id') != project.get('id')]
        self.config_manager.save_projects(projects)
        self.load_projects()
    
    def refresh_all_git_status(self):
        """Refresh git status for all project cards"""
        for card in self.cards:
            card.update_git_status()
    
    def pull_all_projects(self):
        """Pull all git repositories"""
        def pull_all():
            for project in self.projects:
                repo_path = project.get('path', '')
                if repo_path and os.path.exists(os.path.join(repo_path, '.git')):
                    success, message = self.git_service.pull(repo_path)
                    logger.info("%s: %s", project.get('name'), message)
            # Refresh status after pulling
            self.after(1000, self.refresh_all_git_status)
        
        threading.Thread(target=pull_all, daemon=True).start()
    
    def start_git_polling(self):
        """Start git status monitoring using GitService's built-in monitoring"""
        # Use closure over queue only — no self access from background thread
        update_queue = self._git_update_queue
        def on_update(project_id: str, status: Dict):
            update_queue.put((project_id, status))
        self.git_service.register_status_callback(on_update)
        self.git_service.start_status_monitoring(self.projects, interval=60)
    
    def on_git_status_update(self, project_id: str, status: Dict):
        """Legacy callback — prefer on_update closure in start_git_polling."""
        self._git_update_queue.put((project_id, status))

    def _start_git_update_polling(self):
        if self._git_update_polling:
            return
        self._git_update_polling = True

        def poll_queue():
            if not self.winfo_exists():
                self._git_update_polling = False
                return

            try:
                while True:
                    try:
                        project_id, _status = self._git_update_queue.get_nowait()
                    except queue.Empty:
                        break

                    for card in self.cards:
                        card_project_id = card.project.get('id') or card.project.get('name', 'unknown')
                        if card_project_id == project_id:
                            card.update_git_status()
                            break
            finally:
                if self._git_update_polling:
                    self.after(100, poll_queue)

        self.after(100, poll_queue)
    
    def setup_drag_drop(self):
        """Set up drag and drop support for the Projects tab"""
        # Try to import tkinterdnd2
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # Register drop target on the main frame
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self.on_file_drop)
            except Exception as e:
                logger.debug(f"Suppressed exception in drag-drop setup: {e}")
        except ImportError:
            # tkinterdnd2 not available, drag-drop won't work
            pass

    def _build_debug_console(self):
        self.debug_panel_expanded = True

        self.debug_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=8, height=200)
        self.debug_frame.pack(fill='x', padx=10, pady=(10, 10))
        self.debug_frame.pack_propagate(False)

        header = ctk.CTkFrame(self.debug_frame, fg_color='transparent')
        header.pack(fill='x', padx=10, pady=(8, 4))

        title = ctk.CTkLabel(
            header,
            text="Debug Console",
            font=('Segoe UI', 12, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(side='left')

        self.auto_scroll = ctk.BooleanVar(value=True)
        auto_scroll_switch = ctk.CTkSwitch(
            header,
            text="Auto-scroll",
            variable=self.auto_scroll,
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        auto_scroll_switch.pack(side='right', padx=(8, 0))

        copy_btn = Button3D(
            header,
            text="Copy",
            width=70,
            height=26,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.copy_console
        )
        copy_btn.pack(side='right', padx=(8, 0))

        clear_btn = Button3D(
            header,
            text="Clear",
            width=70,
            height=26,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.clear_console
        )
        clear_btn.pack(side='right', padx=(8, 0))

        self.toggle_console_btn = Button3D(
            header,
            text="Collapse",
            width=80,
            height=26,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.toggle_console
        )
        self.toggle_console_btn.pack(side='right')

        self.console = ctk.CTkTextbox(
            self.debug_frame,
            height=140,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary']
        )
        self.console.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self._configure_console_tags()

    def _configure_console_tags(self):
        textbox = self.console._textbox
        textbox.tag_configure("info", foreground=COLORS['accent_secondary'])
        textbox.tag_configure("error", foreground=COLORS['error'])
        textbox.tag_configure("stdout", foreground=COLORS['text_primary'])
        textbox.tag_configure("stderr", foreground=COLORS['error'])

    def toggle_console(self):
        self.debug_panel_expanded = not self.debug_panel_expanded
        if self.debug_panel_expanded:
            self.console.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            self.toggle_console_btn.configure(text="Collapse")
        else:
            self.console.pack_forget()
            self.toggle_console_btn.configure(text="Expand")

    def append_console(self, message: str, level: str = "stdout"):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        self.console.insert("end", line, level)
        if self.auto_scroll.get():
            self.console.see("end")

    def clear_console(self):
        self.console.delete("1.0", "end")

    def copy_console(self):
        try:
            text = self.console.get("1.0", "end").strip()
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            logger.debug("Suppressed exception in console copy")
    
    def on_file_drop(self, event):
        """Handle file drop on Projects tab"""
        try:
            from tkinterdnd2 import TkinterDnD
            
            # Get dropped files
            files = self.tk.splitlist(event.data)
            if files:
                # Use the first file
                dropped_file = files[0]
                
                # Validate file type
                if os.path.isfile(dropped_file):
                    ext = os.path.splitext(dropped_file)[1].lower()
                    valid_extensions = ['.exe', '.py', '.ps1', '.bat', '.cmd']
                    if ext not in valid_extensions:
                        return
                elif not os.path.isdir(dropped_file):
                    return
                
                # Open dialog in drag-drop mode
                self.add_project(dropped_file=dropped_file)
        except Exception as e:
            # Silently handle errors
            logger.debug(f"Suppressed exception in file drop handling: {e}")
