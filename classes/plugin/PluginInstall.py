from classes.utils.Command import Command
from classes.utils.Print import Print
from classes.utils.WPPaths import WPPaths
from pathlib import Path


class PluginInstall:
    def __init__(self):
        self.wp_plugins_dir_path = WPPaths.get_plugin_path()

    # def install_required_plugins(self):
    #     print(f"plugin_path: {self.plugins_dir_path}")
    #
    #     for plugin in self.required_plugins:
    #         if not self.exist_plugin_in_folder(plugin):
    #             Print.info(f"Installing plugin: {plugin}")
    #             Command.run(f"wp plugin install {plugin} --activate --force")
    #         else:
    #             Print.error(f"Plugin {plugin} already exists, skipping installation.")
    #
    # def exist_plugin_in_folder(self, plugin: str) -> bool:
    #     plugin_path = f"{self.plugins_dir_path}/{plugin}"
    #     return Path(plugin_path).exists()
