import json
import unittest

from src.utils.constants import TOOLS_FILE
from src.utils.tool_registry import ToolRegistry


class RegistryIntegrityTests(unittest.TestCase):
    def test_tools_json_is_valid(self):
        with open(TOOLS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertIsInstance(data, dict)
        self.assertIn("sections", data)

    def test_registry_has_no_indexing_issues(self):
        registry = ToolRegistry()
        registry.load_tools(TOOLS_FILE)
        self.assertEqual([], registry.get_integrity_issues())

    def test_expected_plugins_are_registered(self):
        registry = ToolRegistry()
        registry.load_tools(TOOLS_FILE)
        for tool_id in (
            "bleachbit",
            "bcuninstaller",
            "autoruns",
            "crystaldiskinfo",
            "treesize",
            "everything",
            "process_lasso",
            "shutup10",
        ):
            self.assertIsNotNone(registry.get_tool_by_id(tool_id), f"Missing tool: {tool_id}")

    def test_refactor_toolset_shape(self):
        with open(TOOLS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        sections = data["sections"]
        self.assertEqual(7, len(sections))
        self.assertEqual(
            [
                "QUICK CLEANUP",
                "MEMORY & DISK",
                "NETWORK",
                "SYSTEM REPAIR",
                "PRIVACY",
                "PERFORMANCE",
                "DEVELOPER",
            ],
            [section["title"] for section in sections],
        )
        self.assertEqual(29, sum(len(section.get("tools", [])) for section in sections))

    def test_performance_section_is_dev_focused(self):
        with open(TOOLS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        performance_section = next(
            section for section in data["sections"] if section["title"] == "PERFORMANCE"
        )
        performance_tool_ids = [tool["id"] for tool in performance_section.get("tools", [])]

        self.assertEqual(
            ["balanced_plan", "high_performance_plan", "power_options"],
            performance_tool_ids,
        )
        for removed_id in ("enable_hags", "disable_hags", "disable_vbs"):
            self.assertNotIn(removed_id, performance_tool_ids)


if __name__ == "__main__":
    unittest.main()
