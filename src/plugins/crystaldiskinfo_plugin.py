from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "crystaldiskinfo"
    title = "CrystalDiskInfo"
    category = "System Health"
    tab = "maintenance"
    icon = "💿"
    description = "Disk health monitor showing S.M.A.R.T. data"
    download_url = "https://crystalmark.info/en/download/"

