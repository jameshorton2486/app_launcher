"""
Utility helper functions
"""

import os


def normalize_path(path):
    """Normalize and clean a file path."""
    if not path:
        return path
    return os.path.normpath(path.strip().strip('"').strip("'"))


def ensure_dir(directory):
    """Ensure a directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory
