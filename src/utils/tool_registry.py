"""
Tool Registry
Maps tool IDs to metadata and callable handlers.
"""

from typing import Any, Dict, Optional, Callable

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ToolRegistry:
    """Registry for tools and their handlers"""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, tool_id: str, metadata: Dict[str, Any], handler: Callable[[], Any]):
        """Register a tool with metadata and a callable handler"""
        if not tool_id:
            raise ValueError("tool_id is required")
        if not callable(handler):
            raise ValueError(f"Handler for {tool_id} must be callable")

        self._tools[tool_id] = {
            "metadata": metadata or {},
            "handler": handler
        }

    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool entry by ID"""
        return self._tools.get(tool_id)

    def get_handler(self, tool_id: str) -> Optional[Callable[[], Any]]:
        """Get handler callable for a tool"""
        entry = self.get_tool(tool_id)
        if not entry:
            return None
        return entry.get("handler")

    def register_from_config(self, tools_config: Dict[str, Any], services: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """Register tools defined in config using service mappings"""
        context = context or {}
        sections = tools_config.get("sections", []) if isinstance(tools_config, dict) else []

        for section in sections:
            tools = section.get("tools", []) if isinstance(section, dict) else []
            for tool in tools:
                tool_id = tool.get("id")
                handler_config = tool.get("handler")
                handler = None
                if isinstance(handler_config, dict):
                    handler = self._build_handler(handler_config, services, context)
                else:
                    handler = self._build_handler_from_fields(tool, services, context)
                if not handler:
                    logger.warning(f"Tool {tool_id} missing handler configuration")
                    continue

                metadata = {
                    "id": tool_id,
                    "title": tool.get("title", ""),
                    "subtitle": tool.get("subtitle", ""),
                    "icon": tool.get("icon", ""),
                    "tooltip": tool.get("tooltip", "") or tool.get("description", ""),
                    "section": section.get("title", "")
                }
                self.register(tool_id, metadata, handler)

    def _build_handler_from_fields(self, tool: Dict[str, Any], services: Dict[str, Any], context: Dict[str, Any]) -> Optional[Callable[[], Any]]:
        service_name = tool.get("service")
        method_name = tool.get("method")
        args = tool.get("method_args", tool.get("args", []))
        kwargs = tool.get("method_kwargs", tool.get("kwargs", {}))
        handler_config = {
            "service": service_name,
            "method": method_name,
            "args": args,
            "kwargs": kwargs
        }
        return self._build_handler(handler_config, services, context)

    def _build_handler(self, handler_config: Dict[str, Any], services: Dict[str, Any], context: Dict[str, Any]) -> Optional[Callable[[], Any]]:
        if not isinstance(handler_config, dict):
            return None

        service_name = handler_config.get("service")
        method_name = handler_config.get("method")
        args = handler_config.get("args", [])
        kwargs = handler_config.get("kwargs", {})

        service = services.get(service_name)
        if not service or not method_name or not hasattr(service, method_name):
            return None

        method = getattr(service, method_name)

        def handler():
            resolved_args = [self._resolve_value(value, context) for value in args]
            resolved_kwargs = {key: self._resolve_value(value, context) for key, value in kwargs.items()}
            return method(*resolved_args, **resolved_kwargs)

        return handler

    @staticmethod
    def _resolve_value(value: Any, context: Dict[str, Any]) -> Any:
        if isinstance(value, str) and value.startswith("$"):
            key = value[1:]
            return context.get(key)
        return value
