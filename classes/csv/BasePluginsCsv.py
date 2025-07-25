from classes.csv.CsvFile import CsvFile
from classes.utils.WPPaths import WPPaths


class BasePluginsCsv(CsvFile):
    def __init__(self):
        super().__init__(f"{WPPaths.get_csv_folder_path()}/base-plugins.csv")

    def print_plugins(self):
        self.print_csv(title="Base plugins")
