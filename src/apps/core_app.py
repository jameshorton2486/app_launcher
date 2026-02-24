from pathlib import Path
import sys

from src.app import AppLauncher


def _power_tools_command() -> list[str]:
    root = Path(__file__).resolve().parents[2]
    tools_entry = root / "app_launcher_tools_main.py"
    return [sys.executable, str(tools_entry)]


def create_app() -> AppLauncher:
    return AppLauncher(
        enabled_tabs=["Dashboard", "Projects", "Settings"],
        show_power_tools_button=True,
        power_tools_command=_power_tools_command(),
        dashboard_read_only=True,
        validate_tools_on_startup=False,
        window_title="James's Project Launcher (v2.0)",
        sidebar_title="App Launcher",
        show_app_selector=None
    )
