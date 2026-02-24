from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "bleachbit"
    title = "BleachBit"
    category = "System Health"
    tab = "maintenance"
    icon = "🧹"
    description = "Privacy-focused open source cleaner"
    download_url = "https://www.bleachbit.org/download"

