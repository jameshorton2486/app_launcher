"""
Downloads Tab
Manages and organizes downloaded files
"""

import customtkinter as ctk
import sys
import os
import threading
import tkinter.messagebox as msgbox
from tkinter import filedialog

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS
from src.components.button_3d import Button3D, BUTTON_COLORS
from src.services.file_service import FileService
from src.components.file_item import FileItem

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class DownloadsTab(ctk.CTkFrame):
    """Downloads tab for managing downloaded files"""
    
    def __init__(self, parent, config_manager, status_bar=None):
        """
        Initialize downloads tab
        
        Args:
            parent: Parent widget
            config_manager: ConfigManager instance
            status_bar: Optional StatusBar instance for status updates
        """
        super().__init__(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        
        self.config_manager = config_manager
        self.status_bar = status_bar  # Store status bar reference
        self.file_service = FileService()
        self.files = []
        self.filtered_files = []
        self.selected_files = []
        self.current_category = "All"
        self.search_text = ""
        self._initialized = False  # Lazy loading flag
        
        # Get downloads folder from config
        self.downloads_folder = self.config_manager.get_setting('paths.downloads_folder', '')
        
        self.setup_ui()
        # Don't refresh files immediately - wait for tab activation
    
    def setup_ui(self):
        """Set up the downloads tab UI"""
        # Header row
        header_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=0)
        header_frame.pack(fill='x', padx=0, pady=0)
        
        # Downloads folder path
        folder_label = ctk.CTkLabel(
            header_frame,
            text="Downloads:",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        folder_label.pack(side='left', padx=10, pady=8)
        
        self.folder_path_label = ctk.CTkLabel(
            header_frame,
            text=self.downloads_folder or "Not configured",
            font=('Segoe UI', 10),
            text_color=COLORS['text_primary'],
            anchor='w'
        )
        self.folder_path_label.pack(side='left', padx=(0, 10), pady=8, fill='x', expand=True)
        
        # Open folder button
        open_btn = Button3D(
            header_frame,
            text="Open Folder",
            width=110,
            height=34,
            bg_color=BUTTON_COLORS.SECONDARY,
            command=self.open_folder
        )
        open_btn.pack(side='right', padx=(8, 12), pady=8)
        
        # Refresh button
        refresh_btn = Button3D(
            header_frame,
            text="Refresh",
            width=100,
            height=34,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=self.refresh_files
        )
        refresh_btn.pack(side='right', padx=(0, 8), pady=8)
        
        # Filter row
        filter_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=0)
        filter_frame.pack(fill='x', padx=0, pady=(0, 0))
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filter:",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        filter_label.pack(side='left', padx=10, pady=8)
        
        # Filter buttons
        self.filter_buttons = {}
        categories = ['All', 'Code', 'Docs', 'Images', 'Archives', 'Unknown']
        
        for category in categories:
            btn = ctk.CTkButton(
                filter_frame,
                text=category,
                width=80,
                height=28,
                font=('Segoe UI', 10),
                fg_color=COLORS['bg_tertiary'] if category != 'All' else COLORS['accent_primary'],
                hover_color=COLORS['accent_secondary'],
                command=lambda c=category: self.filter_by_category(c)
            )
            btn.pack(side='left', padx=5, pady=8)
            self.filter_buttons[category] = btn
        
        # Select All / Deselect All buttons
        select_all_btn = ctk.CTkButton(
            filter_frame,
            text="Select All",
            width=90,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.select_all
        )
        select_all_btn.pack(side='right', padx=(5, 10), pady=8)
        
        deselect_all_btn = ctk.CTkButton(
            filter_frame,
            text="Deselect All",
            width=90,
            height=28,
            font=('Segoe UI', 10),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent_secondary'],
            command=self.deselect_all
        )
        deselect_all_btn.pack(side='right', padx=(5, 0), pady=8)
        
        # File list (scrollable)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        self.scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Footer row
        footer_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=0)
        footer_frame.pack(fill='x', side='bottom', padx=0, pady=0)
        
        self.selected_label = ctk.CTkLabel(
            footer_frame,
            text="Selected: 0 files",
            font=('Segoe UI', 10),
            text_color=COLORS['text_secondary']
        )
        self.selected_label.pack(side='left', padx=10, pady=8)
        
        # Move Selected button
        move_selected_btn = Button3D(
            footer_frame,
            text="Move Selected",
            width=120,
            height=32,
            bg_color=BUTTON_COLORS.PRIMARY,
            command=self.move_selected
        )
        move_selected_btn.pack(side='right', padx=(5, 10), pady=8)
        
        # Delete Selected button
        delete_selected_btn = Button3D(
            footer_frame,
            text="Delete Selected",
            width=120,
            height=32,
            bg_color=BUTTON_COLORS.DANGER,
            command=self.delete_selected
        )
        delete_selected_btn.pack(side='right', padx=(5, 0), pady=8)
    
    def open_folder(self):
        """Open downloads folder in File Explorer"""
        if not self.downloads_folder or not os.path.isdir(self.downloads_folder):
            msgbox.showerror("Error", "Downloads folder is not configured or does not exist")
            return
        
        try:
            os.startfile(self.downloads_folder)
        except Exception as e:
            msgbox.showerror("Error", f"Could not open folder: {e}")
    
    def refresh_files(self):
        """Refresh the file list with error handling"""
        try:
            if not self.downloads_folder:
                # Try to get from config again
                self.downloads_folder = self.config_manager.get_setting('paths.downloads_folder', '')
                if not self.downloads_folder:
                    self.folder_path_label.configure(text="Not configured")
                    logger.warning("Downloads folder not configured")
                    return
            
            # Validate folder exists
            if not os.path.exists(self.downloads_folder):
                self.folder_path_label.configure(text="Folder not found")
                logger.error(f"Downloads folder does not exist: {self.downloads_folder}")
                msgbox.showerror("Error", f"Downloads folder not found:\n{self.downloads_folder}\n\nPlease configure in Settings.")
                return
            
            if not os.path.isdir(self.downloads_folder):
                self.folder_path_label.configure(text="Invalid path")
                logger.error(f"Downloads folder is not a directory: {self.downloads_folder}")
                msgbox.showerror("Error", f"Downloads folder is not a directory:\n{self.downloads_folder}")
                return
            
            self.folder_path_label.configure(text=self.downloads_folder)
            
            # Show loading state
            if self.status_bar:
                self.status_bar.set_status("Scanning downloads...")
            
            # Load projects for pattern matching
            try:
                projects = self.config_manager.load_projects()
            except Exception as e:
                logger.error(f"Error loading projects: {e}", exc_info=True)
                projects = []
            
            # Scan files in background thread
            def scan_files():
                try:
                    files = self.file_service.scan_downloads(self.downloads_folder, projects)
                    # Update UI on main thread
                    self.after(0, lambda: self._on_scan_complete(files))
                except Exception as e:
                    logger.error(f"Error scanning downloads: {e}", exc_info=True)
                    self.after(0, lambda: self._on_scan_error(str(e)))
            
            threading.Thread(target=scan_files, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error refreshing files: {e}", exc_info=True)
            if self.status_bar:
                self.status_bar.set_status("Error refreshing files")
            msgbox.showerror("Error", f"Failed to refresh files: {str(e)}")
    
    def _on_scan_complete(self, files):
        """Handle file scan completion"""
        try:
            self.files = files
            # Apply current filter
            self.apply_filters()
            self.refresh_display()
            if self.status_bar:
                self.status_bar.set_status(f"Found {len(files)} file(s)")
        except Exception as e:
            logger.error(f"Error displaying files: {e}", exc_info=True)
            if self.status_bar:
                self.status_bar.set_status("Error displaying files")
    
    def _on_scan_error(self, error_msg):
        """Handle file scan error"""
        if self.status_bar:
            self.status_bar.set_status("Scan failed")
        msgbox.showerror("Error", f"Failed to scan downloads folder:\n{error_msg}")
    
    def filter_by_category(self, category: str):
        """Filter files by category"""
        self.current_category = category
        
        # Update button colors
        for cat, btn in self.filter_buttons.items():
            if cat == category:
                btn.configure(fg_color=COLORS['accent_primary'])
            else:
                btn.configure(fg_color=COLORS['bg_tertiary'])
        
        self.apply_filters()
        self.refresh_display()
    
    def apply_filters(self):
        """Apply current filters (category and search)"""
        self.filtered_files = self.files.copy()
        
        # Filter by category
        if self.current_category != "All":
            self.filtered_files = [
                f for f in self.filtered_files
                if f.get('category') == self.current_category
            ]
        
        # Filter by search text
        if self.search_text:
            search_lower = self.search_text.lower()
            self.filtered_files = [
                f for f in self.filtered_files
                if search_lower in f.get('name', '').lower()
            ]
    
    def filter_by_search(self, search_text: str):
        """Filter files by search text"""
        self.search_text = search_text
        self.apply_filters()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the file list display"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.filtered_files:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No files found.\nConfigure downloads folder in settings.",
                font=('Segoe UI', 14),
                text_color=COLORS['text_secondary']
            )
            empty_label.pack(expand=True, pady=50)
            return
        
        # Create file items
        for file_info in self.filtered_files:
            file_item = FileItem(
                self.scrollable_frame,
                file_info,
                self.file_service,
                self.config_manager,
                on_select=self.on_file_select,
                on_move=self.on_file_move,
                on_delete=self.on_file_delete
            )
            file_item.pack(fill='x', padx=5, pady=3)
    
    def on_file_select(self, file_info: dict, selected: bool):
        """Handle file selection"""
        file_path = file_info.get('path')
        
        if selected:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
        else:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
        
        self.update_selected_count()
    
    def select_all(self):
        """Select all visible files"""
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, FileItem):
                widget.set_selected(True)
                file_path = widget.file_info.get('path')
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
        
        self.update_selected_count()
    
    def deselect_all(self):
        """Deselect all files"""
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, FileItem):
                widget.set_selected(False)
        
        self.selected_files.clear()
        self.update_selected_count()
    
    def update_selected_count(self):
        """Update selected files count label"""
        count = len(self.selected_files)
        self.selected_label.configure(text=f"Selected: {count} file{'s' if count != 1 else ''}")
    
    def on_file_move(self, file_info: dict, destination: str):
        """Handle single file move"""
        source = file_info.get('path')
        
        if not source or not os.path.exists(source):
            msgbox.showerror("Error", "File does not exist")
            return
        
        success = self.file_service.move_file(source, destination)
        
        if success:
            msgbox.showinfo("Success", f"File moved to {destination}")
            self.refresh_files()
        else:
            msgbox.showerror("Error", "Failed to move file")
    
    def on_file_delete(self, file_info: dict):
        """Handle single file delete"""
        file_path = file_info.get('path')
        filename = file_info.get('name', 'file')
        
        # Confirm deletion
        if not msgbox.askyesno("Confirm Delete", f"Delete '{filename}'?"):
            return
        
        success_count, fail_count = self.file_service.delete_files([file_path])
        
        if success_count > 0:
            msgbox.showinfo("Success", f"File deleted")
            self.refresh_files()
        else:
            msgbox.showerror("Error", "Failed to delete file")
    
    def move_selected(self):
        """Move all selected files"""
        if not self.selected_files:
            msgbox.showwarning("Warning", "No files selected")
            return
        
        # Ask for destination
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if not destination:
            return
        
        # Move files
        success_count = 0
        fail_count = 0
        
        for file_path in self.selected_files:
            if os.path.exists(file_path):
                success = self.file_service.move_file(file_path, destination)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
        
        # Show results
        if success_count > 0:
            msgbox.showinfo(
                "Move Complete",
                f"Moved {success_count} file(s)\n"
                f"{fail_count} failed" if fail_count > 0 else ""
            )
            self.selected_files.clear()
            self.refresh_files()
        else:
            msgbox.showerror("Error", "Failed to move files")
    
    def delete_selected(self):
        """Delete all selected files"""
        if not self.selected_files:
            msgbox.showwarning("Warning", "No files selected")
            return
        
        # Confirm deletion
        count = len(self.selected_files)
        if not msgbox.askyesno(
            "Confirm Delete",
            f"Delete {count} file(s)?\n\nThis action cannot be undone."
        ):
            return
        
        # Delete files
        success_count, fail_count = self.file_service.delete_files(self.selected_files)
        
        # Show results
        msg = f"Deleted {success_count} file(s)"
        if fail_count > 0:
            msg += f"\n{fail_count} failed"
        
        if success_count > 0:
            msgbox.showinfo("Delete Complete", msg)
            self.selected_files.clear()
            self.refresh_files()
        else:
            msgbox.showerror("Error", "Failed to delete files")
