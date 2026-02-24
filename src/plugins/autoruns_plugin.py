from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "autoruns"
    title = "Autoruns"
    category = "System Health"
    tab = "maintenance"
    icon = "🚀"
    description = "Microsoft Sysinternals startup manager"
    download_url = "https://learn.microsoft.com/sysinternals/downloads/autoruns"
    requires_admin = True

