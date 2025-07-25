import csv

from classes.utils.Menu import Menu


class CsvFile:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_csv(self) -> list[dict] | None:
        try:
            with open(self.file_path, encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                return list(reader)
        except Exception as e:
            print(f"Error reading CSV file {self.file_path}: {e}")
            return None

    def print_csv(self, title: str = ""):
        rows = self.read_csv()
        if rows is None:
            print(f"Error readin file {self.file_path}.")
            return
        self._print_table(rows, title=title)

    def _print_table(self, rows: list[dict], title: str = ""):
        headers = rows[0].keys() if rows else []
        if not headers:
            print(f"Empty CSV: {self.file_path}")
            return
        rows_without_headers = rows[1:] if len(rows) > 1 else []
        Menu.display(
            title=title,
            columns=list(headers),
            rows=[list(row.values()) for row in rows_without_headers],
        )
