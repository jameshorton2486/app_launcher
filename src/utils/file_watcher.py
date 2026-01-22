"""
File Watcher Service
Watches Downloads folder for new files matching project patterns
"""

import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Optional
import fnmatch


class DownloadsFileHandler(FileSystemEventHandler):
    """Handler for file system events in Downloads folder"""
    
    def __init__(self, on_file_added: Callable, projects: list):
        """
        Initialize file handler
        
        Args:
            on_file_added: Callback when file is added (receives file_path, project)
            projects: List of project dictionaries
        """
        self.on_file_added = on_file_added
        self.projects = projects
    
    def on_created(self, event):
        """Handle file creation"""
        if not event.is_directory:
            self.check_file_match(event.src_path)
    
    def check_file_match(self, file_path: str):
        """Check if file matches any project pattern"""
        filename = os.path.basename(file_path).lower()
        
        for project in self.projects:
            patterns = project.get('file_patterns', [])
            for pattern in patterns:
                # Simple pattern matching
                if pattern.lower() in filename:
                    # Check if file extension matches project type
                    if self.is_relevant_file(file_path, project):
                        self.on_file_added(file_path, project)
                        return
    
    def is_relevant_file(self, file_path: str, project: dict) -> bool:
        """Check if file is relevant to project type"""
        ext = os.path.splitext(file_path)[1].lower()
        language = project.get('language', '').lower()
        
        # Map languages to file extensions
        lang_extensions = {
            'python': ['.py', '.pyw'],
            'typescript': ['.ts', '.tsx'],
            'javascript': ['.js', '.jsx'],
            'powershell': ['.ps1', '.psm1'],
        }
        
        if language in lang_extensions:
            return ext in lang_extensions[language]
        
        # Also check code files pattern
        code_extensions = ['.py', '.ts', '.tsx', '.js', '.jsx', '.ps1', '.bat', '.sh']
        return ext in code_extensions


class FileWatcher:
    """Watches Downloads folder for project-related files"""
    
    def __init__(self, downloads_path: str, projects: list, on_file_added: Optional[Callable] = None):
        """
        Initialize file watcher
        
        Args:
            downloads_path: Path to Downloads folder
            projects: List of project dictionaries
            on_file_added: Callback when file matches (receives file_path, project)
        """
        self.downloads_path = downloads_path
        self.projects = projects
        self.on_file_added = on_file_added or self.default_notification
        self.observer = None
    
    def default_notification(self, file_path: str, project: dict):
        """Default notification handler"""
        print(f"New file detected: {os.path.basename(file_path)}")
        print(f"Matches project: {project.get('name', 'Unknown')}")
        # Could show a notification here
    
    def start(self):
        """Start watching Downloads folder"""
        if not os.path.exists(self.downloads_path):
            print(f"Downloads folder does not exist: {self.downloads_path}")
            return
        
        event_handler = DownloadsFileHandler(self.on_file_added, self.projects)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.downloads_path, recursive=False)
        self.observer.start()
    
    def stop(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def update_projects(self, projects: list):
        """Update the projects list"""
        self.projects = projects
