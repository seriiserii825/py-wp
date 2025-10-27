from typing import Sequence
from classes.utils.Command import Command
from classes.utils.Print import Print
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths
from pathlib import Path
from dto.CsvPluginDto import CsvPluginDto


class Plugin:
    def __init__(self):
        self.wp_plugins_dir_path = WPPaths.get_plugin_path()
        self.plugins_wp_path = WPPaths.get_plugins_wp_path()

    def list_installed_plugins(self):
        try:
            plugins = self._get_installed_plugins()
            plugins = self._sort_plugins(plugins)
            if not plugins:
                Print.error("No plugins found in the WordPress plugins directory.")
            else:
                Print.info("Installed Plugins:")
                for plugin in plugins:
                    print(plugin)
        except Exception as e:
            Print.error(f"Error listing installed plugins: {e}")

    def _get_installed_plugins(self) -> Sequence[str]:
        try:
            plugins: Sequence[str] = [
                p.name for p in Path(self.wp_plugins_dir_path).iterdir() if p.is_dir()
            ]
            plugins = self._sort_plugins(plugins)
            return plugins

        except Exception as e:
            Print.error(f"Error retrieving installed plugins: {e}")
            return []

    def install_all_plugins(self, plugins: Sequence[CsvPluginDto]):
        if not plugins:
            Print.error("No plugins provided for installation.")
            return
        was_installed = []
        for plugin in plugins:
            slug = self._install_plugin(plugin)
            was_installed.append(slug)
        if len(was_installed) == 0:
            Print.error("All plugins are already installed.")

    def install_plugin_by_slug(self, plugins: Sequence[CsvPluginDto]):
        if not plugins:
            Print.error("No plugins provided for installation.")
            return
        plugin_slugs = [plugin.plugin_slug.strip() for plugin in plugins]
        installed_plugins = self._get_installed_plugins()
        plugins_to_install: list[str] = list(set(plugin_slugs) - set(installed_plugins))
        # sort by alphabetical order
        sorted_plugins = self._sort_array_alphabetically(plugins_to_install)
        # sorted to sequence
        plugins_to_install = list(sorted_plugins)
        print(f"plugins_to_install:: {plugins_to_install:}")
        selected_plugin = Select.select_one(plugins_to_install)
        print(f"selected_plugin: {selected_plugin}")
        if self._is_already_installed(selected_plugin):
            Print.error(f"Plugin '{selected_plugin}' is already installed.")
            return
        self._install_plugin(
            next(p for p in plugins if p.plugin_slug.strip() == selected_plugin)
        )

    def _is_already_installed(self, plugin_slug: str) -> bool:
        return Path.exists(self.wp_plugins_dir_path / plugin_slug)

    def uninstall_plugin(self):
        installed_plugins = self._get_installed_plugins()
        installed_plugins = self._sort_plugins(installed_plugins)
        selected_plugin = Select.select_one(installed_plugins)
        Command.run(f"wp plugin deactivate {selected_plugin}")
        Command.run(f"wp plugin uninstall {selected_plugin}")
        Print.success(f"Plugin '{selected_plugin}' has been uninstalled successfully.")

    def _sort_plugins(self, plugins: Sequence[str]) -> Sequence[str]:
        return sorted(plugins, key=lambda x: x.lower())

    def _sort_array_alphabetically(self, array: Sequence[str]) -> Sequence[str]:
        return sorted(array, key=lambda x: x.lower())

    def _install_plugin(self, plugin: CsvPluginDto) -> str:
        slug = plugin.plugin_slug.strip()
        filename = plugin.filename.strip()
        if self._is_already_installed(slug):
            Print.info(f"Plugin '{slug}' is already installed. Skipping.")
            return ""
        if filename == "False":
            Command.run(f"wp plugin install {slug} --activate")
            Print.success(f"Plugin '{slug}' installed successfully.")
            return slug
        else:
            plugin_path = Path(self.plugins_wp_path) / filename
            if not plugin_path.exists():
                Print.error(f"Plugin file {slug} does not exist.")
                exit(1)
            Command.run(f"wp plugin install {plugin_path} --activate")
            Print.success(
                f"Plugin '{slug}' installed successfully from file {filename}."
            )
            return slug
