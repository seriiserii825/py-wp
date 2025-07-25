from classes.csv.CsvFile import CsvFile
from classes.utils.WPPaths import WPPaths


class OtherPluginsCsv(CsvFile):
    def __init__(self):
        super().__init__(f"{WPPaths.get_csv_folder_path()}/other-plugins.csv")

    def print_plugins(self):
        self.print_csv(title="Other plugins")
