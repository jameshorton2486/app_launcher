from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "treesize"
    title = "TreeSize Free"
    category = "Storage & Files"
    tab = "maintenance"
    icon = "📊"
    description = "Visual disk space analyzer - find large files"
    download_url = "https://www.jam-software.com/treesize_free"

