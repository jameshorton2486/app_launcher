from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "bcuninstaller"
    title = "BCUninstaller"
    category = "System Health"
    tab = "maintenance"
    icon = "📦"
    description = "Thorough software removal with leftover cleanup"
    download_url = "https://www.bcuninstaller.com/"

