"""
Application constants
"""

import os
import sys
from pathlib import Path

# Get app directory (parent of src directory)
if getattr(sys, 'frozen', False):
    APP_DIR = str(Path(sys.executable).parent)
    BUNDLE_DIR = str(Path(sys._MEIPASS))
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BUNDLE_DIR = APP_DIR


def resource_path(*parts: str) -> str:
    """
    Resolve a resource path, preferring writable app directory and
    falling back to bundled resources in frozen builds.
    """
    primary = os.path.join(APP_DIR, *parts)
    if os.path.exists(primary):
        return primary
    return os.path.join(BUNDLE_DIR, *parts)

# Default paths
DEFAULT_DOWNLOADS_FOLDER = "C:\\Users\\james\\Downloads"
DEFAULT_PROJECTS_ROOT = "C:\\Users\\james"

# Window defaults
DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 650

# Config file paths (relative to app directory)
CONFIG_DIR = os.path.join(APP_DIR, "config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
PROJECTS_FILE = os.path.join(CONFIG_DIR, "projects.json")
FILE_PATTERNS_FILE = resource_path("config", "file_patterns.json")
TOOLS_FILE = resource_path("config", "tools.json")
EXTERNAL_TOOL_PATHS_FILE = resource_path("config", "external_tool_paths.json")
PLUGINS_FILE = resource_path("config", "plugins.json")
