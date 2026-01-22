"""
Project Card Component
Displays individual project information and actions
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


class ProjectCard(ctk.CTkFrame):
    """Card widget for displaying project information"""
    
    def __init__(self, parent, project: dict, config_manager, git_service, process_service, on_edit=None, on_remove=None):
        """
        Initialize project card
        
        Args:
            parent: Parent widget
            project: Project dictionary
            config_manager: ConfigManager instance
            git_service: GitService instance
            process_service: ProcessService instance
            on_edit: Callback for edit action
            on_remove: Callback for remove action
        """
        super().__init__(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        
        self.project = project
        self.config_manager = config_manager
        self.git_service = git_service
        self.process_service = process_service
        self.on_edit = on_edit
        self.on_remove = on_remove
        
        self.git_status = None
        self.last_commit = None
        
        self.setup_ui()
        self.update_git_status()
    
    def setup_ui(self):
        """Set up the project card UI"""
        # Top row: Left side (Icon + Name + Description) | Right side (Favorite + Git status)
        header_frame = ctk.CTkFrame(self, fg_color='transparent')
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Left side: Icon + Name + Description
        left_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Icon and name row
        icon_name_row = ctk.CTkFrame(left_frame, fg_color='transparent')
        icon_name_row.pack(fill='x')
        
        icon_label = ctk.CTkLabel(
            icon_name_row,
            text=self.project.get('icon', '📁'),
            font=('Segoe UI', 20),
            width=30
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        name_label = ctk.CTkLabel(
            icon_name_row,
            text=self.project.get('name', 'Unnamed Project'),
            font=('Segoe UI', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        name_label.pack(side='left', fill='x', expand=True)
        
        # Description (muted text)
        description = self.project.get('description', '')
        if description:
            desc_label = ctk.CTkLabel(
                left_frame,
                text=description,
                font=('Segoe UI', 10),
                text_color=COLORS['text_secondary'],
                anchor='w',
                wraplength=350
            )
            desc_label.pack(fill='x', padx=(40, 0), pady=(2, 0))
        
        # Right side: Favorite star + Git status indicator
        right_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        right_frame.pack(side='right')
        
        # Favorite button (star toggle)
        favorite_icon = '⭐' if self.project.get('favorite', False) else '☆'
        self.favorite_btn = ctk.CTkButton(
            right_frame,
            text=favorite_icon,
            width=30,
            height=30,
            font=('Segoe UI', 12),
            fg_color='transparent',
            hover_color=COLORS['bg_tertiary'],
            command=self.toggle_favorite
        )
        self.favorite_btn.pack(side='left', padx=2)
        
        # Git status indicator (🟢 clean, 🟡 uncommitted, 🔴 needs pull)
        self.git_indicator = ctk.CTkLabel(
            right_frame,
            text='',
            width=30,
            height=30,
            font=('Segoe UI', 16)
        )
        self.git_indicator.pack(side='left', padx=2)
        
        # Info frame (language, last commit)
        info_frame = ctk.CTkFrame(self, fg_color='transparent')
        info_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        language = self.project.get('language', 'unknown')
        language_label = ctk.CTkLabel(
            info_frame,
            text=f"Language: {language}",
            font=('Segoe UI', 9),
            text_color=COLORS['text_muted']
        )
        language_label.pack(side='left', padx=(0, 15))
        
        self.commit_label = ctk.CTkLabel(
            info_frame,
            text="Last commit: checking...",
            font=('Segoe UI', 9),
            text_color=COLORS['text_muted']
        )
        self.commit_label.pack(side='left')
        
        # Action buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color='transparent')
        buttons_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # Launch button
        launch_btn = ctk.CTkButton(
            buttons_frame,
            text="▶ Launch",
            width=80,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['accent_success'],
            hover_color='#00a085',
            command=self.launch_project
        )
        launch_btn.pack(side='left', padx=2)
        
        # Folder button
        folder_btn = ctk.CTkButton(
            buttons_frame,
            text="📁",
            width=35,
            height=28,
            font=('Segoe UI', 12),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.open_folder
        )
        folder_btn.pack(side='left', padx=2)
        
        # Terminal button
        terminal_btn = ctk.CTkButton(
            buttons_frame,
            text="💻",
            width=35,
            height=28,
            font=('Segoe UI', 12),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.open_terminal
        )
        terminal_btn.pack(side='left', padx=2)
        
        # IDE dropdown
        self.ide_menu = ctk.CTkOptionMenu(
            buttons_frame,
            values=['🔧 IDE', 'Cursor', 'VS Code', 'PyCharm'],
            width=100,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['bg_tertiary'],
            button_hover_color=COLORS['accent_secondary'],
            command=self.open_ide
        )
        self.ide_menu.set('🔧 IDE')
        self.ide_menu.pack(side='left', padx=2)
        
        # Claude button
        if self.project.get('claude_project_url'):
            claude_btn = ctk.CTkButton(
                buttons_frame,
                text="🤖",
                width=35,
                height=28,
                font=('Segoe UI', 12),
                fg_color=COLORS['bg_tertiary'],
                hover_color=COLORS['accent_secondary'],
                command=self.open_claude
            )
            claude_btn.pack(side='left', padx=2)
        
        # GitHub button
        if self.project.get('repo_url'):
            github_btn = ctk.CTkButton(
                buttons_frame,
                text="🐙",
                width=35,
                height=28,
                font=('Segoe UI', 12),
                fg_color=COLORS['bg_tertiary'],
                hover_color=COLORS['accent_secondary'],
                command=self.open_github
            )
            github_btn.pack(side='left', padx=2)
        
        # Bind right-click for context menu
        self.bind('<Button-3>', self.show_context_menu)
        for widget in self.winfo_children():
            widget.bind('<Button-3>', self.show_context_menu)
    
    def update_git_status(self):
        """Update git status indicator"""
        repo_path = self.project.get('path', '')
        if not repo_path:
            return
        
        self.git_status = self.git_service.get_status(repo_path)
        self.last_commit = self.git_service.get_last_commit(repo_path)
        
        # Update git indicator
        status_text = self.git_status.get('status_text', 'unknown')
        if status_text == 'clean':
            self.git_indicator.configure(text='🟢', text_color=COLORS['accent_success'])
        elif status_text == 'uncommitted':
            self.git_indicator.configure(text='🟡', text_color=COLORS['accent_warning'])
        elif status_text in ['behind', 'diverged']:
            self.git_indicator.configure(text='🔴', text_color=COLORS['accent_danger'])
        else:
            self.git_indicator.configure(text='⚪', text_color=COLORS['text_muted'])
        
        # Update commit label
        if self.last_commit and self.last_commit.get('time_ago'):
            self.commit_label.configure(text=f"Last commit: {self.last_commit['time_ago']}")
        else:
            self.commit_label.configure(text="Last commit: unknown")
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        self.project['favorite'] = not self.project.get('favorite', False)
        favorite_icon = '⭐' if self.project['favorite'] else '☆'
        self.favorite_btn.configure(text=favorite_icon)
        
        # Save to config
        projects = self.config_manager.load_projects()
        for i, p in enumerate(projects):
            if p.get('id') == self.project.get('id'):
                projects[i] = self.project
                break
        self.config_manager.save_projects(projects)
    
    def launch_project(self):
        """Launch the project using appropriate method based on launch_type"""
        project_path = self.project.get('path', '')
        launch_script = self.project.get('launch_script', '')
        launch_type = self.project.get('launch_type', 'python')
        
        try:
            if launch_type == 'python':
                success, message = self.process_service.launch_python_script(project_path, launch_script)
            elif launch_type == 'npm':
                success, message = self.process_service.launch_npm_command(project_path, launch_script)
            elif launch_type == 'powershell':
                success, message = self.process_service.launch_powershell_script(project_path, launch_script)
            elif launch_type == 'exe':
                success, message = self.process_service.launch_exe(launch_script if os.path.isabs(launch_script) else os.path.join(project_path, launch_script))
            else:
                # Fallback to generic launch_project method
                success, message = self.process_service.launch_project(self.project)
            
            if not success:
                # Could show error in status bar or messagebox
                print(f"Error launching project: {message}")
        except Exception as e:
            print(f"Error launching project: {e}")
    
    def open_folder(self):
        """Open project folder in File Explorer"""
        self.process_service.open_in_explorer(self.project.get('path', ''))
    
    def open_terminal(self):
        """Open PowerShell in project directory"""
        self.process_service.open_in_terminal(self.project.get('path', ''))
    
    def open_ide(self, choice):
        """Open project in IDE"""
        if choice == '🔧 IDE':
            return
        
        ide_map = {
            'Cursor': 'cursor',
            'VS Code': 'vscode',
            'PyCharm': 'pycharm'
        }
        
        ide_name = ide_map.get(choice)
        if ide_name:
            self.process_service.open_in_ide(
                self.project.get('path', ''),
                ide_name,
                self.config_manager
            )
        
        # Reset dropdown
        self.ide_menu.set('🔧 IDE')
    
    def open_claude(self):
        """Open Claude project URL"""
        url = self.project.get('claude_project_url', '')
        if url:
            self.process_service.open_url(url)
    
    def open_github(self):
        """Open GitHub repository URL"""
        url = self.project.get('repo_url', '')
        if url:
            self.process_service.open_url(url)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        menu = tk.Menu(self, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                      activebackground=COLORS['accent_primary'], activeforeground=COLORS['text_primary'])
        
        # IDE options
        menu.add_command(
            label="Open in Cursor",
            command=lambda: self.process_service.open_in_ide(self.project.get('path', ''), 'cursor', self.config_manager)
        )
        menu.add_command(
            label="Open in VS Code",
            command=lambda: self.process_service.open_in_ide(self.project.get('path', ''), 'vscode', self.config_manager)
        )
        menu.add_command(
            label="Open in PyCharm",
            command=lambda: self.process_service.open_in_ide(self.project.get('path', ''), 'pycharm', self.config_manager)
        )
        menu.add_command(label="Open in File Explorer", command=self.open_folder)
        menu.add_command(label="Open PowerShell Here", command=self.open_terminal)
        menu.add_separator()
        
        # Git options
        menu.add_command(label="Git Status", command=self.show_git_status)
        menu.add_command(label="Git Pull", command=self.git_pull)
        menu.add_command(label="Git Push", command=self.git_push)
        if self.project.get('repo_url'):
            menu.add_command(label="Open on GitHub", command=self.open_github)
        menu.add_separator()
        
        # Project management
        if self.on_edit:
            menu.add_command(label="Edit Project", command=lambda: self.on_edit(self.project))
        if self.on_remove:
            menu.add_command(label="Remove Project", command=lambda: self.on_remove(self.project))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def show_git_status(self):
        """Show detailed git status in a popup dialog"""
        # Refresh status first
        self.update_git_status()
        
        # Create popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Git Status")
        popup.geometry("400x300")
        popup.transient(self.master)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(popup, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Git Status: {self.project.get('name', 'Project')}",
            font=('Segoe UI', 16, 'bold'),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(10, 20))
        
        # Status details
        if self.git_status:
            status_text = f"Branch: {self.git_status.get('branch', 'unknown')}\n\n"
            status_text += f"Status: {self.git_status.get('status_text', 'unknown')}\n"
            status_text += f"Uncommitted files: {self.git_status.get('uncommitted', 0)}\n"
            status_text += f"Commits ahead: {self.git_status.get('ahead', 0)}\n"
            status_text += f"Commits behind: {self.git_status.get('behind', 0)}"
        else:
            status_text = "Unable to get git status"
        
        # Status text label
        status_label = ctk.CTkLabel(
            main_frame,
            text=status_text,
            font=('Segoe UI', 11),
            text_color=COLORS['text_secondary'],
            justify='left',
            anchor='w'
        )
        status_label.pack(pady=10, padx=20, fill='x')
        
        # Last commit info
        if self.last_commit:
            commit_text = f"\nLast Commit:\n"
            commit_text += f"  {self.last_commit.get('message', 'N/A')}\n"
            commit_text += f"  {self.last_commit.get('author', 'N/A')} - {self.last_commit.get('time_ago', 'N/A')}"
            
            commit_label = ctk.CTkLabel(
                main_frame,
                text=commit_text,
                font=('Segoe UI', 10),
                text_color=COLORS['text_muted'],
                justify='left',
                anchor='w'
            )
            commit_label.pack(pady=10, padx=20, fill='x')
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            width=100,
            height=32,
            font=('Segoe UI', 11),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            command=popup.destroy
        )
        close_btn.pack(pady=20)
    
    def git_pull(self):
        """Pull latest changes"""
        repo_path = self.project.get('path', '')
        if not repo_path:
            return
        
        success, message = self.git_service.pull(repo_path)
        if success:
            self.update_git_status()
            # Show success message
            self._show_message("Git Pull", message, "success")
        else:
            # Show error message
            self._show_message("Git Pull Error", message, "error")
    
    def git_push(self):
        """Push commits"""
        repo_path = self.project.get('path', '')
        if not repo_path:
            return
        
        success, message = self.git_service.push(repo_path)
        if success:
            self.update_git_status()
            # Show success message
            self._show_message("Git Push", message, "success")
        else:
            # Show error message
            self._show_message("Git Push Error", message, "error")
    
    def _show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show a message dialog"""
        import tkinter.messagebox as msgbox
        if msg_type == "success":
            msgbox.showinfo(title, message)
        elif msg_type == "error":
            msgbox.showerror(title, message)
        else:
            msgbox.showinfo(title, message)
