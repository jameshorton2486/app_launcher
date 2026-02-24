from src.plugins.plugin_base import BaseExternalToolPlugin


class ToolPlugin(BaseExternalToolPlugin):
    id = "process_lasso"
    title = "Process Lasso"
    category = "Performance"
    tab = "optimization"
    icon = "🎛"
    description = "Process priority and CPU affinity manager"
    download_url = "https://bitsum.com/processlasso/"

