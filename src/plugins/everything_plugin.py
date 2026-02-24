from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "everything"
    title = "Everything Search"
    category = "Storage & Files"
    tab = "maintenance"
    icon = "🔍"
    description = "Instant file search (much faster than Windows)"
    download_url = "https://www.voidtools.com/downloads/"

