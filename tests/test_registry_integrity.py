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


if __name__ == "__main__":
    unittest.main()

