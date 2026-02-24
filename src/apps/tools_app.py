from src.app import AppLauncher


def create_app() -> AppLauncher:
    return AppLauncher(
        enabled_tabs=["Maintenance", "Optimization", "Downloads"],
        show_power_tools_button=False,
        power_tools_command=None,
        dashboard_read_only=False,
        validate_tools_on_startup=True,
        window_title="App Launcher Power Tools (v2.0)",
        sidebar_title="Power Tools",
        show_app_selector=False
    )
