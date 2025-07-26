from classes.csv.CsvFile import CsvFile
from classes.utils.WPPaths import WPPaths
from dto.CsvPluginDto import CsvPluginDto


class BasePluginsCsv(CsvFile):
    def __init__(self):
        super().__init__(f"{WPPaths.get_csv_folder_path()}/base-plugins.csv")
        self.plugins_folder_path = WPPaths.get_plugin_path()

    def print_plugins(self):
        self.print_csv(title="Base plugins")

    def get_plugin_dtos(self) -> list[CsvPluginDto]:
        rows = self.get_rows_except_first()
        return [
            CsvPluginDto(
                plugin_slug=row.get("plugin_slug", "").strip(),
                filename=row.get("filename", "").strip(),
            )
            for row in rows
            if row.get("plugin_slug")
        ]

    def is_base_plugins_installed(self) -> bool:
        plugin_dtos = self.get_plugin_dtos()
        if not plugin_dtos:
            return False
        installed_plugins = self.get_installed_plugins_from_wp()
        for plugin in plugin_dtos:
            if plugin.plugin_slug not in installed_plugins:
                return False
        return True

    def get_installed_plugins_from_wp(self) -> list[str]:
        try:
            plugins = [
                p.name for p in WPPaths.get_plugin_path().iterdir() if p.is_dir()
            ]
            return plugins
        except Exception as e:
            print(f"Error retrieving installed plugins: {e}")
            return []
