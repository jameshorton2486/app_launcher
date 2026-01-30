"""
External Tool Service
Launches third-party tools based on configuration
"""

import os
import subprocess
import json
from typing import Tuple

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ExternalToolService:
    """Service for launching external tools"""

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

        return False, f"{tool_name} not found. Configure path in settings."

    def _resolve_from_registry(self, tool_name: str) -> str:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "external_tool_paths.json"
        )
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
            subprocess.Popen([path], creationflags=subprocess.CREATE_NO_WINDOW)
            return True, f"{tool_name} launched"
        except Exception as exc:
            logger.error(f"Failed to launch {tool_name}: {exc}")
            return False, f"Failed to launch {tool_name}: {exc}"
