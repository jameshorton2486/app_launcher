"""Base class for external tool plugins."""

from src.services.external_tool_service import ExternalToolService


class BaseExternalToolPlugin:
    id = ""
    title = ""
    category = "External Tools"
    tab = "maintenance"
    icon = ""
    description = ""
    download_url = ""
    requires_admin = False

    def launch(self, config_manager):
        service = ExternalToolService(config_manager)
        return service.launch_tool(self.id)

