import csv
from pathlib import Path

from classes.utils.WPPaths import WPPaths

FIELDNAMES = ["project", "path"]


class MntProjectsPathsCsv:
    def __init__(self):
        self.file_path = WPPaths.get_script_dir_path() / "mnt-projects-paths.csv"

    def _read_rows(self) -> list[dict]:
        if not self.file_path.exists():
            return []
        with open(self.file_path, encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=FIELDNAMES)
            return list(reader)

    def get_path_for_project(self, project_name: str) -> str | None:
        for row in self._read_rows():
            if row.get("project") == project_name:
                return row.get("path")
        return None

    def save_path_for_project(self, project_name: str, path: str) -> None:
        rows = [
            row for row in self._read_rows() if row.get("project") != project_name
        ]
        rows.append({"project": project_name, "path": path})
        with open(self.file_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writerows(rows)
