"""
Tool Usage Tracking
Loads and updates tool usage history.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from src.utils.constants import CONFIG_DIR

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

USAGE_FILE = os.path.join(CONFIG_DIR, "tool_usage.json")


class ToolUsageStore:
    """Helper for tracking tool usage data."""

    def __init__(self):
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        default_data = {
            "tool_runs": {},
            "last_full_cleanup": None,
            "total_space_freed_mb": 0,
            "total_tools_run": 0
        }
        if not os.path.exists(USAGE_FILE):
            self._save(default_data)
            return default_data
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                return default_data
            return {**default_data, **data}
        except Exception as exc:
            logger.error(f"Failed to load tool usage: {exc}")
            return default_data

    def _save(self, data: Dict[str, Any]):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(USAGE_FILE, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
        except Exception as exc:
            logger.error(f"Failed to save tool usage: {exc}")

    def record_run(self, tool_id: str, success: bool, message: str = "", freed_mb: float = 0.0):
        now = datetime.utcnow().isoformat()
        run_entry = self.data["tool_runs"].get(tool_id, {
            "last_run": None,
            "run_count": 0,
            "last_result": None,
            "last_message": ""
        })
        run_entry["last_run"] = now
        run_entry["run_count"] = int(run_entry.get("run_count", 0)) + 1
        run_entry["last_result"] = "success" if success else "error"
        run_entry["last_message"] = message
        self.data["tool_runs"][tool_id] = run_entry
        self.data["total_tools_run"] = int(self.data.get("total_tools_run", 0)) + 1
        if freed_mb > 0:
            self.data["total_space_freed_mb"] = float(self.data.get("total_space_freed_mb", 0)) + freed_mb
        self._save(self.data)

    def mark_full_cleanup(self):
        self.data["last_full_cleanup"] = datetime.utcnow().isoformat()
        self._save(self.data)

    def get_last_run(self, tool_id: str) -> Optional[str]:
        entry = self.data.get("tool_runs", {}).get(tool_id)
        if entry:
            return entry.get("last_run")
        return None

    def get_stats(self) -> Dict[str, Any]:
        return self.data

    def get_most_used(self) -> Tuple[str, int]:
        most_tool = ""
        most_count = 0
        for tool_id, entry in self.data.get("tool_runs", {}).items():
            count = int(entry.get("run_count", 0))
            if count > most_count:
                most_count = count
                most_tool = tool_id
        return most_tool, most_count
