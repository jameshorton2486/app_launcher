"""
Tool Registry
Loads tool definitions and routes execution to services.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import os
from datetime import datetime, timedelta
import re
import threading
import importlib.util
from pathlib import Path

from src.theme import COLORS

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

try:
    from src.components.toast import ToastManager
except Exception:
    ToastManager = None

try:
    from src.utils.tool_usage import ToolUsageStore
except Exception:
    ToolUsageStore = None

try:
    import tkinter.messagebox as messagebox
    import tkinter as tk
except Exception:
    messagebox = None
    tk = None


class ToolRegistry:
    """Registry for tool definitions and execution"""

    def __init__(self) -> None:
        self._tools_data: Dict[str, Any] = {"sections": []}
        self._sections: List[Dict[str, Any]] = []
        self._tool_index: Dict[str, Dict[str, Any]] = {}
        self._service_cache: Dict[str, Any] = {}
        self._plugin_index: Dict[str, Any] = {}
        self._integrity_issues: List[str] = []

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
            self._load_plugins(json_path)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON in tools config: {exc}")
            self._reset_tools()
        except OSError as exc:
            logger.error(f"Unable to read tools config: {exc}")
            self._reset_tools()

    def validate_tools(self, config_manager) -> List[str]:
        """Validate that each tool resolves to a callable service method."""
        errors: List[str] = list(self._integrity_issues)
        for tool_id, tool in self._tool_index.items():
            if not isinstance(tool, dict):
                continue
            handler = tool.get("handler") if isinstance(tool.get("handler"), dict) else {}
            service_name = tool.get("service") or handler.get("service")
            method_name = tool.get("method") or handler.get("method")

            if tool_id in self._plugin_index:
                plugin = self._plugin_index.get(tool_id)
                if not plugin or not hasattr(plugin, "launch") or not callable(getattr(plugin, "launch")):
                    message = f"{tool_id}: plugin launch method unavailable"
                    logger.warning(message)
                    errors.append(message)
                continue

            if not service_name or not method_name:
                message = f"{tool_id}: missing service or method"
                logger.warning(message)
                errors.append(message)
                continue

            service = self._resolve_service(service_name, config_manager)
            if not service:
                message = f"{tool_id}: service not available ({service_name})"
                logger.warning(message)
                errors.append(message)
                continue

            if not hasattr(service, method_name) or not callable(getattr(service, method_name)):
                message = f"{tool_id}: method not callable ({service_name}.{method_name})"
                logger.warning(message)
                errors.append(message)
                continue

        if errors:
            logger.warning("Tool validation completed with %s issues", len(errors))
        else:
            logger.info("Tool validation completed with no issues")
        return errors

    def get_integrity_issues(self) -> List[str]:
        """Return indexing/plugin integrity issues discovered at load time."""
        return list(self._integrity_issues)

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

    def execute_tool(self, tool_id: str, config_manager, skip_confirmation: bool = False) -> Tuple[bool, str]:
        """Execute a tool by ID using the configured services"""
        tool = self.get_tool_by_id(tool_id)
        if not tool:
            return False, f"Tool not found: {tool_id}"

        handler = tool.get("handler") if isinstance(tool.get("handler"), dict) else {}
        service_name = tool.get("service") or handler.get("service")
        method_name = tool.get("method") or handler.get("method")

        if tool_id in self._plugin_index:
            return self._execute_plugin(tool_id, tool, config_manager)

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
            if not skip_confirmation and not self._confirm_tool_execution(tool):
                return True, "Cancelled"
            if not self._check_cooldown(tool):
                return True, "Cancelled"
            result = method(*resolved_args, **resolved_kwargs)
            success, message = self._normalize_result(result)
            self._record_usage(tool, success, message)
            self._notify_toast(tool, success, message, config_manager)
            return success, message
        except Exception as exc:
            logger.error(f"Tool execution failed for {tool_id}: {exc}")
            message = str(exc)
            self._record_usage(tool, False, message)
            self._notify_toast(tool, False, message, config_manager)
            return False, message

    def search_tools(self, query: str) -> List[dict]:
        """Search tools by query across IDs, titles, descriptions, and tags"""
        query_text = str(query or "").strip().lower()
        results: List[dict] = []

        for section in self._sections:
            if not isinstance(section, dict):
                continue
            section_title = str(section.get("title", "")).lower()
            for tool in section.get("tools", []):
                if not isinstance(tool, dict):
                    continue
                if not query_text or self._tool_matches_query(tool, section_title, query_text):
                    tool_entry = self._tool_index.get(tool.get("id"), tool)
                    results.append(tool_entry)
        return results

    def _reset_tools(self) -> None:
        self._tools_data = {"sections": []}
        self._sections = []
        self._tool_index = {}
        self._plugin_index = {}
        self._integrity_issues = []

    def _index_tools(self) -> None:
        self._sections = self._tools_data.get("sections", [])
        if not isinstance(self._sections, list):
            self._sections = []
            self._tool_index = {}
            self._integrity_issues = []
            return

        self._tool_index = {}
        self._integrity_issues = []
        for section in self._sections:
            if not isinstance(section, dict):
                continue
            for tool in section.get("tools", []):
                if not isinstance(tool, dict):
                    continue
                tool_id = tool.get("id")
                if not tool_id:
                    continue
                if tool_id in self._tool_index:
                    issue = f"duplicate tool id: {tool_id}"
                    logger.warning(issue)
                    self._integrity_issues.append(issue)
                    continue
                tool_entry = dict(tool)
                tool_entry.setdefault("section_id", section.get("id"))
                tool_entry.setdefault("section_title", section.get("title"))
                if section.get("tab") and "tab" not in tool_entry:
                    tool_entry["tab"] = section.get("tab")
                self._tool_index[tool_id] = tool_entry

    @staticmethod
    def _slug(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", str(text or "").strip().lower()).strip("_")

    def _load_plugins(self, json_path: str) -> None:
        self._plugin_index = {}
        try:
            root_dir = Path(json_path).resolve().parents[1]
            plugins_dir = root_dir / "src" / "plugins"
            plugins_cfg_path = root_dir / "config" / "plugins.json"

            plugin_settings = {}
            if plugins_cfg_path.exists():
                with open(plugins_cfg_path, "r", encoding="utf-8") as handle:
                    plugin_settings = json.load(handle) or {}
            if not plugin_settings.get("enabled", True):
                return

            if not plugins_dir.exists():
                return

            sections_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
            for section in self._sections:
                if not isinstance(section, dict):
                    continue
                key = (str(section.get("tab", "")), str(section.get("id", "")))
                if key[0] and key[1]:
                    sections_map[key] = section
            settings_by_id = plugin_settings.get("plugins", {}) if isinstance(plugin_settings, dict) else {}

            for plugin_file in plugins_dir.glob("*_plugin.py"):
                module_name = f"tool_plugin_{plugin_file.stem}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                    if not spec or not spec.loader:
                        continue
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    plugin_cls = getattr(module, "ToolPlugin", None)
                    if not plugin_cls:
                        logger.warning(f"Plugin missing ToolPlugin class: {plugin_file.name}")
                        continue
                    plugin = plugin_cls()
                except Exception as exc:
                    logger.warning(f"Plugin load failed ({plugin_file.name}): {exc}")
                    continue

                plugin_id = getattr(plugin, "id", "")
                plugin_title = getattr(plugin, "title", "")
                if not plugin_id or not plugin_title or not hasattr(plugin, "launch"):
                    logger.warning(f"Plugin contract invalid: {plugin_file.name}")
                    continue

                plugin_cfg = settings_by_id.get(plugin_id, {})
                if isinstance(plugin_cfg, dict) and not plugin_cfg.get("enabled", True):
                    continue

                tab = (plugin_cfg.get("tab") if isinstance(plugin_cfg, dict) else None) or getattr(plugin, "tab", "maintenance")
                section_id = (plugin_cfg.get("section_id") if isinstance(plugin_cfg, dict) else None) or self._slug(getattr(plugin, "category", "External Tools"))
                section_title = (plugin_cfg.get("section_title") if isinstance(plugin_cfg, dict) else None) or str(getattr(plugin, "category", "External Tools")).upper()
                section_description = (plugin_cfg.get("section_description") if isinstance(plugin_cfg, dict) else None) or ""
                section_icon = (plugin_cfg.get("section_icon") if isinstance(plugin_cfg, dict) else None) or ""
                order = (plugin_cfg.get("order") if isinstance(plugin_cfg, dict) else None) or 100

                tool_entry = {
                    "id": plugin_id,
                    "title": plugin_title,
                    "icon": getattr(plugin, "icon", ""),
                    "description": getattr(plugin, "description", ""),
                    "service": "plugin",
                    "method": "launch",
                    "requires_admin": bool(getattr(plugin, "requires_admin", False)),
                    "external": True,
                    "download_url": getattr(plugin, "download_url", ""),
                    "tags": ["external", "plugin"],
                    "category": getattr(plugin, "category", "External Tools"),
                    "requires_restart": False,
                    "risk_level": "safe",
                    "recommended_frequency": "as_needed",
                }

                self._plugin_index[plugin_id] = plugin
                if plugin_id in self._tool_index:
                    issue = f"duplicate tool id from plugin: {plugin_id}"
                    logger.warning(issue)
                    self._integrity_issues.append(issue)
                    continue
                self._tool_index[plugin_id] = tool_entry

                key = (str(tab), str(section_id))
                if key not in sections_map:
                    sections_map[key] = {
                        "id": section_id,
                        "title": section_title,
                        "icon": section_icon,
                        "description": section_description,
                        "tab": tab,
                        "tools": [],
                        "_order": order,
                    }
                sections_map[key]["tools"].append(tool_entry)
                if "_order" not in sections_map[key]:
                    sections_map[key]["_order"] = order

            plugin_sections = sorted(
                sections_map.values(),
                key=lambda s: (int(s.get("_order", 100)), str(s.get("title", "")))
            )
            self._sections = []
            for section in plugin_sections:
                section.pop("_order", None)
                self._sections.append(section)
        except Exception as exc:
            logger.warning(f"Plugin loading failed: {exc}")

    def _execute_plugin(self, tool_id: str, tool: Dict[str, Any], config_manager) -> Tuple[bool, str]:
        plugin = self._plugin_index.get(tool_id)
        if not plugin:
            return False, f"Plugin not found: {tool_id}"
        try:
            result = plugin.launch(config_manager)
            success, message = self._normalize_result(result)
            self._record_usage(tool, success, message)
            self._notify_toast(tool, success, message, config_manager)
            return success, message
        except Exception as exc:
            logger.error(f"Plugin execution failed for {tool_id}: {exc}")
            message = str(exc)
            self._record_usage(tool, False, message)
            self._notify_toast(tool, False, message, config_manager)
            return False, message

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

    def _notify_toast(self, tool: Dict[str, Any], success: bool, message: str, config_manager):
        if not ToastManager:
            return
        try:
            enabled = True
            if config_manager:
                enabled = config_manager.get_setting('ui.show_toasts', True)
            if not enabled:
                return
            title = tool.get("title", tool.get("id", "Tool"))
            if success:
                ToastManager.show_success(title, message)
            else:
                ToastManager.show_error(title, message)
        except Exception:
            pass

    def _record_usage(self, tool: Dict[str, Any], success: bool, message: str):
        if not ToolUsageStore:
            return
        try:
            store = ToolUsageStore()
            freed_mb = self._parse_freed_mb(message)
            store.record_run(tool.get("id", "unknown"), success, message, freed_mb=freed_mb)
        except Exception:
            pass

    def _check_cooldown(self, tool: Dict[str, Any]) -> bool:
        if not ToolUsageStore:
            return True
        cooldown = tool.get("cooldown_days")
        if not cooldown:
            return True
        tool_id = tool.get("id")
        if not tool_id:
            return True

        store = ToolUsageStore()
        last_run = store.get_last_run(tool_id)
        if not last_run:
            return True

        try:
            last_dt = datetime.fromisoformat(last_run)
        except Exception:
            return True

        now = datetime.utcnow()
        delta = now - last_dt
        if delta.days >= int(cooldown):
            return True

        days_ago = max(0, delta.days)
        tool_name = tool.get("title", tool_id)
        reason = tool.get("notes") or "cause issues"
        reason_text = self._normalize_cooldown_reason(reason)
        warning = (
            "⚠️ Cooldown Warning\n\n"
            f"You ran '{tool_name}' {days_ago} days ago.\n\n"
            f"Running this tool too frequently can {reason_text}.\n\n"
            f"Recommended: Wait at least {cooldown} days between runs."
        )

        return self._prompt_cooldown("⚠️ Cooldown Warning", warning)

    def _prompt_user(self, title: str, message: str) -> bool:
        if not messagebox:
            return True
        try:
            if tk and tk._default_root:
                return messagebox.askyesno(title, message)
            root = tk.Tk() if tk else None
            if root:
                root.withdraw()
            result = messagebox.askyesno(title, message)
            if root:
                root.destroy()
            return result
        except Exception:
            return True

    def _confirm_tool_execution(self, tool: Dict[str, Any]) -> bool:
        requires_confirmation = bool(tool.get("requires_confirmation"))
        is_high_risk = str(tool.get("risk_level", "")).lower() == "high"
        if not requires_confirmation and not is_high_risk:
            return True

        tool_name = tool.get("title", tool.get("id", "Tool"))
        warning = tool.get("warning") or "This action makes system-level changes."
        restart_note = "This tool requires a restart to fully apply changes." if tool.get("requires_restart") else ""

        title = "High Risk Action" if is_high_risk else "Confirm Action"
        message_parts = [
            f"You're about to run: {tool_name}",
            "",
            warning,
        ]
        if restart_note:
            message_parts.append("")
            message_parts.append(restart_note)
        message_parts.append("")
        message_parts.append("Do you want to continue?")

        return self._prompt_user(title, "\n".join(message_parts))

    def _prompt_cooldown(self, title: str, message: str) -> bool:
        if not tk:
            return self._prompt_user(title, message)

        result = {"value": False}

        def _show():
            root = None
            if not tk._default_root:
                root = tk.Tk()
                root.withdraw()
                dialog = tk.Toplevel(root)
            else:
                dialog = tk.Toplevel(tk._default_root)
            dialog.title(title)
            dialog.configure(bg=COLORS["bg_primary"])
            dialog.resizable(False, False)
            dialog.attributes("-topmost", True)

            frame = tk.Frame(dialog, bg=COLORS["bg_primary"], padx=20, pady=16)
            frame.pack(fill="both", expand=True)

            label = tk.Label(
                frame,
                text=message,
                justify="left",
                anchor="w",
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                wraplength=520
            )
            label.pack(fill="x")

            button_row = tk.Frame(frame, bg=COLORS["bg_primary"])
            button_row.pack(fill="x", pady=(16, 0))

            def cancel():
                result["value"] = False
                dialog.destroy()
                if root:
                    root.destroy()

            def proceed():
                result["value"] = True
                dialog.destroy()
                if root:
                    root.destroy()

            cancel_btn = tk.Button(button_row, text="Cancel", width=12, command=cancel)
            cancel_btn.pack(side="right", padx=(8, 0))

            run_btn = tk.Button(button_row, text="Run Anyway", width=12, command=proceed)
            run_btn.pack(side="right")

            dialog.protocol("WM_DELETE_WINDOW", cancel)
            dialog.update_idletasks()
            dialog.grab_set()
            dialog.wait_window()
            return result["value"]

        if threading.current_thread() is threading.main_thread():
            return _show()

        ready = threading.Event()

        def _show_and_signal():
            _show()
            ready.set()

        if tk._default_root:
            tk._default_root.after(0, _show_and_signal)
        else:
            _show_and_signal()
        ready.wait()
        return result["value"]

    @staticmethod
    def _normalize_cooldown_reason(reason: str) -> str:
        text = str(reason or "").strip()
        if not text:
            return "cause issues"
        lower = text.lower()
        if "can " in lower:
            idx = lower.rfind("can ")
            return text[idx + 4:].strip().rstrip(".")
        if lower.startswith("may need to "):
            return ("require you to " + text[12:]).strip().rstrip(".")
        if lower.startswith("may "):
            return text[4:].strip().rstrip(".")
        if lower.startswith("takes "):
            return ("take " + text[6:]).strip().rstrip(".")
        if lower.startswith("runs "):
            return ("run " + text[5:]).strip().rstrip(".")
        if lower.startswith("uses "):
            return ("use " + text[5:]).strip().rstrip(".")
        return text.rstrip(".")

    

    @staticmethod
    def _parse_freed_mb(message: str) -> float:
        if not message:
            return 0.0
        match = re.search(r"([\d\.]+)\s*(GB|MB)", message, re.IGNORECASE)
        if not match:
            return 0.0
        value = float(match.group(1))
        unit = match.group(2).upper()
        if unit == "GB":
            return value * 1024
        return value

    @staticmethod
    def _tool_matches_query(tool: Dict[str, Any], section_title: str, query: str) -> bool:
        searchable = [
            str(tool.get("id", "")),
            str(tool.get("title", "")),
            str(tool.get("description", "")),
            str(tool.get("detailed_description", "")),
            str(tool.get("category", "")),
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

    @staticmethod
    def _strip_non_ascii(text: str) -> str:
        raw = str(text or "")
        return raw.encode("ascii", "ignore").decode("ascii").strip()

    def get_ui_tool(self, tool: Dict[str, Any], professional_mode: bool = False) -> Dict[str, Any]:
        """Return a tool dictionary normalized for UI rendering mode."""
        tool_ui = dict(tool or {})
        if not professional_mode:
            return tool_ui

        tool_ui["title"] = self._strip_non_ascii(tool_ui.get("title", ""))
        tool_ui["icon"] = ""
        tool_ui["description"] = ""

        risk_level = str(tool_ui.get("risk_level", "")).lower()
        if risk_level in {"safe", "low"}:
            tool_ui["risk_level"] = ""
        return tool_ui
