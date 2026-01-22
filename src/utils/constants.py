"""
Application constants
"""

import os

# Get app directory (parent of src directory)
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default paths
DEFAULT_DOWNLOADS_FOLDER = "C:\\Users\\james\\Downloads"
DEFAULT_PROJECTS_ROOT = "C:\\Users\\james"

# Window defaults
DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 650

# Config file paths (relative to app directory)
CONFIG_DIR = os.path.join(APP_DIR, "config")
SETTINGS_FILE = os.path.join(APP_DIR, "config", "settings.json")
PROJECTS_FILE = os.path.join(APP_DIR, "config", "projects.json")
FILE_PATTERNS_FILE = os.path.join(APP_DIR, "config", "file_patterns.json")
