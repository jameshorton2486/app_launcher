"""
Configuration Manager
Handles loading, saving, and validation of JSON configuration files
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils.constants import CONFIG_DIR, SETTINGS_FILE, PROJECTS_FILE, FILE_PATTERNS_FILE, TOOLS_FILE
from src.utils.helpers import ensure_dir

# Try to import logger, but don't fail if it doesn't exist yet
try:
    from src.utils.logger import logger
except ImportError:
    # Fallback logger if logger module doesn't exist
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ConfigFileHandler(FileSystemEventHandler):
    """Watch for external config file changes"""
    
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)


class ConfigManager:
    """Manages application configuration files"""
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        ensure_dir(self.config_dir)
        
        self.settings = {}
        self.projects = []
        self.file_patterns = {}
        self.tools = {}
        
        self.observers = []
        self._load_all()
        self._setup_watchers()
    
    def _load_all(self):
        """Load all configuration files"""
        self.settings = self.load_settings()
        self.projects = self.load_projects()
        self.file_patterns = self.load_file_patterns()
        self.tools = self.load_tools()
    
    def _setup_watchers(self):
        """Set up file watchers for config changes"""
        observer = Observer()
        
        # Watch config directory
        handler = ConfigFileHandler(self._on_config_changed)
        observer.schedule(handler, self.config_dir, recursive=False)
        observer.start()
        
        self.observers.append(observer)
    
    def _on_config_changed(self, file_path):
        """Handle external config file changes"""
        # Reload the changed file
        if file_path.endswith('settings.json'):
            self.settings = self.load_settings()
        elif file_path.endswith('projects.json'):
            self.projects = self.load_projects()
        elif file_path.endswith('file_patterns.json'):
            self.file_patterns = self.load_file_patterns()
        elif file_path.endswith('tools.json'):
            self.tools = self.load_tools()
    
    def load_json(self, file_path: str, default: Any = None) -> Any:
        """
        Load JSON file with error handling and logging
        
        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist or is invalid
            
        Returns:
            Parsed JSON data or default value
        """
        if default is None:
            default = {}
        
        if not os.path.exists(file_path):
            logger.info(f"Config file not found: {file_path}, using defaults")
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Successfully loaded config: {file_path}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            logger.warning(f"Using default values for {file_path}")
            return default
        except IOError as e:
            logger.error(f"IO error loading {file_path}: {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error loading {file_path}: {e}", exc_info=True)
            return default
    
    def save_json(self, file_path: str, data: Any):
        """
        Save data to JSON file with error handling and logging
        
        Args:
            file_path: Path to JSON file
            data: Data to save
        """
        ensure_dir(os.path.dirname(file_path))
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully saved config: {file_path}")
        except IOError as e:
            logger.error(f"IO error saving {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving {file_path}: {e}", exc_info=True)
            raise
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings.json with defaults and validation"""
        default_settings = {
            "window": {
                "width": 900,
                "height": 650,
                "x": None,  # Will be set on first run
                "y": None,  # Will be set on first run
                "start_minimized": False,
                "start_with_windows": True,  # Changed to True per requirements
                "minimize_to_tray": True,
                "global_hotkey": "win+shift+l"
            },
            "theme": {
                "mode": "dark",
                "accent_color": "#6c5ce7"
            },
            "paths": {
                "downloads_folder": "C:\\Users\\james\\Downloads",
                "projects_root": "C:\\Users\\james",
                "screenshots_folder": "C:\\Users\\james\\Documents\\Screenshots"
            },
            "external_tools": {
                "ccleaner": "C:\\Program Files\\CCleaner\\CCleaner64.exe",
                "wise_memory_cleaner": "C:\\Program Files (x86)\\Wise\\Wise Memory Optimizer\\WiseMemoryOptimizer.exe",
                "cursor": "C:\\Users\\james\\AppData\\Local\\Programs\\cursor\\Cursor.exe",
                "vscode": "C:\\Users\\james\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                "pycharm": "C:\\Program Files\\JetBrains\\PyCharm\\bin\\pycharm64.exe"
            }
        }
        
        settings = self.load_json(SETTINGS_FILE, default_settings)
        
        # Merge with defaults to ensure all keys exist
        merged_settings = self._merge_dicts(default_settings, settings)
        
        # Validate schema
        if self._validate_settings_schema(merged_settings):
            # Create file if it doesn't exist
            if not os.path.exists(SETTINGS_FILE):
                self.save_json(SETTINGS_FILE, merged_settings)
                logger.info(f"Created default settings file: {SETTINGS_FILE}")
            return merged_settings
        else:
            logger.warning("Settings validation failed, using defaults")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings.json with validation"""
        if self._validate_settings_schema(settings):
            self.settings = settings
            self.save_json(SETTINGS_FILE, settings)
            logger.info("Settings saved successfully")
        else:
            logger.error("Settings validation failed, not saving")
            raise ValueError("Invalid settings schema")
    
    def load_projects(self) -> List[Dict[str, Any]]:
        """Load projects.json with validation"""
        default_projects = {
            "projects": []
        }
        
        data = self.load_json(PROJECTS_FILE, default_projects)
        projects = data.get("projects", [])
        
        # Validate each project
        validated_projects = []
        for project in projects:
            if self._validate_project_schema(project):
                validated_projects.append(project)
            else:
                logger.warning(f"Invalid project schema, skipping: {project.get('name', 'Unknown')}")
        
        # Create file if it doesn't exist
        if not os.path.exists(PROJECTS_FILE):
            self.save_json(PROJECTS_FILE, {"projects": validated_projects})
            logger.info(f"Created default projects file: {PROJECTS_FILE}")
        
        return validated_projects
    
    def save_projects(self, projects: List[Dict[str, Any]]):
        """Save projects.json with validation"""
        # Validate all projects
        validated_projects = []
        for project in projects:
            if self._validate_project_schema(project):
                validated_projects.append(project)
            else:
                logger.warning(f"Invalid project schema, skipping: {project.get('name', 'Unknown')}")
        
        self.projects = validated_projects
        self.save_json(PROJECTS_FILE, {"projects": validated_projects})
        logger.info(f"Saved {len(validated_projects)} projects")
    
    def load_file_patterns(self) -> Dict[str, Any]:
        """Load file_patterns.json with validation"""
        default_patterns = {
            "patterns": {
                "code_files": [".py", ".ts", ".tsx", ".js", ".jsx", ".ps1", ".bat", ".sh"],
                "doc_files": [".md", ".txt", ".json", ".yaml", ".yml"],
                "image_files": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"],
                "archive_files": [".zip", ".tar", ".gz", ".7z", ".rar"]
            },
            "ignore_patterns": [
                "python-*",
                "node-*",
                "*.exe",
                "*.msi",
                "*.msix"
            ],
            "screenshot_folder": "C:\\Users\\james\\Documents\\Screenshots",
            "archive_folder": "C:\\Users\\james\\Documents\\Archives"
        }
        
        patterns = self.load_json(FILE_PATTERNS_FILE, default_patterns)
        
        # Validate schema
        if self._validate_file_patterns_schema(patterns):
            # Create file if it doesn't exist
            if not os.path.exists(FILE_PATTERNS_FILE):
                self.save_json(FILE_PATTERNS_FILE, patterns)
                logger.info(f"Created default file_patterns file: {FILE_PATTERNS_FILE}")
            return patterns
        else:
            logger.warning("File patterns validation failed, using defaults")
            return default_patterns
    
    def save_file_patterns(self, patterns: Dict[str, Any]):
        """Save file_patterns.json"""
        self.file_patterns = patterns
        self.save_json(FILE_PATTERNS_FILE, patterns)

    def load_tools(self) -> Dict[str, Any]:
        """Load tools.json with validation"""
        default_tools = {
            "sections": [
                {
                    "id": "quick_cleanup",
                    "title": "QUICK CLEANUP",
                    "tools": [
                        {
                            "id": "empty_recycle_bin",
                            "icon": "🗑️",
                            "title": "Empty Recycle Bin",
                            "subtitle": "",
                            "tooltip": "Permanently delete all files in the Recycle Bin",
                            "handler": {"service": "cleanup_service", "method": "empty_recycle_bin"}
                        },
                        {
                            "id": "clear_temp_files",
                            "icon": "🧹",
                            "title": "Clear Temp Files",
                            "subtitle": "",
                            "tooltip": "Delete temporary files from %temp% and Windows\\Temp",
                            "handler": {"service": "cleanup_service", "method": "clear_temp_files"}
                        },
                        {
                            "id": "flush_dns",
                            "icon": "🔄",
                            "title": "Flush DNS",
                            "subtitle": "",
                            "tooltip": "Clear the DNS resolver cache",
                            "handler": {"service": "cleanup_service", "method": "flush_dns"}
                        },
                        {
                            "id": "clear_prefetch",
                            "icon": "📁",
                            "title": "Clear Prefetch",
                            "subtitle": "",
                            "tooltip": "Clear Windows Prefetch folder (requires admin)",
                            "handler": {"service": "cleanup_service", "method": "clear_prefetch"}
                        }
                    ]
                },
                {
                    "id": "memory_performance",
                    "title": "MEMORY & PERFORMANCE",
                    "tools": [
                        {
                            "id": "clear_standby_ram",
                            "icon": "🧠",
                            "title": "Clear RAM Standby",
                            "subtitle": "",
                            "tooltip": "Free up standby memory",
                            "handler": {"service": "cleanup_service", "method": "clear_standby_ram"}
                        },
                        {
                            "id": "disk_cleanup",
                            "icon": "💾",
                            "title": "Disk Cleanup",
                            "subtitle": "",
                            "tooltip": "Launch Windows Disk Cleanup tool",
                            "handler": {"service": "cleanup_service", "method": "run_disk_cleanup"}
                        },
                        {
                            "id": "defrag_optimize",
                            "icon": "⚡",
                            "title": "Defrag/Optimize",
                            "subtitle": "",
                            "tooltip": "Optimize and defragment drive C:",
                            "handler": {"service": "cleanup_service", "method": "optimize_drive", "args": ["C:"]}
                        },
                        {
                            "id": "restart_explorer",
                            "icon": "🔄",
                            "title": "Restart Explorer",
                            "subtitle": "",
                            "tooltip": "Restart Windows Explorer process",
                            "handler": {"service": "cleanup_service", "method": "restart_explorer"}
                        }
                    ]
                },
                {
                    "id": "external_tools",
                    "title": "EXTERNAL TOOLS",
                    "tools": [
                        {
                            "id": "open_ccleaner",
                            "icon": "🧽",
                            "title": "Open CCleaner",
                            "subtitle": "",
                            "tooltip": "Launch CCleaner (configure path in settings)",
                            "handler": {"service": "cleanup_service", "method": "launch_ccleaner", "args": ["$config_manager"]}
                        },
                        {
                            "id": "open_wise_memory",
                            "icon": "🧠",
                            "title": "Open Wise Memory",
                            "subtitle": "",
                            "tooltip": "Launch Wise Memory Cleaner (configure path in settings)",
                            "handler": {"service": "cleanup_service", "method": "launch_wise_memory_cleaner", "args": ["$config_manager"]}
                        },
                        {
                            "id": "reset_ms_store",
                            "icon": "🏪",
                            "title": "Reset MS Store",
                            "subtitle": "",
                            "tooltip": "Reset Microsoft Store cache",
                            "handler": {"service": "cleanup_service", "method": "reset_ms_store"}
                        }
                    ]
                },
                {
                    "id": "network",
                    "title": "NETWORK",
                    "tools": [
                        {
                            "id": "reset_tcpip",
                            "icon": "🌐",
                            "title": "Reset TCP/IP",
                            "subtitle": "",
                            "tooltip": "Reset network stack (requires admin, restart recommended)",
                            "handler": {"service": "cleanup_service", "method": "reset_network"}
                        },
                        {
                            "id": "release_renew_ip",
                            "icon": "🔌",
                            "title": "Release/Renew IP",
                            "subtitle": "",
                            "tooltip": "Release and renew IP address",
                            "handler": {"service": "cleanup_service", "method": "release_renew_ip"}
                        },
                        {
                            "id": "network_stats",
                            "icon": "📶",
                            "title": "Network Stats",
                            "subtitle": "",
                            "tooltip": "Display network statistics",
                            "handler": {"service": "utilities_tab", "method": "show_network_stats"}
                        }
                    ]
                },
                {
                    "id": "windows_update",
                    "title": "WINDOWS UPDATE",
                    "tools": [
                        {
                            "id": "clear_update_cache",
                            "icon": "🗑️",
                            "title": "Clear Update Cache",
                            "subtitle": "",
                            "tooltip": "Clear Windows Update cache (requires admin)",
                            "handler": {"service": "cleanup_service", "method": "clear_windows_update_cache"}
                        },
                        {
                            "id": "pause_updates",
                            "icon": "⏸️",
                            "title": "Pause Updates",
                            "subtitle": "(7 days)",
                            "tooltip": "Pause Windows Updates for 7 days",
                            "handler": {"service": "cleanup_service", "method": "pause_windows_updates", "args": [7]}
                        }
                    ]
                }
            ]
        }

        tools = self.load_json(TOOLS_FILE, default_tools)

        if self._validate_tools_schema(tools):
            if not os.path.exists(TOOLS_FILE):
                self.save_json(TOOLS_FILE, tools)
                logger.info(f"Created default tools file: {TOOLS_FILE}")
            return tools

        logger.warning("Tools validation failed, using defaults")
        return default_tools
    
    def _merge_dicts(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user dict into default dict"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation (e.g., 'window.width')
        
        Args:
            key_path: Dot-separated path to setting
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def _validate_settings_schema(self, settings: Dict[str, Any]) -> bool:
        """
        Validate settings.json schema
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["window", "theme", "paths", "external_tools"]
        
        if not isinstance(settings, dict):
            logger.error("Settings must be a dictionary")
            return False
        
        for key in required_keys:
            if key not in settings:
                logger.error(f"Missing required key in settings: {key}")
                return False
        
        # Validate window settings
        window = settings.get("window", {})
        if not isinstance(window, dict):
            return False
        required_window_keys = ["width", "height", "start_minimized", "start_with_windows", 
                               "minimize_to_tray", "global_hotkey"]
        for key in required_window_keys:
            if key not in window:
                logger.warning(f"Missing window setting: {key}")
        
        # Validate theme
        theme = settings.get("theme", {})
        if not isinstance(theme, dict):
            return False
        
        # Validate paths
        paths = settings.get("paths", {})
        if not isinstance(paths, dict):
            return False
        
        # Validate external_tools
        tools = settings.get("external_tools", {})
        if not isinstance(tools, dict):
            return False
        
        return True
    
    def _validate_project_schema(self, project: Dict[str, Any]) -> bool:
        """
        Validate a project object schema
        
        Args:
            project: Project dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(project, dict):
            return False
        
        required_fields = ["id", "name", "path", "launch_script", "launch_type"]
        
        for field in required_fields:
            if field not in project:
                logger.warning(f"Project missing required field: {field}")
                return False
        
        # Validate field types
        if not isinstance(project.get("id"), str):
            return False
        if not isinstance(project.get("name"), str):
            return False
        if not isinstance(project.get("path"), str):
            return False
        if not isinstance(project.get("launch_script"), str):
            return False
        if project.get("launch_type") not in ["python", "npm", "powershell", "bat", "exe"]:
            logger.warning(f"Invalid launch_type: {project.get('launch_type')}")
        
        return True
    
    def _validate_file_patterns_schema(self, patterns: Dict[str, Any]) -> bool:
        """
        Validate file_patterns.json schema
        
        Args:
            patterns: File patterns dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(patterns, dict):
            return False
        
        if "patterns" not in patterns:
            return False
        
        patterns_dict = patterns.get("patterns", {})
        if not isinstance(patterns_dict, dict):
            return False
        
        required_pattern_keys = ["code_files", "doc_files", "image_files", "archive_files"]
        for key in required_pattern_keys:
            if key not in patterns_dict:
                logger.warning(f"Missing pattern category: {key}")
        
        return True

    def _validate_tools_schema(self, tools: Dict[str, Any]) -> bool:
        """
        Validate tools.json schema
        
        Args:
            tools: Tools dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(tools, dict):
            return False

        sections = tools.get("sections")
        if not isinstance(sections, list):
            return False

        for section in sections:
            if not isinstance(section, dict):
                return False
            if "title" not in section or "tools" not in section:
                return False
            if not isinstance(section.get("tools"), list):
                return False
            for tool in section.get("tools", []):
                if not isinstance(tool, dict):
                    return False
                if "id" not in tool or "title" not in tool or "handler" not in tool:
                    return False

        return True
    
    def shutdown(self):
        """Stop file watchers"""
        logger.info("Shutting down config manager")
        for observer in self.observers:
            try:
                observer.stop()
                observer.join(timeout=1.0)
            except Exception as e:
                logger.warning(f"Error stopping file watcher: {e}")
