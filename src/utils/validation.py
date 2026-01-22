"""
Validation Utilities
Helper functions for validating user inputs and system state
"""

import os
from pathlib import Path
from typing import Tuple, Optional

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


def validate_path(path: str, must_exist: bool = True, must_be_file: bool = False, must_be_dir: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate a file or directory path
    
    Args:
        path: Path to validate
        must_exist: Whether path must exist
        must_be_file: Whether path must be a file
        must_be_dir: Whether path must be a directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not isinstance(path, str):
        return False, "Path is required"
    
    path = path.strip()
    if not path:
        return False, "Path cannot be empty"
    
    if must_exist:
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"
        
        if must_be_file and not os.path.isfile(path):
            return False, f"Path is not a file: {path}"
        
        if must_be_dir and not os.path.isdir(path):
            return False, f"Path is not a directory: {path}"
    
    return True, None


def validate_project_name(name: str, existing_names: list = None) -> Tuple[bool, Optional[str]]:
    """
    Validate a project name
    
    Args:
        name: Project name to validate
        existing_names: List of existing project names to check for duplicates
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Project name is required"
    
    name = name.strip()
    if not name:
        return False, "Project name cannot be empty"
    
    # Check for invalid characters (Windows file name restrictions)
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        if char in name:
            return False, f"Project name contains invalid character: {char}"
    
    # Check for reserved names (Windows)
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if name.upper() in reserved_names:
        return False, f"Project name cannot be a reserved Windows name: {name}"
    
    # Check for duplicates
    if existing_names and name in existing_names:
        return False, f"Project name already exists: {name}"
    
    return True, None


def validate_launch_script(script: str, project_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a launch script path
    
    Args:
        script: Script filename or path
        project_path: Project directory path
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not script or not isinstance(script, str):
        return False, "Launch script is required"
    
    script = script.strip()
    if not script:
        return False, "Launch script cannot be empty"
    
    # Check if absolute path or relative
    if os.path.isabs(script):
        script_path = script
    else:
        script_path = os.path.join(project_path, script)
    
    # Check if file exists
    if not os.path.exists(script_path):
        return False, f"Launch script not found: {script_path}"
    
    if not os.path.isfile(script_path):
        return False, f"Launch script is not a file: {script_path}"
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"
    
    url = url.strip()
    if not url:
        return False, "URL cannot be empty"
    
    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "URL must start with http:// or https://"
    
    return True, None


def validate_hotkey(hotkey: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a hotkey string
    
    Args:
        hotkey: Hotkey string (e.g., "win+shift+l")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hotkey or not isinstance(hotkey, str):
        return False, "Hotkey is required"
    
    hotkey = hotkey.strip().lower()
    if not hotkey:
        return False, "Hotkey cannot be empty"
    
    # Check for at least one modifier and one key
    parts = hotkey.split('+')
    if len(parts) < 2:
        return False, "Hotkey must include at least one modifier (win, ctrl, alt, shift) and one key"
    
    # Check for valid modifiers
    valid_modifiers = ['win', 'windows', 'ctrl', 'control', 'alt', 'shift']
    modifiers = [p.strip() for p in parts[:-1]]
    key = parts[-1].strip()
    
    for mod in modifiers:
        if mod not in valid_modifiers:
            return False, f"Invalid modifier: {mod}"
    
    if not key:
        return False, "Hotkey must include a key"
    
    return True, None
