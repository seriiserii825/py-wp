import csv

from classes.utils.WPPaths import WPPaths


class CsvPlugin:
    def __init__(self):
        self.csv_folder_path = WPPaths.get_csv_folder_path()
        self.base_plugins_csv_path = f"{self.csv_folder_path}/base-plugins.csv"
        self.other_plugins_csv_path = f"{self.csv_folder_path}/other-plugins.csv"

    def read_csv(self, file_path: str) -> list[dict] | None:
        try:
            with open(file_path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                return list(reader)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def print_base_plugins(self):
        """Вывести базовые плагины в консоль"""
        base_plugins = self._get_base_plugins()
        if base_plugins is None:
            print("Не удалось загрузить базовые плагины.")
            return
        self._print_table(base_plugins, title="Базовые плагины")

    def _get_base_plugins(self) -> list[dict] | None:
        """Получить базовые плагины из CSV"""
        return self.read_csv(self.base_plugins_csv_path)

    def print_other_plugins(self):
        """Вывести другие плагины в консоль"""
        other_plugins = self._get_other_plugins()
        if other_plugins is None:
            print("Не удалось загрузить другие плагины.")
            return
        self._print_table(other_plugins, title="Другие плагины")

    def _get_other_plugins(self) -> list[dict] | None:
        """Получить другие плагины из CSV"""
        return self.read_csv(self.other_plugins_csv_path)

    def _print_table(self, rows: list[dict], title: str = ""):
        if not rows:
            print(f"Не удалось загрузить {title.lower()}.")
            return

        headers = rows[0].keys()
        col_widths = {header: len(header) for header in headers}

        # Calculate max column width per header
        for row in rows:
            for header in headers:
                col_widths[header] = max(
                    col_widths[header], len(str(row.get(header, "")))
                )

        # Print title
        if title:
            print(f"\n{title}")
            print("-" * sum(col_widths.values()) + "-" * (3 * len(col_widths)))

        # Print header
        header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
        print(header_row)
        print("-" * len(header_row))

        # Print rows
        for row in rows:
            line = " | ".join(
                str(row.get(header, "")).ljust(col_widths[header]) for header in headers
            )
            print(line)
