"""
File Service
Handles file operations for downloads tab
"""

import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class FileService:
    """Service for file operations"""
    
    # File category mappings
    CATEGORIES = {
        'Code': ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sh', '.bat', '.ps1'],
        'Docs': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.rtf'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'Unknown': []
    }
    
    def __init__(self):
        """Initialize FileService"""
        pass
    
    def scan_downloads(self, path: str, projects: List[Dict] = None) -> List[Dict]:
        """
        Scan downloads folder for files
        
        Args:
            path: Downloads folder path
            projects: List of project dictionaries for pattern matching
            
        Returns:
            List of file dictionaries with:
            {
                'name': str,
                'path': str,
                'size': int,
                'modified': datetime,
                'category': str,
                'suggested_project': str or None
            }
        """
        files = []
        
        if not path or not os.path.isdir(path):
            logger.warning(f"Downloads path is not a valid directory: {path}")
            return files
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                # Skip directories
                if os.path.isdir(item_path):
                    continue
                
                # Get file info
                try:
                    stat = os.stat(item_path)
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                except Exception as e:
                    logger.error(f"Error getting file stats for {item_path}: {e}")
                    continue
                
                # Determine category
                ext = os.path.splitext(item)[1].lower()
                category = self._get_category(ext)
                
                # Match to project
                suggested_project = None
                if projects:
                    suggested_project = self.match_file_to_project(item, projects)
                
                files.append({
                    'name': item,
                    'path': item_path,
                    'size': file_size,
                    'modified': modified_time,
                    'category': category,
                    'suggested_project': suggested_project
                })
        
        except Exception as e:
            logger.error(f"Error scanning downloads folder {path}: {e}")
        
        # Sort by modified date (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return files
    
    def _get_category(self, extension: str) -> str:
        """
        Get file category from extension
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            Category name
        """
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        
        return 'Unknown'
    
    def match_file_to_project(self, filename: str, projects: List[Dict]) -> Optional[str]:
        """
        Match file to project based on patterns or name
        
        Args:
            filename: File name to match
            projects: List of project dictionaries
            
        Returns:
            Project ID or None
        """
        filename_lower = filename.lower()
        
        for project in projects:
            project_id = project.get('id') or project.get('name', '')
            project_name = project.get('name', '').lower()
            
            # Check file patterns
            file_patterns = project.get('file_patterns', [])
            for pattern in file_patterns:
                if pattern.lower() in filename_lower:
                    return project_id
            
            # Check if project name is in filename
            if project_name and project_name in filename_lower:
                return project_id
        
        return None
    
    def move_file(self, source: str, dest_folder: str, subfolder: Optional[str] = None) -> bool:
        """
        Move file to destination folder
        
        Args:
            source: Source file path
            dest_folder: Destination folder path
            subfolder: Optional subfolder within destination
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(source):
            logger.error(f"Source file does not exist: {source}")
            return False
        
        if not os.path.isdir(dest_folder):
            logger.error(f"Destination folder does not exist: {dest_folder}")
            return False
        
        try:
            # Construct destination path
            if subfolder:
                dest_path = os.path.join(dest_folder, subfolder)
            else:
                dest_path = dest_folder
            
            # Create subfolder if needed
            if subfolder and not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)
            
            # Handle duplicate files
            filename = os.path.basename(source)
            dest_file = os.path.join(dest_path, filename)
            
            if os.path.exists(dest_file):
                # Add number suffix
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_file):
                    new_filename = f"{base} ({counter}){ext}"
                    dest_file = os.path.join(dest_path, new_filename)
                    counter += 1
            
            # Move file
            shutil.move(source, dest_file)
            logger.info(f"Moved file: {source} -> {dest_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error moving file {source} to {dest_folder}: {e}")
            return False
    
    def delete_files(self, paths: List[str]) -> Tuple[int, int]:
        """
        Delete multiple files
        
        Args:
            paths: List of file paths to delete
            
        Returns:
            Tuple of (success_count, fail_count)
        """
        success_count = 0
        fail_count = 0
        
        for file_path in paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    success_count += 1
                    logger.info(f"Deleted file: {file_path}")
                else:
                    logger.warning(f"File does not exist: {file_path}")
                    fail_count += 1
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
                fail_count += 1
        
        return success_count, fail_count
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def format_date(self, date: datetime) -> str:
        """
        Format date in human-readable format
        
        Args:
            date: Datetime object
            
        Returns:
            Formatted string (e.g., "2 days ago", "2024-01-15")
        """
        now = datetime.now()
        delta = now - date
        
        if delta.days == 0:
            if delta.seconds < 60:
                return "just now"
            elif delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
        elif delta.days == 1:
            return "yesterday"
        elif delta.days < 7:
            return f"{delta.days}d ago"
        else:
            return date.strftime("%Y-%m-%d")
