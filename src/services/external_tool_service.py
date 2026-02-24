"""
External Tool Service
Launches third-party tools based on configuration
"""

import os
import subprocess
import json
from typing import Tuple
from src.utils.constants import EXTERNAL_TOOL_PATHS_FILE

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ExternalToolService:
    """Service for launching external tools"""

    SAFE_EXECUTABLE_EXTENSIONS = {".exe", ".bat", ".cmd"}

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def launch_tool(self, tool_name: str) -> Tuple[bool, str]:
        """Launch an external tool by name"""
        if not tool_name:
            return False, "Tool name is required"

        tool_path = self.config_manager.get_setting(f"external_tools.{tool_name}", "")
        if tool_path and os.path.exists(tool_path):
            return self._start_process(tool_path, tool_name)

        fallback_path = self._resolve_from_registry(tool_name)
        if fallback_path:
            return self._start_process(fallback_path, tool_name)

        tool_title, download_url = self._get_tool_info(tool_name)
        display_name = tool_title or tool_name
        if download_url:
            return False, f"{display_name} not found. Download it from: {download_url}"
        return False, f"{display_name} not found. Configure path in settings."

    def _get_tool_info(self, tool_name: str):
        tools_data = getattr(self.config_manager, "tools", {}) or {}
        for section in tools_data.get("sections", []):
            for tool in section.get("tools", []):
                if tool.get("id") == tool_name:
                    return tool.get("title"), tool.get("download_url")
        return None, None

    def _resolve_from_registry(self, tool_name: str) -> str:
        config_path = EXTERNAL_TOOL_PATHS_FILE
        if not os.path.exists(config_path):
            return ""

        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            candidates = data.get(tool_name, [])
        except Exception:
            return ""

        for candidate in candidates:
            expanded = os.path.expandvars(candidate)
            if os.path.exists(expanded):
                return expanded
        return ""

    @staticmethod
    def _start_process(path: str, tool_name: str) -> Tuple[bool, str]:
        try:
            if not os.path.isfile(path):
                logger.warning("Blocked non-file tool path for %s: %s", tool_name, path)
                return False, f"{tool_name} path is invalid"
            ext = os.path.splitext(path)[1].lower()
            if ext not in ExternalToolService.SAFE_EXECUTABLE_EXTENSIONS:
                logger.warning("Blocked unsafe tool extension for %s: %s", tool_name, path)
                return False, f"{tool_name} path has unsupported executable type"
            subprocess.Popen([path], creationflags=subprocess.CREATE_NO_WINDOW)
            return True, f"{tool_name} launched"
        except Exception as exc:
            logger.error(f"Failed to launch {tool_name}: {exc}")
            return False, f"Failed to launch {tool_name}: {exc}"
