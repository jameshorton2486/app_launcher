"""
Tool Registry
Loads tool definitions and routes execution to services.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import os

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ToolRegistry:
    """Registry for tool definitions and execution"""

    def __init__(self) -> None:
        self._tools_data: Dict[str, Any] = {"sections": []}
        self._sections: List[Dict[str, Any]] = []
        self._tool_index: Dict[str, Dict[str, Any]] = {}
        self._service_cache: Dict[str, Any] = {}

    def load_tools(self, json_path: str) -> None:
        """Load tool definitions from JSON path"""
        if not json_path:
            logger.warning("Tool registry load_tools called with empty path")
            self._reset_tools()
            return

        if not os.path.exists(json_path):
            logger.warning(f"Tools config not found: {json_path}")
            self._reset_tools()
            return

        try:
            with open(json_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                logger.error("Tools config is not a JSON object")
                self._reset_tools()
                return
            self._tools_data = data
            self._index_tools()
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON in tools config: {exc}")
            self._reset_tools()
        except OSError as exc:
            logger.error(f"Unable to read tools config: {exc}")
            self._reset_tools()

    def get_sections_by_tab(self, tab_name: str) -> List[dict]:
        """Return sections matching a tab name"""
        if not tab_name:
            return []
        normalized = str(tab_name).strip().lower()
        results: List[dict] = []
        for section in self._sections:
            if not isinstance(section, dict):
                continue
            tab_value = str(section.get("tab", "")).strip().lower()
            if tab_value == normalized:
                results.append(section)
        return results

    def get_tool_by_id(self, tool_id: str) -> Optional[dict]:
        """Get a tool definition by ID"""
        if not tool_id:
            return None
        return self._tool_index.get(tool_id)

    def execute_tool(self, tool_id: str, config_manager) -> Tuple[bool, str]:
        """Execute a tool by ID using the configured services"""
        tool = self.get_tool_by_id(tool_id)
        if not tool:
            return False, f"Tool not found: {tool_id}"

        handler = tool.get("handler") if isinstance(tool.get("handler"), dict) else {}
        service_name = tool.get("service") or handler.get("service")
        method_name = tool.get("method") or handler.get("method")

        args = self._select_args(tool, handler)
        kwargs = self._select_kwargs(tool, handler)

        service = self._resolve_service(service_name, config_manager)
        if not service:
            return False, f"Service not available: {service_name}"

        if not method_name or not hasattr(service, method_name):
            return False, f"Method not found: {service_name}.{method_name}"

        method = getattr(service, method_name)
        resolved_args = [self._resolve_value(value, config_manager) for value in args]
        resolved_kwargs = {
            key: self._resolve_value(value, config_manager)
            for key, value in kwargs.items()
        }

        try:
            result = method(*resolved_args, **resolved_kwargs)
            return self._normalize_result(result)
        except Exception as exc:
            logger.error(f"Tool execution failed for {tool_id}: {exc}")
            return False, str(exc)

    def search_tools(self, query: str) -> List[dict]:
        """Search tools by query across IDs, titles, descriptions, and tags"""
        if not query:
            return []
        query_text = str(query).strip().lower()
        results: List[dict] = []

        for section in self._sections:
            if not isinstance(section, dict):
                continue
            section_title = str(section.get("title", "")).lower()
            for tool in section.get("tools", []):
                if not isinstance(tool, dict):
                    continue
                if self._tool_matches_query(tool, section_title, query_text):
                    tool_entry = self._tool_index.get(tool.get("id"), tool)
                    results.append(tool_entry)
        return results

    def _reset_tools(self) -> None:
        self._tools_data = {"sections": []}
        self._sections = []
        self._tool_index = {}

    def _index_tools(self) -> None:
        self._sections = self._tools_data.get("sections", [])
        if not isinstance(self._sections, list):
            self._sections = []
            self._tool_index = {}
            return

        self._tool_index = {}
        for section in self._sections:
            if not isinstance(section, dict):
                continue
            for tool in section.get("tools", []):
                if not isinstance(tool, dict):
                    continue
                tool_id = tool.get("id")
                if not tool_id:
                    continue
                tool_entry = dict(tool)
                tool_entry.setdefault("section_id", section.get("id"))
                tool_entry.setdefault("section_title", section.get("title"))
                if section.get("tab") and "tab" not in tool_entry:
                    tool_entry["tab"] = section.get("tab")
                self._tool_index[tool_id] = tool_entry

    @staticmethod
    def _select_args(tool: Dict[str, Any], handler: Dict[str, Any]) -> List[Any]:
        if "method_args" in tool:
            return tool.get("method_args", []) or []
        if "args" in tool:
            return tool.get("args", []) or []
        return handler.get("args", []) or []

    @staticmethod
    def _select_kwargs(tool: Dict[str, Any], handler: Dict[str, Any]) -> Dict[str, Any]:
        if "method_kwargs" in tool:
            return tool.get("method_kwargs", {}) or {}
        if "kwargs" in tool:
            return tool.get("kwargs", {}) or {}
        return handler.get("kwargs", {}) or {}

    def _resolve_service(self, service_name: Optional[str], config_manager):
        if not service_name:
            return None

        normalized = str(service_name).strip().lower()
        if normalized in self._service_cache:
            return self._service_cache[normalized]

        service = None
        try:
            if normalized in {"cleanup", "cleanup_service"}:
                from src.services.cleanup_service import CleanupService
                service = CleanupService()
            elif normalized == "process":
                from src.services.process_service import ProcessService
                service = ProcessService()
            elif normalized == "optimization":
                from src.services.optimization_service import OptimizationService
                service = OptimizationService()
            elif normalized == "maintenance":
                from src.services.maintenance_service import MaintenanceService
                service = MaintenanceService()
            elif normalized == "external":
                from src.services.external_tool_service import ExternalToolService
                service = ExternalToolService(config_manager)
        except Exception as exc:
            logger.warning(f"Unable to resolve service '{service_name}': {exc}")
            service = None

        if service:
            self._service_cache[normalized] = service
        return service

    @staticmethod
    def _resolve_value(value: Any, config_manager) -> Any:
        if isinstance(value, str) and value.startswith("$"):
            key = value[1:]
            if key in {"config_manager", "config"}:
                return config_manager
        return value

    @staticmethod
    def _normalize_result(result: Any) -> Tuple[bool, str]:
        if isinstance(result, tuple) and len(result) == 2:
            return result[0], result[1]
        if isinstance(result, bool):
            return result, "Completed" if result else "Failed"
        if result is None:
            return True, "Completed"
        return True, str(result)

    @staticmethod
    def _tool_matches_query(tool: Dict[str, Any], section_title: str, query: str) -> bool:
        searchable = [
            str(tool.get("id", "")),
            str(tool.get("title", "")),
            str(tool.get("description", "")),
            str(tool.get("subtitle", "")),
            section_title or "",
        ]
        for field in searchable:
            if query in field.lower():
                return True

        tags = tool.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                if query in str(tag).lower():
                    return True
        return False
