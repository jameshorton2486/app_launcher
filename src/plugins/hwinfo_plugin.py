from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "hwinfo"
    title = "HWiNFO"
    category = "System Monitoring"
    tab = "maintenance"
    icon = "🖥"
    description = "Comprehensive hardware monitoring"
    download_url = "https://www.hwinfo.com/download/"

