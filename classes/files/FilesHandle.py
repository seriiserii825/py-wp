from datetime import datetime
import os
from pathlib import Path
from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print
from classes.utils.Select import Select

from rich import print
from rich.console import Console
from rich.table import Table
from simple_term_menu import TerminalMenu

console = Console()


def _print_in_columns(items):
    import math
    term = os.get_terminal_size()
    max_len = max(len(i) for i in items) + 2
    num_cols = max(1, term.columns // max_len)
    num_rows = math.ceil(len(items) / num_cols)
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    for _ in range(num_cols):
        table.add_column()
    for row_i in range(num_rows):
        row = []
        for col_i in range(num_cols):
            idx = col_i * num_rows + row_i
            row.append(items[idx] if idx < len(items) else "")
        table.add_row(*row)
    console.print(table)


class FilesHandle:
    def list_files(self, path_to_list, file_extension=None, mtime=True) -> None:
        abs_path = Path(path_to_list).resolve()
        print(f"[green]Listing files in ================ {abs_path}")

        files = [f for f in abs_path.iterdir() if f.is_file()]
        if not files:
            print("[yellow]No files found in this directory.")
            return
        sorted_files = sorted(files, key=lambda f: f.name.lower())

        for f in sorted_files:
            if file_extension:
                if f.name.endswith(file_extension):
                    self._show_file(f, mtime)
            else:
                self._show_file(f, mtime)

    def _show_file(self, file_path, mtime):
        timestamp = file_path.stat().st_mtime
        file_name = file_path.name
        if mtime:
            # Convert timestamp → human readable
            human_mtime = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"{file_name} - {human_mtime}")
        else:
            print(file_name)

    def list_dir(self, path_to_list=""):
        print(f"[blue]Listing directories in ================ {path_to_list}")
        abs_path = Path(path_to_list).resolve()
        with os.scandir(abs_path) as entries:
            sored_dirs = sorted(
                (entry for entry in entries if entry.is_dir()),
                key=lambda e: e.name.lower(),
            )
            names = [entry.name for entry in sored_dirs]
            terminal_lines = os.get_terminal_size().lines
            if len(names) > terminal_lines - 4:
                _print_in_columns(names)
            else:
                for name in names:
                    print(name)

    def create_or_choose_directory(self, path_to_dir="") -> str:
        abs_path = str(Path(path_to_dir).resolve())  # ✅ Абсолютный путь
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        self.list_dir(abs_path)

        if not self._has_dirs(path_to_dir):
            return self._create_dir(abs_path)

        select_or_create = Select.select_one(["Select", "Create"])
        if select_or_create == "Create":
            return self._create_dir(abs_path)
        else:
            selected_dir = self.choose_dir(abs_path)
            return str(Path(path_to_dir) / selected_dir[0])

    def _create_dir(self, abs_path):
        dir_name = InputValidator.get_string("Enter directory name: ")
        current_path = str(Path(abs_path) / dir_name)
        os.makedirs(current_path)
        print("Directory created")
        return current_path

    def choose_dir(self, path_to_dir):
        choosed_dir = []
        abs_path = Path(path_to_dir).resolve()
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    choosed_dir.append(entry.name)
        choosed_dir.sort()
        selected_dir = Select.select_with_fzf(choosed_dir)
        return selected_dir

    def _has_dirs(self, path_to_dir):
        abs_path = Path(path_to_dir).resolve()
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    return True
        return False

    def choose_file(self, path_to_dir, extension=None):
        choosed_files = []
        for entry in os.listdir(path_to_dir):
            if os.path.isfile(os.path.join(path_to_dir, entry)):
                if extension:
                    if entry.endswith(extension):
                        choosed_files.append(entry)
                else:
                    choosed_files.append(entry)
        if len(choosed_files) == 0:
            Print.error("No files found")
            exit()
        else:
            return Select.select_one(choosed_files)

    def append_to_file(self, file_path, text):
        with open(file_path, "a") as f:
            f.write(text)
        os.system(f"bat {file_path}")

    def select_multiple(self, options):
        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            show_search_hint=True,
            preview_command="bat --color=always {}",
            preview_size=0.75,
        )
        terminal_menu.show()
        return terminal_menu.chosen_menu_entries
