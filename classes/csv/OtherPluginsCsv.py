from classes.csv.CsvFile import CsvFile
from classes.utils.WPPaths import WPPaths
from dto.CsvPluginDto import CsvPluginDto


class OtherPluginsCsv(CsvFile):
    def __init__(self):
        super().__init__(f"{WPPaths.get_csv_folder_path()}/other-plugins.csv")

    def print_plugins(self):
        self.print_csv(title="Other plugins")

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
