import os
from pathlib import Path

from rich import print
from simple_term_menu import TerminalMenu

from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print
from classes.utils.Select import Select


class FilesHandle:
    def list_files(self, path_to_list, file_extension=None) -> None:
        abs_path = Path(path_to_list).resolve()
        print(f"[green]Listing files in ================ {abs_path}")

        files = [f for f in abs_path.iterdir() if f.is_file()]
        if not files:
            print("[yellow]No files found in this directory.")
            return

        for f in files:
            if file_extension:
                if f.name.endswith(file_extension):
                    print(f.name)
            else:
                print(f.name)

    def list_dir(self, path_to_list=""):
        print(f"[blue]Listing directories in ================ {path_to_list}")
        abs_path = Path(path_to_list).resolve()
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    print(entry.name)

    def create_or_choose_directory(self, path_to_dir="") -> str:
        current_path = ""
        abs_path = str(Path(path_to_dir).resolve())  # ✅ Абсолютный путь
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        self.list_dir(abs_path)
        select_or_create = Select.select_one(["Select", "Create"])
        if select_or_create == "Create":
            dir_name = InputValidator.get_string("Enter directory name: ")
            current_path = str(Path(abs_path) / dir_name)
            os.makedirs(current_path)
            print("Directory created")
            return current_path
        else:
            selected_dir = self.choose_dir(abs_path)
            return str(Path(path_to_dir) / selected_dir[0])

    def choose_dir(self, path_to_dir):
        choosed_dir = []
        with os.scandir(path_to_dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    choosed_dir.append(entry.name)
        choosed_dir.sort()
        selected_dir = Select.select_with_fzf(choosed_dir)
        return selected_dir

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
