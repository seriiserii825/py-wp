from abc import ABC
from pathlib import Path


class PluginAbc(ABC):
    def __init__(self):
        self.user_dir_path = Path.home()
        self.plugins_dir_path = Path(f"{self.user_dir_path}/Documents/plugins-wp")
